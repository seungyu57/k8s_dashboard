from typing import Optional

from pydantic import BaseModel, Field


class EventSummary(BaseModel):
    namespace: Optional[str] = None
    type: Optional[str] = None
    reason: Optional[str] = None
    message: Optional[str] = None
    involved_kind: Optional[str] = Field(None, alias="involvedKind")
    involved_name: Optional[str] = Field(None, alias="involvedName")
    count: Optional[int] = None
    first_timestamp: Optional[str] = Field(None, alias="firstTimestamp")
    last_timestamp: Optional[str] = Field(None, alias="lastTimestamp")

    class Config:
        allow_population_by_field_name = True
