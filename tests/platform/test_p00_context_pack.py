"""閱讀投影保持契約內容；任何未標示歷史不得默默消失。"""

from copy import deepcopy
import json

import pytest

from scripts.p00_context_pack import MARKER, digest, encode_document, expand_json


def test_shared_schema_roundtrip_preserves_security_and_constraints():
    pool = {}
    schema = {"type": "object", "additionalProperties": False, "required": ["id"],
              "properties": {"id": {"type": "string"}}, "description": "必須保留"}
    documents = []
    for security in [{"Bearer": []}, {"Cookie": [], "CSRF": []}]:
        value = {"openapi": "3.1.0", "security": [security], "paths": {},
                 "components": {"schemas": {"Id": schema}}}
        encoded = encode_document("api.json", json.dumps(value).encode(), pool)
        assert expand_json(encoded, pool) == value
        documents.append(encoded)
    assert len(pool) == 1
    changed = deepcopy(pool)
    next(iter(changed.values()))["additionalProperties"] = True
    with pytest.raises(ValueError, match="SCHEMA_POOL_HASH_MISMATCH"):
        expand_json(documents[0], changed)


def test_current_section_and_archive_boundary_are_exact():
    current = "# CURRENT\nAUTHORIZATION = NOT_AUTHORIZED\n\n"
    archive = MARKER + "\n# old\nAUTHORIZATION = GRANTED\n"
    value = encode_document("docs/CURRENT_STATE.md", (current + archive).encode(), {})
    assert value["text"] == current
    assert value["archive_start_line"] == 4
    assert value["archive_text_sha256"] == digest(archive.encode())


@pytest.mark.parametrize("body", ["no marker", MARKER + "\n", "\n" + MARKER])
def test_empty_or_missing_history_boundary_fails(body):
    with pytest.raises(ValueError):
        encode_document("docs/CURRENT_WORK.md", body.encode(), {})


def test_history_words_elsewhere_never_remove_text():
    raw = ("# instructions\n" + MARKER + "\nretained rules").encode()
    assert encode_document("AGENTS.md", raw, {})["text"] == raw.decode()


def test_non_json_yaml_and_scalar_json_are_preserved():
    assert encode_document("x.yaml", b"policy: deny", {}) == {"format": "TEXT", "text": "policy: deny"}
    value = encode_document("x.json", b'[1,true,"deny"]', {})
    assert expand_json(value, {}) == [1, True, "deny"]


def test_later_markers_belong_to_preserved_history_suffix():
    current = "# CURRENT\nDENY\n"
    archive = MARKER + "\nold\n" + MARKER + "\nolder"
    document = encode_document("docs/CURRENT_WORK.md", (current + archive).encode(), {})
    assert document["text"] == current
    assert document["history_marker_count"] == 2
    assert document["archive_text_sha256"] == digest(archive.encode())
