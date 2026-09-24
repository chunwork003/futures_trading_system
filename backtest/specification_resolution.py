from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from enum import Enum

from backtest.risk import RiskConfig
from domain.instruments import InstrumentSpec
from domain.margins import MarginScheduleResolver


class ResolvedParameterSource(str, Enum):
    """記錄回測相容參數的實際來源，供後續 decision provenance 使用。"""

    EXPLICIT_OVERRIDE = "EXPLICIT_OVERRIDE"
    CANONICAL_SPEC = "CANONICAL_SPEC"
    CANONICAL_MARGIN_SCHEDULE = "CANONICAL_MARGIN_SCHEDULE"
    NO_MARGIN_MODE = "NO_MARGIN_MODE"


class SpecificationResolutionError(ValueError):
    """無法從 explicit override 或 canonical specification 解析必要參數。"""


class MarginResolutionError(SpecificationResolutionError):
    """無法解析 margin，且呼叫端未明確選擇 no-margin mode。"""


@dataclass(frozen=True)
class ResolvedMultiplier:
    value: float
    source: ResolvedParameterSource


@dataclass(frozen=True)
class ResolvedMargins:
    initial_margin_per_contract: float
    maintenance_margin_per_contract: float
    source: ResolvedParameterSource
    margin_id: int | None = None


class BacktestSpecificationResolver:
    """在回測邊界解析 scenario override 與 canonical domain specification。"""

    @staticmethod
    def resolve_multiplier(
        *,
        explicit_override: float | None,
        instrument_spec: InstrumentSpec | None,
    ) -> ResolvedMultiplier:
        if explicit_override is not None:
            if explicit_override <= 0:
                raise SpecificationResolutionError(
                    "explicit multiplier override must be > 0"
                )
            return ResolvedMultiplier(
                value=float(explicit_override),
                source=ResolvedParameterSource.EXPLICIT_OVERRIDE,
            )

        if instrument_spec is None or instrument_spec.multiplier is None:
            raise SpecificationResolutionError(
                "multiplier requires an explicit override or canonical "
                "InstrumentSpec.multiplier"
            )

        return ResolvedMultiplier(
            value=float(instrument_spec.multiplier),
            source=ResolvedParameterSource.CANONICAL_SPEC,
        )

    @staticmethod
    def resolve_margins(
        *,
        explicit_override: RiskConfig | None,
        margin_resolver: MarginScheduleResolver | None,
        instrument_id: int,
        as_of_date: date,
        contract_id: int | None = None,
        no_margin_mode: bool = False,
    ) -> ResolvedMargins:
        if explicit_override is not None:
            return ResolvedMargins(
                initial_margin_per_contract=float(
                    explicit_override.initial_margin_per_contract
                ),
                maintenance_margin_per_contract=float(
                    explicit_override.maintenance_margin_per_contract
                ),
                source=ResolvedParameterSource.EXPLICIT_OVERRIDE,
            )

        if margin_resolver is not None:
            entry = margin_resolver.resolve(
                instrument_id=instrument_id,
                contract_id=contract_id,
                as_of_date=as_of_date,
            )
            if entry is not None:
                return ResolvedMargins(
                    initial_margin_per_contract=float(entry.initial_margin),
                    maintenance_margin_per_contract=float(
                        entry.maintenance_margin
                    ),
                    source=(
                        ResolvedParameterSource.CANONICAL_MARGIN_SCHEDULE
                    ),
                    margin_id=entry.margin_id,
                )

        if no_margin_mode:
            return ResolvedMargins(
                initial_margin_per_contract=0.0,
                maintenance_margin_per_contract=0.0,
                source=ResolvedParameterSource.NO_MARGIN_MODE,
            )

        raise MarginResolutionError(
            "margin requires an explicit RiskConfig override, a canonical "
            "schedule entry, or explicit no-margin mode"
        )
