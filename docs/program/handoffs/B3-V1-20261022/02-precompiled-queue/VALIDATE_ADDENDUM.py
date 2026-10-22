"""離線文件／Mock Evidence 驗證，非資格、Grant 或受控 Compiler。"""
import hashlib
import json
import subprocess
from pathlib import Path
from collections import Counter

Q = Path(__file__).resolve().parent
R = Path('D:/00_Learn/量化交易/Code/futures_trading_system')

def read(p):
    return json.loads(p.read_text(encoding='utf-8'))

def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

def canonical(x):
    return hashlib.sha256(json.dumps(x,ensure_ascii=False,sort_keys=True,separators=(',',':'),allow_nan=False).encode()).hexdigest()

def validate():
    idx=read(Q/'PRECOMPILED_WORK_QUEUE.index.json');w=read(Q/'INPUT_SOURCE_WITNESS.json');checks=[]
    def check(name,condition,denominator=None):
        checks.append({'check':name,'status':'PASS' if condition else 'FAIL','denominator':denominator})
    originals=next(x for x in idx['source_pins'] if Path(x['path']).name=='EXECUTION_UNITS.json')
    U={x['unit_alias']:x for x in read(Path(originals['path']))['units']}
    source_projection=next(x for x in idx['source_pins'] if Path(x['path']).name=='ENGINEERING_CONSUMER_PROJECTION_SUCCESSOR.candidate.v1.json')
    original_bindings=read(Path(source_projection['path']))['effective_consumer_bindings']
    errors=[];checked={}
    for pin in w['source_pins']+idx['source_pins']:
        p=Path(pin['path']);key=str(p.resolve())
        expected=pin.get('raw_sha256') or pin.get('raw_bytes_sha256')
        if key in checked and checked[key]!=expected:errors.append({'path':key,'error':'CONFLICTING_PIN'})
        checked[key]=expected
        if not p.is_file() or sha(p)!=expected:errors.append({'path':key,'error':'MISSING_OR_RAW_HASH_DRIFT'})
    check('All named current/input/frozen source raw pins',not errors,len(checked))
    rows=idx['entries'];specs={x['unit_alias']:read(Q/x['spec_file']) for x in rows}
    check('Exact96 permanent Unit IDs/revisions',len(U)==len(specs)==96 and len({x['unit_id'] for x in U.values()})==96 and all(specs[a]['identity']['unit_id']==u['unit_id'] and specs[a]['identity']['plan_revision_id']==u['plan_revision_id'] for a,u in U.items()),96)
    check('All96 original complete bodies preserved',all(specs[a]['immutable_original_contract']==u and canonical(u)==specs[a]['source_binding']['base_unit']['selected_body_canonical_sha256'] for a,u in U.items()),96)
    check('All96 original required cases and negative oracles preserved',all(specs[a]['tests']['required_case_ids']==u['verification_contract']['required_case_ids'] and specs[a]['acceptance_criteria']['required_negative_cases']==u['negative_cases'] and specs[a]['acceptance_criteria']['required_positive_cases']==u['test_cases'] for a,u in U.items()),96)
    check('All spec hashes match Index',all(sha(Q/x['spec_file'])==x['raw_sha256'] for x in rows),96)
    original_E={(d['unit_alias'],a) for a,u in U.items() for d in u['dependencies']};actual_E={(d['unit_alias'],a) for a,s in specs.items() for d in s['dependencies']}
    check('Original364 edges identical',len(original_E)==364 and original_E==actual_E=={tuple(x) for x in idx['original_edges']},364)
    ranks={a:i for i,a in enumerate(idx['queue_order'])}
    check('96 queue ordering respects full DAG and MVP prefix',len(ranks)==96 and all(ranks[a]<ranks[b] for a,b in original_E) and all(x['MVP'] for x in rows[:57]) and all(not x['MVP'] for x in rows[57:]),96)
    B=[(b['operation_id'],b['unit_alias'],b['mode'],b['consumer_role']) for b in original_bindings];A=[(b['operation_id'],a,b['mode'],b['consumer_role']) for a,s in specs.items() for b in s['implementation_scope']['interfaces']]
    check('All578 Consumer roles/modes preserved',len(A)==len(B)==578 and Counter(A)==Counter(B),578)
    check('191 source-only modes not added as DAG edges',sum(b['mode']=='DESIGN_CHECK_SOURCE' for b in original_bindings)==191 and actual_E==original_E,191)
    check('All12 original planning Packages represented',len({x['package'] for x in rows})==12,12)
    m=read(Q/'PRECOMPILED_MVP_ROUTE.json');target={'MA10-U06'};todo=list(target)
    while todo:
        a=todo.pop()
        for d in U[a]['dependencies']:
            if d['unit_alias'] not in target:target.add(d['unit_alias']);todo.append(d['unit_alias'])
    check('57/184/11 exact MVP ancestor closure',len(target)==57 and len(m['MVP_edges'])==184 and len(m['MVP_waves'])==11 and target=={a for wave in m['MVP_waves'] for a in wave},57)
    check('No future Grant/Writer/Invocation/evidence populated',all(s['authority_effect']=='NONE' and all(v is None for k,v in s['execution_evidence'].items() if k!='rule') for s in specs.values()),96)
    check('Deferred ledger has zero phantom actual reviews',read(Q/'DEFERRED_REVIEW_LEDGER.json')['actual_deferred_product_reviews']==[],0)
    imp=read(Q/'REVIEW_DEPENDENCY_IMPACT.json')
    expected_descendants={}
    for alias in U:
        seen=set();todo=[b for a,b in original_E if a==alias]
        while todo:
            node=todo.pop()
            if node in seen:continue
            seen.add(node);todo.extend(b for a,b in original_E if a==node)
        expected_descendants[alias]=seen
    check('All96 direct/transitive impact sets derive from original DAG',len(imp['units'])==96 and all(set(imp['units'][a]['direct_consumers'])=={b for x,b in original_E if x==a} and set(imp['units'][a]['transitive_dependency_consumers'])==expected_descendants[a] for a in U),96)
    api_pin=next(x for x in idx['source_pins'] if Path(x['path']).name=='API_CATALOG.json');ui_pin=next(x for x in idx['source_pins'] if Path(x['path']).name=='UI_PAGE_CONTRACTS.json')
    api_ids={x['operation_id'] for x in read(Path(api_pin['path']))['endpoints']};ui_ids={x['page_id'] for x in read(Path(ui_pin['path']))['pages']}
    check('Original95 API/19 UI identities and all spec references resolve',len(api_ids)==95 and len(ui_ids)==19 and all(b['operation_id'] in api_ids for s in specs.values() for b in s['implementation_scope']['interfaces']) and all(p in ui_ids for s in specs.values() for p in s['implementation_scope']['UI_pages']),114)
    original_six=read(Q/'SIX_FILE_SUPPLEMENT_MAP.json')['old_six_preserved']
    check('Frozen six files unchanged',len(original_six)==6 and all(sha(Path(x['original_path']))==x['original_raw_sha256'] for x in original_six),6)
    poc=read(Q/'poc/POC_RESULTS.json');expected=read(Q/'POC_CONTRACT.json')['cases']
    check('Six Mock cases all actual outcomes match sealed expected',poc['tests_run']==6 and poc['failures']==poc['errors']==poc['skipped']==0 and all(poc['actual_case_sequences'][c['id']]==c['expected'] for c in expected),6)
    check('Mock expected/test-source hashes preserved',sha(Q/'POC_CONTRACT.json')==poc['expected_contract_raw_sha256'] and sha(Q/'poc/test_six_mock_contracts.py')==poc['test_source_raw_sha256'],2)
    check('Mock cannot count as qualification/activation',not poc['formal_Qualification'] and not poc['production_policy_successor_activated'] and poc['actual_Grant_or_Invocation_or_Writer_created']==0 and poc['product_source_writes']==0)
    check('Current Git HEAD/status unchanged',subprocess.check_output(['git','--no-optional-locks','rev-parse','HEAD'],cwd=R).decode().strip()==w['git_HEAD'] and subprocess.check_output(['git','--no-optional-locks','status','--porcelain=v1','--untracked-files=normal'],cwd=R).decode()==w['git_status'])
    return {'scope':'AUTHOR_DOCUMENT_AND_MOCK_VALIDATION_NOT_QUALIFICATION','checks':checks,'source_pin_errors':errors,'source_pins_checked':len(checked),'passed':sum(c['status']=='PASS' for c in checks),'failed':sum(c['status']=='FAIL' for c in checks),'product_coding_authorized':False,'product_tests_executed':0,'formal_independent_review_of_addendum':'NOT_RUN','all_pass':all(c['status']=='PASS' for c in checks)}

if __name__=='__main__':
    result=validate();print(json.dumps(result,ensure_ascii=False,indent=2));raise SystemExit(0 if result['all_pass'] else 1)
