from pydantic import BaseModel, field_validator
from typing import Optional


# --- Category Schemas ---

class CategoryCreate(BaseModel):
    name        : str
    description : Optional[str] = None

    @field_validator("name")
    @classmethod
    def name_must_not_be_empty(cls, value):
        if not value.strip():
            raise ValueError("Category name cannot be empty")
        return value.strip()


class CategoryResponse(BaseModel):
    id          : int
    name        : str
    description : Optional[str] = None

    model_config = {"from_attributes": True}


# --- Transaction Schemas ---

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