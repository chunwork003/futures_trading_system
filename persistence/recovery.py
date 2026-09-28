
from __future__ import annotations

import hashlib
import json
from enum import Enum
from typing import (
    Protocol,
    runtime_checkable,
)

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    field_validator,
    model_validator,
)
from adapters.capabilities import (
    BrokerCapability, BrokerCapabilityEvidence, BrokerCapabilityProvider,
    BrokerCapabilityRegistrySnapshot, BrokerCapabilityUnavailableError,
    BrokerVerificationMode, require_broker_capability,
)
from persistence.account import BrokerPositionObservationRepository, ExpectedPositionSnapshotRepository
from persistence.broker_action import BrokerActionRepository

from persistence.account_authority import (
    AccountAuthorityCommitReceipt,
    AccountRecoveryCheckpoint,
    AccountStateHead,
    validate_authority_closure,
)

from persistence.reconciliation import (
    ReconciliationCaseRepository,
    ReconciliationInputQualification,
    ReconciliationRunBoundary,
    ReconciliationRunOutcome,
    ReconciliationRunTechnicalOutcome,
    blocking_case_state,
    reconciliation_blocker_semantic_fingerprint,
)
from persistence.broker_recovery import BrokerDiscoveryReceipt, BrokerReconstructionReceipt, BrokerRecoveryRepository, BrokerReportInboxEntry, ExecutionContinuityEpoch
from persistence.contracts import normalize_stable_id
from persistence.events import EventLedgerRepository
from persistence.execution import FillRepository, OrderRepository
from persistence.strategy_state import (
    LegacyMarketObservationReferenceError,
    StrategyInstanceRepository,
    StrategyStateReferenceConflictError,
    StrategyStateRepository,
    normalize_market_observation_revision_id,
)
from strategy.registry import (
    StrategyRegistry,
)
from strategy.state import (
    StatefulStrategy,
)
from trading.account import (
    BrokerAccount,
    BrokerPositionProvider,
)
from trading.broker_recovery import BrokerDiscoveryIntegrity, BrokerDiscoveryResult, DiscoveryCompleteness
from trading.reconciliation import (
    ExpectedPositionLoader,
    ReconciliationCaseState,
    ReconciliationPolicy,
    StartupReadinessState,
    reconcile_startup,
    ReconciliationStatus,
)
from trading.execution import (
    TERMINAL_ORDER_STATUSES,
    Fill,
    Order,
    OrderEvent,
    validate_order_event_transition,
)


class RecoveryReadinessState(
    str,
    Enum,
):
    READY = "READY"
    HALT = "HALT"
    REVIEW = "REVIEW"


class TrustedRecoveryEvidenceError(RuntimeError):
    """B2 exact evidence 缺失、stale 或 capability 不足時的 fail-closed resolver 錯誤。"""


class TrustedReconciliationBlockerEvidence(BaseModel):
    """C13 repository 語意的 immutable witness；供後續 gate 重驗，不授予 READY。"""

    model_config=ConfigDict(extra="forbid",frozen=True)
    account: BrokerAccount
    blocking_state: ReconciliationCaseState | None
    unresolved_case_ids: tuple[str,...]
    semantic_fingerprint: str


class TrustedReconciliationBlockerResolver:
    """直接委派 C13 unresolved/blocking owner；不複製 SQL、也不執行 handoff。"""

    def __init__(self, repository: ReconciliationCaseRepository) -> None:
        self._repository=repository

    def resolve(self, *, account: BrokerAccount) -> TrustedReconciliationBlockerEvidence:
        versions=tuple(sorted(self._repository.unresolved(account),key=lambda item:item.case_id))
        if any(item.reconciliation_case.account != account for item in versions):
            raise TrustedRecoveryEvidenceError("unresolved reconciliation case account mismatch")
        if any(item.reconciliation_case.state is ReconciliationCaseState.RESOLVED for item in versions):
            raise TrustedRecoveryEvidenceError("resolved reconciliation case returned as unresolved")
        return TrustedReconciliationBlockerEvidence(
            account=account,
            blocking_state=blocking_case_state(versions),
            unresolved_case_ids=tuple(item.case_id for item in versions),
            semantic_fingerprint=reconciliation_blocker_semantic_fingerprint(versions),
        )


class RecoveryRootSource(str,Enum):
    """C2A minimum recovery root 的 exact durable source category。"""
    BROKER_ACTION_NONTERMINAL="BROKER_ACTION_NONTERMINAL"
    BROKER_ACTION_UNRESOLVED="BROKER_ACTION_UNRESOLVED"
    RECONSTRUCTION_RECEIPT="RECONSTRUCTION_RECEIPT"
    EXPECTED_SNAPSHOT_SOURCE_EVENT="EXPECTED_SNAPSHOT_SOURCE_EVENT"
    BROKER_REPORT_EXACT_ORDER="BROKER_REPORT_EXACT_ORDER"


class RecoveryOrderRoot(BaseModel):
    """單一 Order root 及其全部 deterministic provenance categories。"""
    model_config=ConfigDict(extra="forbid",frozen=True)
    order_id: str
    sources: tuple[RecoveryRootSource,...]

    @field_validator("order_id",mode="before")
    @classmethod
    def _order_id(cls,value: object) -> object:
        return normalize_stable_id(value) if isinstance(value,str) else value

    @model_validator(mode="after")
    def _sources(self) -> "RecoveryOrderRoot":
        order={item:index for index,item in enumerate(RecoveryRootSource)}
        normalized=tuple(sorted(set(self.sources),key=order.__getitem__))
        if not normalized: raise ValueError("recovery order root requires source")
        object.__setattr__(self,"sources",normalized)
        return self


class RecoveryRootSetEvidence(BaseModel):
    """Resolver-produced immutable minimum root set；不代表 READY、finalize 或 handoff。"""
    model_config=ConfigDict(extra="forbid",frozen=True)
    account: BrokerAccount
    recovery_generation: int = Field(ge=1)
    roots: tuple[RecoveryOrderRoot,...]
    order_ids: tuple[str,...]
    ambiguous_report_ingress_ids: tuple[str,...]
    root_set_fingerprint: str = ""

    @model_validator(mode="after")
    def _canonical(self) -> "RecoveryRootSetEvidence":
        roots=tuple(sorted(self.roots,key=lambda item:item.order_id))
        if len({item.order_id for item in roots}) != len(roots): raise ValueError("duplicate recovery root")
        order_ids=tuple(item.order_id for item in roots)
        ambiguous=tuple(sorted(set(self.ambiguous_report_ingress_ids)))
        material={"account":self.account.model_dump(mode="json"),"recovery_generation":self.recovery_generation,"roots":[item.model_dump(mode="json") for item in roots],"ambiguous_report_ingress_ids":list(ambiguous)}
        encoded=json.dumps(material,sort_keys=True,separators=(",",":"),ensure_ascii=False)
        fingerprint=hashlib.sha256(encoded.encode("utf-8")).hexdigest()
        object.__setattr__(self,"roots",roots); object.__setattr__(self,"order_ids",order_ids)
        object.__setattr__(self,"ambiguous_report_ingress_ids",ambiguous); object.__setattr__(self,"root_set_fingerprint",fingerprint)
        return self


class RecoveryRootIntegrityError(RuntimeError):
    """Minimum root evidence 缺失、跨 account/world 或 identity 不一致時 fail closed。"""


class RecoveryRootResolver:
    """由 exact durable owners 組合 minimum roots；不掃描全域 history，也不授予 READY。"""
    def __init__(self,*,broker_action_repository: BrokerActionRepository,order_repository: OrderRepository,broker_recovery_repository: BrokerRecoveryRepository,expected_snapshot_repository: ExpectedPositionSnapshotRepository,event_ledger_repository: EventLedgerRepository) -> None:
        self._actions=broker_action_repository; self._orders=order_repository
        self._recovery=broker_recovery_repository; self._expected=expected_snapshot_repository
        self._events=event_ledger_repository

    def resolve(self,*,trusted_core: TrustedRecoveryEvidenceCore,material_report_entries: tuple[BrokerReportInboxEntry,...]) -> RecoveryRootSetEvidence:
        account=trusted_core.account; generation=trusted_core.recovery_generation
        sources: dict[str,set[RecoveryRootSource]]={}
        def add(order_id: str,source: RecoveryRootSource) -> None:
            sources.setdefault(normalize_stable_id(order_id),set()).add(source)
        for head in self._actions.list_heads(account):
            if (head.broker,head.account_ref)!=(account.broker,account.account_ref): raise RecoveryRootIntegrityError("broker action head account mismatch")
            order=self._orders.get(head.order_id)
            if order is None: raise RecoveryRootIntegrityError("broker action head references missing Order")
            if order.order_id!=head.order_id: raise RecoveryRootIntegrityError("broker action Order identity mismatch")
            if order.status not in TERMINAL_ORDER_STATUSES: add(order.order_id,RecoveryRootSource.BROKER_ACTION_NONTERMINAL)
            if head.unresolved_attempt_id is not None: add(order.order_id,RecoveryRootSource.BROKER_ACTION_UNRESOLVED)
        if len(trusted_core.reconstruction_receipt_ids)!=len(trusted_core.reconstruction_receipt_fingerprints): raise RecoveryRootIntegrityError("reconstruction receipt binding length mismatch")
        for receipt_id,fingerprint in zip(trusted_core.reconstruction_receipt_ids,trusted_core.reconstruction_receipt_fingerprints,strict=True):
            receipt=self._recovery.get_reconstruction_receipt(reconstruction_receipt_id=receipt_id,account=account)
            if receipt is None: raise RecoveryRootIntegrityError("reconstruction receipt is missing")
            receipt=BrokerReconstructionReceipt.model_validate(receipt.model_dump(mode="json"))
            if receipt.reconstruction_receipt_id!=receipt_id or receipt.account!=account or receipt.generation!=generation or receipt.full_receipt_fingerprint!=fingerprint: raise RecoveryRootIntegrityError("reconstruction receipt binding mismatch")
            add(receipt.order_id,RecoveryRootSource.RECONSTRUCTION_RECEIPT)
        snapshot=self._expected.get_exact(snapshot_id=trusted_core.expected_snapshot_id,broker=account.broker,account_ref=account.account_ref)
        if snapshot is None: raise RecoveryRootIntegrityError("expected snapshot is missing")
        if snapshot.snapshot_id!=trusted_core.expected_snapshot_id or (snapshot.broker,snapshot.account_ref)!=(account.broker,account.account_ref): raise RecoveryRootIntegrityError("expected snapshot identity or account mismatch")
        event=self._events.get(snapshot.source_event_id)
        if event is None: raise RecoveryRootIntegrityError("expected snapshot source event is missing")
        if event.event_id!=snapshot.source_event_id: raise RecoveryRootIntegrityError("expected snapshot source event identity mismatch")
        if event.entity_type!="ORDER": raise RecoveryRootIntegrityError("expected snapshot source event is not ORDER")
        add(event.entity_id,RecoveryRootSource.EXPECTED_SNAPSHOT_SOURCE_EVENT)
        ambiguous=[]
        for entry in material_report_entries:
            if (entry.broker,entry.account_ref,entry.generation)!=(account.broker,account.account_ref,generation): raise RecoveryRootIntegrityError("material report world mismatch")
            if "order_id" not in entry.payload_json: ambiguous.append(entry.ingress_id); continue
            order_id=entry.payload_json["order_id"]
            if not isinstance(order_id,str): raise RecoveryRootIntegrityError("material report order_id is malformed")
            try: add(order_id,RecoveryRootSource.BROKER_REPORT_EXACT_ORDER)
            except ValueError as exc: raise RecoveryRootIntegrityError("material report order_id is malformed") from exc
        roots=tuple(RecoveryOrderRoot(order_id=order_id,sources=tuple(categories)) for order_id,categories in sources.items())
        return RecoveryRootSetEvidence(account=account,recovery_generation=generation,roots=roots,order_ids=(),ambiguous_report_ingress_ids=tuple(ambiguous))


class RecoveryRootClosureEvidence(BaseModel):
    """單一 recovery root 的完整 Order/Event/Fill closure；只證明本機證據完整性。"""

    model_config=ConfigDict(extra="forbid",frozen=True)
    order_id: str
    order_fingerprint: str
    event_ids: tuple[str,...]
    fill_ids: tuple[str,...]
    closure_fingerprint: str


class RecoveryClosureEvidence(BaseModel):
    """C2B immutable exact closure；供後續 gate 使用，但不授予 READY 或 handoff。"""

    model_config=ConfigDict(extra="forbid",frozen=True)
    account: BrokerAccount
    recovery_generation: int = Field(ge=1)
    root_set_fingerprint: str
    roots: tuple[RecoveryRootClosureEvidence,...]
    order_ids: tuple[str,...]
    ambiguous_report_ingress_ids: tuple[str,...]
    closure_fingerprint: str


class RecoveryClosureIntegrityError(RuntimeError):
    """Order/Event/Fill exact closure 缺失、矛盾或 lifecycle 非法時的 fail-closed 錯誤。"""


def _canonical_fingerprint(value: object) -> str:
    encoded=json.dumps(value,sort_keys=True,separators=(",",":"),ensure_ascii=False,allow_nan=False)
    return hashlib.sha256(encoded.encode("utf-8")).hexdigest()


class RecoveryClosureResolver:
    """以既有 exact read ports 重建每個 C2A root；不掃描全域 history、不修改經濟權威。"""

    def __init__(self,*,order_repository: OrderRepository,fill_repository: FillRepository,event_ledger_repository: EventLedgerRepository) -> None:
        self._orders=order_repository
        self._fills=fill_repository
        self._events=event_ledger_repository

    @staticmethod
    def _decode_event(envelope) -> OrderEvent:
        if (envelope.event_type,envelope.source,envelope.entity_type)!=("ORDER_STATUS_CHANGED","OMS","ORDER"):
            raise RecoveryClosureIntegrityError("ORDER event envelope mismatch")
        if envelope.idempotency_scope != f"ORDER_EVENT:{envelope.entity_id}":
            raise RecoveryClosureIntegrityError("ORDER event idempotency scope mismatch")
        payload=envelope.payload_json
        try:
            return OrderEvent(
                event_id=envelope.event_id,order_id=envelope.entity_id,
                correlation_id=envelope.correlation_id,causation_id=envelope.causation_id,
                idempotency_key=envelope.idempotency_key,sequence=envelope.sequence,
                previous_status=payload["previous_status"],status=payload["status"],
                occurred_at=envelope.occurred_at,received_at=envelope.received_at,
                broker_order_id=payload["broker_order_id"],provenance=payload["provenance"],
                payload_json=payload["payload"],
            )
        except (KeyError,TypeError,ValueError) as exc:
            raise RecoveryClosureIntegrityError("malformed canonical ORDER event payload") from exc

    def _resolve_root(self,order_id: str) -> RecoveryRootClosureEvidence:
        order=self._orders.get(order_id)
        if order is None:
            raise RecoveryClosureIntegrityError("root Order is missing")
        if order.order_id != order_id:
            raise RecoveryClosureIntegrityError("root Order identity mismatch")

        envelopes=tuple(self._events.list_after("OMS","ORDER",order_id,-1,order.version+2))
        if len({item.event_id for item in envelopes}) != len(envelopes):
            raise RecoveryClosureIntegrityError("duplicate ORDER event identity")
        if len({item.sequence for item in envelopes}) != len(envelopes):
            raise RecoveryClosureIntegrityError("duplicate ORDER event sequence")
        envelopes=tuple(sorted(envelopes,key=lambda item:item.sequence))
        if tuple(item.sequence for item in envelopes) != tuple(range(order.version+1)):
            raise RecoveryClosureIntegrityError("ORDER event sequence is incomplete or exceeds projection version")
        events=[]
        previous=None
        for envelope in envelopes:
            if envelope.entity_id != order_id:
                raise RecoveryClosureIntegrityError("ORDER event envelope entity mismatch")
            event=self._decode_event(envelope)
            try:
                validate_order_event_transition(previous,event)
            except ValueError as exc:
                raise RecoveryClosureIntegrityError("illegal ORDER lifecycle transition") from exc
            events.append(event); previous=event
        if previous is None:
            raise RecoveryClosureIntegrityError("ORDER event sequence is missing")
        if (previous.sequence,previous.status,previous.correlation_id,previous.order_id)!=(order.version,order.status,order.correlation_id,order_id):
            raise RecoveryClosureIntegrityError("final ORDER event does not match projection")

        fills=tuple(self._fills.list_by_order(order_id))
        if len({item.fill_id for item in fills}) != len(fills):
            raise RecoveryClosureIntegrityError("duplicate Fill identity")
        fills=tuple(sorted(fills,key=lambda item:item.fill_id))
        event_ids={item.event_id for item in events}
        for fill in fills:
            if fill.order_id != order_id:
                raise RecoveryClosureIntegrityError("Fill order identity mismatch")
            if fill.event_id not in event_ids:
                raise RecoveryClosureIntegrityError("Fill event is outside exact ORDER sequence")
            if fill.correlation_id != order.correlation_id:
                raise RecoveryClosureIntegrityError("Fill correlation mismatch")
            if fill.causation_id != fill.event_id:
                raise RecoveryClosureIntegrityError("Fill causation mismatch")
        quantity=sum((item.quantity for item in fills),0)
        if order.filled_quantity != quantity:
            raise RecoveryClosureIntegrityError("Order and Fill economic quantity mismatch")
        if not fills:
            if order.average_fill_price is not None:
                raise RecoveryClosureIntegrityError("zero Fill economic closure requires no average price")
        else:
            average=sum((item.price*item.quantity for item in fills),start=0)/quantity
            if order.average_fill_price is None or order.average_fill_price != average:
                raise RecoveryClosureIntegrityError("Order average fill price mismatch")

        order_material=order.model_dump(mode="json")
        event_material=[item.model_dump(mode="json") for item in envelopes]
        fill_material=[item.model_dump(mode="json") for item in fills]
        closure_material={"order":order_material,"events":event_material,"fills":fill_material}
        return RecoveryRootClosureEvidence(
            order_id=order_id,order_fingerprint=_canonical_fingerprint(order_material),
            event_ids=tuple(item.event_id for item in envelopes),fill_ids=tuple(item.fill_id for item in fills),
            closure_fingerprint=_canonical_fingerprint(closure_material),
        )

    def resolve(self,*,root_set: RecoveryRootSetEvidence) -> RecoveryClosureEvidence:
        """解析 immutable C2A root set；caller 無法另行注入 root 或 fingerprint。"""
        canonical=RecoveryRootSetEvidence.model_validate(root_set.model_dump(mode="json"))
        if canonical != root_set or canonical.order_ids != tuple(item.order_id for item in canonical.roots):
            raise RecoveryClosureIntegrityError("non-canonical recovery root set")
        closures=tuple(self._resolve_root(item.order_id) for item in canonical.roots)
        material={
            "account":canonical.account.model_dump(mode="json"),
            "recovery_generation":canonical.recovery_generation,
            "root_set_fingerprint":canonical.root_set_fingerprint,
            "roots":[item.model_dump(mode="json") for item in closures],
            "ambiguous_report_ingress_ids":list(canonical.ambiguous_report_ingress_ids),
        }
        return RecoveryClosureEvidence(
            account=canonical.account,recovery_generation=canonical.recovery_generation,
            root_set_fingerprint=canonical.root_set_fingerprint,roots=closures,
            order_ids=canonical.order_ids,ambiguous_report_ingress_ids=canonical.ambiguous_report_ingress_ids,
            closure_fingerprint=_canonical_fingerprint(material),
        )


class TrustedRecoveryEvidenceCore(BaseModel):
    """B2 resolver 產生的 immutable core；保留 exact provenance，但不表示 C15 READY 或 handoff。"""
    model_config=ConfigDict(extra="forbid",frozen=True)
    account: BrokerAccount
    recovery_generation: int = Field(ge=1)
    recovery_cut_fingerprint: str
    discovery_receipt_id: str
    discovery_result_fingerprint: str
    discovery_receipt_fingerprint: str
    reconstruction_receipt_ids: tuple[str,...]
    reconstruction_output_fingerprints: tuple[str,...]
    reconstruction_receipt_fingerprints: tuple[str,...]
    expected_snapshot_id: str
    broker_observation_id: str
    capability_registry_id: str
    capability_contract_version: str
    capability_matrix_fingerprint: str
    required_verification_mode: BrokerVerificationMode
    capability_evidence: tuple[BrokerCapabilityEvidence,...]
    capability_source_ids: tuple[str,...]


class TrustedRecoveryEvidenceResolver:
    """以 exact IDs 重讀 B1/account/capability 證據；不評估 READY、不 finalize、無 broker I/O。"""
    def __init__(self, *, broker_recovery_repository: BrokerRecoveryRepository, expected_snapshot_repository: ExpectedPositionSnapshotRepository, broker_observation_repository: BrokerPositionObservationRepository, capability_provider: BrokerCapabilityProvider) -> None:
        self._recovery=broker_recovery_repository
        self._expected=expected_snapshot_repository
        self._actual=broker_observation_repository
        self._capabilities=capability_provider

    def resolve(self, *, account: BrokerAccount, recovery_generation: int, recovery_cut_fingerprint: str, discovery_run_id: str, reconstruction_receipt_ids: tuple[str,...], expected_snapshot_id: str, broker_observation_id: str, required_capabilities: tuple[BrokerCapability,...], required_verification_mode: BrokerVerificationMode) -> TrustedRecoveryEvidenceCore:
        try:
            discovery=self._recovery.get_discovery_receipt(discovery_run_id=discovery_run_id,account=account)
            if discovery is None: raise TrustedRecoveryEvidenceError("exact discovery receipt is missing")
            discovery=BrokerDiscoveryReceipt.model_validate(discovery.model_dump(mode="json"))
            if discovery.account != account or discovery.generation != recovery_generation or discovery.discovery_run_id != discovery_run_id:
                raise TrustedRecoveryEvidenceError("discovery receipt scope or generation mismatch")
            normalized_receipt_ids=tuple(normalize_stable_id(item) for item in reconstruction_receipt_ids)
            if len(set(normalized_receipt_ids)) != len(normalized_receipt_ids):
                raise TrustedRecoveryEvidenceError("duplicate reconstruction receipt ID")
            normalized_receipt_ids=tuple(sorted(normalized_receipt_ids))
            reconstructions=[]
            for receipt_id in normalized_receipt_ids:
                receipt=self._recovery.get_reconstruction_receipt(reconstruction_receipt_id=receipt_id,account=account)
                if receipt is None: raise TrustedRecoveryEvidenceError("required positive reconstruction receipt is missing")
                receipt=BrokerReconstructionReceipt.model_validate(receipt.model_dump(mode="json"))
                if receipt.account != account or receipt.generation != recovery_generation:
                    raise TrustedRecoveryEvidenceError("reconstruction receipt scope or generation mismatch")
                if receipt.recovery_cut_fingerprint != recovery_cut_fingerprint:
                    raise TrustedRecoveryEvidenceError("reconstruction receipt recovery cut mismatch")
                if receipt.discovery_run_id != discovery_run_id:
                    raise TrustedRecoveryEvidenceError("reconstruction receipt discovery mismatch")
                reconstructions.append(receipt)
            expected=self._expected.get_exact(snapshot_id=expected_snapshot_id,broker=account.broker,account_ref=account.account_ref)
            if expected is None or expected.snapshot_id != expected_snapshot_id or (expected.broker,expected.account_ref)!=(account.broker,account.account_ref):
                raise TrustedRecoveryEvidenceError("exact expected snapshot is missing or mismatched")
            actual=self._actual.get_exact(observation_id=broker_observation_id,broker=account.broker,account_ref=account.account_ref)
            if actual is None or actual.observation_id != broker_observation_id or (actual.broker,actual.account_ref)!=(account.broker,account.account_ref):
                raise TrustedRecoveryEvidenceError("exact broker observation is missing or mismatched")
            registry=self._capabilities.get_snapshot(account.broker)
            if registry is None: raise TrustedRecoveryEvidenceError("trusted capability registry is missing")
            registry=BrokerCapabilityRegistrySnapshot.model_validate(registry.model_dump(mode="json"))
            if registry.broker != account.broker: raise TrustedRecoveryEvidenceError("capability registry broker mismatch")
            order={capability:index for index,capability in enumerate(BrokerCapability)}
            required=tuple(sorted(set(required_capabilities),key=order.__getitem__))
            evidence=tuple(require_broker_capability(registry.matrix,item,required_mode=required_verification_mode) for item in required)
        except BrokerCapabilityUnavailableError as exc:
            raise TrustedRecoveryEvidenceError(str(exc)) from exc
        source_ids=tuple(sorted({source for item in evidence for source in item.source_ids}))
        return TrustedRecoveryEvidenceCore(account=account,recovery_generation=recovery_generation,recovery_cut_fingerprint=normalize_stable_id(recovery_cut_fingerprint),discovery_receipt_id=discovery.discovery_run_id,discovery_result_fingerprint=discovery.result_fingerprint,discovery_receipt_fingerprint=discovery.full_receipt_fingerprint,reconstruction_receipt_ids=tuple(item.reconstruction_receipt_id for item in reconstructions),reconstruction_output_fingerprints=tuple(item.output_fingerprint for item in reconstructions),reconstruction_receipt_fingerprints=tuple(item.full_receipt_fingerprint for item in reconstructions),expected_snapshot_id=expected.snapshot_id,broker_observation_id=actual.observation_id,capability_registry_id=registry.registry_id,capability_contract_version=registry.contract_version,capability_matrix_fingerprint=registry.matrix_fingerprint,required_verification_mode=required_verification_mode,capability_evidence=evidence,capability_source_ids=source_ids)


class ExecutionRestoreStatus(str, Enum):
    """C12 local restore outcome；VALID 只代表 coherent local cut，不代表 READY。"""

    VALID = "VALID"
    BASELINE_NOT_ESTABLISHED = "BASELINE_NOT_ESTABLISHED"
    RESTORE_FAILURE = "RESTORE_FAILURE"


class RecoveryCut(BaseModel):
    """BrokerAccount-local immutable cut；封裝經濟 revision 與非 revision currentness witness。"""

    model_config = ConfigDict(extra="forbid", frozen=True)

    account: BrokerAccount
    head: AccountStateHead
    checkpoint: AccountRecoveryCheckpoint
    receipt: AccountAuthorityCommitReceipt
    recovery_generation: int | None = Field(default=None, ge=1)
    recovery_ingress_version: int | None = Field(default=None, ge=0)
    inbox_count: int = Field(ge=0)
    application_count: int = Field(ge=0)
    broker_report_witness: tuple[str, ...] = ()
    current_nonterminal_order_anchors: tuple[str, ...] = ()
    fill_event_validation_anchors: tuple[str, ...] = ()
    continuity_epoch_witness: tuple[str, ...] = ()
    sequence_gap_witness: tuple[str, ...] = ()
    reconciliation_currentness_witness: tuple[str, ...] = ()
    unresolved_broker_action_ids: tuple[str, ...] = ()

    @model_validator(mode="after")
    def _closure(self) -> "RecoveryCut":
        scope=(self.account.broker,self.account.account_ref)
        if scope != (self.head.broker,self.head.account_ref):
            raise ValueError("recovery cut account scope mismatch")
        validate_authority_closure(
            head=self.head,
            checkpoint=self.checkpoint,
            receipt=self.receipt,
        )
        if self.head.current_revision != self.checkpoint.account_revision:
            raise ValueError("RecoveryCut requires exact head revision closure")
        if (self.recovery_generation is None) != (self.recovery_ingress_version is None):
            raise ValueError("recovery control witness must be complete")
        for name in (
            "broker_report_witness",
            "current_nonterminal_order_anchors",
            "fill_event_validation_anchors",
            "continuity_epoch_witness",
            "sequence_gap_witness",
            "reconciliation_currentness_witness",
            "unresolved_broker_action_ids",
        ):
            values=getattr(self,name)
            normalized=tuple(value.strip() for value in values)
            if any(not value for value in normalized) or normalized != tuple(sorted(set(normalized))):
                raise ValueError(f"{name} must contain sorted unique nonblank values")
        return self

    @property
    def witness_fingerprint(self) -> str:
        """把 exact revision 與非 revision witness 固定成可重驗的 deterministic fingerprint。"""

        canonical=json.dumps(self.model_dump(mode="json"),ensure_ascii=False,sort_keys=True,separators=(",",":"))
        return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


class ExecutionRestoreResult(BaseModel):
    """ExecutionStateLoader 的明確 immutable 結果；partial diagnostics 不得冒充 VALID。"""

    model_config = ConfigDict(extra="forbid", frozen=True)

    status: ExecutionRestoreStatus
    cut: RecoveryCut | None = None
    evidence: tuple[str, ...]

    @model_validator(mode="after")
    def _status_contract(self) -> "ExecutionRestoreResult":
        if not self.evidence:
            raise ValueError("restore result requires positive evidence")
        if (self.status is ExecutionRestoreStatus.VALID) != (self.cut is not None):
            raise ValueError("only VALID restore result may contain a RecoveryCut")
        return self


class ReconciliationCompletenessEvidence(BaseModel):
    """空集合 MATCH 的 typed completeness 證據；綁定 exact run、account 與 RecoveryCut。"""
    model_config=ConfigDict(extra="forbid",frozen=True)
    evidence_id: str
    account: BrokerAccount
    run_id: str
    recovery_cut_fingerprint: str
    expected_complete: bool
    actual_complete: bool

    @field_validator("evidence_id","run_id","recovery_cut_fingerprint",mode="before")
    @classmethod
    def _ids(cls,value: object) -> object:
        return normalize_stable_id(value) if isinstance(value,str) else value


class ReconstructionReadinessEvidence(BaseModel):
    """C10 reconstruction 結果的 immutable provenance；不以 convenience boolean 取代 authority。"""
    model_config=ConfigDict(extra="forbid",frozen=True)
    evidence_id: str
    account: BrokerAccount
    recovery_cut_fingerprint: str
    discovery_run_id: str
    complete: bool
    conflict: bool

    @field_validator("evidence_id","recovery_cut_fingerprint","discovery_run_id",mode="before")
    @classmethod
    def _ids(cls,value: object) -> object:
        return normalize_stable_id(value) if isinstance(value,str) else value


class CapabilityReadinessEvidence(BaseModel):
    """READY 所需 broker capability 的正向 provenance refs；不授權 LIVE 或 broker action。"""
    model_config=ConfigDict(extra="forbid",frozen=True)
    evidence_id: str
    account: BrokerAccount
    recovery_cut_fingerprint: str
    source_refs: tuple[str,...]
    available: bool

    @field_validator("evidence_id","recovery_cut_fingerprint",mode="before")
    @classmethod
    def _ids(cls,value: object) -> object:
        return normalize_stable_id(value) if isinstance(value,str) else value

    @field_validator("source_refs",mode="before")
    @classmethod
    def _refs(cls,value: object) -> object:
        return tuple(normalize_stable_id(item) for item in value) if isinstance(value,(tuple,list)) else value

    @model_validator(mode="after")
    def _positive_source(self) -> "CapabilityReadinessEvidence":
        if self.available and not self.source_refs:
            raise ValueError("available capability evidence requires source refs")
        return self


class AccountReadinessEvidence(BaseModel):
    """C15 純 local readiness inputs；每個 mandatory predicate 必須有正向證據，UNKNOWN 不得升級 READY。"""

    model_config=ConfigDict(extra="forbid",frozen=True)

    restore_result: ExecutionRestoreResult
    formal_run_boundary: ReconciliationRunBoundary | None
    formal_run_outcome: ReconciliationRunOutcome | None
    discovery_result: BrokerDiscoveryResult | None = None
    continuity_epoch: ExecutionContinuityEpoch | None = None
    result_completeness: ReconciliationCompletenessEvidence | None = None
    reconstruction_evidence: ReconstructionReadinessEvidence | None = None
    capability_evidence: CapabilityReadinessEvidence | None = None
    required_policy: ReconciliationPolicy = ReconciliationPolicy.STRICT_HALT
    discovery_complete: bool
    exact_correlation_integrity: bool
    continuity_current: bool
    pending_material_inbox: bool
    reconstruction_complete: bool
    reconstruction_conflict: bool
    mandatory_capabilities_available: bool
    out_of_horizon_unresolved_action: bool = False

class AccountReadinessEvaluation(BaseModel):
    """BrokerAccount READY/REVIEW/HALT evaluation；保存 exact cut witness 供 final local revalidation。"""

    model_config=ConfigDict(extra="forbid",frozen=True)

    state: RecoveryReadinessState
    reasons: tuple[str,...]
    account: BrokerAccount
    account_revision: int = Field(ge=0)
    recovery_generation: int | None = Field(default=None,ge=1)
    recovery_ingress_version: int | None = Field(default=None,ge=0)
    inbox_count: int = Field(ge=0)
    application_count: int = Field(ge=0)
    recovery_cut_fingerprint: str
    broker_report_witness: tuple[str,...]
    current_nonterminal_order_anchors: tuple[str,...]
    fill_event_validation_anchors: tuple[str,...]
    continuity_epoch_witness: tuple[str,...]
    sequence_gap_witness: tuple[str,...]
    reconciliation_currentness_witness: tuple[str,...]
    formal_run_id: str | None = None
    formal_run_witness: tuple[str,...] = ()
    unresolved_broker_action_ids: tuple[str,...]


def evaluate_account_readiness(*,account: BrokerAccount,evidence: AccountReadinessEvidence) -> AccountReadinessEvaluation:
    """依 HALT > REVIEW > READY 聚合 frozen predicates；不 repair、不呼叫 broker、不授權交易。"""

    restore=evidence.restore_result
    if restore.status is not ExecutionRestoreStatus.VALID or restore.cut is None:
        return AccountReadinessEvaluation(state=RecoveryReadinessState.HALT,reasons=("coherent recovery cut is not valid",),account=account,account_revision=0,inbox_count=0,application_count=0,recovery_cut_fingerprint="INVALID",broker_report_witness=(),current_nonterminal_order_anchors=(),fill_event_validation_anchors=(),continuity_epoch_witness=(),sequence_gap_witness=(),reconciliation_currentness_witness=(),unresolved_broker_action_ids=())
    cut=restore.cut
    boundary=evidence.formal_run_boundary
    outcome=evidence.formal_run_outcome
    formal_witness=tuple(json.dumps(item.model_dump(mode="json"),ensure_ascii=False,sort_keys=True,separators=(",",":")) for item in (boundary,outcome) if item is not None)
    common=dict(account=account,account_revision=cut.head.current_revision,recovery_generation=cut.recovery_generation,recovery_ingress_version=cut.recovery_ingress_version,inbox_count=cut.inbox_count,application_count=cut.application_count,recovery_cut_fingerprint=cut.witness_fingerprint,broker_report_witness=cut.broker_report_witness,current_nonterminal_order_anchors=cut.current_nonterminal_order_anchors,fill_event_validation_anchors=cut.fill_event_validation_anchors,continuity_epoch_witness=cut.continuity_epoch_witness,sequence_gap_witness=cut.sequence_gap_witness,reconciliation_currentness_witness=cut.reconciliation_currentness_witness,formal_run_id=None if boundary is None else boundary.run_id,formal_run_witness=formal_witness,unresolved_broker_action_ids=cut.unresolved_broker_action_ids)
    halt=[]
    if cut.account != account: halt.append("requested BrokerAccount does not match recovery cut")
    if not evidence.mandatory_capabilities_available: halt.append("mandatory capability unavailable")
    if not evidence.exact_correlation_integrity: halt.append("broker correlation integrity conflict")
    if evidence.reconstruction_conflict: halt.append("canonical reconstruction integrity conflict")
    if boundary is None: halt.append("eligible formal reconciliation run boundary is missing")
    elif (
        boundary.account != account
        or boundary.account != cut.account
        or boundary.policy is not evidence.required_policy
        or boundary.recovery_cut_fingerprint != cut.witness_fingerprint
        or boundary.account_revision != cut.head.current_revision
        or boundary.expected_snapshot_id != cut.checkpoint.expected_snapshot_id
        or boundary.authority_commit_id != cut.checkpoint.authority_commit_id
        or boundary.recovery_generation != cut.recovery_generation
        or boundary.recovery_ingress_version != cut.recovery_ingress_version
        or boundary.discovery_run_id is None
        or boundary.observation_id is None
    ): halt.append("formal reconciliation run boundary does not bind the current recovery cut")
    if outcome is None: halt.append("eligible formal reconciliation run is missing")
    elif boundary is not None and outcome.run_id != boundary.run_id: halt.append("formal reconciliation outcome does not bind the established run")
    elif outcome.technical_outcome is ReconciliationRunTechnicalOutcome.FAILED: halt.append("formal reconciliation run failed")
    if halt:
        return AccountReadinessEvaluation(state=RecoveryReadinessState.HALT,reasons=tuple(halt),**common)
    review=[]
    discovery=evidence.discovery_result
    if (discovery is None or boundary is None or discovery.account != account or discovery.discovery_run_id != boundary.discovery_run_id or discovery.completeness is not DiscoveryCompleteness.COMPLETE or discovery.integrity is not BrokerDiscoveryIntegrity.CONSISTENT):
        review.append("typed broker discovery evidence is incomplete or mismatched")
    continuity=evidence.continuity_epoch
    if (continuity is None or continuity.broker != account.broker or continuity.account_ref != account.account_ref or continuity.generation != cut.recovery_generation or not continuity.trusted_current or not any(continuity.epoch_id in anchor for anchor in cut.continuity_epoch_witness)):
        review.append("typed execution continuity evidence is not current")
    if not evidence.discovery_complete: review.append("broker discovery is incomplete")
    if not evidence.continuity_current: review.append("execution continuity is not current")
    if evidence.pending_material_inbox: review.append("material broker inbox evidence is pending")
    if any(any(status in anchor for status in ('"DEFERRED"','"CONFLICT"')) for anchor in cut.broker_report_witness):
        review.append("current broker report disposition is unresolved")
    if not evidence.reconstruction_complete: review.append("canonical reconstruction is incomplete")
    if cut.unresolved_broker_action_ids: review.append("broker action disposition is unresolved")
    if evidence.out_of_horizon_unresolved_action: review.append("broker action requires external disposition evidence")
    completeness=evidence.result_completeness
    if outcome is not None and not outcome.results and (completeness is None or completeness.account != account or completeness.run_id != outcome.run_id or completeness.recovery_cut_fingerprint != cut.witness_fingerprint or not completeness.expected_complete or not completeness.actual_complete):
        review.append("empty reconciliation result lacks bound completeness evidence")
    reconstruction=evidence.reconstruction_evidence
    if (reconstruction is None or reconstruction.account != account or reconstruction.recovery_cut_fingerprint != cut.witness_fingerprint or boundary is None or reconstruction.discovery_run_id != boundary.discovery_run_id or not reconstruction.complete or reconstruction.conflict):
        review.append("reconstruction evidence is incomplete or mismatched")
    capability=evidence.capability_evidence
    if (capability is None or capability.account != account or capability.recovery_cut_fingerprint != cut.witness_fingerprint or not capability.available or not capability.source_refs):
        review.append("mandatory capability evidence is unavailable or mismatched")
    if outcome is not None and (
        outcome.input_qualification is not ReconciliationInputQualification.QUALIFIED
        or outcome.technical_outcome is not ReconciliationRunTechnicalOutcome.COMPLETED
        or any(result.status is not ReconciliationStatus.MATCH for result in outcome.results)
    ): review.append("formal reconciliation is not a qualified MATCH")
    if review:
        return AccountReadinessEvaluation(state=RecoveryReadinessState.REVIEW,reasons=tuple(review),**common)
    return AccountReadinessEvaluation(state=RecoveryReadinessState.READY,reasons=(),**common)


class RecoveryResult(
    BaseModel
):
    """Restart recovery gate ?????? strategy?? repair broker/account?"""

    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
        arbitrary_types_allowed=True,
    )

    state: RecoveryReadinessState
    reasons: tuple[
        str,
        ...,
    ] = ()
    restored_strategies: tuple[
        object,
        ...,
    ] = ()


@runtime_checkable
class ExecutionStateLoader(
    Protocol
):
    def load(
        self,
        account: BrokerAccount,
    ) -> ExecutionRestoreResult:
        ...


def _required_revision_id(
    *,
    required_market_observation_revision_id: (
        str
        | None
    ),
    required_market_observation_id: (
        str
        | None
    ),
) -> str:
    canonical = (
        None
        if (
            required_market_observation_revision_id
            is None
        )
        else (
            normalize_market_observation_revision_id(
                required_market_observation_revision_id
            )
        )
    )

    legacy = (
        None
        if (
            required_market_observation_id
            is None
        )
        else (
            normalize_market_observation_revision_id(
                required_market_observation_id
            )
        )
    )

    if (
        canonical is None
        and legacy is None
    ):
        raise (
            LegacyMarketObservationReferenceError(
                "required_market_observation_"
                "revision_id is required"
            )
        )

    if canonical is None:
        canonical = legacy

    if canonical is None:
        raise (
            LegacyMarketObservationReferenceError(
                "canonical market observation "
                "revision is required"
            )
        )

    if (
        legacy is not None
        and legacy != canonical
    ):
        raise (
            StrategyStateReferenceConflictError(
                "required legacy/canonical "
                "market observation references "
                "disagree"
            )
        )

    return canonical


def recover_runtime(
    *,
    account: BrokerAccount,
    execution_loader: ExecutionStateLoader,
    expected_loader: ExpectedPositionLoader,
    broker_position_provider: (
        BrokerPositionProvider
    ),
    reconciliation_policy: (
        ReconciliationPolicy
    ),
    case_repository: (
        ReconciliationCaseRepository
    ),
    strategy_instance_ids: tuple[
        str,
        ...,
    ],
    instance_repository: (
        StrategyInstanceRepository
    ),
    state_repository: (
        StrategyStateRepository
    ),
    registry: StrategyRegistry,
    required_market_observation_revision_id: (
        str
        | None
    ) = None,
    required_market_observation_id: (
        str
        | None
    ) = None,
) -> RecoveryResult:
    """Frozen ordering?exact canonical mor1 ?? restore strategy?"""

    restore_result=execution_loader.load(account)
    if not isinstance(restore_result,ExecutionRestoreResult) or restore_result.status is not ExecutionRestoreStatus.VALID:
        return RecoveryResult(state=RecoveryReadinessState.HALT,reasons=("legacy recovery lacks a valid coherent RecoveryCut",))

    account_result = (
        reconcile_startup(
            account=account,
            expected_loader=expected_loader,
            broker_position_provider=(
                broker_position_provider
            ),
            policy=(
                reconciliation_policy
            ),
            strategy_state_ready=True,
        )
    )

    if (
        account_result.state
        is StartupReadinessState.HALT
    ):
        return RecoveryResult(
            state=(
                RecoveryReadinessState.HALT
            ),
            reasons=(
                "account reconciliation halted",
            ),
        )

    if (
        account_result.state
        is StartupReadinessState.REVIEW
    ):
        return RecoveryResult(
            state=(
                RecoveryReadinessState.REVIEW
            ),
            reasons=(
                "account reconciliation "
                "requires review",
            ),
        )

    case_state = blocking_case_state(
        case_repository.unresolved(account)
    )

    if (
        case_state
        is ReconciliationCaseState.HALT
    ):
        return RecoveryResult(
            state=(
                RecoveryReadinessState.HALT
            ),
            reasons=(
                "persisted reconciliation "
                "HALT case",
            ),
        )

    if (
        case_state
        is (
            ReconciliationCaseState
            .REVIEW_REQUIRED
        )
    ):
        return RecoveryResult(
            state=(
                RecoveryReadinessState.REVIEW
            ),
            reasons=(
                "persisted reconciliation "
                "review case",
            ),
        )

    try:
        required_revision_id = (
            _required_revision_id(
                required_market_observation_revision_id=(
                    required_market_observation_revision_id
                ),
                required_market_observation_id=(
                    required_market_observation_id
                ),
            )
        )
    except (
        LegacyMarketObservationReferenceError,
        StrategyStateReferenceConflictError,
    ) as exc:
        return RecoveryResult(
            state=(
                RecoveryReadinessState.HALT
            ),
            reasons=(
                str(exc),
            ),
        )

    restored: list[
        object
    ] = []

    for (
        instance_id
    ) in strategy_instance_ids:
        instance = (
            instance_repository.get(
                instance_id
            )
        )

        try:
            snapshot = (
                state_repository.latest(
                    instance_id
                )
            )
        except (
            LegacyMarketObservationReferenceError,
            StrategyStateReferenceConflictError,
            ValueError,
        ) as exc:
            return RecoveryResult(
                state=(
                    RecoveryReadinessState.HALT
                ),
                reasons=(
                    str(exc),
                ),
            )

        if (
            instance is None
            or snapshot is None
        ):
            return RecoveryResult(
                state=(
                    RecoveryReadinessState.HALT
                ),
                reasons=(
                    "required strategy "
                    "instance/snapshot missing",
                ),
            )

        if (
            snapshot.strategy_instance_id
            != instance.strategy_instance_id
            or snapshot.strategy_id
            != instance.strategy_id
            or snapshot.strategy_version
            != instance.strategy_version
            or snapshot.config_version
            != instance.config_version
            or snapshot.config_fingerprint
            != instance.config_fingerprint
            or snapshot.instrument_id
            != instance.instrument_id
            or snapshot.timeframe
            != instance.timeframe
            or (
                snapshot
                .last_market_observation_revision_id
                != required_revision_id
            )
        ):
            return RecoveryResult(
                state=(
                    RecoveryReadinessState.HALT
                ),
                reasons=(
                    "strategy snapshot identity/"
                    "config/scope/revision mismatch",
                ),
            )

        try:
            strategy = (
                registry.create_instance(
                    instance
                )
            )

            if not isinstance(
                strategy,
                StatefulStrategy,
            ):
                raise ValueError(
                    "strategy does not expose "
                    "explicit state codec"
                )

            if (
                strategy.state_schema_version
                != snapshot.state_schema_version
            ):
                raise ValueError(
                    "strategy state schema mismatch"
                )

            strategy.restore_state(
                snapshot.state_json
            )

        except (
            KeyError,
            TypeError,
            ValueError,
        ) as exc:
            return RecoveryResult(
                state=(
                    RecoveryReadinessState.HALT
                ),
                reasons=(
                    str(exc),
                ),
            )

        restored.append(
            strategy
        )

    return RecoveryResult(
        state=RecoveryReadinessState.REVIEW,
        reasons=("legacy recovery lacks eligible formal reconciliation/currentness evidence",),
        restored_strategies=tuple(
            restored
        ),
    )
