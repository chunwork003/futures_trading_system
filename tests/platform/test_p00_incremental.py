"""EMA codec 候選 golden contract；測試內 reference 不接入產品 runtime。"""

import json
import math
from pathlib import Path

import polars as pl
import pytest
from jsonschema import Draft202012Validator, ValidationError

from features.rolling import ema

ROOT = Path(__file__).resolve().parents[2]
FIXTURE = json.loads((ROOT / "docs/architecture/contracts/ema_close.fixture.v1.json").read_text(encoding="utf-8"))
SPEC = json.loads((ROOT / "docs/architecture/contracts/python.openapi.v1.json").read_text(encoding="utf-8"))


def validate(state):
    Draft202012Validator({"$ref": "#/components/schemas/EmaIncrementalCodec", "components": SPEC["components"]}).validate(state)


def state(count=0, value=None):
    return {"codec_version": "ema_close.v1", "span": 3, "processed_count": count,
        "ema_hex": value.hex() if value is not None else None,
        "last_observation_revision_id": "mor1_" + f"{count:064x}" if count else None,
        "governing_config_fingerprint": "0" * 64}


def test_literal_golden_fixture_matches_existing_batch():
    values = ema(pl.DataFrame({"close": [float(x) for x in FIXTURE["closes"]]}), FIXTURE["span"])["ema_3"].to_list()
    for actual, expected in zip(values, FIXTURE["expected_outputs"], strict=True):
        if expected is None:
            assert actual is None
        else:
            assert actual == pytest.approx(expected, rel=1e-12, abs=1e-12)


@pytest.mark.parametrize("restart_after", range(6))
def test_hex_checkpoint_roundtrip_at_every_golden_boundary(restart_after):
    previous = None
    alpha = 2 / (FIXTURE["span"] + 1)
    for index, close in enumerate(FIXTURE["closes"]):
        if index == restart_after:
            checkpoint = json.loads(json.dumps(state(index, previous)))
            validate(checkpoint)
            previous = float.fromhex(checkpoint["ema_hex"]) if checkpoint["ema_hex"] else None
        previous = float(close) if previous is None else (1 - alpha) * previous + alpha * close
        assert previous == FIXTURE["expected_states"][index]
    checkpoint = state(5, previous)
    validate(checkpoint)
    assert float.fromhex(checkpoint["ema_hex"]) == previous


@pytest.mark.parametrize("patch", [{"processed_count": 1}, {"ema_hex": "nan"}, {"ema_hex": "inf"},
    {"span": 0}, {"span": 1001}, {"codec_version": "unknown"}, {"last_observation_revision_id": "last-bar"}])
def test_invalid_codec_cannot_look_like_fresh_state(patch):
    value = state()
    value.update(patch)
    with pytest.raises(ValidationError):
        validate(value)


@pytest.mark.parametrize("span", [1, 20, 60])
def test_recurrence_matches_batch_across_nontrivial_streams(span):
    closes = [100.0 + ((i * 7) % 31) / 8 for i in range(160)]
    expected = ema(pl.DataFrame({"close": closes}), span)[f"ema_{span}"].to_list()
    previous = None
    alpha = 2 / (span + 1)
    for index, close in enumerate(closes):
        previous = close if previous is None else (1 - alpha) * previous + alpha * close
        # 任意分割點均可持久化為 hex，不允許 decimal roundtrip 改掉 state。
        if index % 13 == 0:
            previous = float.fromhex(previous.hex())
        if index + 1 < span:
            assert expected[index] is None
        else:
            assert math.isclose(previous, expected[index], rel_tol=1e-12, abs_tol=1e-12)
