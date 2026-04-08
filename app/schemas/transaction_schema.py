from pydantic import BaseModel, field_validator
from typing import Optional
from app.schemas.category_schema import CategoryResponse


class TransactionCreate(BaseModel):
    description : str
    amount      : float
    is_expense  : bool
    category_id : Optional[int] = None

    @field_validator("amount")
    @classmethod
    def amount_must_be_positive(cls, value):
        if value <= 0:
            raise ValueError("Amount must be greater than zero")
        return value

    @field_validator("description")
    @classmethod
    def description_must_not_be_empty(cls, value):
        if not value.strip():
            raise ValueError("Description cannot be empty")
        return value.strip()


class TransactionResponse(BaseModel):
    id          : int
    description : str
    amount      : float
    is_expense  : bool
    category_id : Optional[int] = None
    category    : Optional[CategoryResponse] = None

    model_config = {"from_attributes": True}