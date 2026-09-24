from pydantic import BaseModel, Field, model_validator


class FixedRatioRiskThresholds(BaseModel):
    level_1_drawdown: float = Field(gt=0, lt=1)
    level_2_drawdown: float = Field(gt=0, lt=1)
    level_3_drawdown: float = Field(gt=0, lt=1)

    @model_validator(mode="after")
    def validate_order(self) -> "FixedRatioRiskThresholds":
        if not (
            self.level_1_drawdown
            < self.level_2_drawdown
            < self.level_3_drawdown
        ):
            raise ValueError(
                "risk thresholds must satisfy level_1 < level_2 < level_3"
            )

        return self
