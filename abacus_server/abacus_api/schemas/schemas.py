from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional


class CoinbasePositions(BaseModel):
    id: str
    currency: str
    balance: str
    available: str
    hold: str
    profile_id: str


class UserOut(BaseModel):
    id: int
    email: str
    created_at: datetime

    # converts model to dict
    class Config:
        orm_mode = True


class UserCreate(BaseModel):
    email: EmailStr
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    id: Optional[str] = None
