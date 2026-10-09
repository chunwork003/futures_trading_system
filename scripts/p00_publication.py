"""精確 publication manifest 產生器；唯讀 Git，沒有 push、rebase、merge或acceptance。"""
from __future__ import annotations

import argparse
from collections import Counter
import hashlib
import io
import json
from pathlib import Path
import re
import subprocess

try:
    from p00_context import Snapshot, canonical, safe_path
except ModuleNotFoundError:
    from scripts.p00_context import Snapshot, canonical, safe_path

BRANCH = "architecture/p00-v1-baseline"
REPOSITORY = "chunwork003/futures_trading_system"


def allowed(path):
    safe_path(path.rstrip("/"))
    return path == "docs/work/P00_BASELINE.md" or path.startswith(("docs/architecture/", "docs/program/", "automation/platform/", "scripts/p00_", "tests/platform/"))


def changes(snapshot, before, after):
    items = snapshot.git("diff", "--raw", "-z", "--no-abbrev", "--no-renames", before, after).split(b"\0")
    result = []
    for i in range(0, len(items) - 1, 2):
        meta, path = items[i], items[i + 1].decode("utf-8")
        old_mode, new_mode, old, new, status = meta[1:].decode("ascii").split()
        if status not in ("A", "M", "D", "T"):
            raise ValueError("UNSUPPORTED_DIFF_STATUS")
        if not allowed(path):
            raise ValueError("PROTECTED_SCOPE_CHANGE: " + path)
        if any(m not in ("000000", "100644", "100755") for m in (old_mode, new_mode)):
            raise ValueError("NON_REGULAR_PUBLICATION_FILE")
        result.append({"path": path, "status": status, "old_mode": old_mode, "new_mode": new_mode,
                       "before_blob": None if set(old) == {"0"} else old,
                       "after_blob": None if set(new) == {"0"} else new})
    return result


def blob_metadata(snapshot, ids):
    ids = sorted(set(ids))
    if not ids:
        return {}
    # 一次batch讀取精確diff選出的regular blobs，不掃描data或整棵repository。
    process = subprocess.run(["git", "--no-replace-objects", "-C", str(snapshot.root), "cat-file", "--batch"],
                             input=("\n".join(ids) + "\n").encode(), capture_output=True, check=True)
    stream, output = io.BytesIO(process.stdout), {}
    for oid in ids:
        header = stream.readline().decode().strip().split()
        if len(header) != 3 or header[0] != oid or header[1] != "blob":
            raise ValueError("BLOB_UNAVAILABLE")
        size = int(header[2]); raw = stream.read(size)
        if len(raw) != size or stream.read(1) != b"\n":
            raise ValueError("BLOB_BATCH_FRAMING")
        output[oid] = {"git_blob": oid, "content_sha256": hashlib.sha256(raw).hexdigest(), "size_bytes": size}
    return output


def build_manifest(root, payload, expected_remote, observed_master):
    snapshot = Snapshot(root, payload)
    Snapshot(root, expected_remote); Snapshot(root, observed_master)
    branch = snapshot.git("branch", "--show-current").decode().strip()
    if branch != BRANCH or snapshot.git("rev-parse", "HEAD").decode().strip() != payload:
        raise ValueError("SOURCE_BRANCH_OR_HEAD_MISMATCH")
    url = snapshot.git("remote", "get-url", "origin").decode().strip()
    if url not in ("https://github.com/" + REPOSITORY + ".git", "https://github.com/" + REPOSITORY,
                   "git@github.com:" + REPOSITORY + ".git"):
        raise ValueError("REMOTE_REPOSITORY_MISMATCH")
    remote_ref = "refs/remotes/origin/" + BRANCH
    if snapshot.git("rev-parse", remote_ref).decode().strip() != expected_remote:
        raise ValueError("EXPECTED_REMOTE_HEAD_DRIFT")
    if snapshot.git("rev-parse", "origin/master").decode().strip() != observed_master:
        raise ValueError("OBSERVED_MASTER_DRIFT")
    snapshot.git("merge-base", "--is-ancestor", expected_remote, payload)
    snapshot.git("merge-base", "--is-ancestor", observed_master, payload)
    commits = snapshot.git("rev-list", "--reverse", "--topo-order", expected_remote + ".." + payload).decode().splitlines()
    if not commits:
        raise ValueError("NO_UNPUBLISHED_COMMITS")
    records = []
    for sha in commits:
        parents = snapshot.git("show", "-s", "--format=%P", sha).decode().strip().split()
        # 完整父鏈列出；每個父邊均檢查，防止protected修改後再回復。
        edges = [{"parent": p, "files": changes(snapshot, p, sha)} for p in parents]
        records.append({"order": len(records) + 1, "sha": sha, "parents": parents,
                        "purpose": snapshot.git("show", "-s", "--format=%s", sha).decode().strip(),
                        "parent_deltas": edges})
    net = changes(snapshot, expected_remote, payload)
    master_delta = changes(snapshot, observed_master, payload)
    all_rows = net + [r for c in records for e in c["parent_deltas"] for r in e["files"]]
    ids = [r[k] for r in all_rows for k in ("before_blob", "after_blob") if r[k]]
    metadata = blob_metadata(snapshot, ids)
    for row in all_rows:
        row["before"] = metadata.get(row["before_blob"])
        row["after"] = metadata.get(row["after_blob"])
    status = snapshot.read_json("docs/program/p00_status.v1.json")
    evidence_path = safe_path(status["current_checkpoint_evidence"])
    evidence = snapshot.read_json(evidence_path)
    state = snapshot.git("status", "--porcelain", "--untracked-files=normal").decode().splitlines()
    excluded = []
    for line in state:
        if line == "?? data/":
            continue
        path = line[3:]
        if not allowed(path):
            raise ValueError("OUT_OF_SCOPE_WORKTREE_CHANGE")
        excluded.append(line)

    output = {"schema_version": "p00.publication_manifest.v1", "status": "APPROVAL_REQUIRED_NOT_PUBLISHED",
              "repository": REPOSITORY, "remote": "origin", "remote_url": "https://github.com/" + REPOSITORY + ".git",
              "source_branch": BRANCH, "destination_branch": BRANCH,
              "source_ref": "refs/heads/" + BRANCH, "destination_ref": "refs/heads/" + BRANCH,
              "local_head": payload, "expected_remote_head": expected_remote, "observed_origin_master": observed_master,
              "local_master_ref_unchanged": snapshot.git("rev-parse", "master").decode().strip(),
              "push_refspec_if_exactly_approved": payload + ":refs/heads/" + BRANCH,
              "ordinary_fast_forward": True, "force": False, "rebase": False,
              "commits": records, "commit_count": len(records), "files": net,
              "file_count": len(net), "net_status_counts": dict(sorted(Counter(r["status"] for r in net).items())),
              "all_commit_touched_files": sorted({r["path"] for r in all_rows}),
              "uncommitted_worktree_changes_excluded_from_payload": excluded,
              "protected_scope": {"status": "PASS", "method": "Every pending parent-edge delta and net origin/master delta allowlist checked",
                                  "origin_master_delta_file_count": len(master_delta), "intermediate_protected_changes": 0,
                                  "product_source_migrations_accepted_control_data_credentials": "UNCHANGED",
                                  "untracked_data": "EXCLUDED_NOT_READ_NOT_STAGED"},
              "validation_evidence": {"source": snapshot.read(evidence_path)[1], "checkpoint": evidence,
                                      "classification": "AUTHOR_OFFLINE_VALIDATION_NOT_ACCEPTANCE"},
              "publication_effects": {"LOCAL_COMMITTED": True, "REMOTE_PUBLISHED": False,
                                      "REVIEW_PENDING": True, "ACCEPTED": False, "product_authorization": "NOT_AUTHORIZED",
                                      "acceptance": False, "merge": False, "controller_activation": False},
              "approval_rule": "Approval binds repository/destination/exact payload SHA and manifest hash; new commits are not included implicitly",
              "freshness": "CALLER_FETCH_AND_REF_OBSERVATION_NOT_NETWORK_ATTESTATION"}
    output["manifest_sha256"] = hashlib.sha256(canonical(output)).hexdigest()
    return output


def render_markdown(manifest):
    m = manifest
    lines = ["# 精確 Git Publication Manifest", "", "狀態：APPROVAL_REQUIRED / NOT_PUBLISHED。", "",
             "- Repository：`" + m["repository"] + "`",
             "- Source / destination branch：`" + m["source_branch"] + "` → `" + m["destination_branch"] + "`",
             "- 完整 local HEAD：`" + m["local_head"] + "`", "- 預期 remote HEAD：`" + m["expected_remote_head"] + "`",
             "- Manifest SHA256：`" + m["manifest_sha256"] + "`",
             "- 普通 fast-forward：true；force/rebase/merge/master修改：false。",
             "- Commits：" + str(m["commit_count"]) + "；淨檔案：" + str(m["file_count"]) + "；A/M/D：`" + json.dumps(m["net_status_counts"]) + "`。",
             "- Protected scope：PASS（包含每個commit父邊及origin/master delta）；data未讀／未stage。",
             "- Publication僅發布已提交候選；不包含acceptance、merge、controller activation或product authorization。", "",
             "## Commits（完整 ancestry / parent deltas見同名JSON）", "", "| 順序 | 完整SHA | 用途 |", "|---|---|---|"]
    for c in m["commits"]:
        lines.append("| " + str(c["order"]) + " | `" + c["sha"] + "` | " + c["purpose"].replace("|", chr(92) + "|") + " |")
    lines += ["", "## 全部檔案（before/after content SHA256與mode見JSON）", "", "| A/M/D | Path | after Git blob / deletion before blob |", "|---|---|---|"]
    for r in m["files"]:
        lines.append("| " + r["status"] + " | `" + r["path"] + "` | `" + (r["after_blob"] or r["before_blob"]) + "` |")
    e = m["validation_evidence"]["checkpoint"]
    lines += ["", "## 驗證證據與核准界線", "", "Exact checkpoint：`" + m["validation_evidence"]["source"]["path"] + "`；Git blob `" + m["validation_evidence"]["source"]["git_blob"] + "`。",
              "測試／驗證摘要：`" + str(e.get("targeted_tests", "SEE_CHECKPOINT")) + "`；`" + str(e.get("full_platform_tests", "SEE_CHECKPOINT")) + "`。",
              "尚需使用者具體核准repository、目的分支、上述完整payload SHA與manifest SHA256。核准前不push；執行前重新fetch，如remote或payload變動須重建manifest。", ""]
    return "\n".join(lines)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", default=str(Path(__file__).resolve().parents[1]))
    parser.add_argument("--payload", required=True)
    parser.add_argument("--expected-remote", required=True)
    parser.add_argument("--observed-master", required=True)
    args = parser.parse_args()
    print(json.dumps(build_manifest(args.root, args.payload, args.expected_remote, args.observed_master), ensure_ascii=False, indent=2))
