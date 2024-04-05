from typing import Dict, Any, List
from datetime import datetime


from binance.helpers import round_step_size
from binance.enums import KLINE_INTERVAL_15MINUTE
from binance.client import AsyncClient
import pandas as pd

from src.api.endpoint.market_data import AsyncKline
from src.api.endpoint.account import ATradesGetter
from src.common.data.feature import TechincalFeature
from src.config import FEATURE_COLUMNS
from src.api.endpoint.orders import AOpenOrdersGetter


def convert_to_timestamp(timestamp_milliseconds: int) -> datetime:

    timestamp_seconds = timestamp_milliseconds / 1000
    dt_object = datetime.fromtimestamp(timestamp_seconds)
    return dt_object    


def adjust_order_info_to_dict(order: Dict[str, Any]):
    """adjust the order infomation to match the schema of the sql table 
    """
    del order["clientOrderId"]
    del order["orderId"]
    del order["orderListId"]
    del order["workingTime"]
    del order["fills"]
    del order["selfTradePreventionMode"]
    update_data = {
        "transacttime": convert_to_timestamp(order.pop("transactTime")),
        "price": float(order["price"]),
        "origqty": float(order.pop("origQty")),
        "executedqty": float(order.pop("executedQty")),
        "cummulativequoteqty": float(order.pop("cummulativeQuoteQty")),
        "timeinforce": order.pop("timeInForce")
    }
    order.update(update_data)
    return order


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


async def get_open_position_avgprice_quant(symbol: str, aclient):
    """Get the average price and total quantities of your trading history
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

    return average_price, total_quantity


async def initialize_data_queue(aclient, symbol) -> List[List[Any]]:
        """initialize the data queue 
        """
        
        ak = AsyncKline(aclient)
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