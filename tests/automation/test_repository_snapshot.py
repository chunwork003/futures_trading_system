"""Fixture-owned Git bytes 與 repository snapshot contract 的 regression。"""
import hashlib
import json
import copy
import subprocess
from dataclasses import replace
import pytest


def test_minimum_raw_integrity_counterexample():
    from automation.engine.repository_snapshot import BlobBinding, verify_manifest_bindings
    reader = MemoryReader({"docs/a.yaml": b"value: 1\r\n"})
    good = binding(reader, "docs/a.yaml")
    assert verify_manifest_bindings(reader, (good,)).passed
    bad = BlobBinding(good.ref, good.path, good.object_id, "sha256", hashlib.sha256(b"value: 1\n").hexdigest())
    assert not verify_manifest_bindings(reader, (bad,)).passed


def test_minimum_non_candidate_counterexample():
    from automation.engine.repository_snapshot import resolve_repository_snapshot
    reader = MemoryReader({CURRENT: b'{"schema_version":"automation.codex_work_order.v1","status":"COMPLETED_PENDING_REVIEW"}'})
    result = resolve_repository_snapshot(reader, COMMIT)
    assert result.decision.route == "WORK_RESULT_INTAKE"
    assert not result.decision.invocation_allowed


COMMIT = "1" * 40
CURRENT = "automation/work_orders/CURRENT_CODEX.yaml"


class MemoryReader:
    def __init__(self, files):
        self.files = dict(files)
        self.reads = []
        self.ref = COMMIT

    def resolve_commit(self, ref):
        from automation.engine.repository_snapshot import SnapshotError
        if ref not in (COMMIT, "refs/heads/master"):
            raise SnapshotError("MISSING_OR_AMBIGUOUS_REF", ref)
        return self.ref if ref == "refs/heads/master" else COMMIT

    def read_blob(self, commit, path):
        from automation.engine.repository_snapshot import GitBlob, SnapshotError
        self.reads.append((commit, path))
        if path not in self.files:
            raise SnapshotError("MISSING_PATH", path)
        data = self.files[path]
        oid = hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()
        return GitBlob(commit, path, oid, data)


def binding(reader, path):
    from automation.engine.repository_snapshot import BlobBinding
    blob = reader.read_blob(COMMIT, path)
    return BlobBinding(COMMIT, path, blob.object_id, "sha256", hashlib.sha256(blob.data).hexdigest())


def ready_fixture():
    """沒有 ROOT/CURRENT recursion；所有 authority evidence 由此 fixture 明確提供。"""
    scope = ["automation/engine/new.py"]
    digest = hashlib.sha256("\n".join(scope).encode()).hexdigest()
    identity = dict(work_order_id="WO", authorization_id="AUTH", execution_id="EXEC")
    effects = {k: "DENIED" for k in ("runtime", "broker", "db", "migration", "live", "production", "credentials")}
    def encoded(o): return json.dumps(o).encode()
    docs = {
        "automation/programs/definition.yaml": dict(schema_version="automation.implementation_program.v1",
            program_id="PROGRAM", program_revision="4", status="CANDIDATE_PENDING_IMPLEMENTATION",
            compiled_from_freeze_head=COMMIT, frozen_master_manifest_sha256="a"*64,
            master_architecture_version="1.2.2", authority={}, implementation_strategy={},
            near_horizon_exact_packages=[], dag=["FOUNDATION"], waves={}, deferred_milestones=[],
            hard_stops=[], authorization_compilation={}),
        "automation/work_orders/acceptance.json": dict(schema_version="automation.acceptance.v1",
            program_id="PROGRAM", status="ACCEPTED_MATERIALIZED"),
        "automation/work_orders/baseline.json": dict(schema_version="automation.operational_baseline.v1", status="BOUND"),
        "automation/work_orders/closure.json": dict(schema_version="automation.closure.v1", status="CLOSED_ACCEPTED"),
        "automation/policies/normative.yaml": dict(schema_version="fixture.normative", active=True),
        "automation/engine/interface.yaml": dict(schema_version="fixture.interface", pure=True),
    }
    reader = MemoryReader({p: encoded(o) for p,o in docs.items()})
    def proof(p): return dict(path=p, ref=COMMIT, git_blob_sha=reader.read_blob(COMMIT,p).object_id)
    program = dict(program_id="PROGRAM", program_revision="4", status="ACCEPTED_MATERIALIZED",
        definition=proof("automation/programs/definition.yaml"),
        acceptance=proof("automation/work_orders/acceptance.json"),
        operational_baseline=proof("automation/work_orders/baseline.json"))
    deps = dict(dag=["FOUNDATION"], foundation=dict(status="ACCEPTED_MATERIALIZED",
        closure=proof("automation/work_orders/closure.json")),
        normative_bindings=[proof("automation/policies/normative.yaml")],
        current_interfaces=[proof("automation/engine/interface.yaml")])
    paths = dict(authorization_path="automation/authorizations/auth.yaml", work_order_path="automation/work_orders/wo.yaml",
        package_path="automation/packages/package.yaml", handoff_path="automation/runs/EXEC/handoff.yaml",
        reservation_path="automation/runs/EXEC/reservation.yaml", dispatch_path="automation/runs/EXEC/dispatch.yaml",
        writer_lock_path="automation/runs/EXEC/writer_lock.yaml", invocation_evidence_path="automation/runs/EXEC/invocation.json",
        provider_evidence_path="automation/runs/EXEC/provider.json", capacity_estimate_path="automation/runs/EXEC/capacity.json")
    c = dict(identity, **paths, schema_version="automation.codex_work_order.v1", status="READY_FOR_CODEX",
        package_id="PKG", package_revision="2", program_id="PROGRAM", architecture_active="1.2.2",
        exact_write_scope=scope, scope_digest=digest, authorization_state="CONSUMED", writer_state="HELD",
        executor_invoked=False, first_invocation_only=True, auto_imp_003_authorized=False,
        controlled_auto="DISABLED", controller_activation="NOT_ACTIVE", automatic_dispatch=False,
        provider_hard_block="STOP", side_effect_envelope=effects, code_base_sha=COMMIT,
        authority_basis=dict(architecture="1.2.2", dependencies=deps))
    lifecycle = dict(identity, scope_digest=digest, executor_invoked=False, executor_mode="CODEX",
        executor_profile="CODEX_SINGLE_EXECUTOR_MANUAL_TRIGGER_ONLY")
    docs.update({
        CURRENT:c,
        paths["handoff_path"]:dict(lifecycle, state="READY_FOR_MANUAL_CODEX_TRIGGER", handoff_ready=True),
        paths["reservation_path"]:dict(lifecycle, state="CONSUMED"),
        paths["dispatch_path"]:dict(lifecycle, state="DISPATCH_COMMITTED"),
        paths["writer_lock_path"]:dict(lifecycle, state="HELD", owner_execution_id="EXEC", competing_writer_observed=False),
        paths["provider_evidence_path"]:dict(identity, provider_raw=dict(ordinaryUsageAllowed=True,
            rateLimits=dict(spendControlReached=False, rateLimitReachedType=None))),
        paths["capacity_estimate_path"]:dict(identity, scope_digest=digest, capacity_route="ALLOW_WITH_WATCH"),
    })
    docs[paths["work_order_path"]] = dict(c)
    docs[paths["package_path"]] = dict(schema_version="automation.work_package_plan.v1", work_package_id="PKG",
        work_package_revision="2", status="AUTHORIZED", program_id="PROGRAM", planning_baseline_sha=COMMIT,
        wave="W", title="fixture", risk="MEDIUM", depends_on=["FOUNDATION"], purpose="test",
        authorization={}, side_effect_envelope=effects, planned_write_scope=scope, protected_scope=[],
        acceptance_tests=[], cost_forecast={}, telemetry={}, git_policy={}, review_barrier="REVIEW")
    docs[paths["authorization_path"]] = dict(schema_version="automation.authorization.v1", authorization_id="AUTH",
        authorization_revision="1", document_status="CONSUMED_EFFECTIVE", authorization_state="CONSUMED",
        source_candidate_head_sha=COMMIT, decision_evidence={},
        exact_binding=dict(authorization_revision="1", work_order_id="WO", work_package_id="PKG",
            work_package_revision="2", scope_digest=digest, allowed_executor_profile="CODEX_SINGLE_EXECUTOR_MANUAL_TRIGGER_ONLY",
            architecture_revision="1.2.2", architecture_bundle_hash="a"*64),
        package_binding=dict(path=paths["package_path"], work_order_path=paths["work_order_path"],
            scope_digest=digest, planned_write_scope=scope, dependency_bindings=deps),
        program_binding=program, execution_policy=dict(single_use=True, manual_trigger_only=True, automatic_dispatch=False),
        side_effect_envelope=effects, quota_gate=dict(provider_hard_block="STOP"), telemetry_gate={}, decision={},
        single_use_execution=dict(execution_id="EXEC"))
    # Break shared Python aliases so each mutation targets exactly one repository artifact.
    reader.files = {p:encoded(o) for p,o in docs.items()}
    reader.reads.clear()
    return reader


def mutate(reader, path, keys, value, *, delete=False):
    obj = json.loads(reader.files[path])
    nested = obj
    for k in keys[:-1]: nested = nested[k]
    if delete: del nested[keys[-1]]
    else: nested[keys[-1]] = value
    reader.files[path] = json.dumps(obj).encode()


def test_ready_positive_non_vacuity_and_immutable_snapshot():
    from automation.engine.repository_snapshot import resolve_repository_snapshot
    reader = ready_fixture()
    result = resolve_repository_snapshot(reader, COMMIT)
    assert not result.diagnostics, result.diagnostics
    assert result.decision.route == "READY_FOR_MANUAL_DISPATCH"
    assert result.decision.execution_allowed and result.decision.proposal_only
    assert not result.decision.invocation_allowed and not result.decision.authority_granted
    assert reader.reads[0] == (COMMIT, CURRENT)
    assert all(commit == COMMIT for commit,path in reader.reads)
    order = result.snapshot.read_order
    assert order.index("automation/runs/EXEC/dispatch.yaml") < order.index("automation/authorizations/auth.yaml")
    with pytest.raises(TypeError): result.snapshot.current["status"] = "CLOSED"
    with pytest.raises(TypeError): result.snapshot.current["authority_basis"]["architecture"] = "9"
    reader.files[CURRENT] = b"bad"
    assert result.snapshot.current["status"] == "READY_FOR_CODEX"


@pytest.mark.parametrize("status", ["HUMAN_DECISION_REQUIRED","BLOCKED","STOP","COMPLETED_PENDING_REVIEW",
    "REVIEW_PENDING","CLOSED","COMPILED_NOT_AUTHORIZED","HISTORICAL_CANDIDATE"])
def test_non_candidate_before_deep_bindings(status):
    from automation.engine.repository_snapshot import resolve_repository_snapshot
    r = MemoryReader({CURRENT:json.dumps(dict(schema_version="automation.codex_work_order.v1",status=status,
        authorization_path="missing/deep.yaml")).encode()})
    result=resolve_repository_snapshot(r,COMMIT)
    assert not result.diagnostics and not result.decision.execution_allowed
    assert {path for commit,path in r.reads} == {CURRENT,"automation/work_orders/CURRENT_CODEX_TASK.md"}


def test_status_only_never_deep_loads():
    from automation.engine.repository_snapshot import resolve_repository_snapshot
    r=ready_fixture(); result=resolve_repository_snapshot(r,COMMIT,status_only=True)
    assert not result.decision.execution_allowed and not result.decision.invocation_allowed
    assert len(r.reads)==2


@pytest.mark.parametrize("path,keys,value,delete", [
    (CURRENT,["authorization_path"],None,True),
    (CURRENT,["package_path"],None,True),
    (CURRENT,["scope_digest"],"wrong",False),
    (CURRENT,["exact_write_scope"],["automation/engine/new.py"]*2,False),
    (CURRENT,["first_invocation_only"],False,False),
    (CURRENT,["executor_invoked"],True,False),
    (CURRENT,["auto_imp_003_authorized"],True,False),
    (CURRENT,["controlled_auto"],"ENABLED",False),
    (CURRENT,["controller_activation"],"ACTIVE",False),
    (CURRENT,["automatic_dispatch"],True,False),
    (CURRENT,["side_effect_envelope","broker"],"ALLOWED",False),
    (CURRENT,["provider_hard_block"],"WAIVED",False),
    ("automation/authorizations/auth.yaml",["package_binding"],None,True),
    ("automation/authorizations/auth.yaml",["program_binding"],None,True),
    ("automation/authorizations/auth.yaml",["exact_binding","work_order_id"],"OTHER",False),
    ("automation/authorizations/auth.yaml",["exact_binding","work_package_revision"],"3",False),
    ("automation/authorizations/auth.yaml",["exact_binding","authorization_revision"],"2",False),
    ("automation/authorizations/auth.yaml",["exact_binding","allowed_executor_profile"],"WORK",False),
    ("automation/authorizations/auth.yaml",["package_binding","path"],"automation/packages/other.yaml",False),
    ("automation/authorizations/auth.yaml",["program_binding","program_revision"],"5",False),
    ("automation/authorizations/auth.yaml",["package_binding","dependency_bindings","dag"],["OTHER"],False),
    ("automation/authorizations/auth.yaml",["execution_policy","manual_trigger_only"],False,False),
    ("automation/authorizations/auth.yaml",["single_use_execution","execution_id"],"OTHER",False),
    ("automation/authorizations/auth.yaml",["source_candidate_head_sha"],"2"*40,False),
    ("automation/packages/package.yaml",["work_package_id"],"OTHER",False),
    ("automation/packages/package.yaml",["program_id"],"OTHER",False),
    ("automation/packages/package.yaml",["side_effect_envelope","db"],"ALLOWED",False),
    ("automation/work_orders/wo.yaml",["authorization_id"],"OTHER",False),
    ("automation/work_orders/wo.yaml",["auto_imp_003_authorized"],True,False),
    ("automation/runs/EXEC/dispatch.yaml",["execution_id"],"OTHER",False),
    ("automation/runs/EXEC/dispatch.yaml",["executor_profile"],"WORK",False),
    ("automation/runs/EXEC/reservation.yaml",["state"],"RESERVED",False),
    ("automation/runs/EXEC/writer_lock.yaml",["competing_writer_observed"],True,False),
    ("automation/runs/EXEC/writer_lock.yaml",["owner_execution_id"],"OTHER",False),
    ("automation/runs/EXEC/provider.json",["provider_raw","ordinaryUsageAllowed"],None,True),
    ("automation/runs/EXEC/capacity.json",["capacity_route"],None,True),
])
def test_candidate_negative_matrix(path,keys,value,delete):
    from automation.engine.repository_snapshot import resolve_repository_snapshot
    r=ready_fixture()
    assert resolve_repository_snapshot(r,COMMIT).decision.route=="READY_FOR_MANUAL_DISPATCH"
    mutate(r,path,keys,value,delete=delete)
    result=resolve_repository_snapshot(r,COMMIT)
    assert result.diagnostics and not result.decision.execution_allowed
    assert not result.decision.invocation_allowed and not result.decision.authority_granted


@pytest.mark.parametrize("key,value", [("ordinaryUsageAllowed",False),("spendControlReached",True),("rateLimitReachedType","hard")])
def test_provider_denial_delegates_accepted_route(key,value):
    from automation.engine.repository_snapshot import resolve_repository_snapshot
    r=ready_fixture();keys=["provider_raw",key] if key=="ordinaryUsageAllowed" else ["provider_raw","rateLimits",key]
    mutate(r,"automation/runs/EXEC/provider.json",keys,value)
    result=resolve_repository_snapshot(r,COMMIT)
    assert result.decision.route=="WAIT_PROVIDER_AVAILABLE" and not result.decision.execution_allowed


def test_consumed_replay_and_resume_lineage():
    from automation.engine.repository_snapshot import resolve_repository_snapshot
    r=ready_fixture()
    invocation=dict(work_order_id="WO",authorization_id="AUTH",execution_id="EXEC",executor_invoked=True,
        scope_digest=json.loads(r.files[CURRENT])["scope_digest"])
    r.files["automation/runs/EXEC/invocation.json"]=json.dumps(invocation).encode()
    assert not resolve_repository_snapshot(r,COMMIT).decision.execution_allowed
    mutate(r,CURRENT,["status"],"PAUSED_PROVIDER_LIMIT")
    for p in [CURRENT,"automation/runs/EXEC/handoff.yaml","automation/runs/EXEC/reservation.yaml","automation/runs/EXEC/dispatch.yaml"]:
        mutate(r,p,["executor_invoked"],True)
    result=resolve_repository_snapshot(r,COMMIT)
    assert result.decision.route=="RESUME_EXISTING_EXECUTION" and not result.decision.invocation_allowed
    mutate(r,"automation/runs/EXEC/invocation.json",["execution_id"],"OTHER")
    assert not resolve_repository_snapshot(r,COMMIT).decision.execution_allowed


@pytest.mark.parametrize("mode", ["missing_current","bad_schema","bad_yaml","ref_move","mixed_commit","invalid_utf8"])
def test_snapshot_fail_closed(mode):
    from automation.engine.repository_snapshot import resolve_repository_snapshot,GitBlob
    r=MemoryReader({CURRENT:b'{"schema_version":"automation.codex_work_order.v1","status":"CLOSED"}'})
    ref=COMMIT
    if mode=="missing_current":r.files.clear()
    elif mode=="bad_schema":r.files[CURRENT]=b'{"schema_version":"unknown","status":"CLOSED"}'
    elif mode=="bad_yaml":r.files[CURRENT]=b"status: CLOSED\nstatus: READY\n"
    elif mode=="invalid_utf8":r.files[CURRENT]=b"status: CLOSED\n\xff"
    elif mode=="ref_move":
        ref="refs/heads/master";original=r.read_blob
        def read(commit,path):
            r.ref="2"*40
            return original(commit,path)
        r.read_blob=read
    elif mode=="mixed_commit":
        original=r.read_blob
        r.read_blob=lambda commit,path:replace(original(commit,path),commit="2"*40)
    result=resolve_repository_snapshot(r,ref)
    assert result.diagnostics and not result.decision.execution_allowed


@pytest.mark.parametrize("mode",["object","bytes","algorithm","digest","duplicate","missing","ambiguous"])
def test_integrity_negative_matrix(mode):
    from automation.engine.repository_snapshot import verify_manifest_bindings
    r=MemoryReader({"docs/a.yaml":b"x: 1\r\n"});b=binding(r,"docs/a.yaml")
    bindings=(b,)
    if mode=="object":bindings=(replace(b,object_id="0"*40),)
    elif mode=="bytes":r.files[b.path]=b"x: 2\r\n"
    elif mode=="algorithm":bindings=(replace(b,algorithm="md5"),)
    elif mode=="digest":bindings=(replace(b,digest="bad"),)
    elif mode=="duplicate":bindings=(b,b)
    elif mode=="missing":r.files.clear()
    elif mode=="ambiguous":bindings=(replace(b,ref="master"),)
    assert not verify_manifest_bindings(r,bindings).passed


def test_duplicate_pointer_and_duplicate_dependency_proof():
    from automation.engine.repository_snapshot import resolve_repository_snapshot
    r=ready_fixture();mutate(r,CURRENT,["dispatch_path"],"automation/runs/EXEC/reservation.yaml")
    assert resolve_repository_snapshot(r,COMMIT).diagnostics
    r=ready_fixture();o=json.loads(r.files["automation/authorizations/auth.yaml"])
    proofs=o["package_binding"]["dependency_bindings"]["normative_bindings"]
    proofs.append(proofs[0]);r.files["automation/authorizations/auth.yaml"]=json.dumps(o).encode()
    assert resolve_repository_snapshot(r,COMMIT).diagnostics


def test_git_adapter_reads_objects_not_worktree_and_never_mutates(tmp_path,monkeypatch):
    from automation.engine.repository_snapshot import GitObjectReader,SnapshotError,resolve_repository_snapshot
    def git(*args):return subprocess.check_output(["git","-C",str(tmp_path),*args])
    git("init");git("config","core.autocrlf","false")
    (tmp_path/"docs").mkdir();(tmp_path/"docs/a.yaml").write_bytes(b"x: 1\r\n")
    (tmp_path/"automation/work_orders").mkdir(parents=True)
    (tmp_path/CURRENT).write_bytes(b'{"schema_version":"automation.codex_work_order.v1","status":"CLOSED"}')
    git("add",".");git("-c","user.name=fixture","-c","user.email=fixture@example.test","-c","core.hooksPath=NUL","commit","-m","fixture")
    commit=git("rev-parse","HEAD").decode().strip();(tmp_path/"docs/a.yaml").write_bytes(b"worktree changed")
    before=git("status","--porcelain");original=subprocess.run;calls=[]
    def spy(command,**kw):calls.append(command);return original(command,**kw)
    monkeypatch.setattr(subprocess,"run",spy)
    reader=GitObjectReader(tmp_path)
    assert reader.read_blob(commit,"docs/a.yaml").data==b"x: 1\r\n"
    assert not resolve_repository_snapshot(reader,commit).decision.execution_allowed
    assert all(command[3] in {"rev-parse","ls-tree","cat-file"} for command in calls)
    with pytest.raises(SnapshotError):reader.resolve_commit(commit[:8])
    with pytest.raises(SnapshotError):reader.read_blob(commit,"docs/missing.yaml")
    with pytest.raises(SnapshotError):reader.read_blob(commit,"data/credentials")
    assert git("status","--porcelain")==before


def test_declared_historical_ref_is_not_substituted_with_current_bytes():
    from automation.engine.repository_snapshot import GitBlob, BlobBinding, verify_manifest_bindings, SnapshotError
    old="2"*40
    class HistoryReader(MemoryReader):
        def resolve_commit(self,ref):
            if ref in (COMMIT,old):return ref
            raise SnapshotError("MISSING_REF",ref)
        def read_blob(self,commit,path):
            data=b"old\r\n" if commit==old else b"new\n"
            oid=hashlib.sha1(b"blob "+str(len(data)).encode()+b"\0"+data).hexdigest()
            self.reads.append((commit,path))
            return GitBlob(commit,path,oid,data)
    r=HistoryReader({});blob=r.read_blob(old,"docs/history.md")
    declared=BlobBinding(old,blob.path,blob.object_id,"sha256",hashlib.sha256(blob.data).hexdigest())
    r.reads.clear()
    assert verify_manifest_bindings(r,(declared,)).passed and r.reads==[(old,blob.path)]
    assert not verify_manifest_bindings(r,(replace(declared,ref=COMMIT),)).passed


def test_required_pointer_missing_optional_task_and_expected_commit():
    from automation.engine.repository_snapshot import resolve_repository_snapshot
    r=ready_fixture();del r.files["automation/packages/package.yaml"]
    assert resolve_repository_snapshot(r,COMMIT).diagnostics
    r=ready_fixture()
    assert resolve_repository_snapshot(r,COMMIT,expected_commit="2"*40).diagnostics
    r.files["automation/work_orders/CURRENT_CODEX_TASK.md"]=b"historical READY text is not authority"
    result=resolve_repository_snapshot(r,COMMIT,status_only=True)
    assert not result.decision.execution_allowed
    assert result.snapshot.read_order==(CURRENT,"automation/work_orders/CURRENT_CODEX_TASK.md")


def test_raw_bytes_forgery_fails_even_with_trusted_declared_oid():
    from automation.engine.repository_snapshot import verify_manifest_bindings
    r=MemoryReader({"docs/a.yaml":b"a: 1\n"});b=binding(r,"docs/a.yaml");original=r.read_blob
    r.read_blob=lambda commit,path:replace(original(commit,path),data=b"a: 2\n")
    assert not verify_manifest_bindings(r,(b,)).passed


def test_route_owner_is_called_for_every_proposal(monkeypatch):
    from automation.engine import repository_snapshot as module
    original=module.orchestration.resolve_route; calls=[]
    def spy(snapshot): calls.append(snapshot);return original(snapshot)
    monkeypatch.setattr(module.orchestration,"resolve_route",spy)
    result=module.resolve_repository_snapshot(ready_fixture(),COMMIT)
    assert len(calls)==1 and result.decision.invocation_allowed is False
    assert calls[0].exact_authority and calls[0].authority_compatible


def test_pinned_actual_integration_smoke_is_not_a_mutable_current_unit_invariant():
    from pathlib import Path
    from automation.engine.repository_snapshot import GitObjectReader, resolve_repository_snapshot
    reader=GitObjectReader(Path(__file__).resolve().parents[2])
    result=resolve_repository_snapshot(reader,"0d4cb56ad759b299c2e216b063f96a34ed1cc2ed",status_only=True)
    assert result.snapshot.commit=="0d4cb56ad759b299c2e216b063f96a34ed1cc2ed"
    assert not result.decision.invocation_allowed and not result.decision.authority_granted


def test_canonical_nested_work_order_digest_and_execution_recheck():
    from automation.engine.repository_snapshot import resolve_repository_snapshot
    r=ready_fixture(); wo="automation/work_orders/wo.yaml"
    obj=json.loads(r.files[wo]);digest=obj.pop("scope_digest");obj["authority_basis"]["scope_digest"]=digest
    del obj["auto_imp_003_authorized"]
    obj["next_package_restriction"]="AUTO-IMP-003 NOT_AUTHORIZED; automatic next dispatch DENIED"
    r.files[wo]=json.dumps(obj).encode()
    recheck=dict(schema_version="automation.pre_dispatch_recheck.v1",work_order_id="WO",authorization_id="AUTH",
        execution_id="EXEC",scope_digest=digest,state="PASS",
        provider_raw=json.loads(r.files["automation/runs/EXEC/provider.json"])["provider_raw"],
        capacity_gate=dict(route="ALLOW_WITH_WATCH"))
    r.files["automation/runs/EXEC/recheck.json"]=json.dumps(recheck).encode()
    mutate(r,CURRENT,["pre_dispatch_recheck_path"],"automation/runs/EXEC/recheck.json")
    result=resolve_repository_snapshot(r,COMMIT)
    assert not result.diagnostics and result.decision.route=="READY_FOR_MANUAL_DISPATCH"
    assert "automation/runs/EXEC/recheck.json" in result.snapshot.read_order
    assert "automation/runs/EXEC/provider.json" not in result.snapshot.read_order
    mutate(r,"automation/runs/EXEC/recheck.json",["execution_id"],"OTHER")
    assert resolve_repository_snapshot(r,COMMIT).diagnostics


def test_raw_source_interface_proof_is_not_parsed_or_executed_as_yaml():
    from automation.engine.repository_snapshot import resolve_repository_snapshot
    r=ready_fixture();path="automation/engine/source.py"
    r.files[path]=b"raise RuntimeError('MUST_NOT_EXECUTE')\n"
    proof=dict(path=path,ref=COMMIT,git_blob_sha=r.read_blob(COMMIT,path).object_id,
               sha256=hashlib.sha256(r.files[path]).hexdigest())
    for p,keys in [("automation/authorizations/auth.yaml",["package_binding","dependency_bindings","current_interfaces"]),
                   (CURRENT,["authority_basis","dependencies","current_interfaces"]),
                   ("automation/work_orders/wo.yaml",["authority_basis","dependencies","current_interfaces"])]:
        mutate(r,p,keys,[proof])
    result=resolve_repository_snapshot(r,COMMIT)
    assert not result.diagnostics and result.decision.route=="READY_FOR_MANUAL_DISPATCH"
    assert path in result.snapshot.read_order and path not in result.snapshot.documents


@pytest.mark.parametrize("restriction",[None,"AUTO-IMP-003 AUTHORIZED","AUTO-IMP-003 NOT_AUTHORIZED"])
def test_work_order_restriction_cannot_be_missing_or_weakened(restriction):
    from automation.engine.repository_snapshot import resolve_repository_snapshot
    r=ready_fixture();obj=json.loads(r.files["automation/work_orders/wo.yaml"]);del obj["auto_imp_003_authorized"]
    if restriction is not None:obj["next_package_restriction"]=restriction
    r.files["automation/work_orders/wo.yaml"]=json.dumps(obj).encode()
    assert resolve_repository_snapshot(r,COMMIT).diagnostics
