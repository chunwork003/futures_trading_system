"""結果閱讀不得把歷史編譯或已消耗前件轉換成執行權。"""

from copy import deepcopy
import json

import pytest

from scripts import p00_result_context as reader


@pytest.fixture
def evidence(monkeypatch):
    files = {}
    records = []
    for role, pid in [("ACCEPTED_PREDECESSOR", "AUTO-IMP-002"), ("P01_COMPILATION", "P01"), ("P02_COMPILATION", "P02")]:
        path = role + ".json"
        source = {"baseline_sha": "old", "path": path, "git_blob": role}
        records.append({"role": role, "source": source})
        if pid == "AUTO-IMP-002":
            value = {"package_id": pid, "status": "ACCEPTED_MATERIALIZED"}
        else:
            candidate = {"identity": {"package_id": pid, "revision": 1}}
            files[f"docs/program/packages/{pid}.candidate.v1.json"] = candidate
            value = {"package": deepcopy(candidate), "status": "PACKAGE_NOT_READY", "execution_eligible": False}
        files[path] = value
    files[reader.INDEX] = {"status": "CANDIDATE_NOT_AUTHORITY", "source_master": "master", "records": records}

    class FakeSnapshot:
        def __init__(self, root, sha):
            self.sha = sha

        def read_json(self, path):
            return deepcopy(files[path])

        def read(self, path):
            source = next((r["source"] for r in records if r["source"]["path"] == path), {"path": path})
            return json.dumps(files[path]).encode(), deepcopy(source)

    monkeypatch.setattr(reader, "Snapshot", FakeSnapshot)
    monkeypatch.setattr(reader, "bind_loaded_source", lambda *args: {})
    return files


def test_historical_results_never_grant_current_readiness(evidence):
    result = reader.read_results(".", "planning", "master")
    assert result["execution_eligible"] is False
    assert result["complete_current_intake"] is False
    assert all("RECOMPILE" in r["disposition"] for r in result["records"][1:])


@pytest.mark.parametrize("change", [
    lambda f: f[reader.INDEX].update(source_master="new-master"),
    lambda f: f[reader.INDEX]["records"].pop(),
    lambda f: f["P01_COMPILATION.json"].update(execution_eligible=True),
    lambda f: f["docs/program/packages/P01.candidate.v1.json"]["identity"].update(revision=2),
    lambda f: f["ACCEPTED_PREDECESSOR.json"].update(status="PENDING_REVIEW"),
])
def test_stale_and_misclassified_index_fails(evidence, change):
    change(evidence)
    with pytest.raises(ValueError):
        reader.read_results(".", "planning", "master")
