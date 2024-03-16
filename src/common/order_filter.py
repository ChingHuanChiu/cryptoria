from typing import List, Dict, Any
from abc import ABC, abstractmethod
# from src.api.endpoint.general import SymbolInfo

class _OrderFilterGetter:

    def __init__(self, symbol_info: List[Dict[str, Any]]) -> None:
        self.filters = symbol_info["filters"]

    def get_price_filter(self):

        return self.get_filters_by_type("PRICE_FILTER")
    
    def get_lot_size(self):

        return self.get_filters_by_type("LOT_SIZE")
    
    def get_notional(self):

        return self.get_filters_by_type("NOTIONAL")
    
    def get_market_lot_size(self):

        return self.get_filters_by_type("MARKET_LOT_SIZE")

    def get_filters_by_type(self, type: str) -> Dict[str, Any]:

        res = [_dict for _dict in self.filters if _dict["filterType"] == type][0]

        return res

    
class OrderFilterBase(ABC, _OrderFilterGetter):

    def __init__(self, symbol_info: List[Dict[str, Any]]) -> None:
        super().__init__(symbol_info)
    
    @abstractmethod
    def pass_filter(self, *args, **keargs) -> bool:
        raise NotImplementedError("Not Implemented")
        

class PriceFilter(OrderFilterBase):

    def __init__(self, symbol_info: List[Dict[str, Any]]) -> None:
        super().__init__(symbol_info)

        self.price_filter = self.get_price_filter()

    def pass_filter(self, price: float):
        
        if price > float(self.price_filter["maxPrice"]):
            return False
        elif price < float(self.price_filter["minPrice"]):
            return False
        else:
            return True
        
    @property
    def get_tick_size(self) -> float:

        return float(self.price_filter["tickSize"])


class MarketLotSizeFilter(OrderFilterBase):
    """ defines rules around Market orders for a symbol
    """

    def __init__(self, symbol_info: List[Dict[str, Any]]) -> None:
        super().__init__(symbol_info)

        self.market_lot_size_filter = self.get_market_lot_size()
    
    def pass_filter(self, quantity: float):

        if quantity > float(self.market_lot_size_filter["maxQty"]):
            return False
        elif quantity < float(self.market_lot_size_filter["minQty"]):
            return False
        else:
            return True
    
    @property
    def get_step_size(self) -> float:

        return float(self.market_lot_size_filter["stepSize"])


class LotSizeFilter(OrderFilterBase):

    def __init__(self, symbol_info: List[Dict[str, Any]]) -> None:
        super().__init__(symbol_info)

        self.lot_size_filter = self.get_lot_size()

    def pass_filter(self, quantity):

        if quantity > float(self.lot_size_filter["maxQty"]):
            return False
        elif quantity < float(self.lot_size_filter["minQty"]):
            return False
        else:
            return True
        
    @property
    def get_step_size(self) -> float:

        return float(self.lot_size_filter["stepSize"])


class MinNotionalFilter(OrderFilterBase):

    def __init__(self, symbol_info: List[Dict[str, Any]]) -> None:
        super().__init__(symbol_info)
        self.notional_filter = self.get_notional()

    def pass_filter(self, notional: float):

        if notional < float(self.notional_filter["minNotional"]):
            return False
        return True

    @property
    def is_apply_min_to_market(self) -> bool:

        return bool(self.notional_filter["applyMinToMarket"])
    
    @property
    def min_notional(self) -> float:

        return float(self.notional_filter["minNotional"])
        


    


