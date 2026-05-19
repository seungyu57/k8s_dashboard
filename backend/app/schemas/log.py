from typing import Optional

from pydantic import BaseModel, Field


class PodLogResponse(BaseModel):
    namespace: str
    pod: str
    container: Optional[str] = None
    tail_lines: int = Field(..., alias="tailLines")
    logs: str
    truncated: bool = False

    class Config:
        allow_population_by_field_name = True
