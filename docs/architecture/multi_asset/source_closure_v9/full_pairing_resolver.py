"""既有 WORK versioned companion 的純來源輸入配對檢核；不編譯、不派工、不授權。

唯一信任入口是呼叫端從固定 Review Subject 取得的 expected_head_pin。
本檔不自行選擇 latest、不連網，也不將來源充分性轉成 Eligibility。
"""
from __future__ import annotations

import copy
import base64
import hashlib
import json
import pathlib
import re
from collections import Counter
from typing import Any

from jsonschema import Draft202012Validator

STANDARD = "https://json-schema.org/draft/2020-12/schema"
SUCCESS = "SOURCE_INPUTS_VERIFIED_NOT_ELIGIBLE"
REF_FIELDS = ("entity_id", "revision_id", "owner", "hash_domain", "source_hash")
PAIR_FIELDS = (
    "pair_id", "operation_id", "case_id", "source_ref", "schema_ref", "source",
    "schema", "resolution_id", "resolver_method", "producer", "consumers", "unit_aliases",
    "required_descendants", "source_profile", "source_version", "effective_dialect",
    "effective_schema", "effective_schema_ref", "source_representation", "source_binary",
    "source_snapshot_subject", "schema_origin_subject", "source_declaration_aliases",
    "source_declaration", "companion_entity_id", "companion_revision_id",
)


class ContractError(ValueError):
    """來源閉包不足一律明示拒絕，沒有略過或成功降級分支。"""
    def __init__(self, code: str, detail: Any = None):
        self.code = code
        self.detail = detail
        super().__init__(code + (": " + str(detail) if detail is not None else ""))


def canonical(value: Any) -> bytes:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False).encode("utf-8")


def sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def _object_pairs(pairs):
    result = {}
    for name, value in pairs:
        if name in result:
            raise ContractError("DUPLICATE_JSON_MEMBER", name)
        result[name] = value
    return result


def decode(raw: bytes):
    try:
        return json.loads(raw.decode("utf-8"), object_pairs_hook=_object_pairs,
                          parse_constant=lambda value: (_ for _ in ()).throw(ContractError("NONFINITE_JSON", value)))
    except ContractError:
        raise
    except Exception as error:
        raise ContractError("UNREADABLE_JSON_BODY", type(error).__name__) from error


def pointer_get(value, pointer):
    if pointer in ("", "#"):
        return value
    if not isinstance(pointer, str) or not pointer.startswith("#/"):
        raise ContractError("INVALID_JSON_POINTER", pointer)
    try:
        for token in pointer[2:].split("/"):
            token = token.replace("~1", "/").replace("~0", "~")
            value = value[int(token)] if isinstance(value, list) else value[token]
        return value
    except (KeyError, IndexError, ValueError, TypeError) as error:
        raise ContractError("MISSING_REQUIRED_POINTER", pointer) from error


def _unique(rows, field, code):
    if not isinstance(rows, list):
        raise ContractError("INVALID_REQUIRED_COLLECTION", field)
    result = {}
    for row in rows:
        if not isinstance(row, dict) or field not in row:
            raise ContractError("INVALID_REQUIRED_ROW", field)
        identifier = row[field]
        if not isinstance(identifier, str) or not identifier:
            raise ContractError("INVALID_REQUIRED_ID", field)
        if identifier in result:
            raise ContractError(code, identifier)
        result[identifier] = row
    return result


def _rows(document, *keys):
    if isinstance(document, list):
        return document
    for key in keys:
        if isinstance(document.get(key), list):
            return document[key]
    raise ContractError("MISSING_REQUIRED_COLLECTION", keys)


def _exact_set(actual, expected, code):
    if not isinstance(actual, list) or not isinstance(expected, list):
        raise ContractError(code, "NOT_ARRAY")
    if len(actual) != len(set(actual)) or len(expected) != len(set(expected)):
        raise ContractError("DUPLICATE_OR_CONFLICTING_PAIRS", code)
    if set(actual) != set(expected):
        raise ContractError(code, {"missing": sorted(set(expected) - set(actual)), "unexpected": sorted(set(actual) - set(expected))})


class SourceInputVerifier:
    """單一固定來源觀測的檢核器；跨檔案異動後必須建立新實例。

    以 finish() 重新讀取本次全部 pins，偵測讀取期間漂移。
    這是 source-only deterministic check，不是 filesystem/SQL 原子性證明。
    """
    def __init__(self, root, *, expected_head_pin, expected_subject):
        self.root = pathlib.Path(root).resolve(strict=True)
        self.expected_subject = expected_subject
        self.observed = {}
        self.cache = {}
        self.json_cache = {}
        self._pair_results = {}
        self._operation_results = {}
        self._unit_results = {}
        self.head = self.read_json(expected_head_pin)
        self._subject(self.head)
        if self.head.get("authority_effect") != "NONE":
            raise ContractError("SOURCE_HEAD_CANNOT_GRANT_AUTHORITY")
        mandatory = ("expected_pair_spec", "actual_pair_catalog", "operation_index", "unit_index", "base_units", "api_catalog", "ui_catalog", "producer_consumer_map", "resolver")
        if any(name not in self.head for name in mandatory):
            raise ContractError("MISSING_HEAD_AUTHORITY_INPUT", [name for name in mandatory if name not in self.head])
        # 自身也是固定輸入；不以程式內的最新版路徑代替 Review Subject 的 pin。
        self.read(self.head["resolver"])
        self.spec = self.read_json(self.head["expected_pair_spec"])
        self.actual = self.read_json(self.head["actual_pair_catalog"])
        self._subject(self.spec)
        self._subject(self.actual)
        self.operations = _unique(_rows(self.spec, "operations"), "operation_id", "AMBIGUOUS_REQUIRED_OPERATION")
        self.expected_pairs = _unique(_rows(self.spec, "pairs"), "pair_id", "DUPLICATE_EXPECTED_PAIR")
        self.actual_pairs = _unique(_rows(self.actual, "pairs", "rows"), "pair_id", "DUPLICATE_OR_CONFLICTING_PAIRS")
        self.expected_units = _unique(_rows(self.spec, "units"), "unit_id", "DUPLICATE_EXPECTED_UNIT")
        operation_index = self.read_json(self.head["operation_index"])
        unit_index = self.read_json(self.head["unit_index"])
        self._subject(operation_index)
        self._subject(unit_index)
        self.operation_index = _unique(_rows(operation_index, "operations", "rows"), "operation_id", "AMBIGUOUS_OPERATION_COMPANION")
        self.unit_index = _unique(_rows(unit_index, "units", "rows"), "unit_id", "AMBIGUOUS_UNIT_COMPANION")
        self.plans = self.read_json(self.head["base_units"])
        self.base_units = _unique(_rows(self.plans, "units"), "unit_id", "DUPLICATE_BASE_UNIT")
        self.api = self.read_json(self.head["api_catalog"])
        self.ui = self.read_json(self.head["ui_catalog"])
        self.mapping = self.read_json(self.head["producer_consumer_map"])
        self.api_operations = _unique(_rows(self.api, "endpoints"), "operation_id", "DUPLICATE_API_OPERATION")
        self.mapped_operations = _unique(_rows(self.mapping, "operations"), "operation_id", "DUPLICATE_OPERATION_OWNER_MAPPING")
        if len(self.api_operations) != 95 or len(self.expected_units) != 96:
            raise ContractError("PROTECTED_IDENTITY_COVERAGE_CONFLICT")
        self._register_references(self.spec)
        self._register_references(self.actual)
        self._diff_pair_sets()
        _exact_set(list(self.operation_index), list(self.operations), "OPERATION_INDEX_SET_MISMATCH")
        _exact_set(list(self.unit_index), list(self.expected_units), "UNIT_INDEX_SET_MISMATCH")
        _exact_set(list(self.base_units), list(self.expected_units), "BASE_UNIT_SET_MISMATCH")
        # Expected 的固定原始契約／推導來源同樣必須存在，不能只信衍生摘要。
        self._read_nested_pins(self.spec.get("authority_sources", []))
        self._read_nested_pins(self.spec.get("derivation_sources", []))
        self._read_nested_pins(self.spec.get("sources", []))
        catalog_pin = self.head.get("schema_resolution_catalog") or self.actual.get("schema_resolution_catalog")
        if not catalog_pin:
            raise ContractError("MISSING_SCHEMA_RESOLUTION_CATALOG")
        self.catalog = self.read_json(catalog_pin)
        self.resolutions = _unique(_rows(self.catalog, "records"), "record_id", "AMBIGUOUS_SCHEMA_RESOLUTION")
        adapter_pin = self.catalog.get("resolver")
        if not adapter_pin:
            raise ContractError("MISSING_HISTORICAL_ADAPTER_PIN")
        adapter_raw = self.read(adapter_pin)
        self.adapter = {"__name__": "_fixed_protected_v8_schema_contract", "__file__": str(self.root / adapter_pin["path"])}
        # 僅載入已固定的純來源 adapter；不 import 未驗路徑、不建立 pycache。
        exec(compile(adapter_raw, adapter_pin["path"], "exec"), self.adapter)

    def _subject(self, document):
        if not isinstance(document, dict) or document.get("subject") != self.expected_subject:
            raise ContractError("SUBJECT_VERSION_MISMATCH")

    def read(self, pin):
        if not isinstance(pin, dict) or not isinstance(pin.get("path"), str) or not re.fullmatch(r"[0-9a-f]{64}", pin.get("raw_bytes_sha256", "")):
            raise ContractError("INVALID_PIN")
        text = pin["path"]
        relative = pathlib.PurePosixPath(text)
        windows = pathlib.PureWindowsPath(text)
        if not text or "\\" in text or ":" in text or relative.is_absolute() or windows.drive or any(part in ("..", ".") for part in relative.parts):
            raise ContractError("UNSAFE_REFERENCE_PATH", text)
        prior = self.observed.get(text)
        if prior and prior != pin["raw_bytes_sha256"]:
            raise ContractError("SAME_PATH_DIFFERENT_CONTENT_IDENTITY", text)
        if text in self.cache:
            return self.cache[text]
        path = self.root.joinpath(*relative.parts)
        for component in (self.root, *[self.root.joinpath(*relative.parts[:index]) for index in range(1, len(relative.parts) + 1)]):
            try:
                stat = component.lstat()
            except OSError as error:
                raise ContractError("UNREADABLE_REQUIRED_SOURCE", text) from error
            if component.is_symlink() or (getattr(stat, "st_file_attributes", 0) & 0x400):
                raise ContractError("REFERENCE_REPARSE_DENIED", text)
        if not path.resolve(strict=True).is_relative_to(self.root) or not path.is_file():
            raise ContractError("REFERENCE_OUTSIDE_ROOT", text)
        prior = self.observed.get(text)
        if prior and prior != pin["raw_bytes_sha256"]:
            raise ContractError("SAME_PATH_DIFFERENT_CONTENT_IDENTITY", text)
        if text not in self.cache:
            try:
                raw = path.read_bytes()
            except OSError as error:
                raise ContractError("UNREADABLE_REQUIRED_SOURCE", text) from error
            if sha(raw) != pin["raw_bytes_sha256"]:
                raise ContractError("PIN_HASH_CONFLICT", text)
            self.cache[text] = raw
            self.observed[text] = pin["raw_bytes_sha256"]
        return self.cache[text]

    def read_json(self, pin):
        raw = self.read(pin)
        cache_key = (pin["path"], pin["raw_bytes_sha256"])
        if cache_key not in self.json_cache:
            self.json_cache[cache_key] = decode(raw)
        return self.json_cache[cache_key]

    def _read_nested_pins(self, value):
        if isinstance(value, dict):
            if "path" in value and "raw_bytes_sha256" in value:
                self.read(value)
            for child in value.values():
                self._read_nested_pins(child)
        elif isinstance(value, list):
            for child in value:
                self._read_nested_pins(child)

    def _register_references(self, value):
        seen = getattr(self, "_identity_hashes", {})
        self._identity_hashes = seen
        if isinstance(value, dict):
            if all(isinstance(value.get(field), str) for field in REF_FIELDS):
                identity = tuple(value[field] for field in REF_FIELDS[:-1])
                if identity in seen and seen[identity] != value["source_hash"]:
                    raise ContractError("SAME_ID_REVISION_DIFFERENT_CONTENT", identity)
                seen[identity] = value["source_hash"]
            for child in value.values():
                self._register_references(child)
        elif isinstance(value, list):
            for child in value:
                self._register_references(child)

    def _diff_pair_sets(self):
        missing = sorted(set(self.expected_pairs) - set(self.actual_pairs))
        unexpected = sorted(set(self.actual_pairs) - set(self.expected_pairs))
        invalid = []
        versions = []
        for identifier in sorted(set(self.expected_pairs) & set(self.actual_pairs)):
            expected = self.expected_pairs[identifier]
            actual = self.actual_pairs[identifier]
            for field in sorted(set(expected) | set(actual)):
                if field not in actual or field not in expected or canonical(actual.get(field)) != canonical(expected.get(field)):
                    difference = {"pair_id": identifier, "field": field, "expected": expected.get(field), "actual": actual.get(field)}
                    invalid.append(difference)
                    if field in ("source_ref", "schema_ref", "source_version", "source_profile", "effective_schema_ref", "effective_dialect", "schema_origin_subject", "source_snapshot_version", "companion_identity"):
                        versions.append(difference)
        self.pair_difference = {
            "EXPECTED_REQUIRED_PAIRS": sorted(self.expected_pairs),
            "ACTUAL_VALID_RESOLVED_PAIRS": [],
            "MISSING_PAIRS": missing, "INVALID_PAIRS": invalid, "UNEXPECTED_PAIRS": unexpected,
            "VERSION_MISMATCHES": versions, "AMBIGUOUS_RESOLUTIONS": [],
            "DUPLICATE_OR_CONFLICTING_PAIRS": [], "UNREADABLE_BODIES": [],
        }
        if missing or unexpected or invalid:
            raise ContractError("EXPECTED_ACTUAL_REQUIRED_PAIR_SET_MISMATCH", self.pair_difference)

    def _check_schema_references(self, schema):
        def visit(value):
            if isinstance(value, dict):
                for name, child in value.items():
                    if name in ("$ref", "$dynamicRef"):
                        if not isinstance(child, str) or not child.startswith("#"):
                            raise ContractError("UNREGISTERED_EXTERNAL_SCHEMA_REFERENCE", child)
                        if child.startswith("#/"):
                            pointer_get(schema, child)
                        elif child != "#":
                            anchors = []
                            def gather(node):
                                if isinstance(node, dict):
                                    if node.get("$anchor") == child[1:] or node.get("$dynamicAnchor") == child[1:]:
                                        anchors.append(node)
                                    for nested in node.values(): gather(nested)
                                elif isinstance(node, list):
                                    for nested in node: gather(nested)
                            gather(schema)
                            if len(anchors) != 1:
                                raise ContractError("AMBIGUOUS_OR_MISSING_SCHEMA_ANCHOR", child)
                    visit(child)
            elif isinstance(value, list):
                for child in value: visit(child)
        visit(schema)

    def verify_pair(self, pair_id):
        if pair_id in self._pair_results:
            return self._pair_results[pair_id]
        if pair_id not in self.expected_pairs or pair_id not in self.actual_pairs:
            raise ContractError("MISSING_REQUIRED_PAIR", pair_id)
        pair = self.actual_pairs[pair_id]
        aliases = pair.get("source_declaration_aliases", [])
        declarations = [pair.get("source_declaration")] + [alias.get("source_declaration") for alias in aliases]
        if not declarations or any(item is None for item in declarations):
            raise ContractError("MISSING_SOURCE_DECLARATION_PROVENANCE", pair_id)
        for declaration in declarations:
            declared = pointer_get(self.read_json(declaration["source"]), declaration["pointer"])
            declared_source = declared.get("source_ref") or declared.get("subject_ref")
            if canonical(declared_source) != canonical(pair["source_ref"]) or canonical(declared.get("source_schema_ref")) != canonical(pair["schema_ref"]):
                raise ContractError("SOURCE_DECLARATION_IDENTITY_OR_REVISION_CONFLICT", pair_id)
        for alias in aliases:
            if sha(self.read(alias["source"])) != pair["source_ref"]["source_hash"] or sha(self.read(alias["schema"])) != pair["schema_ref"]["source_hash"]:
                raise ContractError("SOURCE_ALIAS_CONTENT_CONFLICT", pair_id)
        source_raw = self.read(pair["source"])
        schema_raw = self.read(pair["schema"])
        if pair["source_ref"]["hash_domain"] != "raw-bytes-sha256-v1" or sha(source_raw) != pair["source_ref"]["source_hash"]:
            raise ContractError("SOURCE_BODY_HASH_DOMAIN_OR_VALUE_CONFLICT", pair_id)
        # fixture-source-schema 域的歷史定義同為 exact raw SHA256；v7 複本
        # 仍保留該域。永久 Ref 與固定宣告不可因搬移而被重新命名。
        if pair["schema_ref"]["hash_domain"] not in ("raw-bytes-sha256-v1", "ma-fixture-source-schema-sha256-v1") or sha(schema_raw) != pair["schema_ref"]["source_hash"]:
            raise ContractError("SOURCE_SCHEMA_HASH_DOMAIN_OR_VALUE_CONFLICT", pair_id)
        resolution_id = pair.get("resolution_id")
        if resolution_id is not None:
            if resolution_id not in self.resolutions:
                raise ContractError("MISSING_REQUIRED_SCHEMA_ADAPTER", resolution_id)
            record = self.resolutions[resolution_id]
            if canonical(pair["source_ref"]) != canonical(record["source_ref"]) or canonical(pair["schema_ref"]) != canonical(record["original_schema_ref"]):
                raise ContractError("UNAUTHORIZED_LEGACY_ADAPTER_SOURCE", pair_id)
            if pair.get("resolver_method") != "EXPLICIT_V8_SCHEMA_SUCCESSOR" or pair.get("source_profile") != record["input_profile"] or pair.get("schema_origin_subject", pair.get("source_version")) != record["original_subject"]:
                raise ContractError("UNKNOWN_SOURCE_PROFILE_OR_VERSION", pair_id)
            if pair.get("effective_dialect") != STANDARD or pair.get("effective_schema") != record["effective_schema"] or pair.get("effective_schema_ref") != record["effective_schema_ref"]:
                raise ContractError("SCHEMA_EFFECTIVE_BINDING_CONFLICT", pair_id)
            binding = self.read_json(record["resolution_document"])
            expected_binding = {key: value for key, value in record.items() if key not in ("resolution_document", "resolution_ref")}
            if canonical(binding) != canonical(expected_binding):
                raise ContractError("SCHEMA_ADAPTER_BINDING_CONFLICT", pair_id)
            self.read(record["original_schema"])
            self.read(record["source"])
            effective_raw = self.read(record["effective_schema"])
            if record["effective_dialect"] != STANDARD:
                raise ContractError("UNKNOWN_SCHEMA_DIALECT", pair_id)
            try:
                effective = self.adapter["resolve"](record, pair["schema_ref"], record["input_profile"], record["original_subject"], schema_raw, source_raw, effective_raw)
            except Exception as error:
                raise ContractError("EXPLICIT_SCHEMA_ADAPTER_REJECTED", {"pair_id": pair_id, "reason": str(error)}) from error
        else:
            if pair.get("resolver_method") != "STANDARD_DIRECT_EXACT_SOURCE_SCHEMA" or pair.get("source_profile") != "EXACT_STANDARD_2020_12_SOURCE" or pair.get("effective_dialect") != STANDARD:
                raise ContractError("UNKNOWN_SOURCE_PROFILE", pair_id)
            effective = decode(schema_raw)
            if effective.get("$schema", STANDARD) != STANDARD:
                raise ContractError("UNKNOWN_SCHEMA_DIALECT", pair_id)
            try:
                Draft202012Validator.check_schema(effective)
                representation = pair.get("source_representation")
                if representation == "BASE64_OF_EXACT_RAW_BYTES" and pair.get("source_binary") is True:
                    source_value = base64.b64encode(source_raw).decode("ascii")
                elif representation == "JSON_PARSED_EXACT_RAW_BYTES" and pair.get("source_binary") is False:
                    source_value = decode(source_raw)
                else:
                    raise ContractError("UNKNOWN_SOURCE_REPRESENTATION", pair_id)
                Draft202012Validator(effective).validate(source_value)
            except Exception as error:
                raise ContractError("STANDARD_SCHEMA_OR_INSTANCE_REJECTED", {"pair_id": pair_id, "reason": str(error)}) from error
        self._check_schema_references(effective)
        descendants = pair.get("required_descendants", [])
        for descendant in descendants:
            raw = self.read(descendant["pin"])
            if "canonical_sha256" in descendant:
                body = pointer_get(self.read_json(descendant["pin"]), descendant.get("pointer", "#"))
                if sha(canonical(body)) != descendant["canonical_sha256"]:
                    raise ContractError("DESCENDANT_READBACK_CONFLICT", {"pair_id": pair_id, "role": descendant.get("role")})
        result = {"pair_id": pair_id, "operation_id": pair["operation_id"], "source_body_sha256": sha(source_raw), "source_schema_sha256": sha(schema_raw), "resolution_id": resolution_id, "descendant_count": len(descendants), "status": SUCCESS}
        self._pair_results[pair_id] = result
        return result

    def _companion(self, row, supplied, kind):
        pin = row.get("companion") or row.get("contract")
        if not pin:
            raise ContractError("MISSING_REGISTERED_COMPANION", kind)
        companion = self.read_json(pin)
        self._subject(companion)
        if supplied is not None and canonical(supplied) != canonical(companion):
            raise ContractError("SUPPLIED_COMPANION_RAW_OR_REVISION_CONFLICT", kind)
        return companion

    def verify_operation(self, operation_id):
        if operation_id in self._operation_results:
            return self._operation_results[operation_id]
        if operation_id not in self.operations:
            raise ContractError("UNREGISTERED_OPERATION", operation_id)
        expected = self.operations[operation_id]
        row = self.operation_index[operation_id]
        companion = self._companion(row, None, operation_id)
        if companion.get("operation_id") != operation_id:
            raise ContractError("OPERATION_COMPANION_IDENTITY_CONFLICT", operation_id)
        for field in ("contract_entity_id", "contract_revision_id"):
            if field not in row or companion.get(field) != row[field]:
                raise ContractError("UNREGISTERED_OPERATION_COMPANION_REVISION", operation_id)
        required = expected.get("required_pair_ids")
        _exact_set(companion.get("required_pair_ids"), required, "OPERATION_REQUIRED_PAIR_SET_MISMATCH")
        if canonical(companion.get("required_descendants")) != canonical(expected.get("required_descendants")):
            raise ContractError("OPERATION_DESCENDANT_SET_MISMATCH", operation_id)
        if companion.get("producer") != expected["producer"] or canonical(companion.get("consumers")) != canonical(expected["consumers"]):
            raise ContractError("WRONG_OPERATION_PRODUCER_OR_CONSUMER", operation_id)
        if operation_id not in self.api_operations or operation_id not in self.mapped_operations:
            raise ContractError("MISSING_API_OR_DOMAIN_MAPPING", operation_id)
        mapping = self.mapped_operations[operation_id]
        producer = {"unit_alias": mapping["producer_unit_alias"], "owner": mapping["producer_existing_owner"]}
        if canonical(expected["producer"]) != canonical(producer) or canonical(expected["consumers"]) != canonical(mapping["consumers"]):
            raise ContractError("EXPECTED_MAPPING_NOT_SOURCE_BOUND", operation_id)
        for field in ("request_model", "response_model"):
            if expected.get(field) != mapping[field] or companion.get(field) != mapping[field]:
                raise ContractError("OPERATION_DTO_SOURCE_BINDING_CONFLICT", {"operation_id": operation_id, "field": field})
        api = self.api_operations[operation_id]
        if api["response_model"] != mapping["response_model"]:
            raise ContractError("API_RESPONSE_DTO_SOURCE_BINDING_CONFLICT", operation_id)
        case_ids = set()
        for case_ref in expected.get("case_refs", []):
            source = self.read_json(case_ref["source"])
            case = pointer_get(source, case_ref["pointer"])
            if case.get("case_id") != case_ref["case_id"] or case.get("operation_id") != operation_id or sha(canonical(case)) != case_ref["case_canonical_sha256"]:
                raise ContractError("OPERATION_CASE_READBACK_CONFLICT", operation_id)
            if case["case_id"] in case_ids:
                raise ContractError("AMBIGUOUS_OPERATION_CASE", case["case_id"])
            case_ids.add(case["case_id"])
        for pair_id in required:
            if self.expected_pairs[pair_id]["operation_id"] != operation_id:
                raise ContractError("PAIR_OPERATION_CONFLICT", pair_id)
            self.verify_pair(pair_id)
        self._read_nested_pins(expected.get("case_refs", []))
        self._read_nested_pins(expected.get("cases", []))
        for descendant in expected.get("required_descendants", []):
            raw = self.read(descendant["pin"])
            if "canonical_sha256" in descendant:
                body = pointer_get(self.read_json(descendant["pin"]), descendant.get("pointer", "#"))
                if sha(canonical(body)) != descendant["canonical_sha256"]:
                    raise ContractError("DESCENDANT_READBACK_CONFLICT", {"operation_id": operation_id, "role": descendant.get("role")})
            self._read_nested_pins(descendant.get("immutable_auxiliary_bytes", []))
        result = {"operation_id": operation_id, "required_pair_count": len(required), "status": SUCCESS}
        self._operation_results[operation_id] = result
        return result

    def verify_unit(self, unit_id, supplied_companion=None):
        if unit_id not in self.expected_units:
            raise ContractError("UNREGISTERED_UNIT", unit_id)
        expected = self.expected_units[unit_id]
        row = self.unit_index[unit_id]
        companion = self._companion(row, supplied_companion, unit_id)
        base = self.base_units[unit_id]
        for field in ("unit_id", "unit_alias", "feature_id"):
            if companion.get(field) != base.get(field) or row.get(field, base[field]) != base[field]:
                raise ContractError("UNIT_FEATURE_OR_ALIAS_CONFLICT", {"unit_id": unit_id, "field": field})
        for field in ("schema_companion_entity_id", "schema_companion_revision_id"):
            if field not in row or companion.get(field) != row[field]:
                raise ContractError("UNREGISTERED_UNIT_COMPANION_REVISION", unit_id)
        if companion.get("base_plan_revision_id") != base["plan_revision_id"] or companion.get("base_unit_canonical_sha256") != sha(canonical(base)):
            raise ContractError("UNIT_BASE_PLAN_REVISION_OR_VALUE_CONFLICT", unit_id)
        if companion.get("base_units") != self.head["base_units"]:
            raise ContractError("UNIT_BASE_SOURCE_PIN_CONFLICT", unit_id)
        interface = base.get("interface_contract", {})
        original_pins = interface.get("companion_raw_bytes_sha256")
        if not isinstance(original_pins, dict):
            raise ContractError("MISSING_BASE_DESIGN_COMPANION_INPUTS", unit_id)
        for relative, digest in original_pins.items():
            self.read({"path": relative, "raw_bytes_sha256": digest})
        dependencies = base.get("dependencies", [])
        if canonical(companion.get("original_dependencies")) != canonical(dependencies):
            raise ContractError("UNIT_DEPENDENCY_CONTRACT_CONFLICT", unit_id)
        required_inputs = expected.get("mandatory_compiler_inputs")
        if required_inputs is None or canonical(companion.get("mandatory_compiler_inputs")) != canonical(required_inputs):
            raise ContractError("UNIT_MANDATORY_INPUT_CONTRACT_CONFLICT", unit_id)
        _exact_set(companion.get("required_operation_ids"), expected["required_operation_ids"], "UNIT_REQUIRED_OPERATION_SET_MISMATCH")
        _exact_set(companion.get("required_pair_ids"), expected["required_pair_ids"], "UNIT_REQUIRED_PAIR_SET_MISMATCH")
        derived_pairs = []
        for operation_id in expected["required_operation_ids"]:
            self.verify_operation(operation_id)
            derived_pairs.extend(self.operations[operation_id]["required_pair_ids"])
        _exact_set(expected["required_pair_ids"], sorted(set(derived_pairs)), "UNIT_DERIVED_REQUIRED_PAIR_SET_MISMATCH")
        if companion.get("execution_authorized") is not False or companion.get("authority_effect", "NONE") != "NONE":
            raise ContractError("SOURCE_COMPANION_CANNOT_GRANT_EXECUTION", unit_id)
        result = {"unit_id": unit_id, "base_plan_revision_id": base["plan_revision_id"], "schema_companion_revision_id": companion["schema_companion_revision_id"], "required_operation_count": len(expected["required_operation_ids"]), "required_pair_count": len(expected["required_pair_ids"]), "input_status": SUCCESS, "execution_authorized": False}
        self._unit_results[unit_id] = result
        return result

    def finish(self):
        for relative, expected_hash in list(self.observed.items()):
            self.cache.pop(relative, None)
            self.read({"path": relative, "raw_bytes_sha256": expected_hash})
        return {"read_pin_count": len(self.observed), "verified_pair_count": len(self._pair_results), "status": SUCCESS, "execution_authorized": False}


def verify_effective_unit_inputs(root, *, expected_head_pin, expected_subject, unit_id, supplied_companion=None):
    verifier = SourceInputVerifier(root, expected_head_pin=expected_head_pin, expected_subject=expected_subject)
    result = verifier.verify_unit(unit_id, supplied_companion)
    result["source_observation"] = verifier.finish()
    return result


def verify_operation(root, *, expected_head_pin, expected_subject, operation_id):
    verifier = SourceInputVerifier(root, expected_head_pin=expected_head_pin, expected_subject=expected_subject)
    result = verifier.verify_operation(operation_id)
    result["source_observation"] = verifier.finish()
    return result


def verify_all_inputs(root, *, expected_head_pin, expected_subject):
    verifier = SourceInputVerifier(root, expected_head_pin=expected_head_pin, expected_subject=expected_subject)
    operations = [verifier.verify_operation(operation_id) for operation_id in sorted(verifier.operations)]
    units = [verifier.verify_unit(unit_id) for unit_id in sorted(verifier.expected_units)]
    difference = copy.deepcopy(verifier.pair_difference)
    difference["ACTUAL_VALID_RESOLVED_PAIRS"] = sorted(verifier._pair_results)
    if difference["ACTUAL_VALID_RESOLVED_PAIRS"] != difference["EXPECTED_REQUIRED_PAIRS"]:
        raise ContractError("REQUIRED_PAIR_NOT_CONSUMED_BY_OPERATION")
    return {"status": SUCCESS, "execution_authorized": False, "operation_results": operations, "unit_results": units, "pair_difference": difference, "source_observation": verifier.finish()}
