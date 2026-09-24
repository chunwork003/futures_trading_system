from pydantic import BaseModel, Field

from backtest.capital_reference_method import CapitalReferenceMethod


class CapitalProtectionReference(BaseModel):
    method: CapitalReferenceMethod
    reference_equity: float = Field(gt=0)
