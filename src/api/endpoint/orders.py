from typing import Any, Literal, Union, Dict, List

from binance.enums import *
from binance.client import AsyncClient, Client

from src.api.base import APIBase, AsyncAPIBase
from src.common.enum import TradingDirection, OrderType


class OrderBase(APIBase):
     ...


class AsyncOrderBase(AsyncAPIBase):
     ...


class OpenOrdersGetter(OrderBase):

     def __init__(self, client: Client) -> None:
         super().__init__(client)
     
     def __call__(self, symbol: str) -> List[Dict[str, Any]]:
          """get the infomation of open order
          Returns:
               Example::
               [{
                    'symbol': 'BTCUSDT',
                    'orderId': 13419318,
                    'orderListId': -1,
                    'clientOrderId': '8MTUcB1xMryyi73ctaNpx6',
                    'price': '50000.00000000',
                    'origQty': '0.01000000',
                    'executedQty': '0.00000000',
                    'cummulativeQuoteQty': '0.00000000',
                    'status': 'NEW',
                    'timeInForce': 'GTC',
                    'type': 'STOP_LOSS_LIMIT',
                    'side': 'SELL',
                    'stopPrice': '60000.00000000',
                    'icebergQty': '0.00000000',
                    'time': 1710071846183,
                    'updateTime': 1710071846183,
                    'isWorking': False,
                    'workingTime': -1,
                    'origQuoteOrderQty': '0.00000000',
                    'selfTradePreventionMode': 'EXPIRE_MAKER'
               }]
          """

          orders = self.client.get_open_orders(symbol=symbol)
          return orders
     

class AllOrdersGetter(OrderBase):

     def __init__(self, client: Client) -> None:
         super().__init__(client)
     
     def __call__(self, symbol: str) -> List[Dict[str, Any]]:
          """get the history orders
          """
          orders = self.client.get_all_orders(symbol=symbol)
          return orders
     

class AOpenOrdersGetter(AsyncOrderBase):

     def __init__(self, aclient: AsyncClient) -> None:
          super().__init__(aclient)

     async def __call__(self, symbol: str) -> List[Dict[str, Any]]:

          return await self.aclient.get_open_orders(symbol=symbol)
AOpenOrdersGetter.__call__.__doc__ = OpenOrdersGetter.__call__.__doc__


class ALimitOrderSender(AsyncOrderBase):

    def __init__(self, aclient: AsyncClient) -> None:
         super().__init__(aclient)

    async def __call__(self, 
                       symbol: str, 
                       quantity: float, 
                       price: str, 
                       side: Literal[TradingDirection.BUY, TradingDirection.SELL]
                       ):
            
    
          if side == TradingDirection["BUY"].value:
               order = self.aclient.order_limit_buy(
                                                symbol=symbol,
                                                quantity=quantity,
                                                price=price)
                
          elif side == TradingDirection["SELL"].value:

               order = self.aclient.order_limit_sell(
                                                symbol=symbol,
                                                quantity=quantity,
                                                price=price)
            
          else:
               raise ValueError(f"action argument must be  'SELL' or 'BUY'")
            
          return await order
        

class AMarketOrderSender(AsyncOrderBase):

    def __init__(self, aclient: AsyncClient) -> None:
         super().__init__(aclient)

    async def __call__(self, 
                       symbol: str, 
                       quantity: float, 
                       side: Literal[TradingDirection.BUY, 
                                    TradingDirection.SELL]) -> Dict[str, Any]:
          """send the market order
          Returns:
               Example::
               {
                    'symbol': 'BTCUSDT',
                    'orderId': 13395388,
                    'orderListId': -1,
                    'clientOrderId': '8aloylMwYqR3y3T4ZS5eVi',
                    'transactTime': 1710068462573,
                    'price': '0.00000000',
                    'origQty': '0.00100000',
                    'executedQty': '0.00100000',
                    'cummulativeQuoteQty': '69.74394000',
                    'status': 'FILLED',
                    'timeInForce': 'GTC',
                    'type': 'MARKET',
                    'side': 'BUY',
                    'workingTime': 1710068462573,
                    'fills': [{'price': '69743.94000000',
                    'qty': '0.00100000',
                    'commission': '0.00000000',
                    'commissionAsset': 'BTC',
                    'tradeId': 2915000}],
                    'selfTradePreventionMode': 'EXPIRE_MAKER'
               }
          """
            
          if side == TradingDirection["BUY"].value:
               order = self.aclient.order_market_buy(
                                                symbol=symbol,
                                                quantity=quantity,
                                                )
                
          elif side == TradingDirection["SELL"].value:

               order = self.aclient.order_market_sell(
                                                symbol=symbol,
                                                quantity=quantity,
                                                )
            
          else:
               raise ValueError(f"the argument, *side*, must be 'SELL' or 'BUY', get {side} instead!")
            
          return await order        


class AOrderStatusGetter(AsyncOrderBase):

     def __init__(self, aclient: AsyncClient) -> None:
          super().__init__(aclient)

     async def __call__(self, 
                        symbol: str, 
                        orderId: Union[str, int]
                        ) -> Dict[str, Any]:
          """Get the status for the order id
          Args:
               symbol: symbol name
          Return:
               Example::
               symbol="BTCUSDT", orderid=6565314
               result: 
               {
                    'symbol': 'BTCUSDT',
                    'orderId': 6565219,
                    'orderListId': -1,
                    'clientOrderId': 'vzvPgp1TUZTlsuCpRzocX0',
                    'price': '0.00000000',
                    'origQty': '0.00010000',
                    'executedQty': '0.00010000',
                    'cummulativeQuoteQty': '5.10840400',
                    'status': 'FILLED',
                    'timeInForce': 'GTC',
                    'type': 'MARKET',
                    'side': 'BUY',
                    'stopPrice': '0.00000000',
                    'icebergQty': '0.00000000',
                    'time': 1708761151576,
                    'updateTime': 1708761151576,
                    'isWorking': True,
                    'workingTime': 1708761151576,
                    'origQuoteOrderQty': '0.00000000',
                    'selfTradePreventionMode': 'EXPIRE_MAKER'
               }
          """
          
          return await self.aclient.get_order(symbol=symbol, orderId=orderId)
     

class AOrderCanceller(AsyncOrderBase):

     def __init__(self, aclient: AsyncClient) -> None:
          super().__init__(aclient)

     async def __call__(self, 
                        symbol: str, 
                        orderId: str) -> Dict[str, Any]:
          """get the information of cancelled order
          Returns:
               Example::
               {
                    'symbol': 'BTCUSDT', 
                    'origClientOrderId': 'v1dDLx3uPpzsMEPiEGiYHK', 
                    'orderId': 13427082, 
                    'orderListId': -1, 
                    'clientOrderId': 'Rr9m0CAQmAKGrrSAOuZTgz', 
                    'transactTime': 1710073278769, 
                    'price': '85000.00000000', 
                    'origQty': '0.00100000', 
                    'executedQty': '0.00000000', 
                    'cummulativeQuoteQty': '0.00000000', 
                    'status': 'CANCELED', 
                    'timeInForce': 'GTC', 
                    'type': 'TAKE_PROFIT_LIMIT', 
                    'side': 'SELL', 
                    'stopPrice': '80000.00000000', 
                    'selfTradePreventionMode': 'EXPIRE_MAKER'
               }
          """
          return await self.aclient.cancel_order(symbol=symbol, orderId=orderId)


class AStopLossOrderSender(AsyncOrderBase):

     def __init__(self, aclient: AsyncClient) -> None:
          super().__init__(aclient)
     
     async def __call__(self, 
                        symbol: str,
                        side: Literal[TradingDirection.BUY, TradingDirection.SELL],
                        type: str,
                        timeInForce: str,
                        quantity: float,
                        stopPrice: str,
                        price: str) -> Dict[str, Any]:
          """Returns:
               Example::
              {
                "symbol": "BTCUSDT",
                "orderId": 28,
                "clientOrderId": "6gCrw2kRUAF9CvJDGP16IP",
                "transactTime": 1507725176595,
                "price": "0.00000000",
                "origQty": "10.00000000",
                "executedQty": "10.00000000",
                "cummulativeQuoteQty": "10.00000000",
                "status": "FILLED",
                "timeInForce": "GTC",
                "type": "MARKET",
                "side": "SELL"
            }
          """
          return await self.aclient.create_order(symbol=symbol,
                                                  side=side,
                                                  type=type,
                                                  timeInForce=timeInForce,
                                                  quantity=quantity,
                                                  stopPrice=stopPrice,
                                                  price=price)


class ATakeProfitOrderSender(AStopLossOrderSender):
     ...


class TestOrderSender(OrderBase):
    
     def __init__(self, client: Client) -> None:
          """Create and validate a new order but does not send it into the exchange.
          """
          super().__init__(client)


     def __call__(self, symbol: str, quant: float):
         
          order = self.client.create_test_order(
                                             symbol=symbol,
                                             side=TradingDirection.BUY.value,
                                             type=OrderType["ORDER_TYPE_MARKET"].value,
                                             # timeInForce=TIME_IN_FORCE_GTC,
                                             quantity=quant,
                                             # price=price
                                             )
          return order