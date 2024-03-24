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

    def stop_loss_condition(self) -> bool:
        """Defalt setting is without stop loss in trading
        """
        return False

    def take_profit_condition(self) -> bool:
        """Defalt setting is without take profit in trading
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

    def __init__(self) -> None:
        """only for long trading(can not short the asset) and can not 
        increase position if in position.
        """
        super().__init__()

    def long_condition(self) -> bool:
        """long action for only in empty position and the signal is "BUY"
        """
        
        return (self.trading_side == TradingDirection["BUY"].value) and\
               (self.position_status == PositionStatus["EMPTY"].value)

    def short_condition(self) -> bool:
        """short action for only in "LONG" position and the signal is "SELL"
        """

        return (self.trading_side == TradingDirection["SELL"]) and\
               (self.position_status == PositionStatus["LONG"])

    def stop_loss_condition(self) -> bool:
        """must with stop loss in the trading
        """
        return True