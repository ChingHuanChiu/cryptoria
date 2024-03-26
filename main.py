"""

# https://www.binance.com/zh-TC/support/faq/%E5%A6%82%E4%BD%95%E5%9C%A8%E5%B9%A3%E5%AE%89%E6%B8%AC%E8%A9%A6%E7%B6%B2%E4%B8%8A%E6%B8%AC%E8%A9%A6%E6%88%91%E7%9A%84%E5%8A%9F%E8%83%BD-ab78f9a1b8824cf0a106b4229c76496d 


"""
import os
import time
from typing import Dict, Any, List


import asyncio
from dotenv import load_dotenv
from binance import BinanceSocketManager
from binance.exceptions import BinanceAPIException


from src.trade.strategy import AIStrategy, MockStrategy, StrategyBase
from src.trade.broker import AsyncBroker
from src.trade.condition_handler import LongOnlyTradeConditionHandler, TradeConditionHandler
from src.api.client import ClientGetter, AsyncClientGetter
from src.api.endpoint.general import SymbolInfo

from src.api.endpoint.account import AccountInfo
from src.bot.message import send_message
from src.db.engine import get_db_session
from src.db.orm import insert_data
from src.db.table import Asset, Inference, TransactionRecord
from src.common.monitor import WebsocketMonitor
from src.common.exception import BinanceWebsocketException
from src.common.enum import (
    TradingDirection, 
    PositionStatus,
    OrderType,
    TimeInForce
)
from src.common.data.feature import RNNFeature, TechincalFeature
from src.common.helper import (
    make_inference_data_to_dict, 
    adjust_order_info_to_dict,
    make_account_info_to_list_of_dict,
    get_valid_quantity,
    get_open_position_avgprice_quant,
    convert_to_timestamp,
    initialize_data_queue,
    get_valid_price,
    SaveOrderIDGetter
)

from src.config import (
    SYMBOL,
    QUANT,
    STOP_LOSS_RATE,
    STOP_LOSS_TRIGGER_RATE,
    TAKE_PROFIT_RATE,
    TAKE_PROFIT_TRIGGER_RATE,
    AI_MODEL_PATH
)

load_dotenv()
API_KEY = os.getenv("API_KEY")
API_SECRET = os.getenv("API_SECRET")
TESTNET = os.getenv("TESTNET")



SYMBOL_INFO: Dict[str, Any] = SymbolInfo()(SYMBOL)

#ws stream names : https://binance-docs.github.io/apidocs/spot/en/#trade-streams

async def start_to_trade(symbol: str,
                         trade_condition_handler: TradeConditionHandler,
                         strategy: StrategyBase):

    quant = get_valid_quantity(symbol=symbol,
                               quant=QUANT,
                               symbol_info=SYMBOL_INFO)


    aclient = await AsyncClientGetter.aget(api_key=API_KEY,
                                           api_secret=API_SECRET,
                                           testnet=TESTNET)

    bm = BinanceSocketManager(aclient, user_timeout=60)
    multi_socket = bm.multiplex_socket([f"{symbol.lower()}@kline_5s"])

    account_info = AccountInfo()
    
    DATAQUEUE: List[List[Any]] = await initialize_data_queue(aclient=aclient, symbol=symbol)

    abroker = AsyncBroker(aclient=aclient, strategy=strategy, symbol=symbol)

    async with multi_socket as ms:
        with get_db_session() as sess:
            while True:

                market_order = None
                try:
                    print('Trading STARTING....')
                    msg = await ms.recv()
                    kline_data: Dict[str, Any] = msg["data"]["k"]
                    event_time = convert_to_timestamp(msg["data"]["E"])

                    await WebsocketMonitor().anotify(msg, ms)

                    # If  kline is not closed
                    if kline_data["x"] is not True:
                        continue
                    o, h, l ,c, v = kline_data["o"], kline_data["h"], kline_data["l"], kline_data["c"], kline_data["v"]
                    
                    tech_features: List[float] = TechincalFeature(DATAQUEUE).make(event_time, o, h, l, c, v)
                    DATAQUEUE.pop(0)
                    DATAQUEUE.append(tech_features)


                    # rnn_features = RNNFeature(DATAQUEUE).make(tech_features) # shape (window sizes, feature dimension)
                    # side = aabroker.get_trading_side()
                    print('策略產生中.....s')
                    trading_side = abroker.get_trading_side(kwargs=None)
                    
                    trade_condition_handler.trading_side = trading_side

                    print("=======")
                    print(f'SIDE IS : {trading_side}')
                    print("=======")
                    if trade_condition_handler.short_condition():
                        save_order_id_getter = SaveOrderIDGetter(aclient=aclient, symbol=symbol)
                        stop_loss_order_id = await save_order_id_getter.aget_stop_loss_order_id()
                        take_profit_order_id = await save_order_id_getter.aget_take_profit_order_id()
                        canceled_ordier_id = stop_loss_order_id + take_profit_order_id
                        cancelled_info = abroker.place_cancel_order(order_ids=canceled_ordier_id)

                        print(f'下賣單！！')
                        market_order = await abroker.place_short_mkt_order(quant)

                        #TODO: 確認是否需要檢查有沒有下單成功 : 以order_status: "FILLDE"檢查
                        trade_condition_handler.position_status = PositionStatus["EMPTY"].value
                        
                    if trade_condition_handler.long_condition():
                        
                        print(f'下多單！！ .... qant is {quant}', )
                        market_order = await abroker.place_long_mkt_order(quantity=quant)

                        #TODO: 確認是否需要檢查有沒有下單成功 : 以order_status: "FILLDE"檢查
                        trade_condition_handler.position_status = PositionStatus["LONG"].value

                        #TODO: balance quant ACCOUNT 拿
                        ave_buy_price, balance_quant = await get_open_position_avgprice_quant(symbol, aclient=aclient)
                        balance_quant = get_valid_quantity(
                                            symbol=symbol,
                                            quant=balance_quant,
                                            symbol_info=SYMBOL_INFO
                                        )

                        if trade_condition_handler.stop_loss_condition():
                            stop_loss_price = ave_buy_price * (1-STOP_LOSS_RATE)
                            stop_loss_price: str = get_valid_price(stop_loss_price, SYMBOL_INFO)

                            sl_trigger_price = ave_buy_price * (1 - STOP_LOSS_TRIGGER_RATE)
                            sl_trigger_price: str = get_valid_price(sl_trigger_price, SYMBOL_INFO)

                            print('下停損市價單', stop_loss_price, sl_trigger_price, 'fQ: {balance_quant}') 
                            _ = await abroker.place_stop_loss_order(
                                                        **{
                                                            "side": TradingDirection["SELL"].value,
                                                            "type": OrderType["ORDER_TYPE_STOP_LOSS_LIMIT"].value,
                                                            "timeInForce": TimeInForce["TIME_IN_FORCE_GTC"].value,
                                                            "quantity": balance_quant,
                                                            "stopPrice": sl_trigger_price,# trigger price
                                                            "price": stop_loss_price
                                                            }
                                                        )
                        if trade_condition_handler.take_profit_condition():
                            # take profit order
                            take_profit_price = ave_buy_price * (1+TAKE_PROFIT_RATE)
                            take_profit_price = get_valid_price(take_profit_price, SYMBOL_INFO)

                            tp_trigger_price = ave_buy_price * (1+TAKE_PROFIT_TRIGGER_RATE)
                            tp_trigger_price = get_valid_price(tp_trigger_price, SYMBOL_INFO)
                            print('下停利市價單') 
                            _ = await abroker.place_order(
                                                            **{
                                                                "side": TradingDirection["SELL"].value,
                                                                "type": OrderType["ORDER_TYPE_TAKE_PROFIT_LIMIT"].value,
                                                                "timeInForce": TimeInForce["TIME_IN_FORCE_GTC"].value,
                                                                "quantity": balance_quant,
                                                                "stopPrice": tp_trigger_price,# trigger price
                                                                "price": take_profit_price
                                                                }
                                                            )

                    if market_order is not None:
                        insert_data(session=sess,
                                    table=TransactionRecord,
                                    list_dict_data=[adjust_order_info_to_dict(market_order)])
                        
                    inference_data = make_inference_data_to_dict(timestamp=event_time,
                                                                symbol=symbol,
                                                                prediction=str(trading_side),
                                                                model_version="0.0")
                    insert_data(session=sess,
                                table=Inference,
                                list_dict_data=[inference_data])
                    
                    insert_data(
                        session=sess,
                        table=Asset,
                        list_dict_data=make_account_info_to_list_of_dict(account_info()))
                    print('休息')
                    time.sleep(10)

                except BinanceWebsocketException:

                        await asyncio.sleep(5)
                        await  ms.__aenter__()
                        send_message("websocket 已經重新連線....")

                except BinanceAPIException as e:

                    send_message(f"""幣安API 問題: \n Error Message: {e.message}
                                    """)
                
                    print("Error:", e)
                    print("Error Code:", e.code)
                    print("Error Message:", e.message)
                    await aclient.close_connection()
                    account_info.CLIENT.close_connection()
                    break

                except Exception as e:
                    print(e)
                    send_message(f"交易程式出現問題: {e}")
                    import traceback
                    traceback.print_exc()
                    await aclient.close_connection()
                    #TODO: refactor the code 
                    account_info.CLIENT.close_connection()
                    break
                





async def main():
    # strategy = AIStrategy(AI_MODEL_PATH, asset=symbol)
    strategy = MockStrategy()
    trade_condition_handler = LongOnlyTradeConditionHandler()
    tasks = [trade()]
    _ = await asyncio.gather(*tasks)




if __name__ == "__main__":

    asyncio.run(main())