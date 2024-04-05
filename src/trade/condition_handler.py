from abc import ABC, abstractmethod
from typing import Literal

from src.common.enum import PositionStatus, TradingDirection


class TradeConditionHandler(ABC):

    def __init__(self) -> None:

        self.__trading_side = None
        self.__position_status = PositionStatus["EMPTY"].value
        
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

        return self.__position_status

    @position_status.setter
    def position_status(self, status: PositionStatus) -> None:

        self.__position_status = status

    
    @property
    def trading_side(self) -> Literal[TradingDirection.BUY, 
                                      TradingDirection.SELL, 
                                      TradingDirection.HOLD]:
                
        return self.__trading_side

    @trading_side.setter
    def trading_side(self, side) -> None:
        self.__trading_side = side
        

class LongOnlyTradeConditionHandler(TradeConditionHandler):
    """Only for long trading (cannot short the asset) and 
    cannot increase position if already in position.
    """

    def __init__(self) -> None:

        super().__init__()

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

        return True

    def take_profit_condition(self) -> bool:
        return False