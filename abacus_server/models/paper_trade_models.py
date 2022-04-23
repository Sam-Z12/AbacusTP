from pydantic import BaseModel, Field


class TargetFunction(BaseModel):
    name: str
    kwargs: dict


class PaperTradeRequest(BaseModel):
    target_function: TargetFunction = Field(
        name="",
        kwargs={}
    )


class CreateAccount(BaseModel):
    account_id: int
    funds: float


class BuyRequest(BaseModel):
    ticker: str
    quantity: int
    buy_price: float


class SellRequest(BaseModel):
    ticker: str
    quantity: int
    sell_price: float
