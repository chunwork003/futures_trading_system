"""從 exact Git raw bytes 建立完整CURRENT分段保全索引；不改CURRENT或compiler gate。"""
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "scripts"))
from p00_context import Snapshot, canonical, resolve, bind_loaded_source
from p00_context_pack import encode_document, MARKER
from p00_reading import governance_coverage
INPUT = "bae9dcaff476bd79e8494ac6cd393dea19cb9657"
MASTER = "9b5ab5fdd98744a7db45ec9f14b64ef1f324920f"


def reproduce():
    s = Snapshot(ROOT, INPUT)
    master = Snapshot(ROOT, MASTER)
    sources = []
    payloads = []
    h = lambda b: hashlib.sha256(b).hexdigest()
    for path in ("docs/CURRENT_STATE.md", "docs/CURRENT_WORK.md"):
        raw, ref = s.read(path)
        assert ref["git_blob"] == master.read(path)[1]["git_blob"]
        lines = raw.splitlines(True)
        markers = [i for i, line in enumerate(lines) if line.rstrip(b"\r\n") == MARKER.encode()]
        assert markers
        offsets = [0]
        for line in lines: offsets.append(offsets[-1] + len(line))
        current_end = offsets[markers[0]]
        assert 0 < current_end < len(raw)
        encoded = encode_document(path, raw, {})
        assert encoded["text"].encode() == raw[:current_end]
        assert encoded["archive_text_sha256"] == h(raw[current_end:])
        assert encoded["history_marker_count"] == len(markers)
        cuts = [0, current_end] + [offsets[i] for i in markers[1:]] + [len(raw)]
        segments = []
        for i in range(len(cuts)-1):
            start,end=cuts[i:i+2]
            block = raw[start:end]
            segments.append({"id":path+"#segment-"+str(i), "kind":"CURRENT_FULL_PREFIX" if i==0 else "EXPLICIT_HISTORY_REQUIRES_FULL_SOURCE_FOR_PROVENANCE_OR_CONTRADICTION",
                "start_byte":start,"end_byte_exclusive":end,"size_bytes":len(block),"sha256":h(block),
                "start_line":1 if i==0 else next(j+1 for j,v in enumerate(offsets[:-1]) if v==start),
                "header":block.decode().splitlines()[0],"semantic_omission_review":"NOT_PERFORMED",
                "current_authority":False if i else "RESOLVED_FROM_ORIGINAL_CANONICAL_SOURCE_NOT_THIS_INDEX"})
        reconstructed=b"".join(raw[x["start_byte"]:x["end_byte_exclusive"]] for x in segments)
        assert reconstructed==raw and sum(x["size_bytes"] for x in segments)==len(raw)
        # 所有current段落逐字納入，不用關鍵字篩掉未分類語句。
        paragraphs=[];start=0
        for i,line in enumerate(lines[:markers[0]]):
            if not line.strip():
                end=offsets[i+1]
                if end>start:paragraphs.append({"id":path+"#current-block-"+str(len(paragraphs)),"start_byte":start,"end_byte_exclusive":end,"sha256":h(raw[start:end]),"text":raw[start:end].decode(),"mandatory_reading":True,"semantic_discharge":"NOT_REVIEWED_FULL_BLOCK_REQUIRED"})
                start=end
        if start<current_end:paragraphs.append({"id":path+"#current-block-"+str(len(paragraphs)),"start_byte":start,"end_byte_exclusive":current_end,"sha256":h(raw[start:current_end]),"text":raw[start:current_end].decode(),"mandatory_reading":True,"semantic_discharge":"NOT_REVIEWED_FULL_BLOCK_REQUIRED"})
        assert b"".join(x["text"].encode() for x in paragraphs)==raw[:current_end]
        sources.append({"source":ref,"current_bytes":current_end,"history_bytes":len(raw)-current_end,
            "history_segments":len(markers),"segments":segments,"current_blocks":paragraphs,
            "raw_roundtrip":"PASS_ALL_BYTES_ACCOUNTED_NO_SOURCE_DELETION","full_source_load_rule":encoded["archive_load_rule"]})
        payloads.append({"source":ref,"current_text":raw[:current_end].decode(),"full_source_required_for_history":True})
    coverage=governance_coverage(s,{"mandatory_context":[]})
    negative=s.read("automation/specs/negative_assertions.v2.yaml")
    projection={"schema_version":"p00.compact_current_carrier_candidate.v1","status":"PROPOSAL_NON_AUTHORITY",
        "authority":"NONE_READING_AID_ONLY","execution_eligible":False,"input":INPUT,"source_master":MASTER,
        "documents":payloads,"negative_source":negative[1],"negative_full_text":negative[0].decode(),
        "all_other_active_policy_full_sources_required":coverage["declared_source_refs"],
        "full_source_fallback":"Historical claims, unresolved contradictions, review, provenance or unclassified semantics require complete original exact source",
        "compiler_basis":"ORIGINAL_TOTAL_MANDATORY_SOURCE_BYTES_UNCHANGED","semantic_completeness":"NOT_ASSERTED",
        "trusted_intake":False,"accepted_current_pointer_replacement":False}
    raw_projection=canonical(projection)+b"\n"
    history=sum(x["history_bytes"] for x in sources)
    metrics=[]
    for package in ("P01","P02"):
        request={"task_type":"WORK","package_id":package,"changed_paths":s.read_json("docs/program/packages/"+package+".candidate.v1.json")["authority"]["exact_scope"],"architecture_domains":["program"],"baseline_sha":INPUT}
        context=resolve(ROOT,request)
        full=context["context_budget"]["mandatory_bytes"]
        assert full-history>131072
        metrics.append({"package":package,"original_mandatory_bytes":full,
            "hypothetical_physical_CURRENT_history_reduction_only_bytes":full-history,
            "hypothetical_is_not_accepted_mandatory_context":True,"original_gate":"NOT_PASSED",
            "even_hypothetical_reduction_gate":"NOT_PASSED","projection_metadata_overhead_not_subtracted":True})
    return {"schema_version":"p00.compact_current_preservation_map.v1","input":INPUT,"source_master":MASTER,
        "sources":sources,"source_files":2,"source_bytes":sum(x["source"]["size_bytes"] for x in sources),
        "current_bytes":sum(x["current_bytes"] for x in sources),"history_bytes":history,
        "active_governance_refs":coverage["declared_source_refs"],"negative_full_source_bytes":negative[1]["size_bytes"],
        "projection":projection,"projection_bytes":len(raw_projection),"projection_raw_sha256":h(raw_projection),
        "context_observations":metrics,"packer_already_partitions_history":True,
        "pack_savings_from_merely_repeating_partition":"NOT_ASSERTED_NO_COMPILER_GATE_CHANGE",
        "qualification":{"independent_semantic_review":"NOT_PERFORMED","current_pointer_modified":False,
            "model_reading_golden":"NOT_RUN","receipt_or_intake_trust":False,"operational_migration":"NOT_AUTHORIZED"}}

if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    print(json.dumps(reproduce(),ensure_ascii=False,indent=2))
