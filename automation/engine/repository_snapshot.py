"""Exact Git object 的唯讀 snapshot boundary；route semantics 委派既有 orchestration。

Caller 負責 fresh fetch/re-entry。本模組只證明其傳入 revision 的 object/pointer
一致性，不能從本機 cached ref 宣稱 remote freshness，也不產生 execution authority。
"""
from __future__ import annotations

from dataclasses import dataclass, replace
import hashlib
import math
import os
from pathlib import Path, PurePosixPath
import re
import subprocess
from types import MappingProxyType
from typing import Mapping, Protocol, Sequence

from automation.engine import orchestration
from automation.engine.execution_capacity import ProviderEvidence, provider_gate
from automation.engine.contracts import CONTRACT_BY_SCHEMA
from automation.engine.yaml_io import load_yaml_mapping_bytes

CURRENT = "automation/work_orders/CURRENT_CODEX.yaml"
TASK = "automation/work_orders/CURRENT_CODEX_TASK.md"
EFFECTS = ("runtime", "broker", "db", "migration", "live", "production", "credentials")
CANDIDATES = frozenset({"READY_FOR_CODEX", "READY_FOR_MANUAL_CODEX_TRIGGER", "READY_FOR_MANUAL_DISPATCH"})
CONTINUATIONS = frozenset({"PAUSED_PROVIDER_LIMIT", "RESUME_PENDING_REVALIDATION"})


class SnapshotError(ValueError):
    """可稽核的 deterministic fail-closed diagnostic；不修復 repository。"""
    def __init__(self, code: str, detail: str):
        self.code, self.detail = code, detail
        super().__init__(f"{code}: {detail}")


def _exact_commit(value: str) -> str:
    if not isinstance(value, str) or not re.fullmatch(r"[0-9a-f]{40}|[0-9a-f]{64}", value):
        raise SnapshotError("EXACT_COMMIT_REQUIRED", str(value))
    return value


def _path(value: object) -> str:
    if not isinstance(value, str) or not value or "\\" in value or ":" in value or "\0" in value:
        raise SnapshotError("INVALID_POINTER", str(value))
    parts = value.split("/")
    if PurePosixPath(value).is_absolute() or any(p in ("", ".", "..") for p in parts):
        raise SnapshotError("INVALID_POINTER", value)
    if parts[0] not in {"automation", "docs", "tests", "scripts", "AGENTS.md"}:
        raise SnapshotError("OUTSIDE_READ_BOUNDARY", value)
    if any(p.lower() in {".git", ".env", "credentials", "secrets"} for p in parts):
        raise SnapshotError("OUTSIDE_READ_BOUNDARY", value)
    return value


@dataclass(frozen=True, slots=True)
class GitBlob:
    commit: str
    path: str
    object_id: str
    data: bytes


class GitBlobReader(Protocol):
    def resolve_commit(self, ref: str) -> str: ...
    def read_blob(self, commit: str, path: str) -> GitBlob: ...


class GitObjectReader:
    """只執行 rev-parse、ls-tree、cat-file；不讀 worktree 檔案或執行任何 Git mutation。"""
    def __init__(self, repository: str | Path):
        self.repository = Path(repository)

    def _git(self, *args: str) -> bytes:
        env = dict(os.environ, GIT_NO_REPLACE_OBJECTS="1", GIT_OPTIONAL_LOCKS="0", GIT_NO_LAZY_FETCH="1")
        result = subprocess.run(["git", "-C", str(self.repository), *args],
                                capture_output=True, env=env, check=False)
        if result.returncode:
            raise SnapshotError("GIT_OBJECT_UNAVAILABLE", args[0])
        return result.stdout

    def resolve_commit(self, ref: str) -> str:
        # Short names/prefixes can collide with tags/branches; caller must disambiguate.
        if not isinstance(ref, str) or not (re.fullmatch(r"[0-9a-f]{40}|[0-9a-f]{64}", ref)
                or ref == "HEAD" or ref.startswith(("refs/heads/", "refs/remotes/", "refs/tags/"))):
            raise SnapshotError("MISSING_OR_AMBIGUOUS_REF", str(ref))
        if ref.startswith("refs/") and (any(c in ref for c in "~^:?*[\\ \t\r\n") or "@{" in ref or ".." in ref):
            raise SnapshotError("MISSING_OR_AMBIGUOUS_REF", ref)
        return _exact_commit(self._git("rev-parse", "--verify", "--end-of-options", ref + "^{commit}").decode("ascii").strip())

    def read_blob(self, commit: str, path: str) -> GitBlob:
        commit, path = _exact_commit(commit), _path(path)
        if self.resolve_commit(commit) != commit:
            raise SnapshotError("COMMIT_MISMATCH", commit)
        rows = self._git("ls-tree", "-z", "--full-tree", commit, "--", path).split(b"\0")
        rows = [row for row in rows if row]
        if not rows:
            raise SnapshotError("MISSING_PATH", path)
        if len(rows) != 1:
            raise SnapshotError("AMBIGUOUS_PATH", path)
        header, name = rows[0].split(b"\t", 1)
        mode, kind, oid = header.decode("ascii").split()
        if name.decode("utf-8") != path or kind != "blob" or mode not in {"100644", "100755"}:
            raise SnapshotError("NON_REGULAR_BLOB", path)
        blob = GitBlob(commit, path, oid, self._git("cat-file", "blob", oid))
        _check_blob(blob, commit, path)
        return blob


def _check_blob(blob: GitBlob, commit: str, path: str) -> None:
    if blob.commit != commit or blob.path != path or type(blob.data) is not bytes:
        raise SnapshotError("BLOB_BINDING_MISMATCH", path)
    if not re.fullmatch(r"[0-9a-f]{40}|[0-9a-f]{64}", blob.object_id):
        raise SnapshotError("INVALID_OBJECT_ID", path)
    algorithm = hashlib.sha1 if len(blob.object_id) == 40 else hashlib.sha256
    actual = algorithm(b"blob " + str(len(blob.data)).encode("ascii") + b"\0" + blob.data).hexdigest()
    if actual != blob.object_id:
        raise SnapshotError("RAW_GIT_OBJECT_MISMATCH", path)


@dataclass(frozen=True, slots=True)
class BlobBinding:
    ref: str
    path: str
    object_id: str
    algorithm: str | None = None
    digest: str | None = None


@dataclass(frozen=True, slots=True)
class Diagnostic:
    code: str
    detail: str


@dataclass(frozen=True, slots=True)
class IntegrityReport:
    passed: bool
    verified: tuple[GitBlob, ...]
    diagnostics: tuple[Diagnostic, ...]


def verify_manifest_bindings(reader: GitBlobReader, bindings: Sequence[BlobBinding]) -> IntegrityReport:
    """Historical provenance 僅於其 declared exact ref 驗證；不拿 current blob 代替。"""
    verified: list[GitBlob] = []
    errors: list[Diagnostic] = []
    seen: set[tuple[str, str]] = set()
    for b in bindings:
        try:
            ref, path = _exact_commit(b.ref), _path(b.path)
            if (ref, path) in seen:
                raise SnapshotError("DUPLICATE_BINDING", path)
            seen.add((ref, path))
            if reader.resolve_commit(ref) != ref:
                raise SnapshotError("COMMIT_MISMATCH", ref)
            blob = reader.read_blob(ref, path)
            _check_blob(blob, ref, path)
            if blob.object_id != b.object_id:
                raise SnapshotError("DECLARED_OBJECT_MISMATCH", path)
            if b.algorithm is not None or b.digest is not None:
                if b.algorithm != "sha256" or not isinstance(b.digest, str) or not re.fullmatch(r"[0-9a-f]{64}", b.digest):
                    raise SnapshotError("INVALID_HASH_DECLARATION", path)
                if hashlib.sha256(blob.data).hexdigest() != b.digest:
                    raise SnapshotError("DECLARED_RAW_HASH_MISMATCH", path)
            verified.append(blob)
        except SnapshotError as exc:
            errors.append(Diagnostic(exc.code, exc.detail))
    return IntegrityReport(not errors, tuple(verified), tuple(errors))


def _freeze(value: object, ancestors: frozenset[int] = frozenset()) -> object:
    if value is None or type(value) in (str, int, bool):
        return value
    if type(value) is float and math.isfinite(value):
        return value
    if id(value) in ancestors:
        raise SnapshotError("CYCLIC_SNAPSHOT_DOCUMENT", "recursive authority document")
    nested = ancestors | {id(value)}
    if isinstance(value, Mapping) and all(isinstance(k, str) for k in value):
        return MappingProxyType({k: _freeze(v, nested) for k, v in value.items()})
    if isinstance(value, (list, tuple)):
        return tuple(_freeze(v, nested) for v in value)
    raise SnapshotError("INVALID_SNAPSHOT_VALUE", type(value).__name__)


@dataclass(frozen=True, slots=True)
class RepositorySnapshot:
    commit: str
    current: Mapping[str, object]
    documents: Mapping[str, Mapping[str, object]]
    blobs: tuple[GitBlob, ...]
    read_order: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class SnapshotResolution:
    snapshot: RepositorySnapshot | None
    decision: orchestration.RouteDecision
    diagnostics: tuple[Diagnostic, ...]


def _require(condition: bool, detail: str) -> None:
    if not condition:
        raise SnapshotError("EVIDENCE_MISSING_OR_CONTRADICTORY", detail)


def _section(document: Mapping[str, object], name: str) -> Mapping[str, object]:
    value = document.get(name)
    _require(isinstance(value, Mapping), name)
    return value  # type: ignore[return-value]


class _Assembly:
    def __init__(self, reader: GitBlobReader, commit: str):
        self.reader, self.commit = reader, commit
        self.blobs: dict[str, GitBlob] = {}
        self.documents: dict[str, Mapping[str, object]] = {}
        self.order: list[str] = []

    def blob(self, path: str, *, optional: bool = False) -> GitBlob | None:
        path = _path(path)
        if path not in self.blobs:
            try:
                blob = self.reader.read_blob(self.commit, path)
            except SnapshotError as exc:
                if optional and exc.code == "MISSING_PATH":
                    return None
                raise
            _check_blob(blob, self.commit, path)
            self.blobs[path] = blob
            self.order.append(path)
        return self.blobs[path]

    def document(self, path: str, schema: str | None = None) -> Mapping[str, object]:
        if path not in self.documents:
            blob = self.blob(path)
            assert blob is not None
            payload = load_yaml_mapping_bytes(blob.data, source=path)
            if schema is not None:
                _require(payload.get("schema_version") == schema, "schema: " + path)
            model = CONTRACT_BY_SCHEMA.get(payload.get("schema_version"))
            if model is not None:
                model.model_validate(payload)
            self.documents[path] = _freeze(payload)  # type: ignore[assignment]
        return self.documents[path]

    def pointer(self, current: Mapping[str, object], key: str, schema: str | None = None) -> Mapping[str, object]:
        return self.document(_path(current.get(key)), schema)

    def snapshot(self, current: Mapping[str, object]) -> RepositorySnapshot:
        return RepositorySnapshot(self.commit, current, MappingProxyType(dict(self.documents)),
                                  tuple(self.blobs.values()), tuple(self.order))


def _same_identity(current: Mapping[str, object], other: Mapping[str, object]) -> None:
    for k in ("work_order_id", "authorization_id", "execution_id"):
        _require(isinstance(current.get(k), str) and bool(current[k]) and other.get(k) == current[k], k)


def _denied(document: Mapping[str, object]) -> None:
    effects = _section(document, "side_effect_envelope")
    _require(all(effects.get(k) == "DENIED" for k in EFFECTS), "denied side effects")


def _bound_proof(a: _Assembly, proof: Mapping[str, object]) -> Mapping[str, object]:
    ref, path, oid = proof.get("ref"), _path(proof.get("path")), proof.get("git_blob_sha")
    _require(isinstance(ref, str) and isinstance(oid, str), "exact object proof")
    algorithm, digest = proof.get("algorithm"), proof.get("digest")
    if "sha256" in proof:
        _require(algorithm in (None, "sha256") and digest in (None, proof["sha256"]), "hash declarations")
        algorithm, digest = "sha256", proof["sha256"]
    report = verify_manifest_bindings(a.reader, (BlobBinding(ref, path, oid, algorithm, digest),))  # type: ignore[arg-type]
    if not report.passed:
        d = report.diagnostics[0]
        raise SnapshotError(d.code, d.detail)
    # Historical declared object proof does not authorize stale content as current state.
    current_blob = a.blob(path)
    _require(current_blob is not None and current_blob.object_id == oid, "current proof preimage drift: " + path)
    if path.endswith((".yaml", ".yml", ".json")):
        return a.document(path)
    # Source interface proof is raw object evidence, never YAML or executable code.
    return MappingProxyType({"path": path, "git_blob_sha": oid})


def _candidate(a: _Assembly, c: Mapping[str, object], state: str) -> orchestration.OrchestrationSnapshot:
    resume = state in CONTINUATIONS
    # Current lifecycle is loaded BEFORE candidate package/program/authority.
    lifecycle_keys = ("handoff_path", "reservation_path", "dispatch_path", "writer_lock_path")
    paths = [_path(c.get(k)) for k in lifecycle_keys]
    _require(len(set(paths)) == len(paths), "duplicate lifecycle pointer")
    handoff, reservation, dispatch, writer = [a.document(p) for p in paths]
    for doc in (handoff, reservation, dispatch, writer):
        _same_identity(c, doc)
        _require(doc.get("scope_digest") == c.get("scope_digest"), "lifecycle scope")
    _require(writer.get("state") == c.get("writer_state") == "HELD", "writer state")
    owner = writer.get("owner_execution_id", writer.get("execution_id"))
    _require(owner == c.get("execution_id") and writer.get("competing_writer_observed") is False, "writer owner")
    _require(c.get("executor_invoked") is resume, "current invocation state")
    for doc in (handoff, reservation, dispatch):
        _require(doc.get("executor_invoked") is resume, "lifecycle invocation state")
    _require(reservation.get("state") == "CONSUMED" and dispatch.get("state") == "DISPATCH_COMMITTED", "durable lifecycle")
    invocation_path = _path(c.get("invocation_evidence_path"))
    invocation_blob = a.blob(invocation_path, optional=True)
    if resume:
        _require(invocation_blob is not None, "resume invocation proof")
        invocation = a.document(invocation_path)
        _same_identity(c, invocation)
        _require(invocation.get("executor_invoked") is True and invocation.get("scope_digest") == c.get("scope_digest"), "resume proof")
    else:
        _require(invocation_blob is None, "CONSUMED execution already invoked; redispatch denied")
        _require(handoff.get("state") == "READY_FOR_MANUAL_CODEX_TRIGGER" and handoff.get("handoff_ready") is True,
                 "manual first invocation handoff")
        _require(c.get("first_invocation_only") is True and handoff.get("executor_invoked") is False, "first invocation only")
    auth = a.pointer(c, "authorization_path", "automation.authorization.v1")
    wo = a.pointer(c, "work_order_path", "automation.codex_work_order.v1")
    package = a.pointer(c, "package_path", "automation.work_package_plan.v1")
    _require(len({c[k] for k in ("authorization_path", "work_order_path", "package_path")}) == 3, "duplicate candidate pointer")
    exact, pb, program = (_section(auth, k) for k in ("exact_binding", "package_binding", "program_binding"))
    _require(auth.get("authorization_id") == c.get("authorization_id") == wo.get("authorization_id"), "authorization identity")
    _require(auth.get("authorization_state") == c.get("authorization_state") == "CONSUMED", "authorization lifecycle")
    _require(exact.get("authorization_revision") == auth.get("authorization_revision"), "authorization revision")
    if "authorization_revision" in c:
        _require(c["authorization_revision"] == auth.get("authorization_revision"), "current authorization revision")
    _require(_section(auth, "single_use_execution").get("execution_id") == c.get("execution_id"), "authority execution identity")
    _same_identity(c, wo)
    _require(package.get("program_id") == wo.get("program_id") == c.get("program_id"), "package program identity")
    for k, other in (("work_package_id", "package_id"), ("work_package_revision", "package_revision")):
        _require(exact.get(k) == package.get(k) == c.get(other) == wo.get(other) and isinstance(c.get(other), str), k)
    _require(exact.get("work_order_id") == wo.get("work_order_id") == c.get("work_order_id"), "work order identity")
    _require(pb.get("path") == c.get("package_path") and pb.get("work_order_path") == c.get("work_order_path"), "package paths")
    scope = c.get("exact_write_scope")
    _require(isinstance(scope, tuple) and bool(scope) and len(set(scope)) == len(scope), "exact scope")
    for p in scope:
        _path(p)
    digest = hashlib.sha256("\n".join(scope).encode("utf-8")).hexdigest()
    _require(digest == c.get("scope_digest") == exact.get("scope_digest") == pb.get("scope_digest"), "scope digest")
    _require(scope == pb.get("planned_write_scope") == package.get("planned_write_scope") == wo.get("exact_write_scope"), "scope paths")
    # WO 的 exact digest 可由 current authority_basis 表示，不從缺值建立 default。
    wo_digests = [wo[k] for k in ("scope_digest",) if k in wo]
    wo_basis = _section(wo, "authority_basis")
    if "scope_digest" in wo_basis:
        wo_digests.append(wo_basis["scope_digest"])
    _require(bool(wo_digests) and all(value == digest for value in wo_digests), "work order scope digest")
    _require(auth.get("source_candidate_head_sha") == c.get("code_base_sha") == wo.get("code_base_sha")
             and isinstance(c.get("code_base_sha"), str), "source baseline binding")
    for doc in (c, auth, wo, package):
        _denied(doc)
    _require(c.get("auto_imp_003_authorized") is False, "AUTO-IMP-003 CURRENT")
    restrictions = []
    if "auto_imp_003_authorized" in wo:
        restrictions.append(wo["auto_imp_003_authorized"] is False)
    if "next_package_restriction" in wo:
        restrictions.append(wo["next_package_restriction"] ==
                            "AUTO-IMP-003 NOT_AUTHORIZED; automatic next dispatch DENIED")
    _require(bool(restrictions) and all(restrictions), "AUTO-IMP-003 WO")
    _require(c.get("controlled_auto") == "DISABLED" and c.get("controller_activation") == "NOT_ACTIVE", "controller barrier")
    profile = "CODEX_SINGLE_EXECUTOR_MANUAL_TRIGGER_ONLY"
    _require(exact.get("allowed_executor_profile") == profile, "executor profile")
    for doc in (handoff, reservation, dispatch):
        _require(doc.get("executor_mode") == "CODEX" and doc.get("executor_profile") == profile, "lifecycle executor profile")
    policy = _section(auth, "execution_policy")
    _require(policy.get("single_use") is True and policy.get("manual_trigger_only") is True
             and policy.get("automatic_dispatch") is False and c.get("automatic_dispatch") is False, "manual-only policy")
    _require(exact.get("architecture_revision") == c.get("architecture_active"), "architecture revision")
    basis = _section(c, "authority_basis")
    _require(isinstance(exact.get("architecture_bundle_hash"), str) and
             re.fullmatch(r"[0-9a-f]{64}", exact["architecture_bundle_hash"]) is not None,
             "architecture hash")
    _require(basis.get("architecture") == _section(wo, "authority_basis").get("architecture") ==
             c.get("architecture_active"), "architecture binding")
    deps = _section(pb, "dependency_bindings")
    _require(deps == _section(basis, "dependencies") == _section(_section(wo, "authority_basis"), "dependencies"), "dependency bindings")
    dag = deps.get("dag")
    _require(isinstance(dag, tuple) and len(set(dag)) == len(dag) and dag == package.get("depends_on"), "DAG identity")
    foundation = _section(deps, "foundation")
    _require(foundation.get("status") == "ACCEPTED_MATERIALIZED", "foundation acceptance")
    closure = _bound_proof(a, _section(foundation, "closure"))
    _require(closure.get("status") in {"CLOSED_ACCEPTED", "ACCEPTED", "ACCEPTED_MATERIALIZED"}, "dependency closure")
    _require(program.get("status") == "ACCEPTED_MATERIALIZED" and program.get("program_id") == c.get("program_id"), "program binding")
    definition = _bound_proof(a, _section(program, "definition"))
    acceptance = _bound_proof(a, _section(program, "acceptance"))
    _bound_proof(a, _section(program, "operational_baseline"))
    _require(definition.get("program_id") == acceptance.get("program_id") == c.get("program_id"), "program identity")
    _require(definition.get("program_revision") == program.get("program_revision"), "program revision")
    _require(acceptance.get("status") == "ACCEPTED_MATERIALIZED", "materialized acceptance wins over phase snapshot")
    for key in ("normative_bindings", "current_interfaces"):
        proofs = deps.get(key)
        _require(isinstance(proofs, tuple) and bool(proofs), key)
        seen = set()
        for proof in proofs:
            _require(isinstance(proof, Mapping) and proof.get("path") not in seen, "duplicate dependency proof")
            seen.add(proof.get("path"))
            _bound_proof(a, proof)
    # Prefer exact execution's latest recheck over pre-writer planning telemetry.
    recheck = None
    if "pre_dispatch_recheck_path" in c:
        recheck = a.pointer(c, "pre_dispatch_recheck_path", "automation.pre_dispatch_recheck.v1")
        _same_identity(c, recheck)
        _require(recheck.get("state") == "PASS" and recheck.get("scope_digest") == digest, "execution recheck")
    provider = recheck if recheck is not None else a.pointer(c, "provider_evidence_path")
    raw = _section(provider, "provider_raw")
    limits = _section(raw, "rateLimits")
    _require(type(raw.get("ordinaryUsageAllowed")) is bool and type(limits.get("spendControlReached")) is bool
             and "rateLimitReachedType" in limits, "explicit provider evidence")
    availability = provider_gate(ProviderEvidence(ordinary_usage_allowed=raw["ordinaryUsageAllowed"],
        hard_block=limits["rateLimitReachedType"] is not None,
        rate_limit_denied=limits["rateLimitReachedType"] is not None,
        spend_control_denied=limits["spendControlReached"], raw=raw))
    available = availability.route == "PROVIDER_AVAILABLE"
    _require(_section(auth, "quota_gate").get("provider_hard_block") == c.get("provider_hard_block") == "STOP", "provider guard")
    capacity = recheck if recheck is not None else a.pointer(c, "capacity_estimate_path")
    route = _section(capacity, "capacity_gate").get("route") if recheck is not None else capacity.get("capacity_route")
    _require(route in {"ALLOW_WITH_WATCH", "WAIT_5H_CAPACITY"}, "explicit capacity evidence")
    _require(capacity.get("scope_digest") == c.get("scope_digest"), "capacity scope")
    _same_identity(c, capacity)
    return orchestration.OrchestrationSnapshot(a.commit, (str(exact["architecture_bundle_hash"]),),
        str(c["package_revision"]), 0, lane_item_ready=True, dag_prerequisites_satisfied=True,
        exact_authority=True, authority_compatible=True, provider_available=available,
        capacity_state="INSUFFICIENT" if route == "WAIT_5H_CAPACITY" else "UNKNOWN",
        dispatch_mode="MANUAL", executor_mode="CODEX", paused_execution_exists=resume,
        paused_executor_invoked=resume, paused_lineage_valid=resume)


def resolve_repository_snapshot(reader: GitBlobReader, ref: str, *, expected_commit: str | None = None,
                                status_only: bool = False) -> SnapshotResolution:
    """先 status 後 deep binding；唯一 routing owner 為 accepted resolve_route。"""
    assembly = None
    current: Mapping[str, object] = MappingProxyType({})
    commit = ""
    try:
        commit = _exact_commit(reader.resolve_commit(ref))
        if expected_commit is not None and commit != _exact_commit(expected_commit):
            raise SnapshotError("REF_MOVED_REVALIDATION_REQUIRED", ref)
        assembly = _Assembly(reader, commit)
        current = assembly.document(CURRENT, "automation.codex_work_order.v1")
        assembly.blob(TASK, optional=True)
        state = current.get("status")
        _require(isinstance(state, str), "current status")
        base = orchestration.OrchestrationSnapshot(commit, (), str(current.get("package_revision", "")), 0,
            provider_available=False, executable_identity_count=0, blocker=state)
        if status_only:
            proposal = base
        elif state in CANDIDATES or state in CONTINUATIONS:
            proposal = _candidate(assembly, current, state)
        else:
            proposal = replace(base,
                completion_pending_intake=state == "COMPLETED_PENDING_REVIEW",
                awaiting_review=state == "REVIEW_PENDING",
                missing_required_identity=state in {"STOP", "HUMAN_DECISION_REQUIRED"})
        if reader.resolve_commit(ref) != commit:
            raise SnapshotError("REF_MOVED_REVALIDATION_REQUIRED", ref)
        return SnapshotResolution(assembly.snapshot(current), orchestration.resolve_route(proposal), ())
    except (SnapshotError, ValueError, TypeError, KeyError, RecursionError) as exc:
        code = exc.code if isinstance(exc, SnapshotError) else "INVALID_REPOSITORY_EVIDENCE"
        detail = exc.detail if isinstance(exc, SnapshotError) else str(exc)
        failed = orchestration.OrchestrationSnapshot(commit, (), "", 0, provider_available=False,
            missing_required_identity=True, executable_identity_count=0)
        snapshot = assembly.snapshot(current) if assembly is not None else None
        return SnapshotResolution(snapshot, orchestration.resolve_route(failed), (Diagnostic(code, detail),))
