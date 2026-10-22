import pathlib,json,hashlib,subprocess,datetime,os
O=pathlib.Path(__file__).parent;R=pathlib.Path('D:/00_Learn/量化交易/Code/futures_trading_system')
def j(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def h(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def git(*args):
 env=dict(os.environ);env['GIT_OPTIONAL_LOCKS']='0'
 return subprocess.check_output(['git',*args],cwd=R,env=env).decode('utf-8','replace').strip()
before=j(O/'SOURCE_AND_GIT_BEFORE.json');pins=[]
for x in before['pins']:
 p=pathlib.Path(x['path']);pins.append({'path':str(p),'expected':x['raw_sha256'],'actual':h(p),'valid':h(p)==x['raw_sha256']})
for x in j(O/'SOURCE_PIN_AND_SIX_FILE_CURRENTNESS.json')['source_pins']:
 p=pathlib.Path(x['resolved_path']);pins.append({'path':str(p),'expected':x['expected'],'actual':h(p),'valid':h(p)==x['expected']})
bundle=[]
for rec in j(O/'PREDECESSOR_MANIFEST_VERIFICATION.json')['records']:
 m=pathlib.Path(rec['manifest']);bundle.append({'path':str(m),'valid':h(m)==rec['manifest_sha256']})
 for x in rec['members']:bundle.append({'path':x['path'],'valid':h(pathlib.Path(x['path']))==x['expected']})
P=O/'candidate';cm=P/'CANDIDATE_MANIFEST.json';expected=j(O/'NARROW_REVIEW_REQUEST.json')['manifest_raw_sha256']
assert h(cm)==expected
for x in j(cm)['files']:assert h(P/x['path'])==x['raw_sha256']
after={'recorded_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'HEAD':git('rev-parse','HEAD'),'branch':git('branch','--show-current'),'status':git('status','--porcelain=v1','--untracked-files=normal'),'heads_and_remotes':git('for-each-ref','--format=%(refname) %(objectname)','refs/heads','refs/remotes'),'index_raw_sha256':h(R/'.git/index'),'pins':pins,'predecessor_bundle_members':bundle,'candidate_manifest_raw_sha256':h(cm)}
after['comparison']={'HEAD_unchanged':after['HEAD']==before['HEAD'],'branch_unchanged':after['branch']==before['branch'],'status_unchanged':after['status']==before['status'],'all_refs_unchanged':after['heads_and_remotes']==before['heads_and_remotes'],'index_raw_bytes_unchanged':after['index_raw_sha256']==before['index_raw_sha256'],'source_pin_drift_count':sum(not x['valid'] for x in pins),'protected_bundle_drift_count':sum(not x['valid'] for x in bundle),'source_writes_by_this_task':0}
with (O/'SOURCE_AND_GIT_AFTER.json').open('x',encoding='utf-8') as f:json.dump(after,f,ensure_ascii=False,indent=2)
print(json.dumps(after['comparison']))

