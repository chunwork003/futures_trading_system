"""資料集候選 wire 的 unknown/qualified 與 receipt 邊界；不驗證 importer runtime。"""

from copy import deepcopy

import pytest
from jsonschema import ValidationError

from test_p00_contracts import validate


REF = {"owner": "fixture", "identity": "fixture", "version": "1", "sha256": "0" * 64}
COVERAGE = {"timeframe": "1m", "start_at": "2026-01-01T00:00:00Z", "end_at": "2026-01-01T00:02:00Z",
            "contracts": [{"instrument_id": 1, "contract_id": 1}]}


def report():
    return {"schema_version": "dataset.quality.v1", "report_id": "q1", "coverage": deepcopy(COVERAGE),
            "calendar_ref": REF, "mapping_ref": REF, "quality_policy_ref": REF,
            "verdict": "QUALIFIED_RESEARCH", "counts": {"required_bars": 2, "observed_bars": 2,
            "missing_bars": 0, "duplicate_rows": 1, "conflicting_keys": 0,
            "out_of_session_keys": 0, "out_of_range_keys": 0},
            "expected_keys_hash": "1" * 64, "observed_keys_hash": "1" * 64, "reason_codes": []}


def test_qualified_report_allows_exact_duplicates_but_not_missing_bars():
    value = report()
    validate("DatasetQualityReport", value)
    value["counts"]["missing_bars"] = 1
    with pytest.raises(ValidationError):
        validate("DatasetQualityReport", value)


def test_unqualified_reference_cannot_invent_zero_counts():
    value = report()
    value.update(verdict="UNQUALIFIED_REFERENCE", counts=None, expected_keys_hash=None,
                 observed_keys_hash=None, reason_codes=["CALENDAR_COVERAGE_MISSING"])
    validate("DatasetQualityReport", value)
    value["counts"] = {k: 0 for k in report()["counts"]}
    with pytest.raises(ValidationError):
        validate("DatasetQualityReport", value)


@pytest.mark.parametrize("mutation", ["missing_coverage", "duplicate_contract", "non_minute"])
def test_import_requires_unambiguous_coverage(mutation):
    value = {"dataset_id": "d1", "source_name": "csv", "source_sha256": "0" * 64,
             "format": "CSV_V1", "coverage": deepcopy(COVERAGE), "calendar_ref": REF,
             "mapping_ref": REF, "quality_policy_ref": REF, "parent_version_id": None,
             "correction_reason": None}
    validate("ImportMetadata", value)
    if mutation == "missing_coverage":
        del value["coverage"]
    elif mutation == "duplicate_contract":
        value["coverage"]["contracts"] *= 2
    else:
        value["coverage"]["start_at"] = "2026-01-01T00:00:01Z"
    with pytest.raises(ValidationError):
        validate("ImportMetadata", value)


def test_rejected_receipt_cannot_claim_published_version():
    value = {"schema_version": "dataset.import-receipt.v1", "receipt_id": "i1", "operation_id": "op1",
             "dataset_id": "d1", "source_name": "csv", "source_sha256": "0" * 64,
             "metadata_ref": REF, "recorded_at": "2026-01-01T00:00:00Z", "outcome": "REJECTED",
             "version_id": None, "quality_report_ref": REF}
    validate("DatasetImportReceipt", value)
    value["version_id"] = "dv1"
    with pytest.raises(ValidationError):
        validate("DatasetImportReceipt", value)
