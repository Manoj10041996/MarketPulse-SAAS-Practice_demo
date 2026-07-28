from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class ApiKeyCreateRequest(BaseModel):
    owner_label: str = Field(min_length=1, max_length=200)


class ApiKeyCreateResponse(BaseModel):
    id: UUID
    owner_label: str
    api_key: str
    created_at: datetime
