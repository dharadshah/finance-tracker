from pydantic import BaseModel, field_validator
from typing import Optional


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