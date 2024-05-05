from typing import Dict, List

from sqlalchemy import Column, String, DateTime, DECIMAL, Integer
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
# from sqlalchemy.ext.asyncio import AsyncAttrs


Base = declarative_base()


class Inference(Base):

    __tablename__ = "inference"
    id = Column(Integer, primary_key=True, autoincrement=True)
    infer_time =  mapped_column(DateTime, nullable=False)
    symbol: Mapped[str] = mapped_column(nullable=False)
    prediction: Mapped[str] = mapped_column(String)
    model_version: Mapped[str] = mapped_column(String)

class TransactionRecord(Base):
    __tablename__ = "transactionrecord"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    orderId: Mapped[str] = mapped_column(String)
    symbol: Mapped[str] = mapped_column(String)
    transactTime = mapped_column(DateTime)
    price: Mapped[float] = mapped_column(DECIMAL)
    origQty: Mapped[float] = mapped_column(DECIMAL)
    executedQty: Mapped[float] = mapped_column(DECIMAL)
    cummulativeQuoteQty: Mapped[float] = mapped_column(DECIMAL)
    qty: Mapped[float] = mapped_column(DECIMAL)
    commission: Mapped[float] = mapped_column(DECIMAL)
    commissionAsset: Mapped[str] = mapped_column(String)
    status: Mapped[str] = mapped_column(String)
    timeInForce : Mapped[str] = mapped_column(String)
    type: Mapped[str] = mapped_column(String)
    side: Mapped[str] = mapped_column(String)

class Asset(Base):

    __tablename__ = "asset"
    id = Column(Integer, primary_key=True, autoincrement=True)
    update_time =  mapped_column(DateTime)
    symbol: Mapped[str] = mapped_column()
    amount: Mapped[float] = mapped_column(DECIMAL)