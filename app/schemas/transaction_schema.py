from pydantic import BaseModel, model_validator, computed_field
from typing import Optional
from app.schemas.category_schema import CategoryResponse
from app.schemas.types import Amount, ShortString


class TransactionCreate(BaseModel):
    description : ShortString
    amount      : Amount
    is_expense  : bool
    category_id : Optional[int] = None

    @model_validator(mode="after")
    def validate_transaction(self) -> "TransactionCreate":
        if self.amount > 500000 and not self.is_expense:
            raise ValueError(
                "Income above Rs.500000 requires a category for tracking"
            )
        return self


class TransactionResponse(BaseModel):
    id          : int
    description : str
    amount      : float
    is_expense  : bool
    category_id : Optional[int] = None
    category    : Optional[CategoryResponse] = None

    model_config = {
        "from_attributes"  : True,
        "populate_by_name" : True
    }

    @computed_field
    @property
    def transaction_type(self) -> str:
        return "EXPENSE" if self.is_expense else "INCOME"

    @computed_field
    @property
    def formatted_amount(self) -> str:
        return f"Rs.{self.amount:,.2f}"

    @classmethod
    def from_orm_with_rel(cls, obj):
        return cls(
            id          = obj.id,
            description = obj.description,
            amount      = obj.amount,
            is_expense  = obj.is_expense,
            category_id = obj.category_id,
            category    = obj.category_rel
        )

class BulkTransactionCreate(BaseModel):
    transactions: list[TransactionCreate]

    @model_validator(mode="after")
    def validate_bulk(self) -> "BulkTransactionCreate":
        if len(self.transactions) == 0:
            raise ValueError("At least one transaction is required")
        if len(self.transactions) > 100:
            raise ValueError("Maximum 100 transactions allowed per bulk create")
        return self