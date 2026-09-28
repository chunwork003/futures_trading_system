from datetime import datetime, timezone

import pytest
from pydantic import ValidationError

from persistence.broker_recovery import BrokerDiscoveryReceipt
from trading.account import BrokerAccount
from trading.broker_recovery import (
    BrokerDiscoveryError, BrokerDiscoveryIntegrity, BrokerDiscoveryRequest,
    BrokerDiscoveryScopeError, BrokerOrderDiscoveryProvider, BrokerOrderObservation,
    DiscoveryCompleteness, ExactMatchCardinality, classify_broker_discovery,
)

NOW = datetime(2026, 9, 27, 5, tzinfo=timezone.utc)
ACCOUNT = BrokerAccount(broker="SINOPAC", account_ref="A")


def request(**updates):
    values = dict(discovery_run_id="DISCOVERY-1", account=ACCOUNT, broker_client_order_ref="CLIENT-1", required_scope="ALL-FUTURES-ORDERS", horizon_start=datetime(2026, 9, 26, tzinfo=timezone.utc), horizon_end=NOW, refresh_required=True)
    values.update(updates); return BrokerDiscoveryRequest(**values)


def observation(**updates):
    values = dict(broker="SINOPAC", account_ref="A", broker_order_id="BROKER-1", broker_client_order_ref="CLIENT-1", observed_at=NOW, payload_fingerprint="FP-1")
    values.update(updates); return BrokerOrderObservation(**values)


def classify(observations=(), completeness=DiscoveryCompleteness.COMPLETE, **updates):
    values = dict(request=request(), observations=tuple(observations), completeness=completeness, refreshed_at=NOW, evidence=("verified required scope and horizon",))
    values.update(updates); return classify_broker_discovery(**values)


def test_request_and_result_are_immutable_stable_account_scoped() -> None:
    item = request(discovery_run_id="  DISCOVERY-1  ")
    result = classify((observation(),), request=item)
    assert item.discovery_run_id == result.discovery_run_id == "DISCOVERY-1"
    assert result.account == ACCOUNT
    with pytest.raises(ValidationError): result.discovery_run_id = "OTHER"


def test_wrong_account_evidence_fails_closed() -> None:
    with pytest.raises(BrokerDiscoveryScopeError, match="different account"):
        classify((observation(account_ref="B"),))


@pytest.mark.parametrize(("items", "cardinality", "integrity"), [
    ((), ExactMatchCardinality.ZERO, BrokerDiscoveryIntegrity.CONSISTENT),
    ((observation(),), ExactMatchCardinality.ONE, BrokerDiscoveryIntegrity.CONSISTENT),
    ((observation(), observation(broker_order_id="BROKER-2", payload_fingerprint="FP-2")), ExactMatchCardinality.MULTIPLE, BrokerDiscoveryIntegrity.AMBIGUOUS_EXACT_MATCH),
])
def test_exact_cardinality_and_ambiguity_are_deterministic(items, cardinality, integrity) -> None:
    result = classify(items)
    assert result.cardinality is cardinality and result.integrity is integrity


def test_matching_uses_only_exact_client_reference_not_attributes_or_time() -> None:
    similar = observation(broker_order_id="SIMILAR", broker_client_order_ref="OTHER", payload_fingerprint="SAME-QUANTITY-PRICE-TIME")
    result = classify((similar, observation()))
    assert result.cardinality is ExactMatchCardinality.ONE
    assert result.exact_matches[0].broker_order_id == "BROKER-1"


def test_incomplete_zero_is_not_absence_authority_but_retains_positive_evidence() -> None:
    incomplete_zero = classify((), completeness=DiscoveryCompleteness.INCOMPLETE)
    assert not incomplete_zero.proves_no_exact_match_in_verified_scope(unresolved_attempt_exists=False)
    positive = classify((observation(),), completeness=DiscoveryCompleteness.INCOMPLETE, refreshed_at=None, evidence=("partial page retained exact match",))
    assert positive.cardinality is ExactMatchCardinality.ONE and positive.exact_matches


def test_complete_zero_only_proves_absence_in_verified_world_and_never_overrides_attempt() -> None:
    result = classify(())
    assert result.proves_no_exact_match_in_verified_scope(unresolved_attempt_exists=False)
    assert not result.proves_no_exact_match_in_verified_scope(unresolved_attempt_exists=True)


def test_complete_discovery_requires_refresh_and_scope_horizon_evidence() -> None:
    with pytest.raises(ValidationError, match="refresh evidence"): classify((), refreshed_at=None)
    with pytest.raises(ValidationError, match="scope/horizon evidence"): classify((), evidence=())


def test_provider_contract_is_read_only_and_broker_neutral() -> None:
    class Provider:
        def discover(self, value): return classify((), request=value)
    provider = Provider()
    assert isinstance(provider, BrokerOrderDiscoveryProvider)
    assert not hasattr(provider, "submit") and not hasattr(provider, "cancel")
    assert "shioaji" not in __import__("trading.broker_recovery").broker_recovery.__dict__


def test_query_failure_is_typed_and_account_scoped() -> None:
    error = BrokerDiscoveryError(ACCOUNT, " external state unavailable ")
    assert error.broker == "SINOPAC" and error.account_ref == "A"
    assert str(error) == "external state unavailable"


def test_client_reference_is_correlation_not_idempotency_or_capability_claim() -> None:
    dumped = observation().model_dump()
    assert "idempotency" not in dumped and "shioaji" not in repr(dumped).lower()


def test_discovery_receipt_derives_fingerprint_and_binds_exact_result() -> None:
    result = classify((observation(),))
    receipt = BrokerDiscoveryReceipt(
        discovery_run_id=result.discovery_run_id, account=ACCOUNT, generation=3,
        result=result, producer_id="RECOVERY", contract_version="W4R-B1-V1",
        recorded_at=NOW,
    )
    assert receipt.result_fingerprint == BrokerDiscoveryReceipt.fingerprint(result)
    with pytest.raises(ValidationError, match="discovery_run_id"):
        BrokerDiscoveryReceipt(
            discovery_run_id="OTHER", account=ACCOUNT, generation=3, result=result,
            producer_id="RECOVERY", contract_version="W4R-B1-V1", recorded_at=NOW,
        )
