"""重現 exact published subject 的 full-carrier 大小；所有 JSON 值保留，無 gate/adoption。"""
import argparse
import hashlib
import json
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT/"scripts"))
from p00_context import Snapshot,canonical,resolve
from p00_context_pack import build_pack,expand_json
SUBJECT="75ef4207aafaaabbf8bf130dea25f78726361626"

def unique(pairs):
    d={}
    for k,v in pairs:
        if k in d: raise ValueError("DUPLICATE_JSON_KEY")
        d[k]=v
    return d

def observe():
    s=Snapshot(ROOT,SUBJECT)
    result={"schema_version":"p00.context_carrier_analysis.v1","subject":SUBJECT,
        "status":"REPRODUCIBLE_SIZE_AND_FULL_JSON_VALUE_PRESERVATION_ONLY",
        "authority":"NO_TOOL_POLICY_POINTER_COMPILER_OR_BUDGET_ADOPTION",
        "target_max_bytes":131072,"packages":[]}
    for pid in ["P01","P02"]:
        req={"task_type":"WORK","package_id":pid,
            "changed_paths":s.read_json(f"docs/program/packages/{pid}.candidate.v1.json")["authority"]["exact_scope"],
            "architecture_domains":["program"],"baseline_sha":SUBJECT}
        c=resolve(ROOT,req)
        raw,metrics=build_pack(ROOT,req,selective=True)
        fullraw,fullmetrics=build_pack(ROOT,req,selective=False)
        pack=json.loads(raw);fullpack=json.loads(fullraw);rows=[]
        for ref in c["mandatory_context"]:
            b,actual=s.read(ref["path"])
            assert actual==ref
            row={"source":ref,"carrier":"RAW_FULL_SOURCE","candidate_bytes":len(b),
                "reading":"FULL_SOURCE_UNLESS_EXACT_REVIEWED_OBLIGATION_DISCHARGE",
                "semantic_review":"NOT_PERFORMED"}
            # YAML manifests 保持 raw；JSON 不移除任何值/required/negative/security/error/extension。
            if ref["path"].endswith(".json"):
                x=json.loads(b,object_pairs_hook=unique);z=canonical(x)
                assert json.loads(z,object_pairs_hook=unique)==x
                row.update(carrier="FULL_JSON_WHITESPACE_ONLY_NOT_ADOPTED",
                    candidate_bytes=len(z),canonical_sha256=hashlib.sha256(z).hexdigest(),
                    semantic_values_roundtrip=True)
            rows.append(row)
        api=[]
        for doc in fullpack["documents"]:
            if doc["source"]["path"].endswith(".openapi.v1.json"):
                original=s.read_json(doc["source"]["path"])
                restored=expand_json(doc,fullpack["schema_pool"])
                assert restored==original
                api.append({"source":doc["source"],"full_value_roundtrip":True,
                    "path_count":len(original["paths"]),"schema_count":len(original["components"]["schemas"]),
                    "top_level_keys_preserved":sorted(original),
                    "full_security_errors_constraints_extensions_refs_preserved":True,
                    "canonical_value_bytes":len(canonical(original))})
        negative=s.read("automation/specs/negative_assertions.v2.yaml")[1]
        hypothetical=sum(x["candidate_bytes"] for x in rows)
        result["packages"].append({"package":pid,"original_metrics":metrics,
            "full_OpenAPI_dedup_pack_metrics":fullmetrics,
            "mandatory_sources":sorted(rows,key=lambda x:-x["source"]["size_bytes"]),
            "full_JSON_whitespace_only_total_without_metadata":hypothetical,
            "hypothetical_JSON_plus_prior_CURRENT_history_reference_total_without_metadata":hypothetical-142779,
            "prior_CURRENT_history_bytes":142779,"hypothetical_is_not_gate_input":True,
            "required_negative_supplement":negative,
            "negative_assertions_original_resolver":"NOT_MANDATORY_SOURCE01_UNADOPTED",
            "full_JSON_plus_negative_without_metadata":hypothetical+negative["size_bytes"],
            "full_OpenAPI_carriers":api,
            "selective_documents":[{"source":d["source"],"format":d["format"],
                "carrier_bytes":len(canonical(d)),"projection":d.get("projection")}
                for d in pack["documents"]],
            "selected_schema_pool_bytes":len(canonical(pack["schema_pool"])),
            "selected_schema_pool_entries":len(pack["schema_pool"]),
            "gate":"NOT_PASSED_ORIGINAL_RAW_AGGREGATE",
            "semantic_reading_qualification":False,"trusted_intake":False,
            "model_backend_qualification":False})
    return result

if __name__=="__main__":
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output",required=True)
    args=parser.parse_args();sys.stdout.reconfigure(encoding="utf-8")
    out=Path(args.output).resolve()
    assert out.is_relative_to((ROOT/".tmp").resolve())
    result=observe();out.write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({"subject":SUBJECT,"canonical_sha256":hashlib.sha256(canonical(result)).hexdigest(),
        "packages":[{"package":p["package"],"original":p["original_metrics"],
            "full_pack":p["full_OpenAPI_dedup_pack_metrics"],
            "full_JSON":p["full_JSON_whitespace_only_total_without_metadata"],
            "JSON_plus_CURRENT_reference":p["hypothetical_JSON_plus_prior_CURRENT_history_reference_total_without_metadata"]}
            for p in result["packages"]]},ensure_ascii=False,indent=2))
