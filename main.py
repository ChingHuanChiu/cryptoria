"""
      
#TODO:
# 2. 限制交易次數
# 3. error : 沒有刪除停損單雨停利單
# 4. restruct main function (after the system is running without bug)
# https://www.binance.com/zh-TC/support/faq/%E5%A6%82%E4%BD%95%E5%9C%A8%E5%B9%A3%E5%AE%89%E6%B8%AC%E8%A9%A6%E7%B6%B2%E4%B8%8A%E6%B8%AC%E8%A9%A6%E6%88%91%E7%9A%84%E5%8A%9F%E8%83%BD-ab78f9a1b8824cf0a106b4229c76496d 


"""
import os
import time
from typing import Dict, Any, List


import asyncio
from dotenv import load_dotenv
from binance import BinanceSocketManager
from binance.exceptions import BinanceAPIException
from binance.enums import *


from src.trade.strategy import AIStrategy, MockStrategy
from src.trade.broker import AsyncTrader
from src.api.client import get_aclient
from src.api.endpoint.general import SymbolInfo
from src.api.endpoint.orders import (
                                        MarketOrderSender, 
                                        AStopLossOrProfitOrder, 
                                        AOpenOrdersGetter,
                                        OrderCanceller
                                    )
from src.api.endpoint.account import AccountInfo
from src.bot.message import send_message
from src.db.engine import get_db_session
from src.db.orm import insert_data
from src.db.table import Asset, Inference, TransactionRecord
from src.common.monitor import WebsocketMonitor
from src.common.exception import BinanceWebsocketException
from src.common.enum import DirectionStatus, PositionStatus
from src.common.data.feature import RNNFeature, TechincalFeature
from src.common.helper import (
                                make_inference_data_to_dict, 
                                adjust_order_info_to_dict,
                                make_account_info_to_list_of_dict,
                                get_valid_quantity,
                                get_open_position_avgprice_quant,
                                convert_to_timestamp,
                                initialize_data_queue,
                                get_valid_price
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

async def trade():

    quant = get_valid_quantity(symbol=SYMBOL,
                               quant=QUANT,
                               symbol_info=SYMBOL_INFO)


    aclient = await get_aclient()
    bm = BinanceSocketManager(aclient, user_timeout=60)
    multi_socket = bm.multiplex_socket([
                                        f"{SYMBOL.lower()}@kline_1s", 
                                        # f"{SYMBOL.lower()}@trade"
                                        ])
    account_info = AccountInfo()
    
    DATAQUEUE: List[List[Any]] = await initialize_data_queue(aclient=aclient, symbol=SYMBOL)

    # strategy = AIStrategy(AI_MODEL_PATH, asset=SYMBOL)
    strategy = MockStrategy()
    atrader = AsyncTrader(strategy, aclient=aclient)

    POSITION_STATUS = PositionStatus["EMPTY"].value

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
                    # side = atrader.get_trading_side(x=rnn_features)
                    print('策略產生中.....s')
                    # TODO: trading side is from Broker class
                    side = atrader.get_trading_side()
                    
                    print("=======")
                    print(f'SIDE IS : {side}')
                    print("=======")
                    # place the sell order when being in position
                    #TODO: trade condition is from Trade class
                    if side == DirectionStatus["SELL"].value and POSITION_STATUS == PositionStatus["LONG"].value:
                        POSITION_STATUS = PositionStatus["EMPTY"].value
                        #TODO: from helper module:  OpenOrder class
                        oog = AOpenOrdersGetter(aclient)
                        open_order_list = await oog(SYMBOL)


                        # cancel the stop loss limit order and 
                        # take profit limit order before placing the sell order
                        if len(open_order_list) != 0: #TODO: --> remove, because before set the status of position, neet to check the order ==>  'status': 'FILLED'
                            # TODO: from helper class::
                            stop_loss_order_id = [order["orderId"] for order in open_order_list if order["type"] == "STOP_LOSS_LIMIT"]
                            take_profit_order_id = [order["orderId"] for order in open_order_list if order["type"] == "TAKE_PROFIT_LIMIT"]
                            
                            #TODO: make cancelled list of cancelled orderid and call the Broker.place_cancel_order once! 
                            if stop_loss_order_id:
                                print('取消停損單')
                                sl_cancelled_order = await atrader.place_order(OrderCanceller(aclient), 
                                                                        **{
                                                                            "symbol": SYMBOL, 
                                                                            "orderId": stop_loss_order_id[0]
                                                                            }
                                                                        )
                            
                            if take_profit_order_id:
                                print('取消停利單')
                                tp_cancelled_order = await atrader.place_order(OrderCanceller(aclient), 
                                                                        **{
                                                                            "symbol": SYMBOL, 
                                                                            "orderId": take_profit_order_id[0]
                                                                            }
                                                                        )
                        print(f'下賣單！！')
                        market_order = await atrader.place_order(
                                                                MarketOrderSender(aclient), 
                                                                **{
                                                                        "symbol": SYMBOL,
                                                                        "quantity" : quant,
                                                                        "side": side 
                                                                    }
                                                                )
                        
                    # place the limit stop loss order when the buy order is filled and not increasing positions
                    if side == DirectionStatus["BUY"].value and POSITION_STATUS == PositionStatus["EMPTY"].value:
                        
                        # NOTICE: before set the status of position, neet to check the order ==>  'status': 'FILLED'
                        POSITION_STATUS = PositionStatus["LONG"].value
                        print(f'下多單！！ .... qant is {quant}', )
                        market_order = await atrader.place_order(
                                                                MarketOrderSender(aclient), 
                                                                **{
                                                                        "symbol": SYMBOL,
                                                                        "quantity" : quant,
                                                                        "side": side 
                                                                    }
                                                                )
                        ave_buy_price, balance_quant = await get_open_position_avgprice_quant(SYMBOL, aclient=aclient)
                        balance_quant = get_valid_quantity(
                                            symbol=SYMBOL,
                                            quant=balance_quant,
                                            symbol_info=SYMBOL_INFO
                                        )

                        stop_loss_price = ave_buy_price * (1-STOP_LOSS_RATE)
                        stop_loss_price: str = get_valid_price(stop_loss_price, SYMBOL_INFO)

                        sl_trigger_price = ave_buy_price * (1 - STOP_LOSS_TRIGGER_RATE)
                        sl_trigger_price: str = get_valid_price(sl_trigger_price, SYMBOL_INFO)
                        print('下停損市價單', stop_loss_price, sl_trigger_price, 'fQ: {balance_quant}') 
                        _ = await atrader.place_order(
                                                    AStopLossOrProfitOrder(aclient),
                                                    **{
                                                        "symbol": SYMBOL,
                                                        "side": SIDE_SELL,
                                                        "type": ORDER_TYPE_STOP_LOSS_LIMIT,
                                                        "timeInForce": TIME_IN_FORCE_GTC,
                                                        "quantity": balance_quant,
                                                        "stopPrice": sl_trigger_price,# trigger price
                                                        "price": stop_loss_price
                                                        }
                                                    )
                        
                        take_profit_price = ave_buy_price * (1+TAKE_PROFIT_RATE)
                        take_profit_price = get_valid_price(take_profit_price, SYMBOL_INFO)

                        tp_trigger_price = ave_buy_price * (1+TAKE_PROFIT_TRIGGER_RATE)
                        tp_trigger_price = get_valid_price(tp_trigger_price, SYMBOL_INFO)
                        print('下停利市價單') 
                        take_profit_market_order = await atrader.place_order(

                                                                            AStopLossOrProfitOrder(aclient),
                                                                            **{
                                                                                "symbol": SYMBOL,
                                                                                "side": SIDE_SELL,
                                                                                "type": ORDER_TYPE_TAKE_PROFIT_LIMIT,
                                                                                "timeInForce": TIME_IN_FORCE_GTC,
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
                                                        symbol=SYMBOL,
                                                        prediction=str(atrader.trading_signal),
                                                        model_version="0.0"
                                                        )
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
    tasks = [trade()]
    _ = await asyncio.gather(*tasks)




if __name__ == "__main__":

    asyncio.run(main())