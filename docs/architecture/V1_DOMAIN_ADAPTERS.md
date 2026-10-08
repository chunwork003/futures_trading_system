# Domain adapter closure — P00 candidate

No runtime migration or acceptance is implied. Generated schemas describe new boundary records; existing canonical constructors/validators remain authoritative. Source bindings are pinned in `contracts/domain_source_bindings.v1.json`.

## Verified differences from earlier candidate assumptions

`StrategyInstance.strategy_version` is a normalized string, exposed as implementation_revision; it is not required to be a Git SHA. API revision fields now retain that identity. ResearchRun separately pins code_sha and dependency_lock_hash. A strategy-version-to-code-artifact registration must resolve exactly; cannot substitute current checkout SHA for the registered version.

`backtest/target_position.py` and `backtest/strategy_position.py` still use symbol/optional contract strings. Their Blueprint acceptance is acceptance of the existing scope, not proof that canonical integer identity is implemented in those classes. Backtest Direction/quantity remain compatibility representations; operational adapters require an explicit versioned mapping to instrument_id/contract_id before any intent. Ambiguous/missing mapping rejects. No prefix inference and no silent rewriting of legacy constructors.

`strategy/signal.py` is a DataFrame helper, not the canonical provenance Signal. New Signal lives under E ownership and references an accepted strategy snapshot/observation. Existing `persistence/strategy_state.py::StrategyStateSnapshot` owns durable state; IncrementalState is a versioned qualification/provenance attachment to that snapshot, not another writable state store.

## Signal and cohort

Signal asserts a desired **virtual net position** in signed contracts for one StrategyInstance/contract/observation. Positive=long, negative=short, zero=explicit virtual flat. It is not a delta order. Stable key is (instance, config version, observation revision, strategy version); material changes under the same key reject. HOLD still emits the unchanged desired virtual target, so required cohort members never disappear merely because they have no action.

Legacy signal action adapter consumes the prior committed virtual position. ENTER establishes a new desired target only if allowed by the strategy contract; EXIT gives virtual zero; HOLD preserves prior target. A legacy REVERSE expresses an opposite desired target, never simultaneous physical close/open. Missing prior virtual state is UNKNOWN, not zero. Each adapter requires golden fixtures for ENTER/HOLD/EXIT/REVERSE and no-position initialization; the accepted physical reversal invariant remains downstream.

Decision requires exact policy-required cohort membership; no duplicate instance, missing member, mixed config binding or mixed observation revision. Same-direction desired targets aggregate; conflicting directions retain the existing PriorityStrategyConflictPolicy convention: larger priority wins; opposite directions tied at highest priority reject and require an explicit separately versioned resolution policy. Stable instance ID orders audit output only; it never silently breaks a conflict. Sum selected attributions equals desired_net_quantity, before reversal staging. Excluded signals remain referenced with exclusion reason in decision audit. A conflict with no valid policy fails closed.

## Decision and risk boundary

Decision holds immutable inputs/proposal. RiskDecision is a separate immutable permission linked by decision_id; do not mutate Decision in place to add approval. A joined API projection may display both. Risk rejection has approved_net_quantity=null, not zero: no permission is not an instruction to flatten.

For expected position e and policy-selected desired target t: e=t => HOLD; e=0,t!=0 => ENTER; e!=0,t=0 => EXIT; equal nonzero signs and |t|>|e| => ADD; equal signs and |t|<|e| => REDUCE. Opposite signs produce EXIT with staged proposed target zero and preserve the ultimate desired target in evidence. No inverse opening intent is created until authoritative expected/actual reconciliation and order completion confirm FLAT, followed by a fresh cohort/observation/risk decision. Never reuse the pre-exit risk permission.

The schema stores desired_net_quantity (ultimate logical target) separately from proposed_net_quantity (staged executable target). In an opposite-direction decision, desired retains the opposite target and proposed is zero; selected attributions sum to desired. After confirmed FLAT the prior desired target is evidence only, never automatic permission to enter.

ALLOW requires approved target equal proposed target. REDUCE may only reduce the requested risk increase, never reverse direction or turn a requested close into an opening. REJECT has no approved target and preserves current account truth. Risk-decreasing commands still require known current position, valid contract identity and current cut; they may be allowed despite entry limits under the exact reduction policy. Missing margin/reference is an error, never numeric zero. RiskDecision must bind account/capital revisions and constraints to the same current governing inputs; stale approved decisions fail the final execution fence.

Canonical OrderIntent already has target_position_ref, risk_decision_ref and execution_trigger_ref. Their constructor permits optional refs for compatibility; V1 operational adapter requires all three plus exact mor1 observation revision before risk-increasing execution. Tighten the adapter, not the accepted constructor. REJECT creates no intent. Order/Fill events retain accepted duplicate-material comparison, sequence and UoW semantics.

## Capital and incremental state

CapitalState is a projection of manual genesis, accepted account/fill ledger, mark and margin policies: available = initial + realized + unrealized - fees - reserved_margin. Fees/reserved margin are nonnegative costs/reservations; no external flows or cross-strategy borrowing. All arithmetic is Decimal; fee/settlement rounding uses pinned policy. Negative available is representable as an observed constraint violation, never clamped to hide insolvency. UI cannot write balances. Projection identity includes account checkpoint and mark provenance, not timestamp alone.

Warmup is READY only when completed_bar_count >= required_warmup_bars and codec/version/observation bindings are valid; a count alone never proves readiness. Empty history is not warm. Feature algorithms must define the minimal sufficient state and batch-equivalence tolerance; operational money remains exact. State persistence uses existing explicit export_state/restore_state and StrategyStateSnapshot; no reflection/pickle of arbitrary instances. Duplicate observation gives the same persisted state/signal, not another action. Historical revision affecting the checkpoint invalidates qualification and requires deterministic rebuild from pinned history, not in-place economic history repair.

## Required counterexamples and remaining design gate

Before P05/P06 execution: prove duplicate identity/different material rejection; absent prior virtual state; incomplete cohort; legacy mapping ambiguity; mixed frontier; rejected risk != flat; stale capital revision; opposite-direction staged exit; partial fill before FLAT; snapshot codec mismatch; history correction/rebuild. Schema tests alone cannot establish these causal/economic invariants.

Still to finish in R01: exact feature codec first implementation, complete DTO adapter coverage and independent semantic review. Simulation genesis/operation transitions and auth-handler contracts are now specified in V1_GENESIS_AUTH_CONTRACT.md. This document deliberately identifies unfinished public semantics rather than authorizing implementation to guess them.
