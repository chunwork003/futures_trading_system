"""六個離線 Mock 情境；只操作記憶體 fixture，不實作 Controller 或操作 Repository。

此處 MOCK_ONLY Gate 判定不是原機器 eligibility，也不能產生正式 Grant／結果收據。
Expected 固定於先建立的 POC_CONTRACT.json，與本實作分離。
"""
import copy
import hashlib
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX = json.loads((ROOT / 'PRECOMPILED_WORK_QUEUE.index.json').read_text(encoding='utf-8'))
IMPACT = json.loads((ROOT / 'REVIEW_DEPENDENCY_IMPACT.json').read_text(encoding='utf-8'))
ORACLES = {x['id']: x['expected'] for x in json.loads((ROOT / 'POC_CONTRACT.json').read_text(encoding='utf-8'))['cases']}
ROWS = {x['unit_alias']: x for x in INDEX['entries']}
A, B, OTHER = 'MA02-U01', 'MA02-U05', 'MA10-U01'
OBSERVED = {}

def digest(body):
    return hashlib.sha256(json.dumps(body, ensure_ascii=False, sort_keys=True, separators=(',', ':'), allow_nan=False).encode()).hexdigest()

def accepted_fixture(alias):
    """合成 Result＋外部接受；不是現實 Unit Result，禁止寫入 actual ledger。"""
    body = {'mock_only': True, 'unit_id': ROWS[alias]['unit_id'], 'revision': ROWS[alias]['plan_revision_id'], 'output': {'nested': {'fixture': 'not_product_output'}}}
    h = digest(body)
    return {'body': body, 'ref': {'id': 'MOCK_ONLY_RESULT_' + alias, 'source_hash': h}, 'external_acceptance': {'mock_only': True, 'result_hash': h}, 'independent_review': {'mock_only': True, 'author': 'MOCK_AUTHOR', 'reviewer': 'MOCK_REVIEWER', 'result_hash': h}}

def world():
    grants = {a: {'id': 'MOCK_ONLY_GRANT_' + a, 'unit': a, 'used': False, 'lane': 'A', 'valid': True, 'run_scope': 'MOCK_NATIVE_SCOPE_1' if a in [A, B] else 'MOCK_NATIVE_SCOPE_2'} for a in [A, B, OTHER]}
    return {'mock_only': True, 'grants': grants, 'accepted': {'MA01-U01': accepted_fixture('MA01-U01')}, 'source_hash': {a: ROWS[a]['source_unit_canonical_sha256'] for a in ROWS}, 'qualified': {A, B, OTHER}, 'budget_ok': True, 'writer': None, 'unfinished': False, 'pending_review': [], 'policy_world': 'CURRENT_STRICT', 'proposed_policy_receipt_fixture': None, 'run_scope': None, 'invocation_events': [], 'real_progress_credit': 0}

def accepted(s, alias):
    r = s['accepted'].get(alias)
    if not r:
        return False
    h = digest(r['body']); review = r.get('independent_review') or {}; acceptance = r.get('external_acceptance') or {}
    return (r['body'].get('unit_id') == ROWS[alias]['unit_id'] and r['body'].get('revision') == ROWS[alias]['plan_revision_id'] and h == r['ref'].get('source_hash') == review.get('result_hash') == acceptance.get('result_hash') and review.get('author') != review.get('reviewer') and review.get('mock_only') is True and acceptance.get('mock_only') is True)

def project_mock_only(s, alias, lane='A'):
    assert s['mock_only'] is True, 'NO_PRODUCTION_ENTRY_POINT'
    g = s['grants'].get(alias)
    if not g or not g.get('valid') or g.get('unit') != alias or g.get('lane') != lane:
        return 'STOP_GRANT_MISSING'
    if g['used']:
        return 'STOP_GRANT_CONSUMED'
    if s['source_hash'].get(alias) != ROWS[alias]['source_unit_canonical_sha256']:
        return 'STOP_SOURCE_DRIFT'
    if alias not in s['qualified']:
        return 'STOP_QUALIFICATION'
    if not s['budget_ok']:
        return 'STOP_BUDGET'
    if s['writer'] is not None:
        return 'STOP_COMPETING_WRITER'
    if s['unfinished']:
        return 'STOP_UNFINISHED_EXECUTION'
    if s['pending_review']:
        # 此分支只模擬尚未採納的新規則；永遠不聲稱 current policy 允許。
        future_fixture = s['policy_world'] == 'PROPOSED_NOT_ACTIVE' and s['proposed_policy_receipt_fixture'] == 'MOCK_ONLY_REVIEWED_POLICY_SUCCESSOR'
        if not future_fixture:
            return 'STOP_REVIEW_BARRIER'
    if s['run_scope'] is not None and s['run_scope'] != g['run_scope']:
        return 'STOP_PACKAGE_RUN_BOUNDARY'
    for dep in ROWS[alias]['direct_dependencies']:
        if not accepted(s, dep):
            return 'STOP_DEPENDENCY_UNACCEPTED'
    return 'MOCK_ONLY_GATES_SATISFIED'

def mock_resume(s, checkpoint):
    assert s['mock_only']
    if not checkpoint.get('already_invoked') or not all(checkpoint.get(k) for k in ['execution','invocation','reservation','dispatch']):
        return 'STOP_NO_BACKFILL'
    if checkpoint['source_hash'] != ROWS[A]['source_unit_canonical_sha256']:
        return 'STOP_SOURCE_DRIFT'
    if s['writer'] not in [None, checkpoint['writer']]:
        return 'STOP_COMPETING_WRITER'
    return 'MOCK_RESUME_SAME_INVOCATION'

def batch_order(pending):
    """純資料排序：只組織待審 exact Subjects，不呼叫 Reviewer、不改狀態。"""
    left = {x['unit']: x for x in pending}; batches = []
    while left:
        ready = [u for u in left if not any(d in left for d in ROWS[u]['direct_dependencies'])]
        assert ready, 'PENDING_REVIEW_CYCLE'
        ready.sort(key=lambda a: (-left[a]['risk_rank'], -len(IMPACT['units'][a]['transitive_dependency_consumers']), ROWS[a]['rank']))
        first = ready[0]; key = (left[first]['contract_scope'], left[first]['review_type'])
        same = [u for u in ready if (left[u]['contract_scope'],left[u]['review_type']) == key]
        batches.append(same)
        for u in same:
            del left[u]
    return batches

def inspect_mock_review(packet, expected_hash):
    if packet['author'] == packet['reviewer']:
        return 'REJECT_SAME_AUTHOR_REVIEWER'
    if packet['subject_hash'] != expected_hash:
        return 'REJECT_REVIEW_HASH_DRIFT'
    return 'MOCK_REVIEW_VERIFIED_NOT_ACCEPTED'

class SixMockWorlds(unittest.TestCase):
    def test_P1_continuous_with_fresh_authority(self):
        self.assertEqual(ROWS[A]['direct_dependencies'], ['MA01-U01'])
        self.assertEqual(set(ROWS[B]['direct_dependencies']), {A, 'MA01-U01'})
        s = world(); actual = [project_mock_only(s, A)]
        s['grants'][A]['used'] = True
        s['run_scope'] = s['grants'][A]['run_scope']
        s['accepted'][A] = accepted_fixture(A)  # 明示 synthetic Review+Acceptance，非作者測試升格
        actual.append(project_mock_only(s, B))
        self.assertNotEqual(s['grants'][A]['id'], s['grants'][B]['id'])
        del s['grants'][B]; actual.append(project_mock_only(s, B))
        actual.append(project_mock_only(s, OTHER))
        OBSERVED['P1'] = copy.deepcopy(actual)
        self.assertEqual(actual, ORACLES['P1'])
        self.assertEqual(s['invocation_events'], [])
        self.assertEqual(s['real_progress_credit'], 0)

    def test_P2_resume_without_redispatch(self):
        s=world(); s['grants'][A]['used']=True
        checkpoint={'execution':'MOCK_ONLY_EXEC1','invocation':'MOCK_ONLY_INV1','reservation':'MOCK_ONLY_RES1','dispatch':'MOCK_ONLY_DIS1','already_invoked':True,'source_hash':ROWS[A]['source_unit_canonical_sha256'],'writer':'MOCK_ONLY_WRITER1','cumulative_cost':{'tokens':None,'reason':'UNKNOWN'}}
        original=copy.deepcopy(checkpoint); actual=[mock_resume(s, checkpoint)]
        bad=copy.deepcopy(checkpoint);bad['invocation']=None;actual.append(mock_resume(s,bad))
        bad=copy.deepcopy(checkpoint);bad['source_hash']='0'*64;actual.append(mock_resume(s,bad))
        s['writer']='MOCK_OTHER_WRITER';actual.append(mock_resume(s,checkpoint));s['writer']=None
        actual.append(project_mock_only(s,A))
        OBSERVED['P2'] = copy.deepcopy(actual)
        self.assertEqual(actual,ORACLES['P2']);self.assertEqual(checkpoint,original);self.assertEqual(s['invocation_events'],[])

    def test_P3_deferred_is_pending_not_permission(self):
        s=world();s['pending_review']=[{'unit':A,'status':'PENDING','frozen':True,'writer_released':True}]
        self.assertNotIn(A,s['accepted'])
        actual=['PENDING_NOT_ACCEPTED',project_mock_only(s,OTHER)]
        s['grants'][OTHER]['lane']='B';actual.append(project_mock_only(s,OTHER,'B'))
        s['policy_world']='PROPOSED_NOT_ACTIVE';s['proposed_policy_receipt_fixture']='MOCK_ONLY_REVIEWED_POLICY_SUCCESSOR'
        actual.append(project_mock_only(s,OTHER,'B'))
        OBSERVED['P3'] = copy.deepcopy(actual)
        self.assertEqual(actual,ORACLES['P3']);self.assertFalse(accepted(s,A));self.assertEqual(s['real_progress_credit'],0)
        s['unfinished']=True;self.assertEqual(project_mock_only(s,OTHER,'B'),'STOP_UNFINISHED_EXECUTION')

    def test_P4_missing_or_invalid_authority_has_no_effect(self):
        actual=[]
        for fault in ['missing','request_only','source','qualification','budget','writer']:
            s=world()
            if fault=='missing':del s['grants'][A]
            if fault=='request_only':s['grants'][A]['valid']=False
            if fault=='source':s['source_hash'][A]='wrong'
            if fault=='qualification':s['qualified'].remove(A)
            if fault=='budget':s['budget_ok']=False
            if fault=='writer':s['writer']='OTHER'
            actual.append(project_mock_only(s,A));self.assertEqual(s['invocation_events'],[]);self.assertEqual(s['real_progress_credit'],0)
        OBSERVED['P4'] = copy.deepcopy(actual)
        self.assertEqual(actual,ORACLES['P4'])
        s=world();self.assertEqual(project_mock_only(s,A,'B'),'STOP_GRANT_MISSING')

    def test_P5_unreviewed_upstream_and_body_conflict(self):
        s=world();actual=[project_mock_only(s,B)]
        s['accepted'][A]=accepted_fixture(A)
        s['accepted'][A]['body']['output']['nested']['fixture']='changed'
        # 即使局部 ref 重算，原外部 Review／Acceptance 不得指向新正文。
        s['accepted'][A]['ref']['source_hash']=digest(s['accepted'][A]['body'])
        actual.append(project_mock_only(s,B));OBSERVED['P5'] = copy.deepcopy(actual);self.assertEqual(actual,ORACLES['P5'])
        self.assertIn(B,IMPACT['units'][A]['transitive_dependency_consumers'])
        self.assertIn('MA10-U06',IMPACT['units'][A]['transitive_dependency_consumers'])
        s['accepted'][A]=accepted_fixture(A);s['accepted'][A]['external_acceptance']=None
        self.assertEqual(project_mock_only(s,B),'STOP_DEPENDENCY_UNACCEPTED')
        s['grants'][B]['lane']='B';s['policy_world']='PROPOSED_NOT_ACTIVE';s['proposed_policy_receipt_fixture']='MOCK_ONLY_REVIEWED_POLICY_SUCCESSOR'
        self.assertEqual(project_mock_only(s,B,'B'),'STOP_DEPENDENCY_UNACCEPTED')
        self.assertEqual(len(INDEX['original_edges']),364)
        self.assertTrue(IMPACT['no_runtime_edges_from_source_only_Consumer_modes'])

    def test_P6_catchup_batches_and_required_revalidation(self):
        pending=[{'unit':B,'risk_rank':3,'contract_scope':'CALENDAR','review_type':'NARROW_SEMANTIC'},{'unit':A,'risk_rank':3,'contract_scope':'INSTRUMENT_ID','review_type':'NARROW_SEMANTIC'}]
        ordered=[a for group in batch_order(pending) for a in group]
        actual=ordered
        expected_hash=ROWS[A]['source_unit_canonical_sha256']
        packet={'author':'X','reviewer':'X','subject_hash':expected_hash}
        actual.append(inspect_mock_review(packet,expected_hash));packet['reviewer']='Y';packet['subject_hash']='changed'
        actual.append(inspect_mock_review(packet,expected_hash))
        impact=set(IMPACT['units'][A]['transitive_dependency_consumers']);self.assertIn(B,impact)
        actual.append('REVALIDATION_REQUIRED');OBSERVED['P6'] = copy.deepcopy(actual);self.assertEqual(actual,ORACLES['P6'])
        self.assertNotIn('MA01-U01',ordered)
        s=world();packet={'author':'X','reviewer':'Y','subject_hash':expected_hash}
        self.assertEqual(inspect_mock_review(packet,expected_hash),'MOCK_REVIEW_VERIFIED_NOT_ACCEPTED')
        self.assertFalse(accepted(s,A));self.assertEqual(s['real_progress_credit'],0)
        ledger=json.loads((ROOT/'DEFERRED_REVIEW_LEDGER.json').read_text(encoding='utf-8'))
        self.assertEqual(ledger['actual_deferred_product_reviews'],[])

if __name__=='__main__':
    unittest.main()
