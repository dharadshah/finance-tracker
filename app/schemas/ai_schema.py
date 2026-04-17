"""Pydantic schemas for AI endpoints."""
from pydantic import BaseModel, field_validator
from typing import Optional
from app.schemas.types import ShortString


class ClassifyRequest(BaseModel):
    """Request schema for transaction classification.

    Attributes:
        description: Transaction description to classify.
    """
    description: ShortString

    @field_validator("description")
    @classmethod
    def description_must_not_be_empty(cls, value):
        if not value.strip():
            raise ValueError("Description cannot be empty")
        return value.strip()


class ClassifyResponse(BaseModel):
    """Response schema for transaction classification.

    Attributes:
        description    : Original transaction description.
        classification : INCOME or EXPENSE.
    """
    description    : str
    classification : str


class AdviceRequest(BaseModel):
    """Request schema for financial advice.

    Attributes:
        total_income   : Total income amount.
        total_expenses : Total expenses amount.
        savings_rate   : Savings rate percentage.
        top_category   : Largest expense category.
    """
    total_income   : float
    total_expenses : float
    savings_rate   : float
    top_category   : str

    @field_validator("total_income", "total_expenses")
    @classmethod
    def must_be_non_negative(cls, value):
        if value < 0:
            raise ValueError("Amount cannot be negative")
        return value

    @field_validator("savings_rate")
    @classmethod
    def savings_rate_must_be_valid(cls, value):
        if not -100 <= value <= 100:
            raise ValueError("Savings rate must be between -100 and 100")
        return value


class AdviceResponse(BaseModel):
    """Response schema for financial advice.

    Attributes:
        advice: Personalised financial advice string.
    """
    advice: str


class AnalysisReport(BaseModel):
    """Response schema for full financial analysis report.

    Attributes:
        transactions  : List of analysed transactions.
        summary       : Financial summary dict.
        advice        : Personalised advice string.
        has_high_risk : True if any high risk transaction found.
        error         : Error message if analysis failed.
    """
    transactions  : list
    summary       : dict
    advice        : str
    has_high_risk : bool
    error         : Optional[str] = None