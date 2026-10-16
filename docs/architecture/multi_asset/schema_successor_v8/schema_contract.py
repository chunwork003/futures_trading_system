"""架構候選的確定性 Schema 契約驗證器；不連線、不執行產品、不產生權限。"""
import copy,hashlib,json,pathlib
from jsonschema import Draft202012Validator
STANDARD='https://json-schema.org/draft/2020-12/schema'
CURRENT_PROFILE='MA-C3-LITERAL-EMPTY-PREFIXITEMS-QUIRK-v7'
HISTORY_PROFILE='MA-C2-LITERAL-EMPTY-PREFIXITEMS-QUIRK-v6'
FIELDS=('entity_id','revision_id','owner','hash_domain','source_hash')
class ContractError(ValueError):pass
def canonical(v):return json.dumps(v,ensure_ascii=False,sort_keys=True,separators=(',',':'),allow_nan=False).encode('utf-8')
def sha(b):return hashlib.sha256(b).hexdigest()
def key(r):return tuple(r[k] for k in FIELDS)
def literal_schema(v):
 """固定值模型：空陣列省略 prefixItems；非空 tuple 完整鎖定位置、型別與長度。"""
 if isinstance(v,dict):return dict(type='object',additionalProperties=False,required=list(v),properties={k:literal_schema(x) for k,x in v.items()})
 if isinstance(v,list):
  d=dict(type='array',minItems=len(v),maxItems=len(v),items=False)
  if v:d['prefixItems']=[literal_schema(x) for x in v]
  return d
 return dict(type='null' if v is None else 'boolean' if isinstance(v,bool) else 'integer' if isinstance(v,int) else 'number' if isinstance(v,float) else 'string',const=v)
def pointer_get(d,p):
 assert p.startswith('#/')
 for part in p[2:].split('/'):
  part=part.replace('~1','/').replace('~0','~');d=d[int(part)] if isinstance(d,list) else d[part]
 return d
def transform(raw_schema,pointers):
 """僅移除 fixed allowlist 中且完全符合守衛的空 prefixItems；不修補任意 Schema。"""
 d=copy.deepcopy(raw_schema)
 if len(pointers)!=len(set(pointers)):raise ContractError('DUPLICATE_POINTER')
 for p in pointers:
  if not p.endswith('/prefixItems'):raise ContractError('UNAUTHORIZED_TRANSFORM')
  node=pointer_get(d,p.rsplit('/',1)[0])
  if not (node.get('type')=='array' and node.get('prefixItems')==[] and node.get('items') is False and node.get('minItems')==0 and node.get('maxItems')==0):raise ContractError('TRANSFORM_GUARD_FAILED')
  del node['prefixItems']
 if '$schema' in d and d['$schema']!=STANDARD:raise ContractError('UNKNOWN_DIALECT')
 d['$schema']=STANDARD
 Draft202012Validator.check_schema(d)
 return d
def resolve(record,original_ref,profile,source_version,schema_bytes,source_bytes,effective_bytes):
 """明示 raw→effective 的具名適配；舊 ref 永不改指不同 bytes。"""
 if profile not in (CURRENT_PROFILE,HISTORY_PROFILE) or profile!=record['input_profile']:raise ContractError('UNKNOWN_DIALECT_OR_PROFILE')
 if source_version!=record['original_subject']:raise ContractError('SOURCE_VERSION_MISMATCH')
 if key(original_ref)!=key(record['original_schema_ref']):raise ContractError('SOURCE_ID_REVISION_CONFLICT')
 if sha(schema_bytes)!=record['original_schema_raw_sha256']:raise ContractError('SOURCE_HASH_CONFLICT')
 if sha(source_bytes)!=record['source_raw_sha256']:raise ContractError('SOURCE_CONTENT_HASH_CONFLICT')
 if sha(effective_bytes)!=record['effective_schema_ref']['source_hash']:raise ContractError('ADAPTED_SCHEMA_HASH_CONFLICT')
 effective=json.loads(effective_bytes)
 if effective.get('$schema')!=STANDARD:raise ContractError('UNKNOWN_DIALECT')
 expected=transform(json.loads(schema_bytes),record['transform_pointers'])
 if canonical(expected)!=effective_bytes:raise ContractError('ADAPTER_TRANSFORM_MISMATCH')
 Draft202012Validator.check_schema(effective)
 Draft202012Validator(effective).validate(json.loads(source_bytes))
 return effective
def read_pinned(root,pin):
 """僅讀候選內固定相對來源；拒絕跳脫、link/reparse 與內容漂移。"""
 root=pathlib.Path(root).resolve();rel=pathlib.Path(pin['path'])
 if rel.is_absolute() or rel.drive or '..' in rel.parts:raise ContractError('UNSAFE_REFERENCE_PATH')
 p=root/rel
 for q in (p,*p.parents):
  if q==root:break
  if q.is_symlink() or (hasattr(q,'is_junction') and q.is_junction()):raise ContractError('REFERENCE_REPARSE_DENIED')
 if not p.resolve().is_relative_to(root):raise ContractError('REFERENCE_OUTSIDE_ROOT')
 b=p.read_bytes()
 if sha(b)!=pin['raw_bytes_sha256']:raise ContractError('PIN_HASH_MISMATCH')
 return b
def check_effective_unit_inputs(root,companion,expected_subject):
 """供既有 WORK companion adapter 的純來源輸入檢核；不編譯工作單、不判施工資格。"""
 if companion['subject']!=expected_subject:raise ContractError('COMPANION_SUBJECT_MISMATCH')
 plans=json.loads(read_pinned(root,companion['base_units']))
 unit=pointer_get(plans,companion['base_pointer'])
 if unit['unit_id']!=companion['unit_id'] or unit['plan_revision_id']!=companion['base_plan_revision_id'] or sha(canonical(unit))!=companion['base_unit_canonical_sha256']:raise ContractError('UNIT_PLAN_COMPANION_CONFLICT')
 cat=json.loads(read_pinned(root,companion['source_resolution_catalog']))
 if cat['subject']!=expected_subject:raise ContractError('CATALOG_SUBJECT_MISMATCH')
 for op in companion['operation_companions']:
  wrapper=json.loads(read_pinned(root,op['contract']))
  if wrapper['operation_id']!=op['operation_id'] or wrapper['source_resolution_catalog']!=companion['source_resolution_catalog']:raise ContractError('OPERATION_COMPANION_CONFLICT')
 if companion['execution_authorized'] is not False:raise ContractError('COMPANION_CANNOT_GRANT_EXECUTION')
 return {'unit_id':unit['unit_id'],'base_plan_revision_id':unit['plan_revision_id'],'schema_companion_revision_id':companion['schema_companion_revision_id'],'input_status':'SOURCE_CONTRACT_INPUTS_BOUND_NOT_EXECUTION_ELIGIBILITY'}
