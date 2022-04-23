from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from ..config import settings
DB_USERNAME = settings['DATABASE_USERNAME']
DB_PASSWORD = settings['DATABASE_PASSWORD']
DB_HOSTNAME = settings['DATABASE_HOSTNAME']
DB_PORT = settings['DATABASE_PORT']
DB_NAME = settings['DATABASE_NAME']

SQLALCHEMY_DATABASE_URL = f'postgresql://{DB_USERNAME}:{DB_PASSWORD}@{DB_HOSTNAME}:{DB_PORT}/{DB_NAME}'
abacus_api_engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(
    autocommit=False, autoflush=False, bind=abacus_api_engine)

Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
