from abc import ABC, abstractmethod
from typing import Literal

from src.common.enum import PositionStatus, TradingDirection
from src.api.endpoint.account import AssetBalance


class TradeConditionHandler(ABC):

    def __init__(self, asset: str) -> None:

        self.asset = asset

        self.__trading_side = None
        self.__asset_balance_obj = None
        
    @abstractmethod
    def long_condition(self, *args, **kwargs) -> bool:
        NotImplementedError("Not Implemented!")

    @abstractmethod
    def short_condition(self, *args, **kwargs) -> bool:
        NotImplementedError("Not Implemented!")

    @abstractmethod
    def stop_loss_condition(self) -> bool:

        """
        Check if the stop loss condition for trading is met.

        Returns:
            bool: True if the stop loss condition is met, False otherwise.
        """
        return False

    @abstractmethod
    def take_profit_condition(self) -> bool:
        """
        Check if the take profit condition for trading is met.

        Returns:
            bool: True if the take profit condition is met, False otherwise.
        """
        return False

    @property
    def position_status(self) -> PositionStatus:
        #TODO: check what will the asset_balance is if in the short position
        # call AssetBalance API
        balance = self.asset_balance_obj(asset=self.asset)
        balance = float(balance)
        print(88888888, balance, f"USDT:{self.asset_balance_obj(asset='USDT')}")
        if balance == 0:

            return PositionStatus["EMPTY"].value

        elif balance > 0:

            return PositionStatus["LONG"].value
    
    @property
    def trading_side(self) -> Literal[TradingDirection.BUY, 
                                      TradingDirection.SELL, 
                                      TradingDirection.HOLD]:
                
        return self.__trading_side

    @trading_side.setter
    def trading_side(self, side) -> None:
        self.__trading_side = side

    @property
    def asset_balance_obj(self) -> AssetBalance:
        
        return self.__asset_balance_obj
    
    @asset_balance_obj.setter
    def asset_balance_obj(self, value: AssetBalance) -> None:

        self.__asset_balance_obj = value
        
        
class LongOnlyTradeConditionHandler(TradeConditionHandler):
    """Only for long trading (cannot short the asset) and 
    cannot increase position if already in position.
    """

    def __init__(self, asset: str) -> None:

        super().__init__(asset)

    def long_condition(self) -> bool:
        """
        Check if the long action is permissible, 
        only when the position is empty and the signal is "BUY".

        Returns:
            bool: True if the long condition is met, False otherwise.
        """
        
        return (self.trading_side == TradingDirection["BUY"].value) and\
               (self.position_status == PositionStatus["EMPTY"].value)

    def short_condition(self) -> bool:
        """
        Check if the short action is permissible, only when the position is "LONG" and the signal is "SELL".

        Returns:
            bool: True if the short condition is met, False otherwise.
        """
        return (self.trading_side == TradingDirection["SELL"].value) and\
               (self.position_status == PositionStatus["LONG"].value)

    def stop_loss_condition(self) -> bool:
        
        return self.position_status == PositionStatus["LONG"].value

    def take_profit_condition(self) -> bool:
        return False