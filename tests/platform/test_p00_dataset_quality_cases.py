"""Q01-Q10 的有限集合規格 oracle；不提供產品 importer 或外部 provenance。"""

from collections import defaultdict
from copy import deepcopy
from datetime import datetime, timedelta, date
from decimal import Decimal
import hashlib
import json
from pathlib import Path

import pytest
from jsonschema import ValidationError

from test_p00_contracts import validate
from test_p00_dataset_identity import frame

FIXTURE = json.loads((Path(__file__).resolve().parents[2] /
    "docs/architecture/contracts/dataset_quality.fixture.v1.json").read_text(encoding="utf-8"))
CASES = {case["id"]: case for case in FIXTURE["cases"]}


def instant(value):
    return datetime.fromisoformat(value)


def oracle(value):
    """只驗證固定 fixture 的 coverage/分組語意；不宣稱實作全部 reference port。"""
    for name, key in [("DatasetCoverageRequest", "coverage"), ("DatasetCalendarSnapshot", "calendar"),
                      ("DatasetMappingSnapshot", "mapping"), ("DatasetQualityPolicySnapshot", "policy")]:
        validate(name, value[key])
    request = value["coverage"]
    start, end = instant(request["start_at"]), instant(request["end_at"])
    if end <= start:
        return {"verdict": "INVALID_INPUT", "counts": None}
    for key in ("calendar", "mapping"):
        coverage = value[key]["covered_range"]
        if instant(coverage["start_at"]) > start or instant(coverage["end_at"]) < end:
            return {"verdict": "UNQUALIFIED_REFERENCE", "counts": None}
    contracts = {(x["instrument_id"], x["contract_id"]) for x in request["contracts"]}
    if not contracts <= {(x["instrument_id"], x["contract_id"]) for x in value["calendar"]["contracts"]}:
        return {"verdict": "UNQUALIFIED_REFERENCE", "counts": None}
    expected, sessions = set(), {}
    for segment in value["calendar"]["tradable_intervals"]:
        date.fromisoformat(segment["trade_date"])
        left, right = instant(segment["start_at"]), instant(segment["end_at"])
        if left >= right:
            return {"verdict": "UNQUALIFIED_REFERENCE", "counts": None}
        pair = (segment["instrument_id"], segment["contract_id"])
        cursor = max(start, left)
        while pair in contracts and cursor + timedelta(minutes=1) <= min(end, right):
            key = pair + (cursor,)
            if key in expected:
                return {"verdict": "UNQUALIFIED_REFERENCE", "counts": None}
            expected.add(key)
            sessions[key] = segment
            cursor += timedelta(minutes=1)
    groups = defaultdict(list)
    for row in value["rows"]:
        at = instant(row["bar_open_utc"])
        matches = [entry for entry in value["mapping"]["entries"] if entry["source_code"] == row["source_code"]
                   and instant(entry["start_at"]) <= at < instant(entry["end_at"])]
        if len(matches) != 1:
            return {"verdict": "UNQUALIFIED_REFERENCE", "counts": None}
        entry = matches[0]
        tick = Decimal(entry["tick_size"])
        prices = [Decimal(row[key]) for key in ("open", "high", "low", "close")]
        if tick <= 0 or any(not price.is_finite() or price % tick for price in prices):
            return {"verdict": "INVALID_INPUT", "counts": None}
        op, high, low, close = prices
        if not low <= min(op, close) <= max(op, close) <= high:
            return {"verdict": "INVALID_INPUT", "counts": None}
        key = (entry["instrument_id"], entry["contract_id"], at)
        material = {k: v for k, v in row.items() if k not in ("source_code", "bar_open_utc")}
        groups[key].append(json.dumps(material, sort_keys=True))
    conflicts = {key for key, rows in groups.items() if len(set(rows)) > 1}
    observed = (set(groups) & expected) - conflicts
    counts = {"required": len(expected), "observed": len(observed), "missing": len(expected - observed),
              "duplicates": sum(len(rows) - len(set(rows)) for rows in groups.values()), "conflicts": len(conflicts)}
    verdict = ("CONFLICTING_CONTENT" if conflicts else "INCOMPLETE_COVERAGE"
               if not expected or expected - observed or set(groups) - expected else "QUALIFIED_RESEARCH")
    return {"verdict": verdict, "counts": counts}


@pytest.mark.parametrize("case", FIXTURE["cases"], ids=lambda case: case["id"])
def test_literal_quality_expectations(case):
    assert oracle(case["input"]) == case["expected"]


def test_night_date_comes_from_snapshot_not_utc_row_date():
    value = CASES["Q06"]["input"]
    assert value["calendar"]["tradable_intervals"][0]["trade_date"] == "2026-01-02"
    assert value["rows"][0]["bar_open_utc"].startswith("2026-01-01")


def test_correction_candidate_does_not_mutate_parent_fixture():
    parent = deepcopy(CASES["Q01"]["input"])
    assert CASES["Q07"]["input"]["rows"][0]["close"] == "101"
    assert next(row for row in parent["rows"] if row["bar_open_utc"].endswith("00:00:00Z"))["close"] == "100"
    assert oracle(CASES["Q08"]["input"])["verdict"] == "CONFLICTING_CONTENT"


def test_pinned_calendar_version_changes_snapshot_digest():
    original = CASES["Q01"]["input"]["calendar"]
    changed = CASES["Q09"]["input"]["calendar"]
    encode = lambda x: (json.dumps(x, sort_keys=True, ensure_ascii=False, separators=(",", ":")) + "\n").encode()
    assert hashlib.sha256(encode(original)).digest() != hashlib.sha256(encode(changed)).digest()
    # Reference hash 是 version frame 的 material；不把相同 rows 當相同 dataset version。
    assert frame("dataset-version-v1", [hashlib.sha256(encode(original)).hexdigest()]) != frame(
        "dataset-version-v1", [hashlib.sha256(encode(changed)).hexdigest()])


@pytest.mark.parametrize("mutation", ["overlap", "missing_contract", "ambiguous_mapping", "reversed_range"])
def test_reference_counterexamples_fail_closed(mutation):
    value = deepcopy(CASES["Q01"]["input"])
    if mutation == "overlap":
        value["calendar"]["tradable_intervals"] *= 2
    elif mutation == "missing_contract":
        value["calendar"]["contracts"] = [{"instrument_id": 1, "contract_id": 20}]
    elif mutation == "ambiguous_mapping":
        value["mapping"]["entries"] *= 2
    else:
        value["coverage"]["end_at"] = value["coverage"]["start_at"]
    assert oracle(value)["verdict"] in ("UNQUALIFIED_REFERENCE", "INVALID_INPUT")


def test_snapshot_and_publication_cannot_assert_extra_authority():
    value = deepcopy(CASES["Q01"]["input"]["calendar"])
    value["trading_ready"] = True
    with pytest.raises(ValidationError):
        validate("DatasetCalendarSnapshot", value)
    ref = {"owner": "B", "identity": "q", "version": "1", "sha256": "0" * 64}
    value = {"schema_version": "dataset.publication.v1", "version_id": "dv1_" + "1" * 64,
             "manifest_byte_hash": "2" * 64, "qualified_report_ref": ref, "outcome": "PUBLISHED"}
    validate("DatasetPublicationResult", value)
    value["operation_succeeded"] = True
    with pytest.raises(ValidationError):
        validate("DatasetPublicationResult", value)
