from typing import List, Dict, Any


class OrderFilterGetter:

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