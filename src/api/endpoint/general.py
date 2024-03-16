from typing import Dict, Union, Any

from binance.client import Client

from src.api.base import APIBase


class GeneralBase(APIBase):
     ...


class SystemStatus(GeneralBase):

    def __init__(self, client: Client) -> None:
        super().__init__(client)

    def __call__(self) -> Dict[str, Union[int, str]]:
        """get the system statue for the api client
        Returns:
            Example::
            {'status': 0, 'msg': 'normal'}
        """
        return self.client.get_system_status()
    

class SymbolInfo(GeneralBase):

    def __init__(self, client: Client) -> None:
        super().__init__(client)

    def __call__(self, symbol: str) -> Dict[str, Any]:
        """get the information of symbol
        Returns:
            Example::
            {
                'symbol': 'BTCUSDT',
                'status': 'TRADING',
                'baseAsset': 'BTC',
                'baseAssetPrecision': 8,
                'quoteAsset': 'USDT',
                'quotePrecision': 8,
                'quoteAssetPrecision': 8,
                'baseCommissionPrecision': 8,
                'quoteCommissionPrecision': 8,
                'orderTypes': ['LIMIT',
                'LIMIT_MAKER',
                'MARKET',
                'STOP_LOSS_LIMIT',
                'TAKE_PROFIT_LIMIT'],
                'icebergAllowed': True,...
            }
        """

        symbol_info = self.client.get_symbol_info(symbol=symbol)

        return symbol_info
        