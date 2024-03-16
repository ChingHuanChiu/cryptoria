from typing import Literal, Optional, Union, Generator, List, Any, Dict

from binance.client import AsyncClient, Client

from src.api.base import APIBase, AsyncAPIBase
from src.common.enum import KLineInterval, HistoricalKlinesType


class MarketDataBase(APIBase):
     ...


class AsyncMarketDataBase(AsyncAPIBase):
    ...
    
class HistoricalTrades(MarketDataBase):

    def __init__(self, client: Client) -> None:
        self.client = client

    def __call__(self, symbol, limit: int = 500) -> List[Dict[str, Any]]:
        """Get older trades.
        Args:
            symbol: symbol
            limit: Default 500; max 1000.
        Returns:
            Example::
            [
                {
                    "id": 28457,
                    "price": "4.00000100",
                    "qty": "12.00000000",
                    "time": 1499865549590,
                    "isBuyerMaker": true,
                    "isBestMatch": true
                }
            ]
        """

        return self.client.get_historical_trades(symbol=symbol, limit=limit)


class HistoricalKlineGenerator(MarketDataBase):
    
    def __init__(self, client: Client) -> None:
        self.client = client

    def __call__(self, symbol: str, 
                 interval: str,
                 start_str: Optional[Union[str, int]] = None, 
                 end_str: Optional[Union[str, int]] = None, 
                 limit=1000,
                 klines_type=HistoricalKlinesType.SPOT
                 ) -> Generator:
        """Get Historical Klines generator from Binance
        Args:
            interval: Binance Kline interval
            start_str: Start date string in UTC format or timestamp in milliseconds
            end_str: end date string in UTC format or timestamp in milliseconds 
                    (default will fetch everything up to now)
            limit: amount of candles to return per request (default 1000)
            klines_type: Historical klines type: SPOT or FUTURES
        
        Returns:
            return the following column data:
            [
                "Open time", 
                "Open", 
                "High", 
                "Low", 
                "Close", 
                "Volume", 
                "Close time", 
                "Quote asset volume", 
                "Number of trades", 
                "Taker buy base asset volume", 
                "Taker buy quote asset volume", 
                "Ignore"
            ]
        """
        return self.client.get_historical_klines_generator(symbol=symbol, 
                                                            interval=interval,
                                                            start_str=start_str,
                                                            end_str=end_str,
                                                            limit=limit,
                                                            klines_type=klines_type)


class LatestSymbolPrice(MarketDataBase):

    def __init__(self, client: Client) -> None:
        super().__init__(client)

    def __call__(self, symbol):

        return self.client.get_symbol_ticker(symbol=symbol)
    

class AsyncMarketDepth(AsyncMarketDataBase):

    def __init__(self, aclient: AsyncClient) -> None:
        super().__init__(aclient)

    async def __call__(self, symbol: str) -> Dict[str, Any] :
        """Latest price for a symbol
        Returns:
            Examples::
                    {
                        "symbol": "LTCBTC",
                        "price": "4.00000200"
                    }
        """

        return await self.aclient.get_order_book(symbol=symbol)
    

class AsyncRecentTrades(AsyncMarketDataBase):

    def __init__(self, aclient: AsyncClient) -> None:
        super().__init__(aclient)

    async def __call__(self, symbol: str) -> List[Dict[str, Any]]:
        """Get recent trades (up to last 500)
        Returns:
            Example::
            [
                {
                    "id": 28457,
                    "price": "4.00000100",
                    "qty": "12.00000000",
                    "time": 1499865549590,
                    "isBuyerMaker": true,
                    "isBestMatch": true
                }
            ]
        """

        return await self.aclient.get_recent_trades(symbol=symbol)


class AsyncAggreTrades(AsyncMarketDataBase):

    def __init__(self, aclient: AsyncClient) -> None:
        super().__init__(aclient)

    async def __call__(self, symbol: str) -> List[Dict[str, Any]]:
        """Get compressed, aggregate trades. Trades that fill at the time,
        from the same order, with the same price will have the quantity aggregated.
        Returns:
            Example::
             [
                {
                    "a": 26129,         # Aggregate tradeId
                    "p": "0.01633102",  # Price
                    "q": "4.70443515",  # Quantity
                    "f": 27781,         # First tradeId
                    "l": 27781,         # Last tradeId
                    "T": 1498793709153, # Timestamp
                    "m": true,          # Was the buyer the maker?
                    "M": true           # Was the trade the best price match?
                }
            ]
        """

        return await self.aclient.get_aggregate_trades(symbol=symbol)
     

class AsyncKline(AsyncMarketDataBase):

    def __init__(self, aclient: AsyncClient) -> None:
        super().__init__(aclient)

    async def __call__(self, symbol: str, 
                      interval: Literal[KLineInterval.KLINE_INTERVAL_1SECOND,
                                        KLineInterval.KLINE_INTERVAL_1MINUTE,
                                        KLineInterval.KLINE_INTERVAL_3MINUTE,
                                        KLineInterval.KLINE_INTERVAL_5MINUTE,
                                        KLineInterval.KLINE_INTERVAL_15MINUTE,
                                        KLineInterval.KLINE_INTERVAL_30MINUTE,
                                        KLineInterval.KLINE_INTERVAL_1HOUR,
                                        KLineInterval.KLINE_INTERVAL_2HOUR,
                                        KLineInterval.KLINE_INTERVAL_4HOUR,
                                        KLineInterval.KLINE_INTERVAL_6HOUR,
                                        KLineInterval.KLINE_INTERVAL_8HOUR,
                                        KLineInterval.KLINE_INTERVAL_12HOUR,
                                        KLineInterval.KLINE_INTERVAL_1DAY,
                                        KLineInterval.KLINE_INTERVAL_3DAY,
                                        KLineInterval.KLINE_INTERVAL_1WEEK,
                                        KLineInterval.KLINE_INTERVAL_1MONTH]) -> List[List[str]]:
        """Kline/candlestick bars for a symbol. Klines are uniquely identified by their open time.
        Returns:
            Example:: [
                [
                    1499040000000,      # Open time
                    "0.01634790",       # Open
                    "0.80000000",       # High
                    "0.01575800",       # Low
                    "0.01577100",       # Close
                    "148976.11427815",  # Volume
                    1499644799999,      # Close time
                    "2434.19055334",    # Quote asset volume
                    308,                # Number of trades
                    "1756.87402397",    # Taker buy base asset volume
                    "28.46694368",      # Taker buy quote asset volume
                    "17928899.62484339" # Can be ignored
                ]
            ]
        """

        return await self.aclient.get_klines(symbol=symbol, interval=interval)

class AsyncAveragePrice(AsyncMarketDataBase):

    def __init__(self, aclient: AsyncClient) -> None:
        super().__init__(aclient)

    async def __call__(self, symbol: str) -> Dict[str, Any]:
        """Current average price for a symbol.
        Returns:
            Example::
                {
                "mins": 5,
                "price": "9.35751834"
            }
        """

        return await self.aclient.get_avg_price(symbol=symbol)
    

class Async24HrTicker(AsyncMarketDataBase):

    def __init__(self, aclient: AsyncClient) -> None:
        """24 hour rolling window price change statistics
        """
        super().__init__(aclient)

    async def __call__(self, symbol: str):

        return await self.aclient.get_ticker(symbol=symbol)
    