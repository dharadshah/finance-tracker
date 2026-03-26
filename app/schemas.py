from pydantic import BaseModel, field_validator
from typing import Optional


class TransactionCreate(BaseModel):
    description: str
    amount: float
    is_expense: bool
    category: Optional[str] = None

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
    id: int
    description: str
    amount: float
    is_expense: bool
    category: Optional[str] = None

    model_config = {"from_attributes": True}


if __name__ == "__main__":
    # Valid transaction
    t = TransactionCreate(
        description="Salary",
        amount=50000,
        is_expense=False,
        category="Income"
    )
    print(t)

    # Invalid amount
    try:
        t2 = TransactionCreate(
            description="Netflix",
            amount=-649,
            is_expense=True
        )
    except Exception as e:
        print(f"Validation error: {e}")

    # Empty description
    try:
        t3 = TransactionCreate(
            description="   ",
            amount=649,
            is_expense=True
        )
    except Exception as e:
        print(f"Validation error: {e}")