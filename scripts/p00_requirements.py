"""P00 歷史來源清單的 lossless index／核對；不做驗收、計分或 runtime intake。"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re

from p00_context import Snapshot, canonical
from p00_historical_core import reconcile
from p00_progress import calculate

OWNER = "docs/program/P00_OWNER_REQUEST.md"
CAPABILITIES = "docs/V1_CAPABILITY_MAP.md"
TRACE = "docs/blueprint/TRACEABILITY.md"
BLUEPRINTS = (
    "A_GOVERNANCE", "B_DATA_PIPELINE", "C_CALENDAR_CONTRACT", "D_CANONICAL_DOMAIN",
    "E_FEATURE_STRATEGY", "F_BACKTEST_RESEARCH", "G_DECISION_RISK", "H_EXECUTION_OMS",
    "I_BROKER_ADAPTER", "J_ACCOUNT_RECONCILIATION", "K_PERSISTENCE_RECOVERY",
    "L_SIMULATION_LIVE_SAFETY", "M_PYTHON_SERVICE", "N_ASPNET_APPLICATION", "O_REACT_WORKSPACE",
)
MASTER_PATHS = tuple(sorted((
    "docs/ARCHITECTURE.md", "docs/ROADMAP.md", "docs/V1_SYSTEM_BLUEPRINT.md",
    CAPABILITIES, TRACE, "docs/blueprint/METRICS.md",
    *(f"docs/blueprint/{name}.md" for name in BLUEPRINTS),
)))
LIFECYCLES = {"NOT_DESIGNED", "DESIGNED", "DESIGN_FROZEN", "IMPLEMENTED", "UNIT_VERIFIED",
              "INTEGRATION_VERIFIED", "ACCEPTED", "DEFERRED"}
INDEX_PATHS = ("docs/program/program_baseline.v1.json", "docs/program/accepted_core_reconciliation.v1.json",
               "automation/platform/skill_registry.v1.json")
ROOT_KEYS = {"schema_version", "revision", "status", "authority", "candidate_snapshot", "source_master",
             "source_universe", "source_inventory_coverage", "semantic_reconciliation",
             "full_historical_requirement_coverage", "v1_weight_baseline_accepted", "new_v1_credit",
             "source_evidence", "owner_preamble", "owner_sections", "capabilities", "blueprint_leaves",
             "source_outlines", "acceptance_events", "owner_routes", "capability_routes",
             "accepted_core_index", "candidate_index_evidence", "owner_clause_catalog", "owner_clause_routes", "totals"}


def require(condition, reason):
    if not condition:
        raise ValueError(reason)


def span(path, lines, first, last):
    """列號從 1 起算；hash 含原始換行 bytes，不使用 worktree hash。"""
    return {"path": path, "first_line": first + 1, "last_line": last,
            "sha256": hashlib.sha256(b"".join(lines[first:last])).hexdigest()}


def owner_sections(raw):
    """保留 preamble、全 section body 與每個非空連續區塊；不是原子語意驗收。"""
    lines = raw.splitlines(keepends=True)
    headings = []
    for i, line in enumerate(lines):
        match = re.fullmatch(r"# (\d+)\. (.+)", line.decode("utf-8-sig").rstrip("\r\n"))
        if match:
            headings.append((i, int(match[1]), match[2]))
    require([n for _, n, _ in headings] == list(range(91)), "OWNER_SECTION_MISSING_DUPLICATE_OR_REORDERED")
    preamble = span(OWNER, lines, 0, headings[0][0])
    sections = []
    for index, (first, number, title) in enumerate(headings):
        last = headings[index + 1][0] if index + 1 < len(headings) else len(lines)
        blocks, cursor = [], first
        while cursor < last:
            if not lines[cursor].strip():
                cursor += 1
                continue
            start = cursor
            while cursor < last and lines[cursor].strip():
                cursor += 1
            blocks.append({"id": f"OWNER-{number:03}-B{len(blocks) + 1:03}",
                           "source": span(OWNER, lines, start, cursor)})
        sections.append({"id": f"OWNER-{number:03}", "section": number, "title": title,
                         "source": span(OWNER, lines, first, last), "source_blocks": blocks})
    return preamble, sections


def owner_clause_catalog(raw, sections):
    """將七組明列清單保留為 stable source IDs；其他 prose 不冒充已完成原子解析。"""
    lines = raw.splitlines(keepends=True)
    section_lookup = {s["section"]: s["source"] for s in sections}
    groups = [
        (2, "V1-MUST", "V1_REQUIRED_DELIVERY", 32, r"^- (.+)$"),
        (2, "V1-NONGOAL", "NO_V1_DELIVERY_COMMITMENT", 10, r"^- (.+)$"),
        (21, "JOURNEY", "SIX_RELEASE_JOURNEYS", 6, r"^\d+\. (.+)$"),
        (29, "SKILL", "EVALUATE_REUSE_GAP_NOT_CREATE_ALL", 22, r"^([a-z][a-z-]+)$"),
        (40, "GOLDEN", "REPRESENTATIVE_EVAL_FRAMEWORK", 9, r"^([a-zA-Z][a-zA-Z /-]+)$"),
        (84, "DELIVERABLE", "P00_REQUIRED_DELIVERY", 45, r"^\[ \] (.+)$"),
        (85, "OUTPUT", "FINAL_A_TO_S_RESPONSIBILITY", 19, r"^## [A-S]\. (.+)$"),
    ]
    catalog = []
    for number, name, obligation, count, pattern in groups:
        pointer = section_lookup[number]
        selected = []
        first, last = pointer["first_line"] - 1, pointer["last_line"]
        if number == 2:
            markers = {}
            for i in range(first, last):
                line = lines[i].decode("utf-8-sig").rstrip("\r\n")
                if line in {"V1 必須至少支援：", "V1 不要求：", "Shioaji / broker adapter："}:
                    require(line not in markers, "OWNER_V1_SCOPE_MARKER_DUPLICATE")
                    markers[line] = i
            require(set(markers) == {"V1 必須至少支援：", "V1 不要求：", "Shioaji / broker adapter："},
                    "OWNER_V1_SCOPE_MARKER_MISSING")
            must, non_goal, broker = [markers[key] for key in ("V1 必須至少支援：", "V1 不要求：", "Shioaji / broker adapter：")]
            require(must < non_goal < broker, "OWNER_V1_SCOPE_MARKER_ORDER")
            first, last = (must + 1, non_goal) if name == "V1-MUST" else (non_goal + 1, broker)
        for i in range(first, last):
            line = lines[i].decode("utf-8-sig").rstrip("\r\n")
            match = re.fullmatch(pattern, line)
            if match:
                selected.append((i, match[1]))
        require(len(selected) == count, f"OWNER_CLAUSE_GROUP_CHANGED:{name}")
        for index, (i, text) in enumerate(selected, 1):
            catalog.append({"id": f"OWNER-{number:03}-{name}-{index:02}", "section_id": f"OWNER-{number:03}",
                            "group": name, "obligation": obligation, "text": text,
                            "source": span(OWNER, lines, i, i + 1)})
    return catalog


def table_rows(raw, path, header, width):
    """只解析具唯一 exact header 的表格；拒絕漏欄／錯欄而非靜默忽略。"""
    lines = raw.splitlines(keepends=True)
    text_lines = [line.decode("utf-8-sig").rstrip("\r\n") for line in lines]
    starts = [i for i, line in enumerate(text_lines) if line == header]
    require(starts, "SOURCE_TABLE_HEADER_MISSING")
    rows = []
    for start in starts:
        require(start + 1 < len(lines) and re.fullmatch(r"[| :\-]+", text_lines[start + 1]) is not None,
                "SOURCE_TABLE_SEPARATOR_INVALID")
        i = start + 2
        while i < len(lines) and text_lines[i].startswith("|"):
            cells = [cell.strip() for cell in text_lines[i].split("|")[1:-1]]
            require(text_lines[i].endswith("|") and len(cells) == width, "SOURCE_TABLE_ROW_MALFORMED")
            rows.append((cells, span(path, lines, i, i + 1)))
            i += 1
    return rows


def expand_maps(value):
    """保存原始 Maps 同時展開 D01-D05 等 bounded range，避免漏掉 consumer。"""
    result = []
    for item in value.split(","):
        item = item.strip()
        if re.fullmatch(r"[A-O]\d{2}", item):
            ids = [item]
        else:
            match = re.fullmatch(r"([A-O])(\d{2})-([A-O])(\d{2})", item)
            require(match is not None and match[1] == match[3] and int(match[2]) <= int(match[4]),
                    "SOURCE_CAPABILITY_RANGE_INVALID")
            ids = [f"{match[1]}{n:02}" for n in range(int(match[2]), int(match[4]) + 1)]
        require(not set(ids).intersection(result), "SOURCE_MAP_DUPLICATE")
        result.extend(ids)
    return result


def trace_acceptances(raw):
    """只保留 TRACEABILITY 明載的六次 scope acceptance；不提升其他 lifecycle label。"""
    lines = raw.splitlines(keepends=True)
    text = raw.decode("utf-8-sig")
    headings = [(i, re.fullmatch(r"## (\d+)\. (.+) Acceptance Evidence", line.decode("utf-8-sig").strip()))
                for i, line in enumerate(lines)]
    headings = [(i, match[2]) for i, match in headings if match]
    expected = ["GAP-ACCOUNT-001", "GAP-BROKER-001", "GAP-RECON-001A", "GAP-RECON-001B",
                "GAP-BROKER-002", "GAP-08ABCD"]
    require([name for _, name in headings] == expected, "ACCEPTANCE_EVENT_SOURCE_SET_CHANGED")
    result = []
    for index, (first, package) in enumerate(headings):
        last = headings[index + 1][0] if index + 1 < len(headings) else len(lines)
        body = b"".join(lines[first:last]).decode("utf-8-sig")
        commit = re.search(r"Runtime commit：\s+([0-9a-f]{40})", body)
        leaves = re.search(r"Accepted Blueprint leaves：\s+(.+?)(?:\n\S|\Z)", body, re.S)
        explicit_pass = re.search(r"Acceptance：\s+PASS", body) is not None
        require(commit is not None and leaves is not None
                and (explicit_pass or (package == "GAP-08ABCD" and re.search(r"Accepted weight：\s+77", body))),
                "ACCEPTANCE_COMMIT_SCOPE_OR_PASS_MISSING")
        ids = re.findall(r"\b[A-O][0-9]{3}\b", leaves[1])
        require(ids and len(ids) == len(set(ids)), "ACCEPTANCE_SOURCE_LEAF_DUPLICATE")
        result.append({"id": package, "source": span(TRACE, lines, first, last),
                       "accepted_commit": commit[1], "blueprint_leaves": ids,
                       "claim": "RECORDED_ACCEPTED_HISTORICAL_SCOPE",
                       "disposition_field": "EXPLICIT_PASS" if explicit_pass else "ACCEPTED_SCOPE_LIST_NO_PASS_FIELD",
                       "new_v1_credit": 0})
    require("只有 ACTIVE" in text, "CONSERVATIVE_SCOPE_RULE_MISSING")
    return result


def index_sources(candidate, master):
    """來源宇宙明列 22 檔；沒有全 repo 搜尋、無外部存取，沒有執行 authority。"""
    candidate.git("merge-base", "--is-ancestor", master.baseline, candidate.baseline)
    owner_raw, owner_evidence = candidate.read(OWNER)
    source_raw, evidence = {}, [owner_evidence]
    for path in MASTER_PATHS:
        raw, binding = master.read(path)
        source_raw[path] = raw
        evidence.append(binding)
    preamble, owner = owner_sections(owner_raw)
    capabilities = []
    for cells, pointer in table_rows(source_raw[CAPABILITIES], CAPABILITIES,
                                     "| ID | Capability | Status | Remaining |", 4):
        require(re.fullmatch(r"[A-O]\d{2}", cells[0]) is not None
                and cells[2] in {"COMPLETE", "PARTIAL", "NOT_STARTED"}, "CAPABILITY_SOURCE_ROW_INVALID")
        capabilities.append({"id": cells[0], "name": cells[1], "historical_status": cells[2],
                             "historical_remaining": cells[3], "source": pointer})
    cap_ids = {row["id"] for row in capabilities}
    require(len(capabilities) == len(cap_ids) == 92, "CAPABILITY_SOURCE_COUNT_OR_DUPLICATE")
    leaves = []
    for name in BLUEPRINTS:
        path = f"docs/blueprint/{name}.md"
        for cells, pointer in table_rows(source_raw[path], path,
                                         "| ID | Name | Purpose | Lifecycle | Weight | Maps |", 6):
            require(re.fullmatch(r"[A-O]\d{3}", cells[0]) is not None
                    and cells[0][0] == name[0] and cells[3] in LIFECYCLES
                    and cells[4].isascii() and cells[4].isdigit() and int(cells[4]) > 0,
                    "BLUEPRINT_SOURCE_ROW_INVALID")
            maps = expand_maps(cells[5])
            require(set(maps) <= cap_ids, "BLUEPRINT_MAP_UNKNOWN_CAPABILITY")
            leaves.append({"id": cells[0], "name": cells[1], "purpose": cells[2],
                           "historical_lifecycle_label": cells[3], "historical_weight": int(cells[4]),
                           "maps_raw": cells[5], "capability_ids": maps, "source": pointer})
    require(len(leaves) == len({row["id"] for row in leaves}) == 603
            and sum(row["historical_weight"] for row in leaves) == 2137, "BLUEPRINT_SOURCE_BASELINE_CHANGED")
    require({cid for row in leaves for cid in row["capability_ids"]} == cap_ids, "SOURCE_CAPABILITY_ORPHAN")
    outlines = []
    for path, raw in source_raw.items():
        lines = raw.splitlines(keepends=True)
        entries = []
        for i, line in enumerate(lines):
            heading = re.fullmatch(r"(#{1,6}) (.+)", line.decode("utf-8-sig").rstrip("\r\n"))
            if heading:
                entries.append({"title": heading[2], "level": len(heading[1]),
                                "source": span(path, lines, i, i + 1)})
        outlines.append({"path": path, "headings": entries})
    events = trace_acceptances(source_raw[TRACE])
    known_leaves = {row["id"] for row in leaves}
    accepted_union = set()
    for event in events:
        require(set(event["blueprint_leaves"]) <= known_leaves, "ACCEPTED_LEAF_NOT_IN_BLUEPRINT")
        require(not accepted_union.intersection(event["blueprint_leaves"]), "HISTORICAL_ACCEPTANCE_OVERLAP")
        accepted_union.update(event["blueprint_leaves"])
        master.git("merge-base", "--is-ancestor", event["accepted_commit"], master.baseline)
    return {"source_evidence": evidence, "owner_preamble": preamble, "owner_sections": owner,
            "capabilities": capabilities, "blueprint_leaves": leaves, "source_outlines": outlines,
            "acceptance_events": events, "owner_clause_catalog": owner_clause_catalog(owner_raw, owner)}


def verify_clause_routes(registry, actual, ledger, candidate):
    """明列義務逐项有處置；只核對引用，仍不接受候選語意或 grant。"""
    clauses = {r["id"]: r for r in actual["owner_clause_catalog"]}
    routes = registry["owner_clause_routes"]
    require(len(routes) == len(clauses) and {r["id"] for r in routes} == set(clauses),
            "OWNER_CLAUSE_ROUTE_MISSING_OR_DUPLICATE")
    known = {"workstreams": {f"R{i:02}" for i in range(1, 9)},
             "delta_deliverables": {r["id"] for r in ledger["deliverables"]},
             "journeys": {r["id"] for r in ledger["journeys"]},
             "reuse_skill_ids": {r["skill_id"] for r in candidate.read_json(INDEX_PATHS[2])["skills"]}}
    journey_bindings = []
    for route in routes:
        require(set(route) == {"id", "obligation", "workstreams", "candidate_evidence", "delta_deliverables",
                "journeys", "reuse_skill_ids", "state", "remaining_boundary", "new_v1_credit"},
                "OWNER_CLAUSE_ROUTE_FIELDS_INVALID")
        require(route["obligation"] == clauses[route["id"]]["obligation"]
                and route["state"] in {"PARTIAL_CANDIDATE_NOT_ACCEPTED", "NO_V1_DELIVERY_COMMITMENT",
                "EVALUATION_REQUIRED_NOT_QUALIFIED", "NOT_YET_VERIFIED"}
                and route["remaining_boundary"] and type(route["new_v1_credit"]) is int
                and route["new_v1_credit"] == 0, "OWNER_CLAUSE_NOT_ACCEPTANCE_OR_CREDIT")
        for key, values in known.items():
            require(isinstance(route[key], list) and len(set(route[key])) == len(route[key])
                    and set(route[key]) <= values, "OWNER_CLAUSE_REFERENCE_INVALID")
        require(route["workstreams"], "OWNER_CLAUSE_STREAM_MISSING")
        group = clauses[route["id"]]["group"]
        require((route["state"] == "NO_V1_DELIVERY_COMMITMENT") == (group == "V1-NONGOAL"),
                "OWNER_MANDATORY_REQUIREMENT_CANNOT_BECOME_NONGOAL")
        require((route["state"] == "EVALUATION_REQUIRED_NOT_QUALIFIED") == (group in {"SKILL", "GOLDEN"}),
                "OWNER_EVALUATION_NOT_QUALIFIED")
        require(isinstance(route["candidate_evidence"], list)
                and len(set(route["candidate_evidence"])) == len(route["candidate_evidence"])
                and (route["candidate_evidence"] or route["state"] == "NOT_YET_VERIFIED"),
                "OWNER_CLAUSE_EVIDENCE_MISSING_OR_DUPLICATE")
        for path in route["candidate_evidence"]:
            candidate.read(path)
        if group == "JOURNEY":
            require(len(route["journeys"]) == 1, "OWNER_JOURNEY_ALIAS_MISSING")
            journey_bindings.extend(route["journeys"])
        else:
            require(not route["journeys"], "OWNER_NONJOURNEY_ALIAS_UNEXPECTED")
    require(len(journey_bindings) == 6 and set(journey_bindings) == known["journeys"], "OWNER_JOURNEY_ALIAS_NOT_BIJECTIVE")
    return len(clauses)


def verify(registry, ledger, candidate, master):
    """實際 blob 重建 spine，拒絕漏來源／漏列／假接受；mapping 只驗結構且待語意 review。"""
    require(set(registry) == ROOT_KEYS and type(registry["revision"]) is int and registry["revision"] == 1,
            "REGISTRY_FIELDS_OR_REVISION_INVALID")
    require(registry["schema_version"] == "p00.historical_requirements.v1"
            and registry["candidate_snapshot"] == candidate.baseline
            and registry["source_master"] == master.baseline == ledger["source_master"], "SOURCE_BASELINE_MISMATCH")
    require(registry["status"] == "CANDIDATE_SOURCE_INDEX_NOT_ACCEPTANCE" and registry["authority"] == "NONE",
            "NO_ACCEPTANCE_OR_EXECUTION_AUTHORITY")
    require(registry["source_inventory_coverage"] == "COMPLETE_FOR_DECLARED_22_FILE_UNIVERSE"
            and registry["semantic_reconciliation"] == "INCOMPLETE_PENDING_ATOMIC_REVIEW"
            and registry["full_historical_requirement_coverage"] == "INCOMPLETE"
            and registry["v1_weight_baseline_accepted"] is False
            and registry["new_v1_credit"] == 0 and type(registry["new_v1_credit"]) is int,
            "SOURCE_INDEX_IS_NOT_PRODUCT_ACCEPTANCE")
    require(canonical(ledger) == canonical(candidate.read_json(INDEX_PATHS[0])), "PLANNING_LEDGER_SOURCE_CHANGED")
    require(canonical(registry["candidate_index_evidence"]) == canonical([candidate.read(p)[1] for p in INDEX_PATHS]),
            "CANDIDATE_INDEX_SOURCE_CHANGED")
    calculate(ledger)
    reconcile(candidate.read_json(INDEX_PATHS[1]), ledger, master)
    actual = index_sources(candidate, master)
    for key, expected in actual.items():
        require(canonical(registry[key]) == canonical(expected), f"EXACT_SOURCE_INDEX_MISMATCH:{key}")
    require(registry["source_universe"] == {"candidate": [OWNER], "master": list(MASTER_PATHS),
            "outside_universe": "NOT_CLAIMED_COMPLETE_NO_NEGATIVE_ABSENCE_PROOF"}, "SOURCE_UNIVERSE_CHANGED")
    coverage = registry["owner_routes"]
    require(len(coverage) == 91 and {row["id"] for row in coverage} == {r["id"] for r in actual["owner_sections"]},
            "OWNER_ROUTE_MISSING_OR_DUPLICATE")
    for route in coverage:
        require(set(route) == {"id", "workstreams", "candidate_evidence", "state", "remaining_semantic_check"},
                "OWNER_ROUTE_FIELDS_INVALID")
        require(route["workstreams"] and len(set(route["workstreams"])) == len(route["workstreams"])
                and set(route["workstreams"]) <= {f"R{i:02}" for i in range(1, 9)}, "OWNER_ROUTE_STREAM_INVALID")
        require(route["candidate_evidence"] and route["remaining_semantic_check"]
                and route["state"] == "CANDIDATE_MAPPING_PENDING_INDEPENDENT_REVIEW", "OWNER_SEMANTIC_CLOSURE_NOT_GRANTED")
        for path in route["candidate_evidence"]:
            candidate.read(path)
    routes = registry["capability_routes"]
    require(len(routes) == 92 and {r["id"] for r in routes} == {r["id"] for r in actual["capabilities"]},
            "CAPABILITY_ROUTE_MISSING_OR_DUPLICATE")
    deliverables = {row["id"] for row in ledger["deliverables"]}
    leaf_lookup = {row["id"]: row for row in actual["blueprint_leaves"]}
    for route in routes:
        require(set(route) == {"id", "blueprint_leaves", "delta_deliverables", "scope", "remaining_boundary", "new_v1_credit"},
                "CAPABILITY_ROUTE_FIELDS_INVALID")
        expected_ids = [row["id"] for row in actual["blueprint_leaves"] if route["id"] in row["capability_ids"]]
        require(route["blueprint_leaves"] == expected_ids, "CAPABILITY_LEAF_CLOSURE_CHANGED")
        require(route["delta_deliverables"] and len(set(route["delta_deliverables"])) == len(route["delta_deliverables"])
                and set(route["delta_deliverables"]) <= deliverables, "DELTA_LINK_UNKNOWN_OR_DUPLICATE")
        require(route["scope"] in {"V1_DELTA_WITH_SEPARATE_FUTURE_GATES", "BROKER_PAPER_OR_PRODUCTION_SEPARATE"}
                and route["remaining_boundary"] and route["new_v1_credit"] == 0
                and type(route["new_v1_credit"]) is int, "HISTORICAL_CAPABILITY_IS_NOT_NEW_CREDIT")
    clause_count = verify_clause_routes(registry, actual, ledger, candidate)
    accepted = {leaf for event in actual["acceptance_events"] for leaf in event["blueprint_leaves"]}
    totals = {"owner_sections": 91, "owner_source_blocks": sum(len(r["source_blocks"]) for r in actual["owner_sections"]),
              "owner_explicit_clauses": clause_count,
              "capabilities": 92, "blueprint_leaves": 603, "blueprint_historical_weight": 2137,
              "recorded_acceptance_events": 6, "recorded_acceptance_unique_leaves": len(accepted),
              "recorded_acceptance_historical_weight": sum(leaf_lookup[l]["historical_weight"] for l in accepted),
              "new_v1_credit": 0}
    require(canonical(registry["totals"]) == canonical(totals), "HISTORICAL_TOTALS_CHANGED_OR_DOUBLE_COUNTED")
    require(canonical(registry["accepted_core_index"]) == canonical({
        "path": "docs/program/accepted_core_reconciliation.v1.json",
        "scope": "SEPARATE_GAP08_26_LEAVES_113_WEIGHT_NOT_ADDED_TO_603_OR_2137",
        "new_v1_credit": 0}), "GAP08_CORE_OVERLAP_OR_CREDIT_CHANGED")
    return {"status": "EXACT_SOURCE_INDEX_PASS", **totals, "product_completion": "UNCALIBRATED",
            "semantic_reconciliation": registry["semantic_reconciliation"],
            "independent_review": "NOT_PERFORMED", "execution_eligible": False}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("registry", nargs="?", default="docs/program/historical_requirements.v1.json")
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    registry = json.loads((root / args.registry).read_text(encoding="utf-8"))
    ledger = json.loads((root / "docs/program/program_baseline.v1.json").read_text(encoding="utf-8"))
    print(json.dumps(verify(registry, ledger, Snapshot(root, registry["candidate_snapshot"]),
                            Snapshot(root, ledger["source_master"])), ensure_ascii=True, indent=2))
