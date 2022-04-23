from fastapi import APIRouter, Depends
from starlette.status import HTTP_201_CREATED, HTTP_204_NO_CONTENT, HTTP_404_NOT_FOUND, HTTP_403_FORBIDDEN
from abacus_server.paper_trading_service.startup import pti
from abacus_server.models.paper_trade_models import CreateAccount, BuyRequest, SellRequest
from .. import oauth2
router = APIRouter(
    prefix="/paper",
    tags=['Paper'])


@router.get("/",)
def get_current_positions(current_user: int = Depends(oauth2.get_current_user)):
    positions = pti.current_positions()
    return positions


@router.post("/buy")
def buy_request(buy_request: BuyRequest, current_user: int = Depends(oauth2.get_current_user)):
    buy_reponse = pti.submit_buy_order(
        buy_order=buy_request.dict())
    return buy_reponse


@router.post("/sell")
def sell_request(sell_request: SellRequest, current_user: int = Depends(oauth2.get_current_user)):
    sell_response = pti.submit_sell_order(
        sell_order=sell_request.dict())
    return sell_response


@router.put("/fund/{value}")
def add_funds(value: float, current_user: int = Depends(oauth2.get_current_user)):
    new_value = pti.add_funds(value)
    return {"New Cash Value": new_value}


@router.put("/withdraw/{value}")
def remove_funds(value: float, current_user: int = Depends(oauth2.get_current_user)):
    new_value = pti.remove_funds(value)
    return {"New Cash Value": new_value}


@router.post("/create")
def create_account(account: CreateAccount, current_user: int = Depends(oauth2.get_current_user)):
    new_account = pti.create_account(
        account_id=account.account_id, funds=account.funds)
    return new_account


@router.put("/login/{account_id}")
def login(account_id: int, current_user: int = Depends(oauth2.get_current_user)):
    active_account = pti.login(account_id=account_id)
    return {"New Active Account": active_account}
