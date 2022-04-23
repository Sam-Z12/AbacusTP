from pydantic import BaseModel, EmailStr, FloatError
from datetime import datetime
from typing import Optional


class CandleDetails(BaseModel):
    start: str = None
    end: str = None
    granularity: int = None


class CandleResponse(BaseModel):
    timestamp: int
    low: float
    high: float
    open: float
    close: float
    volume: float
