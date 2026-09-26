from datetime import datetime, timezone

import pytest
from pydantic import ValidationError

from trading.authorization import (
    AuthorizationDecision,
    AuthorizationEnvironment,
    AuthorizationIntegrityConflictError,
    ProtectedActionAuthorization,
    ProtectedActionAuthorizationError,
    require_protected_action_authorization,
)


NOW = datetime(2026, 9, 26, 3, tzinfo=timezone.utc)


def evidence(**updates):
    values=dict(authorization_id="AUTH-1", principal_id="USER-1", policy_id="POLICY-1",
                policy_version="V1", action="EXPECTED_STATE_INITIALIZE", resource="SINOPAC:A",
                protected_world_fingerprint="WORLD-1", command_id="CMD-1", correlation_id="CORR-1",
                decision=AuthorizationDecision.APPROVED, provenance="AUTH-SERVICE", authorized_at=NOW,
                environment=AuthorizationEnvironment.TEST)
    values.update(updates); return ProtectedActionAuthorization(**values)


class Provider:
    def __init__(self, item, environment=AuthorizationEnvironment.TEST):
        self.item=item; self._environment=environment; self.requested=[]
    @property
    def environment(self): return self._environment
    def verify(self, authorization_id): self.requested.append(authorization_id); return self.item


def require(provider, environment=AuthorizationEnvironment.TEST, **updates):
    values=dict(provider=provider, authorization_id="AUTH-1", environment=environment,
                action="EXPECTED_STATE_INITIALIZE", resource="SINOPAC:A",
                protected_world_fingerprint="WORLD-1", command_id="CMD-1", correlation_id="CORR-1")
    values.update(updates); return require_protected_action_authorization(**values)


def test_typed_evidence_is_immutable_normalized_and_exact() -> None:
    item=evidence(action=" expected_state_initialize ")
    assert item.action == "EXPECTED_STATE_INITIALIZE"
    with pytest.raises(ValidationError): item.action = "OTHER"
    with pytest.raises(ValidationError): evidence(extra=True)


def test_exact_trusted_evidence_is_returned_for_durable_attribution() -> None:
    item=evidence(); provider=Provider(item)
    assert require(provider) is item
    assert provider.requested == ["AUTH-1"]


@pytest.mark.parametrize("provider", [None, Provider(None)])
def test_missing_authority_or_evidence_defaults_to_deny(provider) -> None:
    with pytest.raises(ProtectedActionAuthorizationError): require(provider)


def test_test_provider_cannot_masquerade_as_production_authority() -> None:
    provider=Provider(evidence(), AuthorizationEnvironment.TEST)
    with pytest.raises(ProtectedActionAuthorizationError, match="not trusted"):
        require(provider, AuthorizationEnvironment.PRODUCTION)


def test_metadata_only_or_denied_decision_is_not_authorization() -> None:
    with pytest.raises(TypeError): require_protected_action_authorization(confirmed_by="USER")
    with pytest.raises(ProtectedActionAuthorizationError, match="denied"):
        require(Provider(evidence(decision=AuthorizationDecision.DENIED)))


@pytest.mark.parametrize(
    ("field", "value"),
    [("action", "OTHER"), ("resource", "SINOPAC:B"),
     ("protected_world_fingerprint", "WORLD-2"), ("command_id", "CMD-2"),
     ("correlation_id", "CORR-2")],
)
def test_exact_protected_world_mismatch_is_integrity_conflict(field, value) -> None:
    with pytest.raises(AuthorizationIntegrityConflictError):
        require(Provider(evidence(**{field:value})))


def test_authorization_is_not_broker_invocation_authority() -> None:
    item=require(Provider(evidence()))
    assert not hasattr(item, "submit_order")
    assert not hasattr(item, "invoke_broker")
