from .database import Base
from sqlalchemy import Column, String, Integer, Float, ForeignKey
from sqlalchemy.sql.sqltypes import TIMESTAMP
from sqlalchemy.sql.expression import text
from sqlalchemy.orm import relationship


class ActivePositions(Base):
    __tablename__ = "active_positions"
    id = Column(Integer, primary_key=True, nullable=False)
    ticker = Column(String,  nullable=False)
    avg_buy_price = Column(Float, nullable=False)
    quantity = Column(Integer, nullable=False)
    total_value = Column(Float, nullable=False)
    account_id = Column(Integer,  ForeignKey(
        'account.account_id'), nullable=False)
    time = Column(TIMESTAMP(timezone=True),
                  nullable=False, server_default=text('now()'))


class BuyOrders(Base):
    __tablename__ = "buy_orders"
    id = Column(Integer, primary_key=True, nullable=False)
    ticker = Column(String,  nullable=False)
    buy_price = Column(Float, nullable=False)
    quantity = Column(Integer, nullable=False)
    total_value = Column(Float, nullable=False)
    account_id = Column(Integer,  ForeignKey(
        'account.account_id'), nullable=False)
    time = Column(TIMESTAMP(timezone=True),
                  nullable=False, server_default=text('now()'))


class SellOrders(Base):
    __tablename__ = "sell_orders"
    id = Column(Integer, primary_key=True, nullable=False)
    ticker = Column(String, nullable=False)
    buy_price = Column(Float, nullable=False)
    sell_price = Column(Float, nullable=False)
    quantity = Column(Integer, nullable=False)
    profit = Column(Float, nullable=False)
    percent_profit = Column(Float, nullable=False)
    account_id = Column(Integer,  ForeignKey('account.account_id'))
    time = Column(TIMESTAMP(timezone=True),
                  nullable=False, server_default=text('now()'))


class Account(Base):
    __tablename__ = "account"
    account_id = Column(Integer, primary_key=True, nullable=False)
    cash = Column(Float, nullable=False)
    sell_orders = relationship("SellOrders")
    buy_orders = relationship("BuyOrders")
    active_positions = relationship("ActivePositions")
