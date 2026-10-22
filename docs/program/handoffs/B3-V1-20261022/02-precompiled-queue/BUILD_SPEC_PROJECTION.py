"""唯讀原始來源，建立隔離施工規格投影；不是 WORK Compiler、Scheduler 或 Authority。

只允許 CREATE_NEW 導航檔；--verify 只比較原始契約與既存投影。
不 import 專案執行引擎、不呼叫 Compiler／Grant／Writer／網路／SQL。
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import yaml

ROOT = Path(__file__).resolve().parent
BASE = ROOT.parent / 'ultra-b3-mvp-execution-handoff-v1'
REPO = Path('D:/00_Learn/量化交易/Code/futures_trading_system')

def raw_pin(p):
    b = p.read_bytes()
    return {'path': str(p), 'raw_sha256': hashlib.sha256(b).hexdigest(), 'bytes': len(b), 'hash_domain': 'EXACT_RAW_FILE_BYTES_SHA256'}

def canonical_hash(x):
    return hashlib.sha256(json.dumps(x, ensure_ascii=False, sort_keys=True, separators=(',', ':'), allow_nan=False).encode('utf-8')).hexdigest()

def read_json(p):
    return json.loads(p.read_text(encoding='utf-8'))

def verified_json(pin):
    p = Path(pin['path'])
    expected = pin.get('raw_sha256') or pin.get('raw_bytes_sha256')
    assert raw_pin(p)['raw_sha256'] == expected, f'SOURCE_HASH_MISMATCH:{p}'
    return read_json(p)

def write_new(p, x, verify):
    payload = (json.dumps(x, ensure_ascii=False, indent=2, allow_nan=False) + '\n').encode('utf-8')
    if verify:
        assert p.read_bytes() == payload, f'PROJECTION_DIFF:{p}'
    else:
        with p.open('xb') as f:
            f.write(payload)

def ancestors(alias, units):
    todo = [alias]; found = set()
    while todo:
        a = todo.pop()
        if a in found:
            continue
        found.add(a); todo.extend(d['unit_alias'] for d in units[a]['dependencies'])
    return found

def build(verify=False):
    status = read_json(BASE / 'HANDOFF_STATUS.json')
    assert raw_pin(BASE / 'HANDOFF_STATUS.json')['raw_sha256'] == '4b64625861f93086998b8c3b53dcfc0e160414b90eb6f10f972db3c426269ee2'
    for p in status['output_manifest']['files']:
        assert raw_pin(BASE / p['path'])['raw_sha256'] == p['sha256']
    route = yaml.safe_load((BASE / 'MVP_ROUTE.yaml').read_text(encoding='utf-8'))
    stage = yaml.safe_load((BASE / 'STAGE_GATES.yaml').read_text(encoding='utf-8'))
    original = verified_json(route['source_catalogs']['EXECUTION_UNITS.json'])
    units = {u['unit_alias']: u for u in original['units']}
    planning = verified_json(route['planning_input'])
    projection = verified_json(route['required_projection_companion'])
    api = {a['operation_id']: a for a in verified_json(route['source_catalogs']['API_CATALOG.json'])['endpoints']}
    bindings = projection['effective_consumer_bindings']
    assert len(units) == 96 and len(bindings) == 578 and len(api) == 95
    edges = sorted((d['unit_alias'], u['unit_alias']) for u in units.values() for d in u['dependencies'])
    assert len(edges) == 364 and len(set(edges)) == 364
    remaining = set(units); done = set(); levels = []
    while remaining:
        level = sorted(a for a in remaining if all(d['unit_alias'] in done for d in units[a]['dependencies']))
        assert level, 'ORIGINAL_DEPENDENCY_CYCLE'
        levels.append(level); done.update(level); remaining.difference_update(level)
    mvp = ancestors('MA10-U06', units)
    assert len(mvp) == 57 and sum(b in mvp for a,b in edges) == 184
    mvp_order = [a for level in route['waves'] for a in level]
    assert set(mvp_order) == mvp
    ordered = mvp_order + [a for level in levels for a in level if a not in mvp]
    assert len(ordered) == 96 and len(set(ordered)) == 96
    rank = {a: i for i,a in enumerate(ordered)}
    assert all(rank[a] < rank[b] for a,b in edges)
    node_sources = {}; entries = []; pins = {}
    def add_pin(p):
        pin = raw_pin(p); pins[str(p)] = pin; return pin
    for p in [BASE / 'HANDOFF_STATUS.json', BASE / 'MVP_ROUTE.yaml', BASE / 'WORK_ORDER_CONTRACT.yaml', BASE / 'STAGE_GATES.yaml', Path(route['planning_input']['path']), Path(route['required_projection_companion']['path'])]:
        add_pin(p)
    for p in route['source_catalogs'].values():
        add_pin(Path(p['path']))
    stage_closure = {s['label']: set().union(*(ancestors(a, units) for a in s['target_units'])) for s in stage['stages']}
    folder = ROOT / 'unit_specs'
    if not verify:
        folder.mkdir(exist_ok=False)
    for alias in ordered:
        u = units[alias]; p = planning['unit_compilation_inputs'][alias]
        assert p['unit_id'] == u['unit_id'] and p['unchanged_base_plan_revision_id'] == u['plan_revision_id']
        i = next(i for i,x in enumerate(original['units']) if x['unit_alias'] == alias)
        base_selector = {'file': route['source_catalogs']['EXECUTION_UNITS.json'], 'json_pointer': f'#/units/{i}', 'selected_body_canonical_sha256': canonical_hash(u), 'hash_rule': 'UTF8 sorted keys compact JSON ensure_ascii=False; selected-body navigation pin, not new Result hash semantics'}
        companion = p['v9_unit_companion']; verified_json(companion); add_pin(Path(companion['path']))
        chapter = p['effective_chapter_artifact']; chapter_path = Path(chapter['path'])
        assert raw_pin(chapter_path)['raw_sha256'] == chapter['raw_bytes_sha256']; add_pin(chapter_path)
        own = [b for b in bindings if b['unit_alias'] == alias]
        interfaces = []
        for b in own:
            assert b['unit_id'] == u['unit_id'] and b['unit_plan_revision_id'] == u['plan_revision_id']
            op = api[b['operation_id']]
            interfaces.append({'operation_id': b['operation_id'], 'mode': b['mode'], 'consumer_role': b['consumer_role'], 'producer': b['producer'], 'request': b['request'], 'response': b['response'], 'contract_source': b['contract_source'], 'API_source_pointer': b['API_source_pointer'], 'named_model_closure': b['named_model_closure'], 'typed_model_catalog': b['typed_model_catalog'], 'operation_source': b['operation_source'], 'oracle_binding': b['oracle_binding'], 'dto_version': op['dto_version'], 'auth_scope': op['auth_scope'], 'validation_contract': op['validation_contract'], 'failure_contract': op['failure_contract'], 'layer_boundary_binding': b['layer_boundary_binding'], 'source_only_not_new_runtime_edge': b['mode'] == 'DESIGN_CHECK_SOURCE'})
        snapshots = [{'dependency_alias': d['unit_alias'], 'snapshot': 'EXACT_U01_EXTERNAL_ACCEPTANCE_AVAILABLE' if d['unit_alias'] == 'MA01-U01' else 'MISSING_ACCEPTED_RESULT_OR_QUALIFIED_REUSE', 'execution_satisfaction': 'REVALIDATE_ORIGINAL_REQUIRED_GATE_BEFORE_USE', 'receipt_pointer': str(REPO / 'automation/work_orders/MA01-U01-MANUAL-01.acceptance.json') if d['unit_alias'] == 'MA01-U01' else None} for d in u['dependencies']]
        spec = {
          'format_role': 'PRECOMPILED_UNIT_SPEC_NAVIGATION_COMPANION_NOT_NATIVE_WO',
          'spec_revision': 'precompiled.v1', 'authority_effect': 'NONE',
          'identity': {k:u[k] for k in ['unit_alias','unit_id','feature_id','plan_revision','plan_revision_id','source_revision','chapter_revision']},
          'planning_package': p['primary_planning_package'], 'package_identity_rule': 'PK is grouping only, not closed Pxx machine package identity',
          'queue_rank': rank[alias], 'MVP_priority': alias in mvp,
          'MVP_wave': next((i for i,l in enumerate(route['waves']) if alias in l), None),
          'progress_snapshot': 'ACCEPTED_REUSE_ONLY_NO_REDISPATCH' if alias == 'MA01-U01' else 'NO_NEW_CODING_AUTHORITY_OR_ACCEPTED_RESULT',
          'source_binding': {'base_unit':base_selector, 'planning_compilation':{'file':route['planning_input'], 'json_pointer':f'#/unit_compilation_inputs/{alias}', 'selected_body_canonical_sha256':canonical_hash(p)}, 'effective_architecture':p['effective_adopted_architecture_binding'], 'effective_policy':p['effective_adopted_policy_binding'], 'v9_unit_companion':companion, 'effective_chapter':chapter, 'reviewed_consumer_companion':route['required_projection_companion'], 'historical_internal_candidate_labels_preserved':True},
          'immutable_original_contract':u,
          'effective_engineering_supplement':next(({'source':route['required_projection_companion'], 'json_pointer':f'#/affected_unit_companions/{j}/after', 'value':c['after']} for j,c in enumerate(projection['affected_unit_companions']) if c['unit_alias']==alias), {'status':'NO_AFFECTED_SUMMARY_SUCCESSOR_NEEDED; original plus full effective Consumer rows still apply'}),
          'requirements':p['requirements'], 'dependencies':u['dependencies'], 'dependency_snapshot_not_satisfaction':snapshots,
          'qualification':{'current_receipt':'U01_EXTERNAL_ACCEPTED_RESULT_ONLY' if alias == 'MA01-U01' else 'UNKNOWN_NOT_ESTABLISHED_FOR_THIS_INTENDED_USE', 'p00_applicability_rule':p['p00_gate'], 'runtime_applicability_rule':p['runtime_gate'], 'source_profile_context_result_intake':'Exact applicable receipts/profile use; U01/U02 limited Manual receipts not transferable; absent evidence HOLD affected use'},
          'implementation_scope':{'goal':u['goal'], 'source_input_output':u['input_output'], 'interfaces':interfaces, 'UI_pages':p['ui_pages'], 'database_migration_boundary':u['database_migration_boundary'], 'contract_first':'React -> ASP.NET BFF -> Python API -> Quant Core -> Persistence'},
          'paths':{'proposal_only':u['allowed_changes'], 'exists_at_generation':{f:(REPO / f).exists() for f in u['allowed_changes']['proposed_exact_paths']}, 'actual_execution_allowlist':None, 'forbidden_and_protected':u['protected_contracts'], 'rule':'Exact current placement/CreateNew or preimages and control-plane scope required in native WO; no wildcard or implicit mkdir/extra writes'},
          'acceptance_criteria':{'source_gate':u['acceptance_gate'], 'expected_evidence':u['expected_evidence'], 'required_positive_cases':u['test_cases'], 'required_negative_cases':u['negative_cases'], 'author_PASS_is_not_Acceptance':True},
          'tests':{'verification_contract':u['verification_contract'], 'required_case_ids':u['verification_contract']['required_case_ids'], 'required_case_ids_canonical_sha256':canonical_hash(u['verification_contract']['required_case_ids']), 'planned_commands':u['verification_contract']['targeted_test_command_proposal'], 'actual_product_results':'NOT_RUN_BY_THIS_PROJECTION', 'regression_trigger_source':stage['finding_regression']['source'], 'fixture_source':route['source_catalogs']['UNIT_FIXTURES.candidate.v5.json']},
          'review':{'mandatory_original_requirement':u['verification_contract']['review_requirement'], 'stage_aggregation_when_applicable':[k for k,closed in stage_closure.items() if alias in closed], 'stage_source':str(BASE / 'STAGE_GATES.yaml'), 'record_deferral':'Allowed as a derived observation, never PASS', 'review_deferral_eligibility':'NO_IMPLICIT_DELAY_PAST_ORIGINAL_ACCEPTANCE_OR_DEPENDENCY_GATE', 'pending_review_new_dispatch':'FAIL_CLOSED_UNLESS_EXACT_EXISTING_RULE_OR_REVIEWED_ACCEPTED_POLICY_SUCCESSOR', 'Lane_B':'Separate explicit candidate Grant + supported route/policy + writer; unreviewed high-risk semantics cannot become formal downstream dependency', 'independence':'Actual author and reviewer context/identity distinct; qualified substitute allowed, not automatically Ultra-required'},
          'risk':{'original_risk_level':u['risk_level'], 'planning_minimum_and_escalation':p['minimum_change_risk_display_projection'], 'capability':u['model_capability_requirement']},
          'revalidation':{'source_environment_authority':['Fresh HEAD/Current/policies/receipts','Original full source/reverse/required companion closure and body readback','Exact dependency Result+Acceptance or qualified reuse','Intended-use Executor/Operator/Producer/Consumer/Continuity/Context/Profile/Result/Intake','Finite Grant/Budget/provider limits/global Writer/actual invocation','Mandatory review/regression/stage gate and immutable Result ref/body digest'], 'compiler_inputs':p['mandatory_compiler_inputs'], 'required_pair_ids':p['required_pair_ids'], 'required_operation_ids':p['required_operation_ids']},
          'cost':{'WORK_forecast':u['estimated_cost'], 'Executor_actual':None, 'Variance':None, 'unobservable':'UNKNOWN with missing reason, never Provider percent as exact tokens', 'budget_condition':'Explicit original-policy finite authorization/UNKNOWN acceptance required for this Unit; not transferable from prior Grant'},
          'execution_evidence':{'native_WO_id':None,'execution_id':None,'Grant_ref':None,'Writer_ref':None,'source_and_Git':None,'commands_and_exit_and_case_logs':None,'cost_and_timestamps':None,'Result_ref_and_body':None,'independent_Review':None,'Intake':None,'Human_Acceptance':None,'rule':'Future actual evidence only; spec, Mock PoC and fixture output cannot fill these fields'},
          'recovery_checkpoint':{'actual_checkpoint':None,'requirements':'Preserve exact same WO/execution/reservation/dispatch/source/delta/budget/tests/telemetry/writer lineage; resume only real already-invoked identity after fresh validation; UNKNOWN outcome STOP_NO_BACKFILL'},
          'STOP_conditions':u['STOP_conditions'],
          'next_eligible_work_candidates':{'direct_successors_if_all_their_other_original_gates_satisfied':[b for a,b in edges if a == alias], 'actual_eligible_or_authorized_successors':[], 'rule':'Per-edge accepted result, not entire Package completion; re-entry policy and next Grant still required'}
        }
        path = folder / f'{alias}.spec.json'; write_new(path,spec,verify)
        node_sources[alias] = {'identity':spec['identity'], 'package':p['primary_planning_package']}
        entries.append({'unit_alias':alias,'unit_id':u['unit_id'],'plan_revision_id':u['plan_revision_id'],'package':p['primary_planning_package'],'rank':rank[alias],'MVP':alias in mvp,'MVP_wave':spec['MVP_wave'],'spec_file':str(path.relative_to(ROOT)),'raw_sha256':raw_pin(path)['raw_sha256'],'source_unit_canonical_sha256':canonical_hash(u),'direct_dependencies':[d['unit_alias'] for d in u['dependencies']],'accepted_snapshot':alias=='MA01-U01','execution_authorized':False})
    index = {'artifact_role':'DERIVED_PRECOMPILED_QUEUE_NOT_AUTHORIZATION_OR_CURRENT_STATE','revision':'precompiled.v1','source_subject':status['adopted_architecture']['subject'],'Git':{k:status['Git'][k] for k in ['local_HEAD','remote_master','publication_v3','NAV_topic_HEAD']},'counts':{'packages':len({x['package'] for x in entries}),'units':96,'dependencies':364,'API':95,'UI':19,'consumer_bindings':578,'MVP_units':57,'MVP_edges':184,'MVP_waves':11},'queue_order':ordered,'entries':entries,'MVP_waves':route['waves'],'original_edges':edges,'source_pins':list(pins.values()),'actual_executable_frontier':[],'first_MVP_preparation':'MA02-U01','classification':'All96 specs generated; exact runtime compilation/Grants/qualification remain per Unit; U01 historical accepted reuse only'}
    write_new(ROOT/'PRECOMPILED_WORK_QUEUE.index.json',index,verify)
    route_out = {'role':'DERIVED_MVP_AND_COMPLETE_B3_NAVIGATION','source':raw_pin(ROOT/'PRECOMPILED_WORK_QUEUE.index.json'),'MVP_target':'MA10-U06','MVP_wave_count':11,'MVP_waves':route['waves'],'MVP_edges':[(a,b) for a,b in edges if b in mvp],'remaining_complete_B3':[a for a in ordered if a not in mvp],'actual_executable_frontier':[],'hypothetical_frontier_after_current_U01_acceptance':[a for a in ordered if a!='MA01-U01' and all(d['unit_alias']=='MA01-U01' for d in units[a]['dependencies'])],'no_new_Grant_or_Machine_state':True}
    write_new(ROOT/'PRECOMPILED_MVP_ROUTE.json',route_out,verify)
    return {'mode':'VERIFY' if verify else 'CREATE_NEW','specs':96,'MVP_specs':57,'edges':364,'MVP_edges':184,'consumer_links':578,'output_only':str(ROOT),'formal_compiler_invoked':False,'product_tests_run':False,'authority_effect':'NONE'}

if __name__ == '__main__':
    p=argparse.ArgumentParser();p.add_argument('--verify',action='store_true');args=p.parse_args()
    print(json.dumps(build(args.verify),ensure_ascii=False))
