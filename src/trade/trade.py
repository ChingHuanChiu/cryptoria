from abc import ABC, abstractmethod
from typing import Literal

from src.common.enum import PositionStatus, TradingDirection


class AbstractTrade(ABC):

    def __init__(self, 
                 trading_signal: Literal[TradingDirection.BUY, 
                                         TradingDirection.SELL, 
                                         TradingDirection.HOLD]) -> None:

        self.trading_signal = trading_signal
        self.__position_status = None
        
    @abstractmethod
    def long_condition(self, *args, **kwargs) -> bool:
        NotImplementedError("Not Implemented!")

    @abstractmethod
    def short_condition(self, *args, **kwargs) -> bool:
        NotImplementedError("Not Implemented!")

    def stop_loss_condition(self, *args, **kwargs) -> bool:
        """Defalt setting is without stop loss in trading
        """
        return False

    def take_profit_condition(self, *args, **kwargs) -> bool:
        """Defalt setting is without take profit in trading
        """
        return False

    @property
    def position_status(self) -> PositionStatus:
        
        if self.__position_status is None:
            raise ValueError("position stauts is in None status")

        return self.__position_status

    @position_status.setter
    def position_status(self, status: PositionStatus) -> None:

        self.__position_status = status


class LongOnlyTrade(AbstractTrade):

    def __init__(self, 
                 trading_signal: Literal[TradingDirection.BUY, 
                                         TradingDirection.SELL, 
                                         TradingDirection.HOLD]) -> None:
        """only for long trading(can not short the asset) and can not 
        increase position if in position.
        """
        super().__init__(trading_signal)

    def long_condition(self) -> bool:
        """long action for only in empty position and the signal is "BUY"
        """
        
        return (self.trading_signal == TradingDirection["BUY"].value) and\
               (self.position_status == PositionStatus["EMPTY"].value)

    def short_condition(self) -> bool:
        """short action for only in "LONG" position and the signal is "SELL"
        """

        return (self.trading_signal == TradingDirection["SELL"]) and\
               (self.position_status == PositionStatus["LONG"])

    def stop_loss_condition(self) -> bool:
        """must with stop loss in the trading
        """
        return True