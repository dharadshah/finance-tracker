from pydantic import BaseModel
from typing import Optional
from app.schemas.types import ShortString, LongString


class CategoryCreate(BaseModel):
    name        : ShortString
    description : Optional[LongString] = None


class CategoryResponse(BaseModel):
    id          : int
    name        : str
    description : Optional[str] = None

    model_config = {"from_attributes": True}