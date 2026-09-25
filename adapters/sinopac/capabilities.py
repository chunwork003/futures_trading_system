from datetime import date

from adapters.capabilities import (
    BrokerCapability,
    BrokerCapabilityEvidence,
    BrokerCapabilityMatrix,
    BrokerCapabilitySupport,
    BrokerVerificationMode,
)


_COMMON = {
    "support": BrokerCapabilitySupport.SUPPORTED,
    "verification_modes": (BrokerVerificationMode.DOCUMENTATION,),
    "sdk_version": "1.7.6",
    "verified_on": date(2026, 9, 25),
}


# 此矩陣只封裝已核准的官方文件證據；未執行 simulation 或 production 驗證。
SINOPAC_CAPABILITY_MATRIX = BrokerCapabilityMatrix(
    broker="SINOPAC",
    entries=(
        BrokerCapabilityEvidence(
            capability=BrokerCapability.ACCOUNT_QUERY,
            source_ids=("SRC-SINOPAC-LOGIN-001",),
            **_COMMON,
        ),
        BrokerCapabilityEvidence(
            capability=BrokerCapability.POSITION_QUERY,
            source_ids=("SRC-SINOPAC-POSITION-001",),
            **_COMMON,
        ),
        BrokerCapabilityEvidence(
            capability=BrokerCapability.ORDER_PLACE,
            source_ids=("SRC-SINOPAC-FUT-ORDER-001",),
            **_COMMON,
        ),
        BrokerCapabilityEvidence(
            capability=BrokerCapability.ORDER_UPDATE,
            source_ids=("SRC-SINOPAC-FUT-ORDER-001",),
            **_COMMON,
        ),
        BrokerCapabilityEvidence(
            capability=BrokerCapability.ORDER_CANCEL,
            source_ids=("SRC-SINOPAC-FUT-ORDER-001",),
            **_COMMON,
        ),
        BrokerCapabilityEvidence(
            capability=BrokerCapability.ORDER_STATUS,
            source_ids=("SRC-SINOPAC-ORDER-STATUS-001",),
            **_COMMON,
        ),
        BrokerCapabilityEvidence(
            capability=BrokerCapability.TRADE_LIST,
            source_ids=("SRC-SINOPAC-ORDER-STATUS-001",),
            **_COMMON,
        ),
        BrokerCapabilityEvidence(
            capability=BrokerCapability.ORDER_DEAL_EVENT,
            source_ids=(
                "SRC-SINOPAC-ORDER-EVENT-001",
                "SRC-SINOPAC-RELEASE-001",
            ),
            **_COMMON,
        ),
    ),
)
