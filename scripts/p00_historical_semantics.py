"""P00有界歷史語意bridge：exact sources/selected clauses，不提供current authority或驗收。"""

import argparse
import hashlib
import json
from pathlib import Path

from p00_context import Snapshot, canonical, safe_path

MASTER_PATHS = (
    "docs/adr/ADR-001-TRADING-CORE-BOUNDARIES.md",
    "docs/adr/ADR-002-RECOVERY-CONSISTENCY-MARKET-OBSERVATION.md",
    "docs/GAP_REGISTER.md", "docs/BACKTEST_ENGINE.md", "docs/DATA_ARCHITECTURE.md",
    "docs/work/GAP08_FINAL_CLOSURE.md", "docs/work/GAP08_CORRECTION_FREEZE.md", "docs/CURRENT_STATE.md",
)
A1, A2, GAP, BT, DATA, CLOSE, FREEZE, CURRENT = MASTER_PATHS
BASE = "docs/architecture/V1_BASELINE.md"
CUT = "docs/architecture/V1_DECISION_RECOVERY_CUT.md"
DTO = "docs/architecture/V1_DTO_STORE_MAP.md"
QUALITY = "docs/architecture/V1_DATASET_QUALITY.md"
PROGRAM = "docs/program/V1_PROGRAM.md"
CONTRACT = "docs/architecture/V1_CONTRACTS.md"

# 有界選擇是authoring specification，並非全文已被原子review。完整source另外索引。
# id/path/range/disposition/meaning/candidate evidence/existing delta IDs。
CLAUSES = [
 ("A1-STATUS",A1,3,9,"HISTORICAL_STATUS_ONLY","接受的是ownership/dependency/migration，不是runtime已遷移",BASE,[]),
 ("A1-FINDINGS",A1,23,31,"HISTORICAL_STATUS_ONLY","舊source findings不等於此刻產品defects，不重開已closed prefix correction",DTO,[]),
 ("A1-OWNERS",A1,33,61,"INHERIT_ARCHITECTURE_CONTRACT","shared domain/minimal trading/ports/adapters，namespace target不要求mass move",DTO,["P05-ADAPTER"]),
 ("A1-MODELS",A1,63,91,"INHERIT_ARCHITECTURE_CONTRACT","單一canonical model owner；SDK/entity/DTO是representation",DTO,["P05-ADAPTER"]),
 ("A1-DEPENDENCY",A1,93,105,"INHERIT_ARCHITECTURE_CONTRACT","core不做I/O且不依賴adapter/ORM，application選adapter",BASE,["P02-PYTHON-PORT"]),
 ("A1-BACKTEST",A1,107,117,"INHERIT_ARCHITECTURE_CONTRACT","preserve deterministic consumer與EXIT-FLAT重新決策，minimal core依consumer需要遷移",BASE,["P04-ENGINE","P06-DECISION"]),
 ("A1-BROKER",A1,119,123,"INHERIT_ARCHITECTURE_CONTRACT","explicit PositionEffect，不靠ENTRY-prefix；broker SDK不進core",DTO,["P05-ADAPTER"]),
 ("A1-SIMULATION",A1,125,130,"OPEN_DELTA_SCOPE","Paper立即成交baseline不能取代Simulation fault model",BASE,["P07-EXCHANGE","P07-RACES"]),
 ("A1-CAPITAL",A1,132,140,"INHERIT_ARCHITECTURE_CONTRACT","manual LogicalAccount capital；borrowing預設OFF，Portfolio不是broker truth",BASE,["P06-CAPITAL","P06-RISK"]),
 ("A1-REFERENCE",A1,142,148,"INHERIT_ARCHITECTURE_CONTRACT","effective-dated margin/session/reference不能由各config重建truth",DTO,["P01-MANIFEST","P06-RISK"]),
 ("A1-PERSISTENCE",A1,150,160,"INHERIT_ARCHITECTURE_CONTRACT","events/state為authority；completed Trade不能反向取代Order/Fill",DTO,["P08-DURABILITY"]),
 ("A1-LANGUAGE",A1,162,168,"INHERIT_ARCHITECTURE_CONTRACT","Python economic owner，ASP.NET workflow/auth；versioned REST/JSON，非SDK/wire/domain混用",BASE,["P02-PYTHON-PORT","P02-BFF"]),
 ("A1-COMPATIBILITY",A1,170,192,"INHERIT_ARCHITECTURE_CONTRACT","逐slice相容alias/equivalence/rollback；移除alias需獨立package",DTO,["P05-ADAPTER"]),
 ("A1-DEFERRED",A1,194,198,"SEPARATE_FUTURE_GATE","較大產品/production server/framework為原scope deferred，local V1 deployment另有新scope",PROGRAM,[]),
 ("A1-NO-MASS-REWRITE",A1,220,226,"INHERIT_ARCHITECTURE_CONTRACT","原M0-B禁止runtime；保留no mass rename及不猜broker semantics",DTO,["P05-ADAPTER"]),
 ("A2-OLD-STATUS",A2,3,33,"HISTORICAL_STATUS_ONLY","checkpoint4 HOLD/35-151是歷史candidate，不回填為accepted",DTO,[]),
 ("A2-GENESIS",A2,1261,1326,"INHERIT_ARCHITECTURE_CONTRACT","revision1 initialization完整authority closure；broker seed不造歷史fills且不自動READY",CONTRACT,["P08-RECOVERY"]),
 ("A2-ATOMICITY",A2,1363,1373,"INHERIT_ARCHITECTURE_CONTRACT","material strategy frontier與required pending boundary遵守同一crash invariant",CUT,["P05-INCREMENTAL","P08-DURABILITY"]),
 ("A2-OBS-KEY",A2,249,273,"INHERIT_ARCHITECTURE_CONTRACT","logical locus排除payload/provenance；UTC interval與contract dimension保留",DTO,["P01-MANIFEST","P05-ADAPTER"]),
 ("A2-OBS-REVISION",A2,300,367,"INHERIT_ARCHITECTURE_CONTRACT","authority-local sequence不同於cross-env fingerprint；無silent rounding/global store lock",DTO,["P05-ADAPTER"]),
 ("A2-SOURCE-AUTHORITY",A2,541,599,"INHERIT_ARCHITECTURE_CONTRACT","PRIMARY acquisition不等於AUTHORITATIVE；candidate不等於accepted revision",QUALITY,["P01-QUALITY","P05-ADAPTER"]),
 ("A2-DURABLE-DELIVERY",A2,659,717,"INHERIT_ARCHITECTURE_CONTRACT","durable-before-strategy，Parquet歷史authority不同於operational PG；衍生revision與policy不回寫歷史",CUT,["P05-INCREMENTAL","P08-DURABILITY"]),
 ("A2-FINAL-CURRENTNESS",A2,1381,1396,"INHERIT_ARCHITECTURE_CONTRACT","account revision相同仍須完整RecoveryCut/generation/evidence currentness",CUT,["P08-RECOVERY"]),
 ("A2-LOADER",A2,1398,1535,"INHERIT_ARCHITECTURE_CONTRACT","coherent transitive cut；VALID不等於READY，missing不能推never-initialized或FLAT",CUT,["P08-RECOVERY"]),
 ("A2-INSTANCE-FRONTIER",A2,1593,1660,"INHERIT_ARCHITECTURE_CONTRACT","per StrategyInstance frontier；stateless/genesis須正面authority，不用global watermark",CUT,["P05-RESTART"]),
 ("A2-COHORT",A2,1662,1699,"INHERIT_ARCHITECTURE_CONTRACT","required membership來自exact policy，不以loaded/restored instances改寫cohort",CUT,["P06-DECISION"]),
 ("A2-CATCHUP",A2,1701,1738,"INHERIT_ARCHITECTURE_CONTRACT","restore/trading/cohort readiness分離；generic catch-up不能發normal material actions",CUT,["P05-RESTART","P08-RECOVERY"]),
 ("A2-CASE",A2,1744,1800,"INHERIT_ARCHITECTURE_CONTRACT","Case一個primary account；open不自證readiness、不改expected economic truth",CUT,["P08-RECONCILIATION"]),
 ("A2-INSTRUMENT",A2,1823,1859,"INHERIT_ARCHITECTURE_CONTRACT","instance/instrument/contract/alias各有authority，mismatch無precedence fallback",DTO,["P05-ADAPTER"]),
 ("A2-CONFIG",A2,1861,1942,"INHERIT_ARCHITECTURE_CONTRACT","instance/config/implementation/policy與transition分離；混合PRE/POST不得normal READY",CUT,["P05-RESTART","P06-DECISION"]),
 ("A2-INIT-PROVENANCE",A2,1968,2014,"INHERIT_ARCHITECTURE_CONTRACT","首snapshot指向初始化event，唯一revision1 closure；missing/empty/MATCH不是FLAT",CONTRACT,["P08-RECOVERY"]),
 ("A2-CLOCK",A2,2040,2128,"INHERIT_ARCHITECTURE_CONTRACT","first durable ingress固定received_at；unknown occurrence不猜，timestamps不替代causal sequence",DTO,["P05-ADAPTER","P08-DURABILITY"]),
 ("A2-RUN",A2,2178,2281,"INHERIT_ARCHITECTURE_CONTRACT","formal Run bound exact world，technical/qualification/domain三軸不互代；MATCH不自授READY",CUT,["P08-RECONCILIATION"]),
 ("A2-RUN-FINALIZATION",A2,2283,2335,"INHERIT_ARCHITECTURE_CONTRACT","append-only/crash-consistent terminal evidence；historical valid不等於current activation",CUT,["P08-RECONCILIATION"]),
 ("A2-AUTHORITY",A2,2341,2395,"INHERIT_ARCHITECTURE_CONTRACT","core消費N/L exact protected-world proof；metadata/booleans不等於production authority",CUT,["P03-IDENTITY","P09-CONTROL"]),
 ("A2-PRODUCTION-AUTH",A2,2450,2483,"SEPARATE_FUTURE_GATE","production enforcement seam不豁免；full authN/authZ/security workflow deferred非waived",PROGRAM,[]),
 ("A2-COVERAGE",A2,2489,2504,"INHERIT_ARCHITECTURE_CONTRACT","completeness是consumer/scope/horizon canonical義務，不是global health/candidate count",QUALITY,["P01-QUALITY"]),
 ("A2-MISSING-STATES",A2,2520,2560,"INHERIT_ARCHITECTURE_CONTRACT","pending/unknown/outage/no-trade不同；positive proof且COMPLETE不充分保證READY",QUALITY,["P01-QUALITY","P08-RECOVERY"]),
 ("A2-DATA-CURRENTNESS",A2,2562,2599,"INHERIT_ARCHITECTURE_CONTRACT","R03 identity/R14 coverage/K520 derived horizon分離；currentness不靠wall clock",CUT,["P05-INCREMENTAL","P08-RECOVERY"]),
 ("A2-PRODUCTION-COMPLETENESS",A2,2601,2626,"SEPARATE_FUTURE_GATE","approved authority/fail-closed seam保留，full production detector另外gate",PROGRAM,[]),
 ("BT-TIMING",BT,21,44,"PRESERVE_SUPPLEMENTAL_SEMANTICS","next-bar EXIT/ENTRY/position/signal順序與no look-ahead須產品equivalence gate",BASE,["P04-ENGINE"]),
 ("BT-FILL-COST",BT,58,72,"PRESERVE_SUPPLEMENTAL_SEMANTICS","actual fill authoritative，slippage不二次扣除",BASE,["P04-ENGINE"]),
 ("BT-DETERMINISM",BT,122,141,"PRESERVE_SUPPLEMENTAL_SEMANTICS","final close選項與deterministic resets為保留條件，沒有本輪產品run",BASE,["P04-ENGINE"]),
 ("BT-OLD-LIMITS",BT,143,154,"HISTORICAL_STATUS_ONLY","文件明標部分limitations被取代，不能據此宣稱此刻defect/feature maturity",BASE,[]),
 ("BT-SIZING",BT,156,180,"PRESERVE_SUPPLEMENTAL_SEMANTICS","sizing optional/nonpositive skip/無sizer保留quantity；risk gate需integration驗證",BASE,["P06-RISK"]),
 ("BT-OLD-METRIC-DEFERRAL",BT,182,197,"HISTORICAL_STATUS_ONLY","舊Return/Sharpe post-P12不取消新V1 research metrics義務",BASE,["P04-ENGINE"]),
 ("DATA-STORES",DATA,21,35,"PRESERVE_SUPPLEMENTAL_SEMANTICS","Parquet/DuckDB/Polars為analytical plane，不代替operational PG truth",BASE,["P01-IMPORT"]),
 ("DATA-IDENTITY",DATA,103,111,"PRESERVE_SUPPLEMENTAL_SEMANTICS","Instrument/Contract/Continuous各異，synthetic series不直接成execution contract",DTO,["P01-MANIFEST"]),
 ("DATA-CALENDAR",DATA,113,124,"PRESERVE_SUPPLEMENTAL_SEMANTICS","calendar/session/holiday/exception/night/expiry reference為first-class data",QUALITY,["P01-QUALITY"]),
 ("DATA-INTEGRITY",DATA,126,143,"PRESERVE_SUPPLEMENTAL_SEMANTICS","duplicate/missing/OHLC/order/session/rollover/symbol/timezone先驗證，再擴策略",QUALITY,["P01-QUALITY","P01-FIXTURES"]),
 ("GAP-ROLE",GAP,3,34,"HISTORICAL_STATUS_ONLY","GAP不是完整roadmap，Blueprint/GAP/queue責任不同",PROGRAM,[]),
 ("GAP-CLOSURE-TOP",GAP,36,58,"PRESERVE_ACCEPTED_SCOPE","corrected113/113 scope與runtime/broker/DB/LIVE NOT_AUTHORIZED分開",DTO,[]),
 ("GAP-QUEUE",GAP,82,123,"OPEN_DELTA_SCOPE","source open/partial gaps不等於新V1授權；逐項保留source labels與候選routes",PROGRAM,[]),
 ("GAP-OLD-DETAIL",GAP,374,470,"HISTORICAL_STATUS_ONLY","detail98/113與C17 pending被final closure supersede，只取歷史phase證據",DTO,[]),
 ("GAP-NONWAIVER",GAP,941,966,"SEPARATE_FUTURE_GATE","auth/completeness deferred不豁免，K520 remains GAP09，不猜production readiness",PROGRAM,[]),
 ("CLOSE-CORE",CLOSE,22,61,"PRESERVE_ACCEPTED_SCOPE","correctedhead與五frozen leaves/consumed grants保持immutable，不重開",DTO,[]),
 ("CLOSE-BOUNDARY",CLOSE,63,95,"PRESERVE_ACCEPTED_SCOPE","scope接受不含production/broker/V07/LIVE，P8/P9分離",PROGRAM,[]),
 ("CLOSE-ORIGINAL",CLOSE,97,110,"PRESERVE_ACCEPTED_SCOPE","original35/151未retroactively accepted，不加重複credit",DTO,[]),
 ("FREEZE-OLD-STATUS",FREEZE,3,27,"HISTORICAL_STATUS_ONLY","planning HOLD由後續scope closure取代，freeze本身始終不授權runtime",DTO,[]),
 ("FREEZE-DEFERRED",FREEZE,766,786,"SEPARATE_FUTURE_GATE","舊correction排除API/web/backup不等於新產品排除，production gate未豁免",PROGRAM,[]),
 ("FREEZE-GRANT",FREEZE,790,818,"INHERIT_ARCHITECTURE_CONTRACT","exact scope/environment/effects/tests/stop required，bare AUTHORIZED不足",PROGRAM,[]),
 ("CURRENT-OPERATIONAL",CURRENT,1,15,"CANONICAL_CURRENT_OBSERVATION","唯一canonical operational current仍003 rev2 NOT_AUTHORIZED；P00 human grant不能dispatch003",PROGRAM,[]),
]


def span(snapshot, path, first, last):
    raw, _ = snapshot.read(path)
    lines = raw.splitlines(keepends=True)
    if type(first) is not int or type(last) is not int or not 1 <= first <= last <= len(lines):
        raise ValueError("SEMANTIC_SOURCE_RANGE_INVALID")
    return {"path": path, "first_line": first, "last_line": last,
            "sha256": hashlib.sha256(b"".join(lines[first - 1:last])).hexdigest()}


def source_blocks(snapshot, path):
    """完整索引非空連續source bytes，未分類內容不冒充已review。"""
    raw, evidence = snapshot.read(path)
    lines = raw.splitlines(keepends=True)
    blocks, start = [], None
    for offset in range(len(lines) + 1):
        present = offset < len(lines) and bool(lines[offset].strip())
        if present and start is None:
            start = offset + 1
        elif not present and start is not None:
            blocks.append({"path":path,"first_line":start,"last_line":offset,
                           "sha256":hashlib.sha256(b"".join(lines[start - 1:offset])).hexdigest()})
            start = None
    return {"source_ref": evidence, "line_count": len(lines), "nonblank_line_count": sum(bool(l.strip()) for l in lines),
            "blocks": blocks, "semantic_review": "SELECTED_CLAUSES_ONLY_PENDING_INDEPENDENT_REVIEW"}


def gaps(master):
    """只抽三個已指定table；GAP source labels不轉成current product status。"""
    raw, _ = master.read(GAP)
    lines = raw.decode("utf-8-sig").splitlines()
    result = []
    for first, last in ((84, 98), (104, 112), (118, 123)):
        rows = [(i, [v.strip() for v in lines[i - 1].strip("|").split("|")])
                for i in range(first, last + 1) if lines[i - 1].startswith("|")]
        header = rows[0][1]
        for number, values in rows[2:]:
            if len(values) != len(header):
                raise ValueError("GAP_SOURCE_TABLE_MALFORMED")
            result.append({"id": values[0], "source": span(master, GAP, number, number),
                           "source_columns": dict(zip(header, values)),
                           "status": "SOURCE_DECLARATION_NOT_NEW_PRODUCT_VERIFICATION",
                           "new_v1_credit": 0, "execution_eligible": False})
    return result


def build_registry(candidate, master):
    """建立不可授權的candidate；語意為明列author提案，仍須獨立review。"""
    candidate.git("merge-base", "--is-ancestor", master.baseline, candidate.baseline)
    ledger = candidate.read_json("docs/program/program_baseline.v1.json")
    if ledger["source_master"] != master.baseline:
        raise ValueError("SEMANTIC_MASTER_NOT_EXISTING_LEDGER_BASELINE")
    delta_ids = {r["id"] for r in ledger["deliverables"]}
    rows = []
    for cid, path, first, last, disposition, meaning, evidence_path, deltas in CLAUSES:
        if not set(deltas) <= delta_ids:
            raise ValueError("SEMANTIC_DELTA_NOT_IN_EXISTING_LEDGER")
        _, evidence = candidate.read(evidence_path)
        rows.append({"id": cid, "source": span(master, path, first, last), "disposition": disposition,
                     "candidate_interpretation": meaning, "candidate_evidence": evidence, "existing_delta_ids": deltas,
                     "integration": "PARTIAL_CANDIDATE_NOT_INDEPENDENTLY_ACCEPTED", "new_v1_credit": 0})
    documents = [source_blocks(master, path) for path in MASTER_PATHS]
    for doc in documents:
        path = doc["source_ref"]["path"]
        lines = master.read(path)[0].splitlines(keepends=True)
        selected = {i for r in rows if r["source"]["path"] == path
                    for i in range(r["source"]["first_line"], r["source"]["last_line"] + 1) if lines[i - 1].strip()}
        doc["selected_nonblank_lines"] = len(selected)
        doc["unselected_nonblank_lines"] = doc["nonblank_line_count"] - len(selected)
    old_index = candidate.read_json("docs/program/historical_requirements.v1.json")
    conflicts = [
        ("H01", "A2-OLD-STATUS", "CLOSE-CORE", "checkpoint4 HOLD is superseded for corrected scope; original35/151 remains NOT_ACCEPTED"),
        ("H02", "GAP-OLD-DETAIL", "CLOSE-CORE", "98/113 and pending C17/C19/C20/C18 superseded by113/113; no re-opening or source rewrite"),
        ("H03", "FREEZE-OLD-STATUS", "CLOSE-BOUNDARY", "planning HOLD superseded for accepted correction scope only; conformance/production remain NOT_ASSERTED"),
        ("H04", "A1-FINDINGS", "GAP-QUEUE", "ENTRY-prefix finding is a historical note; GAP-BROKER-001 source CLOSED is limited acceptance, not fresh broker qualification"),
    ]
    bridges = [
        ("S01", "BT-OLD-METRIC-DEFERRAL", BASE, "Sharpe", ["P04-ENGINE"], "New V1 research metrics candidate does not inherit old post-P12 deferral; actual implementation not claimed"),
        ("S02", "FREEZE-DEFERRED", PROGRAM, "| P11 | Install/config", ["P02-BFF","P11-BACKUP-RESTORE"], "API/web/backup excluded from old correction core are separate V1 deltas; old acceptance is not expanded"),
        ("S03", "A1-DEFERRED", PROGRAM, "單人、本機部署", ["P11-INSTALL"], "Local clean-machine deployment is V1; full production server/platform and activation remain separate"),
        ("S04", "CLOSE-BOUNDARY", PROGRAM, "broker credentials", [], "Credentialless BACKTEST/SIMULATED release does not require P8 broker qualification; future broker gate is not waived"),
    ]
    scope_bridges = []
    for cid, origin, path, anchor, deltas, meaning in bridges:
        raw, evidence = candidate.read(path)
        numbers = [i for i, l in enumerate(raw.decode("utf-8-sig").splitlines(), 1) if anchor in l]
        if len(numbers) != 1 or not set(deltas) <= delta_ids:
            raise ValueError("SCOPE_BRIDGE_ANCHOR_OR_DELTA_INVALID")
        scope_bridges.append({"id": cid, "source_clause_id": origin, "candidate_ref": evidence,
                              "candidate_source": span(candidate,path,numbers[0],numbers[0]), "candidate_interpretation": meaning,
                              "existing_delta_ids": deltas, "status": "CANDIDATE_SCOPE_BRIDGE_PENDING_REVIEW", "new_v1_credit": 0})
    future = [
        ("F-P8-BROKER", "CLOSE-BOUNDARY", "Separate P8 broker capability/world evidence; fixture does not prove broker semantics"),
        ("F-P9-V07", "CLOSE-BOUNDARY", "Original actual PostgreSQL V07 remains NOT_EXECUTED_NOT_VERIFIED; new P05/P08 PG conformance also needs its own evidence"),
        ("F-PRODUCTION-AUTH", "A2-PRODUCTION-AUTH", "Full production N/L authority remains required for protected production paths; V1 application permissions remain P03/P09 obligations"),
        ("F-PRODUCTION-COMPLETENESS", "A2-PRODUCTION-COMPLETENESS", "Full approved operational detector/coverage authority is production gate; P01 quality does not qualify it"),
        ("F-LIVE", "CLOSE-BOUNDARY", "LIVE/production activation denied; credentialless V1 does not remove future safety gates"),
        ("F-EXPANDED-PRODUCT", "A1-DEFERRED", "Original deferred broader product/frameworks retained as source scope; no automatic future commitment or new V1 denominator"),
    ]
    _, primary_ref = candidate.read("docs/program/historical_requirements.v1.json")
    _, ledger_ref = candidate.read("docs/program/program_baseline.v1.json")
    return {"schema_version":"p00.historical_semantics.v1", "revision":1, "status":"CANDIDATE_AUTHORED_NOT_ACCEPTED",
            "authority":"NONE_SOURCE_AND_PROPOSAL_ONLY", "source_master":master.baseline,"source_candidate":candidate.baseline,
            "source_documents":documents, "selected_clauses":rows, "gap_source_rows":gaps(master),
            "status_reconciliations":[{"id":i,"historical_clause_id":a,"selected_evidence_clause_id":b,"reason":reason,
                                       "status":"SOURCE_STATUS_RECONCILIATION_PENDING_INDEPENDENT_REVIEW","accepted_source_modified":False}
                                      for i,a,b,reason in conflicts],
            "scope_bridges":scope_bridges,
            "future_dependencies":[{"id":i,"source_clause_id":c,"scope":reason,"gate":"PRESERVED_NOT_WAIVED",
                                    "verification":"NOT_ASSERTED_BY_THIS_BRIDGE","execution_authority":"NOT_GRANTED"} for i,c,reason in future],
            "primary_index_preservation":{"source_ref":primary_ref,"source_files":len(old_index["source_evidence"]),
                "owner_sections":len(old_index["owner_sections"]),"explicit_clauses":len(old_index["owner_clause_catalog"]),
                "status":"UNCHANGED_PINNED_PREDECESSOR_NOT_MERGED_OR_RECOUNTED"},
            "delta_ledger_preservation":{"source_ref":ledger_ref,"status":"UNCHANGED_NO_NEW_WEIGHT_OR_ACCEPTANCE"},
            "coverage":{"source_index":"COMPLETE_FOR_EIGHT_DECLARED_MASTER_FILES_ONLY","semantic_review":"SELECTED_CLAUSES_ONLY_PENDING_INDEPENDENT_REVIEW",
                "outside_universe":"UNKNOWN_NOT_EXHAUSTIVELY_CLOSED","full_product_requirement_coverage":"INCOMPLETE",
                "unselected_nonblank_lines":sum(d["unselected_nonblank_lines"] for d in documents)},
            "remaining":["Resolve unselected/outside-universe semantic scope without whole-repo rescan or fabricated completeness",
                "Independent clause/status/scope bridge review and provisional weight-baseline acceptance",
                "Trusted current/result/acceptance/telemetry intake and actual qualified environment evidence",
                "Original R06 context/source/read-intake gate; R07 actual golden qualification; R08 final A-S review"],
            "independent_review":"NOT_PERFORMED","actual_runtime_verification":"NOT_PERFORMED","new_v1_credit":0,
            "product_completion":"UNCALIBRATED","execution_eligible":False,"runtime_or_controller_effects":"NONE"}


def verify(registry,candidate,master):
    # typed canonical comparison prevents bool/int equality, field insertion, source/obligation omission and authority promotion。
    if registry.get("source_candidate") != candidate.baseline or registry.get("source_master") != master.baseline:
        raise ValueError("SEMANTIC_SOURCE_BASELINE_MISMATCH")
    expected=build_registry(candidate,master)
    if canonical(registry) != canonical(expected):
        raise ValueError("SEMANTIC_SOURCE_SCOPE_OR_PROPOSAL_MISMATCH")
    return {"status":"EXACT_BOUNDED_SOURCE_AND_PROPOSAL_CHECK_PASS","master_source_files":len(registry["source_documents"]),
            "source_blocks":sum(len(d["blocks"]) for d in registry["source_documents"]),"selected_clauses":len(registry["selected_clauses"]),
            "gap_source_rows":len(registry["gap_source_rows"]),"status_reconciliations":len(registry["status_reconciliations"]),
            "scope_bridges":len(registry["scope_bridges"]),"future_gates":len(registry["future_dependencies"]),
            "unselected_nonblank_lines":registry["coverage"]["unselected_nonblank_lines"],"full_semantic_coverage":"INCOMPLETE",
            "independent_review":"NOT_PERFORMED","new_v1_credit":0,"product_completion":"UNCALIBRATED","execution_eligible":False}


if __name__ == "__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("--registry", default="docs/program/historical_semantic_bridge.v1.json")
    args=parser.parse_args()
    root=Path(__file__).resolve().parents[1]
    registry=json.loads((root/safe_path(args.registry)).read_text(encoding="utf-8"))
    print(json.dumps(verify(registry,Snapshot(root,registry["source_candidate"]),Snapshot(root,registry["source_master"])),indent=2))
