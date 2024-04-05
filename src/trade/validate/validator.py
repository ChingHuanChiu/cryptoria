from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional

from binance.helpers import round_step_size

from src.trade.validate.filter import OrderFilterGetter


class OrderValidatorBase(ABC):

    def __init__(self, symbol_info: List[Dict[str, Any]]) -> None:
        self.symbol_info = symbol_info

    @abstractmethod
    def is_valid(self, *args, **kwargs) -> bool:

        raise NotImplementedError("Please overide the 'is_valid' ")

    @abstractmethod
    def get_valid_value(self) -> Any:

        raise NotImplementedError("Please overide the 'get_valid_value' ")


class Price(OrderValidatorBase, OrderFilterGetter):

    def __init__(self, symbol_info: List[Dict[str, Any]]) -> None:
        OrderValidatorBase.__init__(self, symbol_info)
        OrderFilterGetter.__init__(self,symbol_info)
        self.price_filter = self.get_price_filter()

    def is_valid(self, price: float) -> bool:

        if price > float(self.price_filter["maxPrice"]):
            return False
        elif price < float(self.price_filter["minPrice"]):
            return False
        else:
            return True

    def get_valid_value(self, price: str) -> str:

        if self.is_valid(price):
            quote_precision = self.symbol_info['quoteAssetPrecision']
            valid_price = round_step_size(price, self.get_tick_size)
            return "{:0.0{}f}".format(valid_price, quote_precision)

        else:
            raise   

    @property
    def get_tick_size(self) -> float:

        return float(self.price_filter["tickSize"])


class LotSize(OrderValidatorBase, OrderFilterGetter):

    def __init__(self, symbol_info: List[Dict[str, Any]]) -> None:
        OrderValidatorBase.__init__(self, symbol_info)
        OrderFilterGetter.__init__(self, symbol_info)
        self.lot_size_filter = self.get_lot_size()

    def is_valid(self, quantity: str) -> bool:

        if (quantity > float(self.lot_size_filter["maxQty"]))\
            or (quantity < float(self.lot_size_filter["minQty"])):
            return False
            
        else:
            return True
    
    def get_valid_value(self, 
                        balance_equity: Optional[str],
                        cur_market_price: Optional[str],
                        quantity: Optional[str] = None) -> str:
        if quantity is None:
            quant = float(balance_equity) / float(cur_market_price)
        else:
            quant = quantity

        if self.is_valid(quantity=quant):

            if self.get_step_size == 0:
                valid_quant = quant
            else:
                valid_quant = round_step_size(quant, self.get_step_size)
            return valid_quant

        else:
            raise

    @property
    def get_step_size(self) -> float:

        return float(self.lot_size_filter["stepSize"])


class MinNotional(OrderValidatorBase, OrderFilterGetter):

    def __init__(self, symbol_info: List[Dict[str, Any]]) -> None:
        OrderValidatorBase.__init__(symbol_info)
        OrderFilterGetter.__init__(symbol_info)
        self.notional_filter = self.get_notional()

    def is_valid(self, notional: str) -> bool:

        if notional < float(self.notional_filter["minNotional"]):
            return False
        return True

    def get_valid_value(self) -> str:

        return self.min_notional

    @property
    def min_notional(self) -> float:

        return float(self.notional_filter["minNotional"])
