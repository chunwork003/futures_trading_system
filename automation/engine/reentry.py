"""唯讀 unified re-entry snapshot；route 是交接建議，不是 claim/dispatch 授權。"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import re
import hashlib
from types import MappingProxyType
from typing import Mapping

from automation.engine.contracts import _freeze_yaml_value
from automation.engine.manifest import (
    ManifestIntegrityError, ManifestVerification, parse_mapping, read_git_blob,
    resolve_commit, verify_manifest, _git,
)


@dataclass(frozen=True)
class ReentrySnapshot:
    """同一 SHA 的最低必要上下文；不自動升級執行或變更 governance。"""
    source_head_sha: str
    manifest: ManifestVerification
    current_state: Mapping[str, str]
    documents: Mapping[str, object]
    route: str
    next_action: str
    stop_reason: str | None
    execution_allowed: bool = False


def _current_projection(text: str) -> Mapping[str, str]:
    """只讀 canonical snapshot 第一個 text fence，避免歷史 NEXT 覆寫 CURRENT。"""
    marker = "### CURRENT_AUTHORITY_SNAPSHOT"
    if marker not in text:
        raise ManifestIntegrityError("canonical CURRENT snapshot missing")
    match = re.search(r"```text\s*\n(.*?)```", text.split(marker, 1)[1], re.S)
    if match is None:
        raise ManifestIntegrityError("canonical CURRENT fence missing")
    state: dict[str, str] = {}
    for line in match.group(1).splitlines():
        if not line.strip():
            continue
        if "=" not in line:
            raise ManifestIntegrityError("invalid CURRENT projection line")
        key, value = (part.strip() for part in line.split("=", 1))
        if not key or not value or key in state:
            raise ManifestIntegrityError("ambiguous CURRENT projection")
        state[key] = value
    if state.get("branch") != "master":
        raise ManifestIntegrityError("authoritative branch must be master")
    return MappingProxyType(state)


class _BindingMismatch(ValueError):
    """只回報矛盾，不修復 pointer、不授予 authority。"""


def _require(value: object, expected: object, reason: str) -> None:
    # 不允許 0/1 被視為 bool，也不讓缺欄位以 None == None 通過。
    if expected is None or type(value) is not type(expected) or value != expected:
        raise _BindingMismatch(reason)


def _validate_bindings(repo, sha, state, current, work, auth, quota, eligibility,
                       package, dependency) -> None:
    """在任何 candidate routing 前核對已載入 documents 的完整交叉契約。

    path 由既有 repository identity 命名規則核對；有效副本仍不能替代 exact
    pointer。原始 package 是 planning record，只有 auth 的 exact binding
    能界定其 revision/scope；dependency 的 ACCEPTED 必須同時有正確 identity。
    """
    for key in ("work_order_id", "package_id", "package_revision", "authorization_id",
                "authorization_revision", "exact_write_scope", "execution_branch",
                "authorization_path", "eligibility_path"):
        _require(current.get(key), work.get(key), "CURRENT_WORK_ORDER_BINDING_MISMATCH")
    # WORK 另有 provider/policy 註記；比較共同 authority 欄位，不能要求整個
    # navigation descriptor byte-for-byte 相等，也不能忽略任一核心欄位。
    for key in ("amendment_id", "path", "status", "effect"):
        _require(current["quota_amendment"].get(key), work["quota_amendment"].get(key),
                 "CURRENT_WORK_ORDER_BINDING_MISMATCH")
    for document in (current, work):
        for key in ("provider_hard_limits_waived", "frozen_policy_modified"):
            if key in document["quota_amendment"]:
                _require(document["quota_amendment"][key], False, "AMENDMENT_EFFECT_MISMATCH")
    for key in ("authorization_id", "authorization_revision"):
        _require(auth.get(key), current.get(key), "EXACT_AUTHORITY_BINDING_MISMATCH")
    for document in (current, work):
        _require(document.get("authorization_state"), auth.get("authorization_state"),
                 "AUTHORIZATION_NOT_AVAILABLE")
    _require(state.get("development_automation_current_authorization_state"),
             auth.get("authorization_state"), "AUTHORIZATION_NOT_AVAILABLE")
    _require(state.get("development_automation_current_package"), current.get("package_id"),
             "EXACT_AUTHORITY_BINDING_MISMATCH")
    _require(state.get("development_automation_current_authorization_id"), auth.get("authorization_id"),
             "EXACT_AUTHORITY_BINDING_MISMATCH")
    _require(state.get("development_automation_current_authorization_revision"),
             auth.get("authorization_revision"), "EXACT_AUTHORITY_BINDING_MISMATCH")

    binding, package_binding = auth["exact_binding"], auth["package_binding"]
    program_binding, quota_binding = auth["program_binding"], quota["exact_binding"]
    package_id, revision = current["package_id"], current["package_revision"]
    auth_path = f"automation/authorizations/{auth['authorization_id']}.v{auth['authorization_revision']}.yaml"
    work_path = f"automation/work_orders/{current['work_order_id']}.yaml"
    _require(current.get("authorization_path"), auth_path, "AUTHORIZATION_POINTER_MISMATCH")
    _require(current.get("work_order_path"), work_path, "WORK_ORDER_POINTER_MISMATCH")
    _require(current.get("eligibility_path"), f"automation/work_orders/{package_id}.eligibility.json",
             "ELIGIBILITY_POINTER_MISMATCH")
    for actual, expected in [
        (binding.get("work_package_id"), package_id),
        (binding.get("work_package_revision"), revision),
        (package.get("work_package_id"), package_id),
        (package.get("work_package_revision"), revision),
        (package_binding.get("path"), f"automation/packages/{package_id}.yaml"),
        (package_binding.get("planned_write_scope"), current["exact_write_scope"]),
        (package.get("planned_write_scope"), current["exact_write_scope"]),
    ]:
        _require(actual, expected, "PACKAGE_BINDING_MISMATCH")
    if "package_revision" in package_binding:
        _require(package_binding["package_revision"], revision, "PACKAGE_BINDING_MISMATCH")
    package_oid = _git(repo, "rev-parse", sha + ":" + package_binding["path"]).decode().strip()
    _require(package_binding.get("git_blob_sha"), package_oid, "PACKAGE_BLOB_MISMATCH")
    digest = hashlib.sha256("\n".join(current["exact_write_scope"]).encode()).hexdigest()
    _require(binding.get("scope_digest"), digest, "SCOPE_DIGEST_MISMATCH")
    _require(binding.get("allowed_executor_profile"), "CODEX_SINGLE_EXECUTOR_MANUAL_TRIGGER_ONLY",
             "EXECUTOR_PROFILE_MISMATCH")
    _require(binding.get("review_barrier"), "REQUIRED_BEFORE_ACCEPTANCE", "REVIEW_BARRIER_MISMATCH")

    descriptor = current["quota_amendment"]
    _require(descriptor.get("path"), f"automation/work_orders/{quota['amendment_id']}.yaml",
             "AMENDMENT_POINTER_MISMATCH")
    _require(descriptor.get("amendment_id"), quota.get("amendment_id"), "AMENDMENT_IDENTITY_MISMATCH")
    _require(descriptor.get("status"), quota.get("status"), "AMENDMENT_STATE_MISMATCH")
    _require(quota.get("status"), "AUTHORIZED_EFFECTIVE", "AMENDMENT_STATE_MISMATCH")
    _require(descriptor.get("effect"), "EXACT_QUOTA_ADMISSION_ONLY", "AMENDMENT_EFFECT_MISMATCH")
    _require(quota["effect"].get("quota_admission_blocker_only"), True, "AMENDMENT_EFFECT_MISMATCH")
    _require(quota["effect"].get("effective_scope"), "THIS_EXACT_WORK_ORDER_ONLY", "AMENDMENT_EFFECT_MISMATCH")
    for key in ("authorization_replay", "extra_work_order_created", "automatic_threshold_mutation"):
        _require(quota["effect"].get(key), False, "AMENDMENT_EFFECT_MISMATCH")
    _require(quota.get("decision"), "WAIVED_FOR_BOUNDED_AUTOMATION_PILOT", "AMENDMENT_EFFECT_MISMATCH")
    _require(quota["quota"].get("admission_gate"), quota.get("decision"), "AMENDMENT_EFFECT_MISMATCH")
    _require(quota["quota"].get("provider_enforced_limits_waived"), False, "AMENDMENT_EFFECT_MISMATCH")
    for key in ("work_order_id", "package_id", "package_revision"):
        _require(quota_binding.get(key), current.get(key), "AMENDMENT_IDENTITY_MISMATCH")
    for actual, expected in [
        (quota_binding.get("work_order_path"), work_path),
        (quota_binding.get("base_authorization_path"), auth_path),
        (quota_binding.get("base_authorization_id"), auth.get("authorization_id")),
        (quota_binding.get("base_authorization_revision"), auth.get("authorization_revision")),
        (quota_binding.get("executor_profile"), binding.get("allowed_executor_profile")),
    ]:
        _require(actual, expected, "AMENDMENT_AUTHORIZATION_BINDING_MISMATCH")

    for key in ("work_order_id", "package_id", "authorization_id"):
        _require(eligibility.get(key), current.get(key), "ELIGIBILITY_IDENTITY_MISMATCH")
    # 舊 eligibility schema 沒有 revision 欄位；出現時必須一致，不能忽略矛盾。
    for key in ("package_revision", "authorization_revision"):
        if key in eligibility:
            _require(eligibility[key], current.get(key), "ELIGIBILITY_REVISION_MISMATCH")
    _require(eligibility.get("status"), "ELIGIBLE_FOR_MANUAL_TRIGGER", "ELIGIBILITY_STATE_MISMATCH")
    _require(eligibility.get("trigger_mode"), "MANUAL_TRIGGER_ONLY", "ELIGIBILITY_TRIGGER_MISMATCH")
    for key in ("automatic_dispatch", "automatic_next_package"):
        _require(eligibility.get(key), False, "ELIGIBILITY_TRIGGER_MISMATCH")
    # 既有 CURRENT/WORK 使用兩種等效 guard 標籤；只接受這兩個明示標籤。
    compatible = {"ELIGIBLE_FOR_MANUAL_TRIGGER_WITH_MANIFEST_INTEGRITY_PASS",
                  "ELIGIBLE_FOR_MANUAL_TRIGGER_WITH_PROVIDER_HARD_BLOCK_GUARD"}
    for document in (current, work):
        if document.get("execution_eligibility") not in compatible:
            raise _BindingMismatch("ELIGIBILITY_PROJECTION_MISMATCH")
    expected_dependencies = package.get("depends_on")
    if not isinstance(expected_dependencies, list) or len(expected_dependencies) != 1:
        raise _BindingMismatch("DEPENDENCY_BINDING_UNSUPPORTED")
    expected_dependency = expected_dependencies[0]
    _require(program_binding.get("package_dependency"), expected_dependency + "_ACCEPTED_MATERIALIZED",
             "DEPENDENCY_IDENTITY_MISMATCH")
    _require(program_binding.get("dependency_closure_path"),
             f"automation/work_orders/{expected_dependency}.closure.yaml", "DEPENDENCY_POINTER_MISMATCH")
    _require(dependency.get("package_id"), expected_dependency, "DEPENDENCY_IDENTITY_MISMATCH")
    _require(dependency.get("status"), "ACCEPTED_MATERIALIZED", "DEPENDENCY_STATE_MISMATCH")


def resolve_reentry(
    repo: str | Path, revision: str, *, status_only: bool = False,
    handoff_paths: tuple[str, ...] = (),
) -> ReentrySnapshot:
    """讀 exact repository pointers，不 fetch、不寫檔、不詢問 repo 已有答案。

    open handoff/result/review/STOP 由 caller 提供 exact paths，避免全 repo 掃描。
    完整 executor gates 與 single-use claim 仍由 executor fresh revalidate。
    """
    sha = resolve_commit(repo, revision)
    documents: dict[str, object] = {}

    def text(path: str) -> str:
        value = read_git_blob(repo, sha, path).decode("utf-8")
        documents[path] = value
        return value

    def mapping(path: str) -> dict[str, object]:
        value = parse_mapping(read_git_blob(repo, sha, path))
        documents[path] = value
        return value

    text("AGENTS.md")
    state = _current_projection(text("docs/CURRENT_STATE.md"))
    verification = verify_manifest(repo, sha)
    manifest = mapping(verification.manifest_path)
    for policy in manifest["policies"].values():
        mapping(policy["path"])
    text("docs/CURRENT_WORK.md")
    handoffs = [mapping(path) for path in handoff_paths]
    current = mapping("automation/work_orders/CURRENT_CODEX.yaml")
    text("automation/work_orders/CURRENT_CODEX_TASK.md")
    work = mapping(current["work_order_path"])
    auth = mapping(current["authorization_path"])
    quota = mapping(current["quota_amendment"]["path"])
    eligibility = mapping(current["eligibility_path"])
    package = mapping(auth["package_binding"]["path"])
    dependency = mapping(auth["program_binding"]["dependency_closure_path"])

    reason = None
    if not verification.valid:
        reason = "MANIFEST_INTEGRITY_MISMATCH"
    else:
        try:
            _validate_bindings(repo, sha, state, current, work, auth, quota,
                               eligibility, package, dependency)
        except _BindingMismatch as exc:
            reason = str(exc)
        except (KeyError, TypeError, AttributeError, ValueError):
            reason = "INVALID_BINDING_DOCUMENT"

    statuses = [doc.get("status") for doc in handoffs] + [current.get("status"), work.get("status")]
    if reason:
        route, action = "STOP", "RESOLVE_GOVERNANCE_INTEGRITY_OR_BINDING"
    elif any(s in ("STOP", "STOPPED", "HARD_BLOCK", "BLOCKED") for s in statuses):
        route, action, reason = "STOP", "RESOLVE_REPOSITORY_STOP", "OPEN_STOP_OR_BLOCKER"
    elif any(s in ("COMPLETED_PENDING_REVIEW", "PENDING_REVIEW", "RESULT_READY", "IMPLEMENTED_PENDING_REVIEW") for s in statuses):
        route, action = "PENDING_REVIEW", "ROUTE_DURABLE_RESULT_TO_WORK"
    elif (auth.get("authorization_state") != "AUTHORIZED"
            or state.get("development_automation_current_authorization_state") != "AUTHORIZED"):
        route, action, reason = "STOP", "RESOLVE_CURRENT_AUTHORIZATION", "AUTHORIZATION_NOT_AVAILABLE"
    elif dependency.get("status") != "ACCEPTED_MATERIALIZED":
        route, action, reason = "WAIT", "WAIT_FOR_DEPENDENCY_CLOSURE", "DEPENDENCY_NOT_ACCEPTED"
    elif (quota.get("status") != "AUTHORIZED_EFFECTIVE"
            or eligibility.get("status") != "ELIGIBLE_FOR_MANUAL_TRIGGER"):
        route, action, reason = "WAIT", "FRESH_ELIGIBILITY_RESOLUTION", "ELIGIBILITY_NOT_READY"
    elif current.get("status") == work.get("status") == "READY_FOR_CODEX" and current.get("handoff_ready") is True:
        route, action = "CODEX_EXECUTION_CANDIDATE", "FRESH_EXECUTOR_GATES_AND_SINGLE_USE_CLAIM_REQUIRED"
    else:
        route, action, reason = "STOP", "RESOLVE_CURRENT_WORK", "NO_LEGAL_READY_WORK"
    if status_only:
        action = "REPORT_CURRENT_STATE_WITHOUT_EXECUTION"
    return ReentrySnapshot(
        sha, verification, state, _freeze_yaml_value(documents), route, action, reason,
    )
