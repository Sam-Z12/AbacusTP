
from ..global_events import global_events_manager
from .database import PaperTradeDB
from . import db_tables
from sqlalchemy.orm import Session
import sqlalchemy
import datetime
from statistics import mean
from pydantic import validate_arguments
from ..models.paper_trade_models import PaperTradeRequest, BuyRequest, SellRequest
from pathlib import Path
import asyncio


"""
Make Paper Trade Order:

buy_order = {
    "ticker": "stocky",
    "buy_price": 20.00,
    "quantity": 10,
}

t_func = {
    "name": 'submit_buy_order',
    "kwargs": {buy_order: buy_order}
}
# ptr = PaperTradeRequest(target_function=t_func)

# global_events_manager.send_signal(
#     service_name='paper_trading_service', sender='me', message=ptr)


"""

class PaperTradingInterface():
    def __init__(self, db=PaperTradeDB):
        # self.input_signal = input_signal
        parent_dir_name = Path(__file__).parent.name
        global_events_manager.connect(
            self.reciever, f'{parent_dir_name}')
        self.db = db
        if self.table_is_empty(table=db_tables.Account):
            self.create_account(account_id=1, funds=0)
        self._active_account_id = 1

    @validate_arguments
    def reciever(self, sender, signal, message: PaperTradeRequest):

        try:
            message_dict = message.dict()
            target_function = self.__getattribute__(
                message_dict['target_function']['name'])

            def _run_target_func(function, **kwargs):
                return function(**kwargs)
            results = _run_target_func(
                function=target_function, **message_dict['target_function']['kwargs'])

            return results
        except Exception as e:
            print(f"ERROR: {e}, could not complete paper trade request")

    def table_is_empty(self, table):
        with self.db() as db:
            first_element = db.query(table).first()
        if not first_element:
            return True
        else:
            return False

    def submit_buy_order(self, buy_order: dict):
        """ Check if enough funds
            Add buy order to BuyOrder table 
            Update the ActivePositions table"""
        try:
            ticker = buy_order['ticker']
            total_trade_value = buy_order['buy_price'] * buy_order['quantity']

            with self.db() as db:
                current_cash_query = db.query(db_tables.Account.cash).filter(
                    db_tables.Account.account_id == self._active_account_id)
                current_cash = current_cash_query.first()[0]
                if total_trade_value > current_cash:
                    raise NotEnoughFundsError(
                        "Do not have enough funds to place this order")

                buy_order['total_value'] = total_trade_value
                buy_order['account_id'] = self._active_account_id

                new_order = db_tables.BuyOrders(**buy_order)
                db.add(new_order)
                active_position_query = db.query(db_tables.ActivePositions).filter(
                    db_tables.ActivePositions.ticker == ticker)
                active_position = active_position_query.first()
                if active_position is None:
                    new_position_dict = {"ticker": ticker,
                                         "avg_buy_price": buy_order['buy_price'],
                                         "quantity": buy_order['quantity'],
                                         "total_value": total_trade_value,
                                         "account_id": self._active_account_id}
                    new_position = db_tables.ActivePositions(
                        **new_position_dict)
                    db.add(new_position)

                else:
                    prev_quantity = db.query(db_tables.ActivePositions.quantity).filter(
                        db_tables.ActivePositions.ticker == ticker).first()[0]

                    prev_total_value = db.query(db_tables.ActivePositions.total_value).filter(
                        db_tables.ActivePositions.ticker == ticker).first()[0]

                    new_quantity = prev_quantity + buy_order['quantity']
                    new_total_value = prev_total_value + total_trade_value
                    new_avg_buy_price = new_total_value / new_quantity

                    new_position_dict = {"ticker": ticker,
                                         "avg_buy_price": new_avg_buy_price,
                                         "quantity": new_quantity,
                                         "total_value": new_total_value}
                    active_position_query.update(new_position_dict)

                account_query = db.query(db_tables.Account).filter(
                    db_tables.Account.account_id == self._active_account_id)
                account_query.update(
                    {"cash": current_cash - total_trade_value})

                db.commit()
                db.refresh(new_order)
            return new_order

        except Exception as e:
            print(f"ERROR: {e}, could not submit paper buy order")

    # Need to delete position if selling all shares
    def submit_sell_order(self, sell_order: dict):
        """Add to SellOrders table
            Update ActivePositions table"""
        try:
            ticker = sell_order['ticker']
            with self.db() as db:
                shares_holding_query = db.query(db_tables.ActivePositions.quantity).filter(
                    db_tables.ActivePositions.ticker == ticker)
                shares_holding = db.execute(
                    shares_holding_query).first()

                if not shares_holding:
                    raise NoSharesHoldingError(
                        f"Not holding any shares of {ticker}")
                shares_holding = shares_holding[0]

                if shares_holding < sell_order['quantity']:
                    raise NotEnoughSharesError(
                        f"Tried to sell {sell_order['quantity']} shares of {ticker} but only have {shares_holding}")

                avg_buy_price = db.query(db_tables.ActivePositions.avg_buy_price).filter(
                    db_tables.ActivePositions.ticker == ticker).first()[0]
                active_position_query = db.query(db_tables.ActivePositions).filter(
                    db_tables.ActivePositions.ticker == ticker)

                if shares_holding == sell_order['quantity']:
                    active_position_query.delete(synchronize_session=False)

                else:
                    new_quantity = shares_holding - sell_order['quantity']
                    new_total_value = new_quantity * avg_buy_price
                    new_position_dict = {
                        "quantity": new_quantity,
                        "total_value": new_total_value
                    }
                    active_position_query.update(new_position_dict)

                sell_order['buy_price'] = avg_buy_price

                sell_order['profit'] = (
                    sell_order['sell_price'] - avg_buy_price) * sell_order['quantity']

                sell_order['percent_profit'] = (sell_order['profit'] /
                                                (sell_order['quantity'] * avg_buy_price)) * 100
                sell_order['account_id'] = self._active_account_id

                new_sell_order = db_tables.SellOrders(**sell_order)
                db.add(new_sell_order)

                current_cash_query = db.query(db_tables.Account.cash).filter(
                    db_tables.Account.account_id == self._active_account_id)
                current_cash = current_cash_query.first()[0]
                sell_value = sell_order["quantity"] * sell_order["sell_price"]

                account_query = db.query(db_tables.Account).filter(
                    db_tables.Account.account_id == self._active_account_id)

                account_query.update({"cash": current_cash + sell_value})

                db.commit()
            return sell_order
        except Exception as e:
            print(f"ERROR: {e}, could not place paper sell order")

    def create_account(self, account_id, funds):
        try:
            with self.db() as db:
                account = db.query(db_tables.Account).filter(
                    db_tables.Account.account_id == account_id).first()
                if account:
                    raise AccountAlreadyExistsError(
                        f"Account with account_id {account_id} already exists")

                account_data = {"account_id": account_id,
                                "cash": funds}
                new_account = db_tables.Account(**account_data)
                db.add(new_account)
                db.commit()
                db.refresh(new_account)
            return account_data
        except Exception as e:
            print(f"ERROR: {e}, could not create account")

    def current_positions(self, dict_format: bool = True):
        with self.db() as db:

            account_positions = db.query(db_tables.ActivePositions).filter(
                db_tables.ActivePositions.account_id == self._active_account_id).all()

        def position_parser(positions: list):
            current_cash_query = db.query(db_tables.Account.cash).filter(
                db_tables.Account.account_id == self._active_account_id)
            current_cash = current_cash_query.first()[0]

            positions_dict = {'active account': self._active_account_id,
                              'cash': current_cash,
                              'number_of_position': len(positions),
                              'positions': []}

            for position in positions:
                position_dict = {}
                position_dict['ticker'] = position.ticker
                position_dict['quantity'] = position.quantity
                position_dict['avg_buy_price'] = position.avg_buy_price
                position_dict['entry_date'] = position.time.isoformat()
                positions_dict['positions'].append(position_dict)

            return positions_dict

        if dict_format:
            return position_parser(account_positions)
        else:
            return account_positions

    def login(self, account_id):
        try:

            with self.db() as db:
                account = db.query(db_tables.Account).filter(
                    db_tables.Account.account_id == account_id).first()

            if not account:
                raise AccountDoesNotExistError(
                    f"Account with account_id {account_id} does not exist")

            self._active_account_id = account_id
            return self._active_account_id
        except Exception as e:
            print(f"ERROR: {e}, could not login")

    def add_funds(self, value: int):
        try:
            with self.db() as db:
                current_cash = db.query(db_tables.Account.cash).filter(
                    db_tables.Account.account_id == self._active_account_id).first()[0]
                new_cash_value = current_cash + value
                active_account_query = db.query(db_tables.Account).filter(
                    db_tables.Account.account_id == self._active_account_id)
                active_account_query.update({"cash": new_cash_value})
                db.commit()
            return new_cash_value
        except Exception as e:
            print(f"ERROR: {e}, could not add funds")

    def remove_funds(self, value: float):
        try:
            with self.db() as db:
                current_cash = db.query(db_tables.Account.cash).filter(
                    db_tables.Account.account_id == self._active_account_id).first()[0]

                if current_cash >= value:
                    new_cash_value = current_cash - value
                    active_account_query = db.query(db_tables.Account).filter(
                        db_tables.Account.account_id == self._active_account_id)

                    active_account_query.update({"cash": new_cash_value})
                    db.commit()

                else:
                    raise NotEnoughFundsError(
                        f"Tried to remove {value} but current account balance is {current_cash}")

            return new_cash_value
        except Exception as e:
            print(f"ERROR {e} could not remove funds")

    def current_value(self):
        pass

    def trade_history(self):
        pass

    def test(self):
        print("Paper Trade Test")


class NotEnoughFundsError(Exception):
    """Is raised when trying to use more funds than are in the account"""
    pass


class NoSharesHoldingError(Exception):
    """Is raised when a sell order is placed for a stock that is not owned"""
    pass


class NotEnoughSharesError(Exception):
    """Is raised when a sell order is placed for more shares of a stock then are currently held"""
    pass


class AccountAlreadyExistsError(Exception):
    """Is raised when trting to create an account with an already existing account_id"""
    pass


class AccountDoesNotExistError(Exception):
    """Is raised when trying to login to an account that does not exist"""
    pass
