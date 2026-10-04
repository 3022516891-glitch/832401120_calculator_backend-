from datetime import datetime
from typing import Literal
from pydantic import BaseModel, Field


class CalculationRequest(BaseModel):
    expression: str = Field(min_length=1, max_length=500)
    angle_mode: Literal["DEG", "RAD"] = "DEG"


class CalculationResponse(BaseModel):
    success: bool = True
    expression: str
    result: int | float


class HistoryRecord(BaseModel):
    id: int
    expression: str
    result: int | float
    is_favorite: bool
    created_at: datetime
    angle_mode: str = "DEG"
    note: str = ""
    tag: str = ""


class FavoriteRequest(BaseModel):
    is_favorite: bool


class HistoryMetadataRequest(BaseModel):
    note: str = Field(default="", max_length=200)
    tag: str = Field(default="", max_length=30)


class BatchDeleteRequest(BaseModel):
    ids: list[int] = Field(min_length=1, max_length=100)


class HistoryPage(BaseModel):
    items: list[HistoryRecord]
    total: int
    page: int
    page_size: int
