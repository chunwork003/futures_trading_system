"""Literal framing vectors 與既有 canonical observation 的相容驗證；非 importer。"""

from copy import deepcopy
from datetime import date, datetime
import hashlib
import json
from pathlib import Path

import pytest

from domain.market_observation import (
    canonicalize_market_observation_logical_key,
    canonicalize_market_observation_content,
    build_market_observation_revision_id,
)

FIXTURE = json.loads((Path(__file__).resolve().parents[2] /
    "docs/architecture/contracts/dataset_identity.fixture.v1.json").read_text(encoding="utf-8"))


def frame(tag, values):
    output = bytearray(tag.encode("ascii"))
    output.append(10)
    for value in values:
        encoded = value.encode("utf-8")
        output.extend(str(len(encoded)).encode("ascii"))
        output.append(58)
        output.extend(encoded)
        output.append(10)
    return bytes(output)


def check(tag, values, expected):
    actual = frame(tag, values)
    assert actual == expected["frame_utf8"].encode("utf-8")
    assert hashlib.sha256(actual).hexdigest() == expected["sha256"]


def normalized_rows(rows):
    distinct = {}
    for row in rows:
        key = tuple(row["key"])
        if key in distinct and distinct[key]["revision_id"] != row["revision_id"]:
            raise ValueError("CONFLICTING_CONTENT")
        distinct[key] = row
    return sorted(distinct.values(), key=lambda r: (int(r["key"][0]), int(r["key"][1]),
                  r["key"][2].encode(), r["key"][3]))


def test_literal_rows_reuse_accepted_observation_identity():
    for row in FIXTURE["rows"]:
        parts = row["key"]
        key = canonicalize_market_observation_logical_key(instrument_id=int(parts[0]),
            contract_id=int(parts[1]), timeframe=parts[2], interval_start_at=datetime.fromisoformat(parts[3]),
            requires_contract_id=True)
        content = canonicalize_market_observation_content(**{**row["content"],
            "trade_date": date.fromisoformat(row["content"]["trade_date"])})
        assert key.interval_start_at_lexical == parts[3]
        assert build_market_observation_revision_id(logical_key=key,
            content_fingerprint=content.content_fingerprint).value == row["revision_id"]


def test_content_and_key_literals_ignore_order_and_exact_duplicates():
    rows = normalized_rows(list(reversed(FIXTURE["rows"])) + [FIXTURE["rows"][0]])
    check("dataset-keys-v1", [str(len(rows))] + [p for r in rows for p in r["key"]], FIXTURE["expected_keys"])
    check("dataset-content-v1", [str(len(rows))] + [p for r in rows for p in r["key"] + [r["revision_id"]]], FIXTURE["content"])


def test_conflicting_key_has_no_file_order_winner():
    changed = deepcopy(FIXTURE["rows"][0])
    changed["revision_id"] = "mor1_" + "0" * 64
    for rows in [[changed, FIXTURE["rows"][0]], [FIXTURE["rows"][0], changed]]:
        with pytest.raises(ValueError, match="CONFLICTING_CONTENT"):
            normalized_rows(rows)


def test_version_parent_and_reference_changes_are_not_content_identity():
    fields = FIXTURE["root_version_fields"]
    assert fields[1:3] == [FIXTURE["content"]["sha256"], FIXTURE["expected_keys"]["sha256"]]
    check("dataset-version-v1", fields, FIXTURE["root_version"])
    check("dataset-version-v1", FIXTURE["child_same_content_fields"], FIXTURE["child_same_content"])
    assert FIXTURE["root_version"]["sha256"] != FIXTURE["child_same_content"]["sha256"]
    changed = list(fields)
    changed[12] = "d" * 64  # calendar reference hash
    assert hashlib.sha256(frame("dataset-version-v1", changed)).hexdigest() != FIXTURE["root_version"]["sha256"]


def test_utf8_byte_lengths_and_null_parent_are_unambiguous():
    check("dataset-frame-test-v1", ["台灣", "", ":\n"], FIXTURE["unicode_frame"])
    assert frame("x", ["ab", "c"]) != frame("x", ["a", "bc"])
    assert frame("x", [""]) != frame("x", ["null"])
