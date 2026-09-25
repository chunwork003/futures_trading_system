from datetime import datetime, timezone

import pytest

from persistence.reconciliation import ReconciliationCaseVersion
from persistence.recovery import RecoveryReadinessState, recover_runtime
from persistence.strategy_state import StrategyStateSnapshot
from strategy.instance import StrategyInstance, config_fingerprint
from strategy.registry import StrategyRegistry
from strategies.ema_cross import EMACrossStrategy
from trading.account import AccountPosition, BrokerAccount, BrokerPositionSnapshot, PositionDirection
from trading.reconciliation import ReconciliationPolicy, compare_positions, create_reconciliation_case

NOW=datetime(2026,9,25,1,tzinfo=timezone.utc)
ACCOUNT=BrokerAccount(broker="SINOPAC",account_ref="A")


class ExecutionLoader:
    def __init__(self, trace): self.trace=trace
    def load(self, account): self.trace.append("execution")
class ExpectedLoader:
    def __init__(self, positions, trace): self.positions=positions; self.trace=trace
    def load_positions(self, account): self.trace.append("expected"); return self.positions
class Provider:
    def __init__(self, positions, trace): self.positions=positions; self.trace=trace
    def list_positions(self, account): self.trace.append("broker"); return self.positions
class Cases:
    def __init__(self, values=()): self.values=values
    def unresolved(self): return self.values
class Instances:
    def __init__(self, value, trace): self.value=value; self.trace=trace
    def get(self, key): self.trace.append("instance"); return self.value
class States:
    def __init__(self, value, trace): self.value=value; self.trace=trace
    def latest(self, key): self.trace.append("state"); return self.value


def setup(market="BAR-1"):
    config={"symbol":"TX","timeframe":"1m"}
    instance=StrategyInstance(strategy_instance_id="SI",strategy_id="EMA_CROSS",strategy_version="1.0.0",config_version="C1",config_fingerprint=config_fingerprint(config),instrument_id=1,timeframe="1m",config_json=config)
    snapshot=StrategyStateSnapshot(snapshot_id="SS",strategy_instance_id="SI",strategy_id="EMA_CROSS",strategy_version="1.0.0",config_version="C1",config_fingerprint=instance.config_fingerprint,instrument_id=1,timeframe="1m",state_schema_version=1,last_market_observation_id=market,captured_at=NOW,state_json={"schema_version":1,"previous_ema20":1.0,"previous_ema60":2.0})
    registry=StrategyRegistry(); registry.register("EMA_CROSS","1.0.0",EMACrossStrategy)
    return instance,snapshot,registry


def recover(*, expected=(), actual=(), cases=(), snapshot_override=True, market="BAR-1"):
    trace=[]; instance,snapshot,registry=setup(market)
    snapshot_value=snapshot if snapshot_override is True else snapshot_override
    result=recover_runtime(account=ACCOUNT,execution_loader=ExecutionLoader(trace),expected_loader=ExpectedLoader(expected,trace),broker_position_provider=Provider(actual,trace),reconciliation_policy=ReconciliationPolicy.STRICT_HALT,case_repository=Cases(cases),strategy_instance_ids=("SI",),instance_repository=Instances(instance,trace),state_repository=States(snapshot_value,trace),registry=registry,required_market_observation_id="BAR-1")
    return result,trace


def test_successful_reconciliation_restores_strategy_and_is_ready() -> None:
    result,trace=recover()
    assert result.state is RecoveryReadinessState.READY
    assert isinstance(result.restored_strategies[0],EMACrossStrategy)
    assert trace == ["execution","expected","broker","instance","state"]


def test_account_halt_prevents_strategy_restore() -> None:
    expected=(AccountPosition(broker="SINOPAC",account_ref="A",instrument_id=1,contract_id=2,direction=PositionDirection.LONG,quantity=1),)
    result,trace=recover(expected=expected)
    assert result.state is RecoveryReadinessState.HALT
    assert "instance" not in trace and "state" not in trace


def test_account_review_prevents_ready_and_restore() -> None:
    trace=[]
    expected=(AccountPosition(broker="SINOPAC",account_ref="A",instrument_id=1,contract_id=2,direction=PositionDirection.LONG,quantity=1),)
    instance,snapshot,registry=setup()
    result=recover_runtime(account=ACCOUNT,execution_loader=ExecutionLoader(trace),expected_loader=ExpectedLoader(expected,trace),broker_position_provider=Provider((),trace),reconciliation_policy=ReconciliationPolicy.MANUAL_REVIEW,case_repository=Cases(),strategy_instance_ids=("SI",),instance_repository=Instances(instance,trace),state_repository=States(snapshot,trace),registry=registry,required_market_observation_id="BAR-1")
    assert result.state is RecoveryReadinessState.REVIEW and "instance" not in trace


def test_unresolved_case_gate_precedes_strategy_restore() -> None:
    mismatch=compare_positions(AccountPosition(broker="SINOPAC",account_ref="A",instrument_id=1,contract_id=2,direction=PositionDirection.LONG,quantity=1),None)
    case=create_reconciliation_case(case_id="CASE",result=mismatch,policy=ReconciliationPolicy.STRICT_HALT)
    version=ReconciliationCaseVersion(case_id="CASE",version=1,recorded_at=NOW,reconciliation_case=case)
    result,trace=recover(cases=(version,))
    assert result.state is RecoveryReadinessState.HALT and "instance" not in trace


@pytest.mark.parametrize(("snapshot_override","market"),[(None,"BAR-1"),(True,"OTHER")])
def test_missing_snapshot_or_market_boundary_mismatch_halts(snapshot_override,market) -> None:
    result,_=recover(snapshot_override=snapshot_override,market=market)
    assert result.state is RecoveryReadinessState.HALT


@pytest.mark.parametrize("field", ["strategy_version","config_version","config_fingerprint","instrument_id","timeframe","state_schema_version"])
def test_snapshot_identity_config_scope_or_schema_mismatch_halts(field: str) -> None:
    instance,snapshot,_=setup()
    replacement={
        "strategy_version":"2", "config_version":"C2", "config_fingerprint":"0"*64,
        "instrument_id":2, "timeframe":"5m", "state_schema_version":2,
    }[field]
    result,_=recover(snapshot_override=snapshot.model_copy(update={field:replacement}))
    assert result.state is RecoveryReadinessState.HALT


def test_decode_restore_failure_halts() -> None:
    _,snapshot,_=setup()
    broken=snapshot.model_copy(update={"state_json":{"schema_version":1,"unexpected":True}})
    result,_=recover(snapshot_override=broken)
    assert result.state is RecoveryReadinessState.HALT
