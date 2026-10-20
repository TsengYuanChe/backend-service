from typing import Literal
from uuid import UUID

from pydantic import BaseModel, Field, field_validator


class WebsiteVisitCreate(BaseModel):
    site_key: Literal["adamtseng", "andessence"]
    visitor_id: UUID
    page_path: str = Field(min_length=1, max_length=2048)

    @field_validator("page_path")
    @classmethod
    def validate_page_path(cls, value: str) -> str:
        if not value.startswith("/") or value.startswith("//"):
            raise ValueError("page_path must start with a single /")
        if "?" in value or "#" in value:
            raise ValueError("page_path must not contain query or fragment")
        return value
    

class WebsiteVisitPeriodStats(BaseModel):
    yearly: int
    monthly: list[int]
    daily: list[int]


class WebsiteVisitStatsResponse(BaseModel):
    site_key: str
    year: int
    month: int
    pages: dict[str, WebsiteVisitPeriodStats]
    
    
    