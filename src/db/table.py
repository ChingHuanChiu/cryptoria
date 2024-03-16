from typing import Dict, List

from sqlalchemy import Column, String, DateTime, DECIMAL, Integer
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
# from sqlalchemy.ext.asyncio import AsyncAttrs

class Base(DeclarativeBase):
    pass

class Inference(Base):

    __tablename__ = "inference"
    id = Column(Integer, primary_key=True, autoincrement=True)
    infer_time =  mapped_column(DateTime, nullable=False)
    symbol: Mapped[str] = mapped_column(nullable=False)
    prediction: Mapped[str] = mapped_column(String)
    model_version: Mapped[str] = mapped_column(String)

class TransactionRecord(Base):
    #TODO: create the  column of commission
    __tablename__ = "transactionrecord"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    symbol: Mapped[str] = mapped_column(String)
    transacttime = mapped_column(DateTime)
    price: Mapped[float] = mapped_column(DECIMAL)
    origqty: Mapped[float] = mapped_column(DECIMAL)
    executedqty: Mapped[float] = mapped_column(DECIMAL)
    cummulativequoteqty: Mapped[float] = mapped_column(DECIMAL)
    status: Mapped[str] = mapped_column(String)
    timeinforce : Mapped[str] = mapped_column(String)
    type: Mapped[str] = mapped_column(String)
    side: Mapped[str] = mapped_column(String)

class Asset(Base):

    __tablename__ = "asset"
    id = Column(Integer, primary_key=True, autoincrement=True)
    update_time =  mapped_column(DateTime)
    symbol: Mapped[str] = mapped_column()
    amount: Mapped[float] = mapped_column(DECIMAL)



