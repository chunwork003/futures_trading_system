"""P00 候選 ledger 的離線結構與權重計算；不驗收 evidence、不授權執行。"""

import argparse
import json
from fractions import Fraction
from pathlib import Path

GATES = {"implementation": 2, "targeted_tests": 1, "integration": 1,
         "independent_acceptance": 1}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def unique(rows):
    result = {row["id"]: row for row in rows}
    require(len(result) == len(rows), "duplicate identity")
    return result


def validate_regrouping(previous, current):
    """相同 baseline 的拆包／correction 不得偷偷重設 deliverable 分母。"""
    calculate(previous)
    calculate(current)
    require(previous["revision"] == current["revision"], "baseline revision requires independent change review")
    before = {r["id"]: (r["weight"], r["contract_revision"]) for r in previous["deliverables"]}
    after = {r["id"]: (r["weight"], r["contract_revision"]) for r in current["deliverables"]}
    require(before == after, "stable deliverables changed; explicit baseline revision required")


def calculate(ledger):
    """只報候選資料的可重算結構；非空證據必須由未來獨立 intake 處理。"""
    require(ledger["schema_version"] == "p00.progress.v1", "unknown schema")
    require(ledger["status"] == "CANDIDATE_NOT_FROZEN" and ledger["authority"] == "NONE",
            "not a candidate ledger")
    require(ledger["scope"] == "KNOWN_V1_REMAINING_INTEGRATION_DELTA", "scope mismatch")
    packages = unique(ledger["packages"])
    require(set(packages) == {f"P{i:02}" for i in range(13)}, "baseline package set changed")
    visited, visiting = set(), set()

    def visit(pid):
        require(pid in packages, "unknown dependency")
        require(pid not in visiting, "dependency cycle")
        if pid in visited:
            return
        visiting.add(pid)
        package = packages[pid]
        require(package["acceptance"] is None, "accepted evidence intake not implemented")
        require(package["kind"] == ("DESIGN" if pid == "P00" else "ENGINEERING"), "kind mismatch")
        require(len(set(package["dependencies"])) == len(package["dependencies"]), "duplicate dependency")
        for parent in package["dependencies"]:
            visit(parent)
        visiting.remove(pid)
        visited.add(pid)

    for pid in packages:
        visit(pid)
    deliverables = unique(ledger["deliverables"])
    total = 0
    allocations = set()
    by_package = {pid: 0 for pid in packages}
    for did, row in deliverables.items():
        pid = row["package"]
        require(pid in packages and packages[pid]["kind"] == "ENGINEERING", "design has no runtime credit")
        require(type(row["weight"]) is int and row["weight"] > 0, "positive integer weight required")
        require(type(row["contract_revision"]) is int and row["contract_revision"] > 0, "invalid contract revision")
        require(set(row["gates"]) == set(GATES), "gate set mismatch")
        require(all(v is None for v in row["gates"].values()), "verified gate intake not implemented")
        parts = unique(row["allocations"])
        require(parts and not allocations.intersection(parts), "duplicate allocation")
        require(all(type(p["weight"]) is int and p["weight"] > 0 for p in parts.values()), "invalid allocation weight")
        require(sum(p["weight"] for p in parts.values()) == row["weight"], "split changed denominator")
        allocations.update(parts)
        total += row["weight"]
        by_package[pid] += row["weight"]
    require(all(weight > 0 for pid, weight in by_package.items() if pid != "P00"), "engineering package missing deliverables")
    for correction in unique(ledger["corrections"]).values():
        require(correction["deliverable"] in deliverables, "unknown corrected deliverable")
        require(type(correction["added_weight"]) is int and correction["added_weight"] == 0,
                "correction inflated denominator")
    require(ledger["invalidations"] == [], "invalidation intake not implemented")
    journeys = unique(ledger["journeys"])
    require(set(journeys) == {f"J{i}" for i in range(1, 7)}, "journey set changed")
    require(all(j["evidence"] is None for j in journeys.values()), "journey evidence intake not implemented")
    chain = ledger["critical_chain_hypothesis"]
    require(chain and len(set(chain)) == len(chain), "invalid critical chain")
    require(all(pid in packages for pid in chain), "unknown critical package")
    require(all(a in packages[b]["dependencies"] for a, b in zip(chain, chain[1:])), "chain lacks dependency edge")
    require(ledger["eta"] == dict.fromkeys(("optimistic", "base", "conservative")), "uncalibrated ETA must remain unknown")
    effort_low = effort_high = 0
    for pid, package in packages.items():
        effort = package["effort_days"]
        if pid == "P00":
            require(effort is None, "P00 remaining effort uncalibrated")
        else:
            require(isinstance(effort, list) and len(effort) == 2 and
                    all(type(x) is int and x > 0 for x in effort) and effort[0] <= effort[1], "invalid effort range")
            effort_low += effort[0]
            effort_high += effort[1]
    return {
        "authority": "NONE", "execution_eligible": False,
        "accounting_scope": ledger["scope"], "weight_status": "PROVISIONAL_NOT_FROZEN",
        "candidate_engineering_weight": total, "weight_by_package": by_package,
        "recorded_delta_credit": 0, "recorded_delta_fraction": str(Fraction(0, total)),
        "product_completion": "UNCALIBRATED_HISTORICAL_COVERAGE_INCOMPLETE",
        "v1_engineering_weight_completion": "UNCALIBRATED_BASELINE_NOT_ACCEPTED",
        "v1_deployable_completion": {"verified": 0, "required": 6},
        "total_v1_packages_remaining": len(packages),
        "critical_packages_remaining": len(chain), "critical_count_basis": "DEPENDENCY_HYPOTHESIS_NOT_CPM",
        "current_critical_stage": "P00_BASELINE_AND_INDEPENDENT_REVIEW",
        "engineering_effort_days_excluding_p00": [effort_low, effort_high],
        "eta": ledger["eta"], "automation_progress": "UNQUALIFIED_NOT_A_PRODUCT_PERCENTAGE",
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("ledger", type=Path)
    args = parser.parse_args()
    print(json.dumps(calculate(json.loads(args.ledger.read_text(encoding="utf-8"))), indent=2))


if __name__ == "__main__":
    main()
