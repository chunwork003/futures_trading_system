"""從固定來源契約正向推導必要配對；不讀取現行操作宣告的 resolution_ids。"""
from __future__ import annotations

import collections
import hashlib
import json
import pathlib
import uuid

FIELDS = ('entity_id', 'revision_id', 'owner', 'hash_domain', 'source_hash')
STANDARD = 'https://json-schema.org/draft/2020-12/schema'
NS = uuid.UUID('e306af13-7f0f-5a4b-a4d8-9e60d58e3686')
WORLD = 'CYCLE03_FINITE_OPERATION_WORLD.candidate.v7.json'
ARCHIVE = 'fixtures/operation_worlds/private/BUILDER_OPERATION_WORLD.candidate.v6.json'
BODY_CATALOG = 'CYCLE03_BODY_VALUE_CATALOG.candidate.v7.json'
MAP = 'OPERATION_PRODUCER_CONSUMER_MAP.candidate.v5.json'


def canonical(value):
    return json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(',', ':'), allow_nan=False).encode('utf-8')


def sha(value):
    return hashlib.sha256(value).hexdigest()


def key(value):
    return tuple(value[f] for f in FIELDS)


def is_ref(value):
    return isinstance(value, dict) and all(isinstance(value.get(f), str) for f in FIELDS)


def all_refs(value):
    if isinstance(value, dict):
        if is_ref(value):
            yield value
        for child in value.values():
            yield from all_refs(child)
    elif isinstance(value, list):
        for child in value:
            yield from all_refs(child)


def pointer(value, text):
    if text == '#':
        return value
    for part in text.removeprefix('#/').split('/'):
        part = part.replace('~1', '/').replace('~0', '~')
        value = value[int(part)] if isinstance(value, list) else value[part]
    return value


def derive_expected(P):
    """P 為固定候選 multi_asset 目錄；回傳來源資格投影，不賦予任何正式權限。

    所有需求由 immutable case 的 ContractRef 正向跟隨固定 source/body/binding
    關聯。v8 operation companion 只用於固定 43 項範圍及 original case pin；
    其 resolution_ids、resolver 成功輸出及本輪 actual pair catalog 均不讀取。
    """
    P = pathlib.Path(P)
    pin_cache = {}
    def load(rel):
        return json.loads((P / rel).read_bytes())
    def pin(rel):
        target = pathlib.Path(rel)
        target = target if target.is_absolute() else P / target
        if str(target) in pin_cache:
            return pin_cache[str(target)]
        try:
            name = target.relative_to(P).as_posix()
        except ValueError:
            name = str(target)
        result = {'path': name, 'raw_bytes_sha256': sha(target.read_bytes())}
        pin_cache[str(target)] = result
        return result
    def found_path(raw_path, expected_hash, alternatives=()):
        paths = [pathlib.Path(raw_path)] + [P / a for a in alternatives]
        if not pathlib.Path(raw_path).is_absolute():
            paths.insert(0, P / raw_path)
        matches = [p for p in paths if p.is_file() and sha(p.read_bytes()) == expected_hash]
        if not matches:
            raise ValueError('EXACT_SOURCE_PATH_NOT_FOUND:' + str(raw_path))
        # 優先本候選可攜式路徑；歷史原路徑僅作唯讀來源證據。
        matches.sort(key=lambda p: (not p.is_relative_to(P), str(p)))
        return pin(matches[0])

    world = load(WORLD)
    archive = load(ARCHIVE)
    catalog = load(BODY_CATALOG)
    mappings = load(MAP)['operations']
    mapping = {r['operation_id']: r for r in mappings}
    v8_scope = load('schema_successor_v8/43_OPERATION_SCHEMA_CLOSURE.v8.json')
    resolutions = load('schema_successor_v8/SCHEMA_RESOLUTION_CATALOG.v8.json')['records']
    resolution_by_pair = collections.defaultdict(list)
    for record in resolutions:
        resolution_by_pair[(key(record['source_ref']), key(record['original_schema_ref']))].append(record)

    nodes = collections.defaultdict(list)
    registry = {}
    source_pairs = []
    body_pins = {}
    body_pins_by_source = collections.defaultdict(list)

    def add(ref, obj, location, role):
        if not is_ref(ref):
            return
        registry[key(ref)] = ref
        nodes[key(ref)].append({'object': obj, 'location': location, 'role': role})

    def index_objects(obj, location):
        if isinstance(obj, dict):
            add(obj.get('ref'), obj, location, 'EXPLICIT_REF_OWNER_OBJECT')
            for name, child in obj.items():
                index_objects(child, location + '/' + name)
        elif isinstance(obj, list):
            for i, child in enumerate(obj):
                index_objects(child, location + '/' + str(i))

    index_objects(world, WORLD + '#')
    index_objects(archive, ARCHIVE + '#')
    for label, source in world['sources'].items():
        # 共享 read-cut 只綁定其自身 source/schema，不擴張 archive membership。
        body = {n: source[n] for n in ('source_ref', 'source_schema_ref')} if label == 'predecessor-read-cut' else source
        loc = WORLD + '#/sources/' + label
        add(source['source_ref'], body, loc, 'SOURCE_TO_SCHEMA_AND_EXPLICIT_BODY_REFERENCES')
        source_pairs.append({
            'source_label': label, 'source_ref': source['source_ref'], 'schema_ref': source['source_schema_ref'],
            'source': found_path(source['relative_path'], source['raw_bytes_sha256'], ('fixtures/finite_worlds/' + source['relative_path'],)),
            'schema': found_path(source['source_schema_path'], source['source_schema_raw_sha256'], ('fixtures/finite_worlds/' + source['source_schema_path'],)),
            'source_version': 'MA-ARCH-REVIEW-v6-CYCLE02' if source.get('original_candidate_path') else 'MA-ARCH-REVIEW-v7-CYCLE03', 'source_declaration': {'source': pin(WORLD), 'pointer': '#/sources/' + label},
            'source_snapshot_version': 'MA-ARCH-REVIEW-v7-CYCLE03',
            'source_representation': 'BASE64_OF_EXACT_RAW_BYTES' if source.get('binary') else 'JSON_PARSED_EXACT_RAW_BYTES',
            'source_binary': bool(source.get('binary')),
        })
    for label, source in archive['source_blobs'].items():
        loc = ARCHIVE + '#/source_blobs/' + label
        archive_node = {'subject_ref': source['subject_ref'], 'source_schema_ref': source['source_schema_ref']} if source['subject_ref'] == archive['read_snapshot_ref'] else source
        add(source['subject_ref'], archive_node, loc, 'HISTORICAL_SOURCE_TO_SCHEMA_AND_EXPLICIT_BODY_REFERENCES')
        schema = archive['source_schemas'][label]
        source_pairs.append({
            'source_label': 'C2-PROTECTED:' + label, 'source_ref': source['subject_ref'], 'schema_ref': source['source_schema_ref'],
            'source': found_path(source['exact_bytes_path'], source['raw_bytes_sha256'], ('fixtures/operation_worlds/private/source/' + label + '.json', 'fixtures/operation_worlds/private/source/' + label + '.bin')),
            'schema': found_path(schema['exact_bytes_path'], schema['raw_bytes_sha256'], ('fixtures/operation_worlds/private/source_schemas/' + label + '.schema.json',)),
            'source_version': 'MA-ARCH-REVIEW-v6-CYCLE02', 'source_declaration': {'source': pin(ARCHIVE), 'pointer': '#/source_blobs/' + label},
            'source_snapshot_version': 'MA-ARCH-REVIEW-v6-CYCLE02',
            'source_representation': 'JSON_PARSED_EXACT_RAW_BYTES' if source.get('media_type') == 'application/json' else 'BASE64_OF_EXACT_RAW_BYTES',
            'source_binary': source.get('media_type') != 'application/json',
        })
    for i, row in enumerate(catalog['entries']):
        loc = BODY_CATALOG + '#/entries/' + str(i)
        add(row['contract_ref'], row, loc, 'BODY_CONTRACT_TO_SOURCE_REF_AND_MODEL_SCHEMA')
        body_pin = found_path(row['relative_path'], row['raw_bytes_sha256'], ('fixtures/finite_worlds/' + row['relative_path'], 'fixtures/operation_worlds/private/' + row['relative_path']))
        body_pins[key(row['contract_ref'])] = {'role': 'IMMUTABLE_BODY_READBACK', 'pin': body_pin, 'contract_ref': row['contract_ref'], 'canonical_sha256': row['canonical_body_sha256'], 'evidence': {'source': pin(BODY_CATALOG), 'pointer': '#/entries/' + str(i)}}
        if is_ref(row.get('source_ref')):
            body_pins_by_source[key(row['source_ref'])].append(body_pins[key(row['contract_ref'])])
    for label, binding in world['typed_body_bindings'].items():
        add(binding.get('subject_ref'), binding, WORLD + '#/typed_body_bindings/' + label, 'SUBJECT_TO_EXPLICIT_SOURCE_BINDINGS')
    for label, body in archive['typed_bodies'].items():
        for ref in (body.get('binding', {}).get('subject_ref'), body.get('value', {}).get('ref')):
            add(ref, body, ARCHIVE + '#/typed_bodies/' + label, 'HISTORICAL_SUBJECT_TO_SOURCE_BINDINGS')
            for required_label in body.get('closure_body_labels', []):
                add(ref, archive['typed_bodies'][required_label], ARCHIVE + '#/typed_bodies/' + required_label, 'EXPLICIT_REQUIRED_CLOSURE_BODY_LABEL')

    # 同一 exact source/schema 的存放 alias 不產生第二個功能/配對身份。
    unique_sources = {}
    for row in source_pairs:
        k = (key(row['source_ref']), key(row['schema_ref']))
        if k not in unique_sources:
            unique_sources[k] = row
            row['source_declaration_aliases'] = []
        else:
            unique_sources[k]['source_declaration_aliases'].append({'source_label': row['source_label'], 'source_declaration': row['source_declaration'], 'source': row['source'], 'schema': row['schema'], 'source_version': row['source_version']})
            if row['source_version'] == 'MA-ARCH-REVIEW-v6-CYCLE02':
                unique_sources[k]['source_version'] = row['source_version']
    source_pairs = list(unique_sources.values())
    auxiliary_by_hash = collections.defaultdict(list)
    for row in source_pairs:
        auxiliary_by_hash[row['source']['raw_bytes_sha256']].append(row['source'])

    def descendants_for(reached):
        result = {}
        for k in sorted(reached):
            for node in nodes.get(k, []):
                location = node['location']
                role = None
                if '/typed_body_bindings/' in location or '/binding' in location:
                    role = 'BODY_BINDING_AND_EXPLICIT_SOURCE_BINDINGS'
                elif '/expected_capture_receipts/' in location or '/expected_source_capture_receipts/' in location:
                    role = 'DURABLE_CAPTURE_DESIGN_EXPECTATION'
                elif '/artifact_revisions/' in location or '/source_artifact_revisions/' in location:
                    role = 'ARTIFACT_REVISION_DESIGN_EXPECTATION'
                if not role:
                    continue
                source_rel, selector = location.split('#', 1)
                if source_rel not in (WORLD, ARCHIVE):
                    continue
                digest = sha(canonical(node['object']))
                proof = {'role': role, 'pin': pin(source_rel), 'pointer': '#' + selector, 'canonical_sha256': digest, 'contract_ref': registry[k], 'immutable_auxiliary_bytes': auxiliary_by_hash.get(digest, []), 'qualification': 'DESIGN_EXPECTED_NOT_PROVIDER_DURABILITY_OR_RUNTIME_EVIDENCE'}
                result[(source_rel, selector, digest)] = proof
        return [result[k] for k in sorted(result)]

    def closure(case):
        roots = {key(r): r for r in all_refs(case)}
        registry.update(roots)
        queue = collections.deque(sorted(roots))
        predecessor = {r: None for r in roots}
        steps = {}
        visited = set()
        while queue:
            ref_key = queue.popleft()
            if ref_key in visited:
                continue
            visited.add(ref_key)
            for node in nodes.get(ref_key, []):
                refs = {key(r): r for r in all_refs(node['object'])}
                registry.update(refs)
                for nxt in sorted(refs):
                    if nxt != ref_key and nxt not in predecessor:
                        predecessor[nxt] = ref_key
                        steps[nxt] = {'pointer': node['location'], 'edge_role': node['role']}
                        queue.append(nxt)
        def proof(ref_key):
            result = []
            while ref_key is not None:
                result.append({'ref': registry[ref_key], 'via': steps.get(ref_key, {'edge_role': 'IMMUTABLE_CASE_ROOT'})})
                ref_key = predecessor[ref_key]
            return list(reversed(result))
        return visited, proof

    operations = []
    flat_pairs = []
    for item in v8_scope['operations']:
        op = item['operation_id']
        old_contract = load(item['contract']['path'])
        m = mapping[op]
        consumer_aliases = sorted({r['unit_alias'] for r in m['consumers']})
        unit_aliases = sorted(set(consumer_aliases + [m['producer_unit_alias']]))
        cases, op_pairs = [], []
        for cp in old_contract['cases']:
            # 此處只選 immutable predecessor case，絕不讀 cp.resolution_ids。
            source = load(cp['source']['path'])
            case = pointer(source, cp['pointer'])
            if case['operation_id'] != op or case['case_id'] != cp['case_id']:
                raise ValueError('CASE_SCOPE_CONFLICT:' + op)
            case_pin = {'source': pin(cp['source']['path']), 'pointer': cp['pointer'], 'case_id': case['case_id'], 'case_canonical_sha256': sha(canonical(case))}
            reached, proof = closure(case)
            operation_descendants = descendants_for(reached)
            pairs = []
            for source_pair in source_pairs:
                sk, schk = key(source_pair['source_ref']), key(source_pair['schema_ref'])
                if sk not in reached and schk not in reached:
                    continue
                records = resolution_by_pair.get((sk, schk), [])
                if len(records) > 1:
                    raise ValueError('AMBIGUOUS_V8_SCHEMA_ADAPTER:' + source_pair['source_label'])
                record = records[0] if records else None
                identity = [op, case['case_id'], list(sk), list(schk)]
                row = dict(source_pair)
                row.update({
                    'pair_id': str(uuid.uuid5(NS, canonical(identity).decode())), 'operation_id': op, 'case_id': case['case_id'],
                    'original_schema_ref': source_pair['schema_ref'],
                    'resolution_id': record['record_id'] if record else None,
                    'resolver_method': 'EXPLICIT_V8_SCHEMA_SUCCESSOR' if record else 'STANDARD_DIRECT_EXACT_SOURCE_SCHEMA',
                    'source_profile': record['input_profile'] if record else 'EXACT_STANDARD_2020_12_SOURCE',
                    'source_version': record['original_subject'] if record else source_pair['source_version'],
                    'schema_origin_subject': record['original_subject'] if record else source_pair['source_version'],
                    'effective_schema_ref': record['effective_schema_ref'] if record else source_pair['schema_ref'],
                    'effective_schema': record['effective_schema'] if record else source_pair['schema'],
                    'effective_dialect': STANDARD,
                    'producer': {'unit_alias': m['producer_unit_alias'], 'owner': m['producer_existing_owner']},
                    'consumers': m['consumers'], 'unit_aliases': unit_aliases, 'required_unit_aliases': unit_aliases,
                    'requirement': 'REQUIRED_IN_FIXED_POSITIVE_SOURCE_WORLD', 'condition': None,
                    'requirement_proof': proof(sk if sk in reached else schk), 'case_ref': case_pin,
                    'required_descendants': body_pins_by_source.get(sk, []),
                    'failure_semantics': ['MISSING_REQUIRED_PAIR_HOLD', 'WRONG_EXACT_SOURCE_OR_SCHEMA_REJECT', 'UNKNOWN_DIALECT_REJECT', 'UNEXPECTED_PAIR_REJECT', 'AMBIGUOUS_OR_CONFLICT_REJECT'],
                    'qualification': 'SOURCE_DESIGN_ONLY_NOT_IMPLEMENTATION_OR_RUNTIME_EVIDENCE', 'authority_effect': 'NONE',
                })
                if record:
                    row['adapter_record'] = {'source': pin('schema_successor_v8/SCHEMA_RESOLUTION_CATALOG.v8.json'), 'record_id': record['record_id']}
                pairs.append(row)
            pairs.sort(key=lambda r: r['pair_id'])
            cases.append({'case_id': case['case_id'], 'case_ref': case_pin, 'required_pair_ids': [r['pair_id'] for r in pairs], 'required_pairs': pairs, 'reachable_ref_count': len(reached), 'required_descendants': operation_descendants})
            op_pairs.extend(pairs)
        operations.append({'operation_id': op, 'producer': {'unit_alias': m['producer_unit_alias'], 'owner': m['producer_existing_owner']}, 'consumers': m['consumers'], 'unit_aliases': unit_aliases, 'cases': cases, 'case_refs': [c['case_ref'] for c in cases], 'required_pair_ids': [r['pair_id'] for r in op_pairs], 'required_pairs': op_pairs, 'required_descendants': [r for c in cases for r in c['required_descendants']], 'request_model': m['request_model'], 'response_model': m['response_model'], 'source_mapping': {'source': pin(MAP), 'pointer': '#/operations/' + str(mappings.index(m))}})
        flat_pairs.extend(op_pairs)
    units = []
    policy_rel = 'source_closure_v9/EXPECTED_PAIR_POLICY.v9.json'
    policy = load(policy_rel) if (P / policy_rel).is_file() else None
    for i, unit in enumerate(load('EXECUTION_UNITS.json')['units']):
        alias = unit['unit_alias']
        required = [o for o in operations if alias in o['unit_aliases']]
        units.append({'unit_id': unit['unit_id'], 'unit_alias': alias, 'required_operation_ids': sorted(o['operation_id'] for o in required), 'required_pair_ids': sorted(r['pair_id'] for o in required for r in o['required_pairs']), 'source': {'source': pin('EXECUTION_UNITS.json'), 'pointer': '#/units/' + str(i)}, 'mandatory_compiler_inputs': policy['mandatory_compiler_input_roles'] if policy else [], 'compiler_pair_policy': pin(policy_rel) if policy else None, 'authority_effect': 'NONE'})
    return {'kind': 'SOURCE_QUALIFICATION_EXPECTED_PAIR_PROJECTION_NOT_REGISTRY', 'derivation_revision': 'candidate.9', 'authority_effect': 'NONE', 'expected_independence': 'IMMUTABLE_CASE_SOURCE_BODY_BINDING_AND_EXPLICIT_CLOSURE_EDGES; NEVER_ACTUAL_RESOLUTION_IDS', 'shared_read_cut_policy': 'SNAPSHOT_IDENTITY_AND_SCHEMA_ONLY_NOT_ARCHIVE_MEMBERSHIP', 'sources': [pin(x) for x in (WORLD, ARCHIVE, BODY_CATALOG, MAP, 'EXECUTION_UNITS.json', 'schema_successor_v8/SCHEMA_RESOLUTION_CATALOG.v8.json')] + ([pin(policy_rel)] if policy else []), 'operations': operations, 'pairs': flat_pairs, 'units': units, 'compiler_policy_present': bool(policy), 'counts': {'operations': len(operations), 'cases': sum(len(o['cases']) for o in operations), 'required_pairs': len(flat_pairs), 'units': len(units), 'all_source_schema_inventory': len(source_pairs)}}


if __name__ == '__main__':
    import sys
    result = derive_expected(sys.argv[1])
    out = pathlib.Path(sys.argv[2])
    out.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps(result['counts']))
