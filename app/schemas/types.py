from typing import Annotated
from pydantic import Field, StringConstraints

# Reusable field types
Amount      = Annotated[float, Field(gt=0, description="Amount must be greater than zero")]
ShortString = Annotated[str,   StringConstraints(min_length=1, max_length=100, strip_whitespace=True)]
LongString  = Annotated[str,   StringConstraints(min_length=0, max_length=500, strip_whitespace=True)]