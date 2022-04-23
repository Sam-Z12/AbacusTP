from .. import oauth2
from ..database import get_db
from ...crypto_service.api_clients import crypto_client
from ..schemas.schemas import CoinbasePositions
from typing import List, Optional
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ..schemas.coinbase_service_schemas import CandleDetails, CandleResponse

router = APIRouter(
    prefix="/coinbase",
    tags=["Coinbase API"]
)


@router.get("/", response_model=List[CoinbasePositions])
def get_coinbase_positions(db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):
    return crypto_client.find_all_positions()


@router.get("/candles/{product_id}", response_model=List[CandleResponse])
def get_coinbase_candles(product_id: str, db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user), candle_details: Optional[CandleDetails] = None):
    if candle_details:
        candles = crypto_client.get_product_candles(
            product_id, candle_details.start, candle_details.end, candle_details.granularity)
    else:
        candles = crypto_client.get_product_candles(product_id=product_id)

    dict_candles = []
    for candle in candles:
        candle_dict = {
            "timestamp": candle[0],
            "low": candle[1],
            "high": candle[2],
            "open": candle[3],
            "close": candle[4],
            "volume": candle[5]
        }
        dict_candles.append(candle_dict)

    return dict_candles
