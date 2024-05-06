from typing import Dict, Any, List
from datetime import datetime


from binance.helpers import round_step_size
from binance.enums import KLINE_INTERVAL_15MINUTE
from binance.client import AsyncClient
import pandas as pd

from src.api.endpoint.market_data import AsyncKline
from src.api.endpoint.account import ATradesGetter, AssetBalance
from src.common.data.feature import TechincalFeature
from src.config import FEATURE_COLUMNS
from src.api.endpoint.orders import AOpenOrdersGetter
from src.db.orm import insert_data


def convert_to_timestamp(timestamp_milliseconds: int) -> datetime:

    timestamp_seconds = timestamp_milliseconds / 1000
    dt_object = datetime.fromtimestamp(timestamp_seconds)
    return dt_object


def adjust_order_info_to_list_of_dict(order: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Adjust the order information to match the schema of the SQL table.

    Args:
        order (Dict[str, Any]): The order information.

    Returns:
        List[Dict[str, Any]]: A list of  adjusted order information.
    
    """
    filled_orders_metadata = order["fills"]

    del order["clientOrderId"]
    del order["orderListId"]
    del order["workingTime"]
    del order["fills"]
    del order["selfTradePreventionMode"]
    
    res_list = []
    for filled_order_metadata in filled_orders_metadata:
        filled_order = order.copy()
        update_data = {
            "transactTime": convert_to_timestamp(order["transactTime"]),
            "origQty": float(order["origQty"]),
            "executedQty": float(order["executedQty"]),
            "cummulativeQuoteQty": float(order["cummulativeQuoteQty"]),
            "timeInForce": order["timeInForce"],
            "price": float(filled_order_metadata["price"]),
            "qty": float(filled_order_metadata["qty"]),
            "commission": float(filled_order_metadata["commission"]),
            "commissionAsset": filled_order_metadata["commissionAsset"]
        }
        filled_order.update(update_data)

        res_list.append(filled_order)
    return res_list


def make_inference_data_to_dict(timestamp,
                          symbol,
                          prediction,
                          model_version):
    
    res = {
        "infer_time": timestamp,
        "symbol": symbol,
        "prediction": prediction,
        "model_version": model_version
    }

    return res


def make_account_info_to_list_of_dict(account_info) -> List[Dict[str, Any]]:
    update_time = account_info['updateTime']
    update_time = convert_to_timestamp(update_time)
    tmp_df = pd.DataFrame(account_info['balances'])
    tmp_df['update_time'] = [update_time] * len(tmp_df)
    tmp_df = tmp_df.drop(labels=['locked'], axis=1)
    tmp_df.rename(columns={'asset': 'symbol', 'free': 'amount'}, inplace=True)
    list_of_dict = tmp_df.to_dict(orient='records')
    return list_of_dict


async def get_open_position_avgprice(symbol: str, aclient):
    """Get the average price  of open position.
    """
    
    total_quantity = 0.0
    total_cost = 0.0
    tg = ATradesGetter(aclient)
    trades = await tg(symbol=symbol)

    for trade in trades:
        if trade['isBuyer']:
            total_quantity += float(trade['qty'])
            total_cost += float(trade['quoteQty']) 

    average_price = total_cost / total_quantity

    return average_price


class SaveOrderIDGetter:

    def __init__(self, aclient: AsyncClient, symbol: str) -> None:

        self.aclient = aclient
        self.symbol = symbol
        self.open_order_list = None

    async def _aget_open_order_list(self):
        if self.open_order_list is None:
            aoog = AOpenOrdersGetter(self.aclient)
            self.open_order_list = await aoog(self.symbol)
        return  self.open_order_list

    async def aget_stop_loss_order_id(self) -> List[str]:
        open_order_list = await self._aget_open_order_list()

        stop_loss_order_id = [str(order["orderId"]) for order in open_order_list \
                                                    if order["type"] == "STOP_LOSS_LIMIT"]
        return stop_loss_order_id

    async def aget_take_profit_order_id(self) -> List[str]:
        
        open_order_list = await self._aget_open_order_list()
        take_profit_order_id = [order["orderId"] for order in open_order_list \
                                                if order["type"] == "TAKE_PROFIT_LIMIT"]

        return take_profit_order_id


class TradingInitializer:

    def __init__(self, abroker, aclient) -> None:
        self.abroker = abroker
        self.aclient = aclient

        self.__clean_position_order = None

    async def initial(self, asset_balance: Dict[str, str]):
        """The following initial subject:
        1. Remove the 'stop_loss' and 'take_profit' orders 
           when the beginning of the trading.
        2. Clean the blance at the beginng of the trading.
        """
        asset_balance = float(asset_balance["free"])
        quantity = asset_balance
        
        await self.abroker.remove_stop_loss_and_take_profit_orders()
        if quantity != 0:
            self.__clean_position_order = await self.abroker.place_short_mkt_order(quantity)

    async def initialize_data_queue(self, symbol) -> List[List[Any]]:
        """initialize the data queue 
        """
        
        ak = AsyncKline(self.aclient)
        data = await ak(symbol=symbol, interval=KLINE_INTERVAL_15MINUTE)
        # get the latest 100 k bars
        data = data[-100: ]
        tmp_df = pd.DataFrame(data)[[0, 1, 2, 3, 4, 5]]
        tmp_df.columns = FEATURE_COLUMNS[: 6]
        tmp_df[FEATURE_COLUMNS[0]] = tmp_df[FEATURE_COLUMNS[0]].apply(lambda x: convert_to_timestamp(x))

        tmp_df.set_index(FEATURE_COLUMNS[0], inplace=True)
        tmp_df = tmp_df.astype(dict(zip(FEATURE_COLUMNS[1: 6], ['float32']*5)))
        TechincalFeature.make_all_indicator_from_ta(tmp_df)
        res_df = tmp_df
        res_df[FEATURE_COLUMNS[0]] = res_df.index

        return res_df[FEATURE_COLUMNS].values.tolist()

    @property
    def clean_position_order(self):

        return self.__clean_position_order