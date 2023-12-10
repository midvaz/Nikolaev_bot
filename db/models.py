import datetime

from sqlalchemy import VARCHAR, Column, Integer, ForeignKey, DateTime, Float, Sequence, Boolean
from sqlalchemy.dialects.postgresql import BIGINT
from sqlalchemy.schema import PrimaryKeyConstraint

from db.metadata import DeclarativeBase

TABLE_ID = Sequence('table_id_seq', start=1)


class Users(DeclarativeBase):
    __tablename__ = "users"

    user_id = Column(BIGINT, primary_key=True, unique=True)
    chat_id = Column(BIGINT, nullable=False)
    is_admin = Column(Boolean, default=False,nullable=True)
    user_name = Column(VARCHAR)


class Wallets(DeclarativeBase):
    __tablename__ = "wallets"

    id = Column(BIGINT, primary_key=True, unique=True)
    user = Column(ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False)
    chain = Column(VARCHAR, nullable=False)
    wallet = Column(VARCHAR, nullable=False)
    w_name = Column(VARCHAR)


class TrackingFlags(DeclarativeBase):
    __tablename__ = "trackingflags"
    user_flag_id = Column(ForeignKey("users.user_id", ondelete="CASCADE"), primary_key=True, unique=True)
    flag = Column(Boolean, default=False)

