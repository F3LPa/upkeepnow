from typing import Optional

import sqlalchemy as sa
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.future.engine import Engine

from models.model_base import Base

__engine: Optional[Engine] = None


def create_engine(sqlite: bool = False) -> Engine:
    """
    configura conexao com BD
    """
    global __engine

    if __engine:
        return

    conn_str = "jdbc:mysql://localhost:3306/upkeepnow"
    __engine = sa.create_engine(url=conn_str, echo=False)

    return __engine


def create_session() -> None:
    global __engine

    if not __engine:
        create_engine()

    __session = sessionmaker(__engine, expire_on_commit=False, class_=Session)

    return Session


def create_tables() -> None:
    global __engine

    if not __engine:
        create_engine()

    Base.metadata.drop_all(__engine)
    Base.metadata.create_all(__engine)
