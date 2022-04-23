from sqlalchemy import create_engine
from sqlalchemy_utils import create_database, database_exists
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from ..config import settings

DB_USERNAME = settings['DATABASE_USERNAME']
DB_PASSWORD = settings['DATABASE_PASSWORD']
DB_HOSTNAME = settings['DATABASE_HOSTNAME']
DB_PORT = settings['DATABASE_PORT']
DB_NAME = settings['PAPER_DATABASE_NAME']

SQLALCHEMY_DATABASE_URL = f'postgresql://{DB_USERNAME}:{DB_PASSWORD}@{DB_HOSTNAME}:{DB_PORT}/{DB_NAME}'
paper_trade_engine = create_engine(SQLALCHEMY_DATABASE_URL)
if not database_exists(url=paper_trade_engine.url):
    create_database(paper_trade_engine.url)
PaperSession = sessionmaker(
    autocommit=False, autoflush=False, bind=paper_trade_engine)

Base = declarative_base()


class PaperTradeDB:
    def __init__(self) -> None:
        self.db = PaperSession()

    def __enter__(self):
        return self.db

    def __exit__(self, exc_type, exc_value, exc_traceback):
        self.db.close()


# def get_db():
#     db = PaperSession()
#     try:
#         yield db
#     finally:
#         db.close()
