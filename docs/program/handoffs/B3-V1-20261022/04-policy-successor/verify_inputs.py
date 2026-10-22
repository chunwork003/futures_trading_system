import pathlib,json,hashlib,subprocess,datetime
R=pathlib.Path('D:/00_Learn/量化交易/Code/futures_trading_system')
V=pathlib.Path('C:/Users/CHUNs/.codex/visualizations/2026/10/10/01a12634-1a08-7b51-bdfd-2d8ecbcc4889')
O=pathlib.Path(__file__).parent
def h(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def j(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def write(name,x):
 p=O/name
 with p.open('x',encoding='utf-8',newline='\n') as f:f.write(json.dumps(x,ensure_ascii=False,indent=2)+'\n')
def git(*a):return subprocess.check_output(['git',*a],cwd=R).decode('utf-8','replace').strip()
Q=V/'ultra-b3-precompiled-queue-addendum-v1';H=V/'ultra-b3-mvp-execution-handoff-v1';IR=V/'bounded-continuous-policy-independent-review-20261022T044814Z'
records=[];errors=[]
for dr,mn,pin in [(Q,'ADDENDUM_MANIFEST.json','86b61152e8188c5495da5ba0bfd3cf063f7de1a62f6d82abb48cb1188fdd51c6'),(IR,'REVIEW_OUTPUT_MANIFEST.json','0f30d04a44395fa64972807f62a9284481d228f54ddc92b3801dcd54d486464e')]:
 m=dr/mn;assert h(m)==pin,(m,h(m));mm=j(m);ls=[]
 for x in mm['files']:
  p=dr/x['path'];want=x.get('raw_sha256',x.get('raw_SHA256'));ok=p.is_file() and h(p)==want and p.stat().st_size==x['bytes']
  ls.append({'path':str(p),'expected':want,'actual':h(p) if p.is_file() else None,'bytes':p.stat().st_size if p.is_file() else None,'valid':ok})
  if not ok:errors.append(str(p))
 actual={str(p.relative_to(dr)).replace('\\','/') for p in dr.rglob('*') if p.is_file()};expected={x['path'] for x in mm['files']}|{mn}
 records.append({'directory':str(dr),'manifest':str(m),'manifest_sha256':h(m),'member_count':len(ls),'all_valid':all(x['valid'] for x in ls),'missing':sorted(expected-actual),'extra':sorted(actual-expected),'members':ls})
 if expected!=actual:errors.append(str(dr)+' set mismatch')
hs=j(H/'HANDOFF_STATUS.json');print('handoff_manifest',json.dumps(hs['output_manifest'],ensure_ascii=False)[:2000]);print('handoff_source_keys',hs['protection_and_currentness'].keys())
idx=j(Q/'PRECOMPILED_WORK_QUEUE.index.json');wit=j(Q/'INPUT_SOURCE_WITNESS.json')
print('pin0',idx['source_pins'][0]);print('witnesskeys',wit.keys())
paths=[R/'AGENTS.md',R/'docs/CURRENT_STATE.md',R/'docs/CURRENT_WORK.md',R/'docs/AI_HANDOFF.md',R/'automation/governance/master_manifest.v1.yaml',
 R/'docs/PROJECT_OPERATING_GUIDE.md',R/'docs/architecture/B3_V1_ARCHITECTURE.md',R/'docs/architecture/adopted/B3_V1_ACCEPTED_BASELINE.v1.json',
 R/'docs/program/decisions/B3-V1-DUAL-ADOPTION-20261015-v1.owner.v1.json',R/'automation/work_orders/MA01-U01-MANUAL-01.acceptance.json',R/'docs/program/decisions/MA01-U01-FIRST-RESULT-ACCEPTANCE.owner.v1.json']
for folder in ['automation/policies','automation/telemetry','automation/specs']:
 for fn in ['development_entry_protocol.v2.yaml','authorization_lifecycle.v1_1.yaml','development_state_machine.v2.yaml','execution_capacity_policy.v2_2.yaml','execution_cost_contract.v2.yaml','work_cost_accounting.v2.yaml']:
  p=R/folder/fn
  if p.is_file():paths.append(p)
paths.extend([R/'automation/prompts/WORK_ORCHESTRATOR_KERNEL.md',R/'automation/prompts/CODEX_EXECUTOR_KERNEL.md'])
pins=[{'path':str(p),'bytes':p.stat().st_size,'raw_sha256':h(p)} for p in paths]
index=R/'.git/index'
snap={'recorded_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'HEAD':git('rev-parse','HEAD'),'master':git('rev-parse','master'),'branch':git('branch','--show-current'),'status':git('status','--porcelain=v1','--untracked-files=normal'),'heads_and_remotes':git('for-each-ref','--format=%(refname) %(objectname)','refs/heads','refs/remotes'),'worktrees':git('worktree','list','--porcelain'),'index_raw_sha256':h(index),'pins':pins}
write('SOURCE_AND_GIT_BEFORE.json',snap);write('PREDECESSOR_MANIFEST_VERIFICATION.json',{'records':records,'errors':errors})
print(json.dumps({'verified_bundle_members':sum(len(x['members']) for x in records),'errors':errors,'pins':len(pins),'index_raw_sha256':h(index)}))

