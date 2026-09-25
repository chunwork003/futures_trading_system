from __future__ import annotations

from enum import Enum
from typing import Protocol, runtime_checkable

from pydantic import (
    BaseModel,
    ConfigDict,
    field_validator,
    model_validator,
)

from trading.account import (
    AccountPosition,
    BrokerAccount,
    BrokerPositionProvider,
    BrokerPositionSnapshot,
)


class ReconciliationStatus(str, Enum):
    """Pairwise reconciliation 的完整、固定狀態集合。"""

    MATCH = "MATCH"
    INTERNAL_ONLY = "INTERNAL_ONLY"
    BROKER_ONLY = "BROKER_ONLY"
    CONTRACT_MISMATCH = "CONTRACT_MISMATCH"
    DIRECTION_MISMATCH = "DIRECTION_MISMATCH"
    QUANTITY_MISMATCH = "QUANTITY_MISMATCH"
    UNKNOWN_EXTERNAL_STATE = "UNKNOWN_EXTERNAL_STATE"


class PositionComparisonError(ValueError):
    """兩個 position identity 不屬於同一個可比較 pair。"""


class ReconciliationResult(BaseModel):
    """不可變的比較證據；只描述結果，不覆寫狀態或執行修正。"""

    model_config = ConfigDict(extra="forbid", frozen=True)

    status: ReconciliationStatus
    expected: AccountPosition | None
    actual: BrokerPositionSnapshot | None
    evidence: tuple[str, ...] = ()

    @field_validator("evidence", mode="before")
    @classmethod
    def normalize_evidence(cls, value: object) -> object:
        if isinstance(value, (list, tuple)):
            normalized: list[str] = []
            for item in value:
                if not isinstance(item, str):
                    normalized.append(item)
                    continue
                stripped = item.strip()
                if not stripped:
                    raise ValueError("evidence item must not be blank")
                normalized.append(stripped)
            return tuple(normalized)
        return value

    @model_validator(mode="after")
    def validate_unknown_external_state(self) -> "ReconciliationResult":
        if self.status != ReconciliationStatus.UNKNOWN_EXTERNAL_STATE:
            return self
        if not self.evidence:
            raise ValueError("UNKNOWN_EXTERNAL_STATE requires evidence")
        if self.actual is not None:
            raise ValueError("UNKNOWN_EXTERNAL_STATE actual must be None")
        return self


class ExternalStateUnknownError(RuntimeError):
    """Broker external observation 無法安全取得或 canonicalize 的明確契約。"""


class ReconciliationPolicy(str, Enum):
    """Mismatch 的處理權限；不代表自動採用或自動修復。"""

    STRICT_HALT = "STRICT_HALT"
    MANUAL_REVIEW = "MANUAL_REVIEW"
    BROKER_AUTHORITATIVE = "BROKER_AUTHORITATIVE"
    INTERNAL_AUTHORITATIVE = "INTERNAL_AUTHORITATIVE"


class ReconciliationCaseState(str, Enum):
    """人工或受控流程中的 reconciliation case lifecycle。"""

    HALT = "HALT"
    REVIEW_REQUIRED = "REVIEW_REQUIRED"
    RESOLVED = "RESOLVED"


class ReconciliationCaseError(ValueError):
    """Case 建立或狀態轉移違反 frozen reconciliation contract。"""


class ReconciliationCase(BaseModel):
    """不可變的 mismatch case；不含 persistence、broker action 或 hidden time。"""

    model_config = ConfigDict(extra="forbid", frozen=True)

    case_id: str
    result: ReconciliationResult
    policy: ReconciliationPolicy
    state: ReconciliationCaseState
    resolution_note: str | None = None

    @field_validator("case_id", mode="before")
    @classmethod
    def normalize_case_id(cls, value: object) -> object:
        if isinstance(value, str):
            normalized = value.strip()
            if not normalized:
                raise ValueError("case_id must not be blank")
            return normalized
        return value

    @field_validator("resolution_note", mode="before")
    @classmethod
    def normalize_resolution_note(cls, value: object) -> object:
        if isinstance(value, str):
            normalized = value.strip()
            if not normalized:
                raise ValueError("resolution_note must not be blank")
            return normalized
        return value

    @model_validator(mode="after")
    def validate_resolution_state(self) -> "ReconciliationCase":
        if self.state == ReconciliationCaseState.RESOLVED:
            if self.resolution_note is None:
                raise ValueError("RESOLVED case requires resolution_note")
        elif self.resolution_note is not None:
            raise ValueError(
                "HALT or REVIEW_REQUIRED case must not have resolution_note"
            )
        return self


def create_reconciliation_case(
    *,
    case_id: str,
    result: ReconciliationResult,
    policy: ReconciliationPolicy,
) -> ReconciliationCase:
    """依 policy 建立純 mismatch case；MATCH 不產生 case。"""

    if result.status == ReconciliationStatus.MATCH:
        raise ReconciliationCaseError("MATCH result cannot create a case")
    state = (
        ReconciliationCaseState.HALT
        if policy == ReconciliationPolicy.STRICT_HALT
        else ReconciliationCaseState.REVIEW_REQUIRED
    )
    return ReconciliationCase(
        case_id=case_id,
        result=result,
        policy=policy,
        state=state,
    )


def resolve_reconciliation_case(
    case: ReconciliationCase,
    *,
    resolution_note: str,
) -> ReconciliationCase:
    """以明確說明建立新的 RESOLVED case；不修改原 case 或交易狀態。"""

    if case.state == ReconciliationCaseState.RESOLVED:
        raise ReconciliationCaseError("RESOLVED case cannot be resolved again")
    normalized_note = resolution_note.strip()
    if not normalized_note:
        raise ReconciliationCaseError("resolution_note must not be blank")
    return ReconciliationCase(
        case_id=case.case_id,
        result=case.result,
        policy=case.policy,
        state=ReconciliationCaseState.RESOLVED,
        resolution_note=normalized_note,
    )


class ReconciliationCollectionError(ValueError):
    """Collection 無法依 exact identity 唯一配對，或超出指定帳戶 scope。"""


@runtime_checkable
class ExpectedPositionLoader(Protocol):
    """讀取指定 BrokerAccount 內部預期部位的唯讀 port；backend 留給 GAP-08。"""

    def load_positions(
        self,
        account: BrokerAccount,
    ) -> tuple[AccountPosition, ...]: ...


class StartupReadinessState(str, Enum):
    """Startup reconciliation 的固定 gate 結果，不負責啟動策略。"""

    READY = "READY"
    HALT = "HALT"
    REVIEW = "REVIEW"


class StartupReconciliationResult(BaseModel):
    """不可變 startup 判斷；只回報 readiness，不修復或採用任何部位。"""

    model_config = ConfigDict(extra="forbid", frozen=True)

    policy: ReconciliationPolicy
    state: StartupReadinessState
    results: tuple[ReconciliationResult, ...]
    strategy_state_ready: bool

    @model_validator(mode="after")
    def validate_ready_invariants(self) -> "StartupReconciliationResult":
        if self.state != StartupReadinessState.READY:
            return self
        if not self.strategy_state_ready:
            raise ValueError("READY requires strategy_state_ready")
        if any(
            result.status != ReconciliationStatus.MATCH
            for result in self.results
        ):
            raise ValueError("READY requires all reconciliation results to MATCH")
        return self


def _scope_key(
    position: AccountPosition | BrokerPositionSnapshot,
) -> tuple[str, str, int]:
    return (
        position.broker,
        position.account_ref,
        position.instrument_id,
    )


def _contract_sort_key(contract_id: int | None) -> tuple[int, int]:
    return (0, 0) if contract_id is None else (1, contract_id)


def _index_positions(
    positions: tuple[AccountPosition, ...]
    | tuple[BrokerPositionSnapshot, ...],
    *,
    side: str,
) -> dict[tuple[str, str, int], dict[int | None, object]]:
    indexed: dict[tuple[str, str, int], dict[int | None, object]] = {}
    for position in positions:
        scope = _scope_key(position)
        by_contract = indexed.setdefault(scope, {})
        if position.contract_id in by_contract:
            raise ReconciliationCollectionError(
                f"duplicate {side} exact position key: "
                f"{scope + (position.contract_id,)}"
            )
        by_contract[position.contract_id] = position
    return indexed


def reconcile_position_collections(
    *,
    expected_positions: tuple[AccountPosition, ...],
    actual_positions: tuple[BrokerPositionSnapshot, ...],
) -> tuple[ReconciliationResult, ...]:
    """依 scope 與 exact contract identity 決定性配對，不猜 quantity/direction。"""

    expected_index = _index_positions(expected_positions, side="expected")
    actual_index = _index_positions(actual_positions, side="actual")
    results: list[ReconciliationResult] = []

    for scope in sorted(set(expected_index) | set(actual_index)):
        expected_by_contract = expected_index.get(scope, {})
        actual_by_contract = actual_index.get(scope, {})
        exact_contracts = sorted(
            set(expected_by_contract) & set(actual_by_contract),
            key=_contract_sort_key,
        )
        for contract_id in exact_contracts:
            results.append(
                compare_positions(
                    expected_by_contract[contract_id],
                    actual_by_contract[contract_id],
                )
            )

        expected_left = sorted(
            set(expected_by_contract) - set(exact_contracts),
            key=_contract_sort_key,
        )
        actual_left = sorted(
            set(actual_by_contract) - set(exact_contracts),
            key=_contract_sort_key,
        )
        if expected_left and actual_left:
            if len(expected_left) != 1 or len(actual_left) != 1:
                raise ReconciliationCollectionError(
                    f"ambiguous unmatched collection for scope={scope}"
                )
            results.append(
                compare_positions(
                    expected_by_contract[expected_left[0]],
                    actual_by_contract[actual_left[0]],
                )
            )
        elif expected_left:
            results.extend(
                compare_positions(expected_by_contract[contract_id], None)
                for contract_id in expected_left
            )
        else:
            results.extend(
                compare_positions(None, actual_by_contract[contract_id])
                for contract_id in actual_left
            )

    return tuple(results)


def _validate_account_scope(
    *,
    account: BrokerAccount,
    positions: tuple[AccountPosition, ...]
    | tuple[BrokerPositionSnapshot, ...],
    source: str,
) -> None:
    for position in positions:
        if (
            position.broker != account.broker
            or position.account_ref != account.account_ref
        ):
            raise ReconciliationCollectionError(
                f"{source} returned position outside supplied account scope"
            )


def _startup_state(
    *,
    results: tuple[ReconciliationResult, ...],
    policy: ReconciliationPolicy,
    strategy_state_ready: bool,
) -> StartupReadinessState:
    if not strategy_state_ready:
        return StartupReadinessState.HALT
    if all(result.status == ReconciliationStatus.MATCH for result in results):
        return StartupReadinessState.READY
    if policy == ReconciliationPolicy.STRICT_HALT:
        return StartupReadinessState.HALT
    return StartupReadinessState.REVIEW


def reconcile_startup(
    *,
    account: BrokerAccount,
    expected_loader: ExpectedPositionLoader,
    broker_position_provider: BrokerPositionProvider,
    policy: ReconciliationPolicy,
    strategy_state_ready: bool,
) -> StartupReconciliationResult:
    """協調唯讀 expected/actual sources 並判斷 startup gate，不啟動或修復交易。"""

    expected_positions = expected_loader.load_positions(account)
    _validate_account_scope(
        account=account,
        positions=expected_positions,
        source="expected loader",
    )
    try:
        actual_positions = broker_position_provider.list_positions(account)
    except ExternalStateUnknownError as exc:
        evidence = str(exc).strip() or "broker external state unavailable"
        results = (
            ReconciliationResult(
                status=ReconciliationStatus.UNKNOWN_EXTERNAL_STATE,
                expected=None,
                actual=None,
                evidence=(evidence,),
            ),
        )
    else:
        _validate_account_scope(
            account=account,
            positions=actual_positions,
            source="broker position provider",
        )
        results = reconcile_position_collections(
            expected_positions=expected_positions,
            actual_positions=actual_positions,
        )

    state = _startup_state(
        results=results,
        policy=policy,
        strategy_state_ready=strategy_state_ready,
    )
    return StartupReconciliationResult(
        policy=policy,
        state=state,
        results=results,
        strategy_state_ready=strategy_state_ready,
    )


def compare_positions(
    expected: AccountPosition | None,
    actual: BrokerPositionSnapshot | None,
) -> ReconciliationResult:
    """依固定 precedence 比較一組 expected / actual position。"""

    if expected is None and actual is None:
        status = ReconciliationStatus.MATCH
    elif expected is not None and actual is None:
        status = ReconciliationStatus.INTERNAL_ONLY
    elif expected is None:
        status = ReconciliationStatus.BROKER_ONLY
    else:
        identity_expected = (
            expected.broker,
            expected.account_ref,
            expected.instrument_id,
        )
        identity_actual = (
            actual.broker,
            actual.account_ref,
            actual.instrument_id,
        )
        if identity_expected != identity_actual:
            raise PositionComparisonError(
                "expected and actual positions do not share broker/account/instrument identity"
            )
        if expected.contract_id != actual.contract_id:
            status = ReconciliationStatus.CONTRACT_MISMATCH
        elif expected.direction != actual.direction:
            status = ReconciliationStatus.DIRECTION_MISMATCH
        elif expected.quantity != actual.quantity:
            status = ReconciliationStatus.QUANTITY_MISMATCH
        else:
            status = ReconciliationStatus.MATCH

    return ReconciliationResult(status=status, expected=expected, actual=actual)
