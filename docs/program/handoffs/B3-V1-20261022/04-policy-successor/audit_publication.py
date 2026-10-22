import json,pathlib,hashlib,datetime
O=pathlib.Path(__file__).parent
V=O.parent;R=pathlib.Path('D:/00_Learn/量化交易/Code/futures_trading_system')
Q=V/'ultra-b3-precompiled-queue-addendum-v1';H=V/'ultra-b3-mvp-execution-handoff-v1';IR=V/'bounded-continuous-policy-independent-review-20261022T044814Z'
def j(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def emit(n,x):
 with (O/n).open('x',encoding='utf-8',newline='\n') as f:f.write(json.dumps(x,ensure_ascii=False,indent=2)+'\n')
remote=j(O/'REMOTE_ALL_BRANCH_TREES.json');blobmap={}
for t in remote['trees']:
 assert t['truncated'] is False
 for x in t['tree']:
  if x['type']=='blob':blobmap.setdefault(x['sha'],[]).append({'branch':t['branch'],'head':t['head'],'path':x['path']})
def blob(p):
 b=p.read_bytes();return hashlib.sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest()
rows=[]
groups={'ORIGINAL_SIX_HANDOFF':[H/n for n in ['MVP_SCOPE.md','MVP_ROUTE.yaml','WORK_ORDER_CONTRACT.yaml','STAGE_GATES.yaml','VS_CODE_EXECUTOR.md','HANDOFF_STATUS.json']],
 'PRECOMPILED_QUEUE_119':[p for p in Q.rglob('*') if p.is_file()],
 'LATEST_POLICY_REVIEW_10':[p for p in IR.rglob('*') if p.is_file()],
 'ADOPTED_ENTRIES_AND_U01':[R/p for p in ['docs/architecture/B3_V1_ARCHITECTURE.md','docs/PROJECT_OPERATING_GUIDE.md','docs/program/decisions/B3-V1-DUAL-ADOPTION-20261015-v1.owner.v1.json','docs/architecture/adopted/B3_V1_ACCEPTED_BASELINE.v1.json','automation/work_orders/MA01-U01-MANUAL-01.acceptance.json','docs/program/decisions/MA01-U01-FIRST-RESULT-ACCEPTANCE.owner.v1.json']],
 'BTRACE_CLOSED_SUPPLEMENT':[V/'b3-engineering-consumer-projection-successor-proposed-v1/candidate/ENGINEERING_CONSUMER_PROJECTION_SUCCESSOR.candidate.v1.json']}
for group,ps in groups.items():
 for p in sorted(ps):
  rows.append({'group':group,'local_path':str(p),'bytes':p.stat().st_size,'raw_sha256':sha(p),'Git_blob_SHA1':blob(p),'published_exact_raw_blob_at':blobmap.get(blob(p),[]),'classification':'PUBLISHED_EXACT_BLOB' if blob(p) in blobmap else 'LOCAL_ONLY_EXACT_BYTES_NOT_IN_ANY_CURRENT_BRANCH_TREE'})
pinrecords=[];pins=j(Q/'PRECOMPILED_WORK_QUEUE.index.json')['source_pins']+j(Q/'INPUT_SOURCE_WITNESS.json')['source_pins']
def resolve(s):
 p=pathlib.Path(s)
 if p.is_file():return p,'DECLARED_PATH'
 # This is a named transport-only root map, never latest-name substitution.
 if 'futures_trading_system' in s:
  tail=s.split('futures_trading_system',1)[1].lstrip('/\\')
  p=R/tail
  if p.is_file():return p,'REPOSITORY_ROOT_LOCATOR_MAP_WITH_EXACT_EXPECTED_HASH'
 return p,'UNRESOLVED'
seen=set()
for x in pins:
 s=x['path'];expected=x.get('raw_sha256',x.get('sha256',x.get('raw_SHA256')));p,method=resolve(s)
 key=(str(p),expected)
 if key in seen:continue
 seen.add(key);ok=p.is_file() and sha(p)==expected
 pinrecords.append({'declared_path':s,'resolved_path':str(p),'method':method,'expected':expected,'actual':sha(p) if p.is_file() else None,'valid':ok})
hs=j(H/'HANDOFF_STATUS.json');hv=[]
assert sha(H/'HANDOFF_STATUS.json')=='4b64625861f93086998b8c3b53dcfc0e160414b90eb6f10f972db3c426269ee2'
for x in hs['output_manifest']['files']:
 p=H/x['path'];hv.append({'path':str(p),'raw_sha256':sha(p),'valid':sha(p)==x['sha256'] and p.stat().st_size==x['bytes']})
# Reuse the independently rebuilt graph. Check current byte identity and bounded graph identities without rerunning architecture.
idx=j(Q/'PRECOMPILED_WORK_QUEUE.index.json');unitids={e['unit_alias'] for e in idx['entries']}
emit('SOURCE_PIN_AND_SIX_FILE_CURRENTNESS.json',{'source_pins':pinrecords,'unique':len(pinrecords),'valid':sum(x['valid'] for x in pinrecords),'six_files_valid':len(hv)+1 if all(x['valid'] for x in hv) else False,'six_file_members':hv,'known_locator_defect':{'source':str(H/'HANDOFF_STATUS.json'),'selector':'#/current_authority_entry','literal':hs['current_authority_entry'],'canonical_entry':str(R/'docs/CURRENT_STATE.md'),'disposition':'HISTORICAL_LITERAL_NOT_USED_TO_RESOLVE_CURRENT_AUTHORITY; exact root locator mapping only; original bytes preserved'}})
summary={g:{'files':len(ps),'published_exact':sum(bool(x['published_exact_raw_blob_at']) for x in rows if x['group']==g),'missing_exact':sum(not x['published_exact_raw_blob_at'] for x in rows if x['group']==g)} for g,ps in groups.items()}
emit('GIT_PUBLICATION_AUDIT.json',{'observed_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'remote_default':'master','all_19_current_branch_trees_complete':all(t['truncated'] is False for t in remote['trees']),'scope':'Exact raw-byte membership in all current branch HEAD trees; not a claim about unreachable/deleted/historical commits or equivalent derived carriers','local_HEAD':'2634717b1443eb95fa0fde4d5d987347ef2160e8','master_HEAD':'9b5ab5fdd98744a7db45ec9f14b64ef1f324920f','topic_HEAD':'e287f6ac0744875e8d4bca103a6b73b4cf53416d','summary':summary,'files':rows,'proposed_document_branch':'codex/b3-v1-precompiled-policy-handoff-successor-01','proposed_base':'e287f6ac0744875e8d4bca103a6b73b4cf53416d','branch_created':False,'publication_authorization':'NOT_GRANTED; old exact publication grants consumed/not reusable','public_privacy_review':'NOT_PERFORMED_FOR_NEW_PUBLISHABLE_SET; audit inventory includes private local paths, do not publish raw audit automatically','publication_split':['Existing accepted B3 publication unchanged','Navigation/queue/supporting successor review in separate exact documentation publication request after candidate freeze','U01 accepted code/current integration separate exact source/Git request; no silent inclusion'],'historical_NAV_warning':'Published NAV original says not yet published and all coding not authorized; retain as historical body, overlay dated current facts from local exact receipts; not current Current State.'})
assert all(x['valid'] for x in pinrecords),'input source drift'
assert all(x['valid'] for x in hv),'six-file drift'
print(json.dumps({'groups':summary,'source_pins':len(pinrecords),'pins_valid':sum(x['valid'] for x in pinrecords),'six':len(hv)+1,'all_remote_trees':len(remote['trees'])}))

