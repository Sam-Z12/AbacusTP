from .interface import PaperTradingInterface
from . import db_tables
from .database import paper_trade_engine

db_tables.Base.metadata.create_all(bind=paper_trade_engine)

pti = PaperTradingInterface()
