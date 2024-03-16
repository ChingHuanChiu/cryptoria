from typing import Literal, Dict, Any, List

from binance.enums import *
from binance.client import AsyncClient


from src.trade.strategy import StrategyBase
from src.common.enum import TradingDirection, OrderType, TimeInForce
from src.api.endpoint.orders import (
    AsyncOrderBase, 
    AOrderCanceller,
    AStopLossOrderSender,
    ATakeProfitOrderSender,
    AMarketOrderSender
)


class AsyncBroker:

    SIDE_MAPPING = {
                    "0": TradingDirection["HOLD"].value, 
                    "-1": TradingDirection["SELL"].value,
                    "1": TradingDirection["BUY"].value
                }

    def __init__(self, 
                 aclient: AsyncClient,
                 strategy: StrategyBase,
                 symbol: str) -> None:
        self.aclient = aclient
        self.strategy = strategy
        self.symbol = symbol

    async def place_long_mkt_order(self, quantity: float) -> Dict[str, Any]:

        order = await self._handle_order(AMarketOrderSender(self.aclient),
                                         **{
                                                "symbol": self.symbol,
                                                "quantity" : quantity,
                                                "side": TradingDirection.BUY.value
                                        })
        return order
        
    async def place_short_mkt_order(self, quantity: float) -> Dict[str, Any]:

        order = await self._handle_order(AMarketOrderSender(self.aclient),
                                         **{
                                                "symbol": self.symbol,
                                                "quantity" : quantity,
                                                "side": TradingDirection.SELL.value
                                        })
        return order

    async def place_stop_loss_order(self, 
                                    side: TradingDirection,
                                    quantity: float,
                                    trigger_price: float,
                                    price: float,
                                    type: OrderType,
                                    time_in_force: TimeInForce,
                                    ) -> Dict[str, Any]:

            sl_order = await self._handle_order(AStopLossOrderSender(self.aclient),
                                                **{
                                                        "symbol": self.symbol,
                                                        "side": side,
                                                        "type": type,
                                                        "timeInForce": time_in_force,
                                                        "quantity": quantity,
                                                        "stopPrice": trigger_price,
                                                        "price": price
                                                        })
            return sl_order
    
    async def place_take_profit_order(self, 
                                      symbol: str,
                                      side: TradingDirection,
                                      quantity: float,
                                      trigger_price: float,
                                      price: float,
                                      type: OrderType,
                                      time_in_force: TimeInForce) -> Dict[str, Any]:

            tp_order = await self._handle_order(ATakeProfitOrderSender(self.aclient),
                                                **{
                                                        "symbol": symbol,
                                                        "side": side,
                                                        "type": type,
                                                        "timeInForce": time_in_force,
                                                        "quantity": quantity,
                                                        "stopPrice": trigger_price,
                                                        "price": price
                                                        })
            return tp_order

    async def place_cancel_order(self, order_ids: List[str]) -> Dict[str, Any]:
        
        for order_id in order_ids:
            cancelled_info = await self._handle_order(AOrderCanceller,
                                                    symbol=self.symbol,
                                                    orderId=order_id)
        return cancelled_info
    
    async def _handle_order(self, 
                           api_order: AsyncOrderBase, 
                           **order_params):

        if not isinstance(api_order, AsyncOrderBase):
            raise TypeError(f"argument *api_order* must be subclass of AsyncOrderBase")
        
        return await api_order(**order_params)

    def get_trading_side(self, **kwargs) -> Literal[TradingDirection.BUY, 
                                                    TradingDirection.SELL, 
                                                    TradingDirection.HOLD]:

        trading_signal = self.strategy.get_signal(**kwargs)
        side = self.SIDE_MAPPING[trading_signal]
        return side