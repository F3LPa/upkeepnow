import os
from typing import Generator, Optional

import sqlalchemy as sa
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.future.engine import Engine
from dotenv import load_dotenv

from models.model_base import Base

__engine: Optional[Engine] = None


def create_engine() -> Engine:
    """
    configura conexao com BD
    """
    global __engine

    if __engine:
        return

    load_dotenv()

    DB_USER = os.getenv("DB_USER")
    DB_PASSWORD = os.getenv("DB_PASSWORD")
    DB_HOST = os.getenv("DB_HOST")
    DB_PORT = os.getenv("DB_PORT")
    DB_NAME = os.getenv("DB_NAME")

    CONN_STR = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    __engine = sa.create_engine(url=CONN_STR, echo=False)

    return __engine


def create_session() -> Generator[Session, None, None]:
    global __engine

    if not __engine:
        create_engine()

    SessionLocal = sessionmaker(bind=__engine, expire_on_commit=False, class_=Session)

    db: Session = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def create_tables() -> None:
    global __engine

    if not __engine:
        create_engine()

    Base.metadata.drop_all(__engine)
    Base.metadata.create_all(__engine)
