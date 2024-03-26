from abc import ABCMeta, abstractmethod


import asyncio


from src.bot.message import send_message
from src.api.endpoint.account import AccountStatus
from src.api.endpoint.general import SystemStatus
from src.common.exception import BinanceWebsocketException


class MonitorBase(metaclass=ABCMeta):

    @abstractmethod
    def notify(self):
        pass


class AMonitorBase(metaclass=ABCMeta):

    @abstractmethod
    async def anotify(self):
        pass


class AccountMonitor(MonitorBase):

    def notify(self) -> None:

        account_status = AccountStatus()
        status = account_status["data"]

        if status != "Normal":

            send_message("您的帳戶狀態異常，系統跳過此交易，當連續超過3次異常系統會自動關閉")
        

class SystemMonitor(MonitorBase):


    def notify(self):

        sys_status = SystemStatus()
        status = sys_status["status"]
        # system maintenance
        if status == 1:
            send_message("幣安API系統維護中...")


class WebsocketMonitor(AMonitorBase):

    async def anotify(self, msg, ws):
        
        if msg["data"]["e"] == "error":

            send_message("幣安websocket遇到問題，5秒後重啟....")
            await ws.__aexit__(None, None, None)
            raise BinanceWebsocketException("Encounter error in binance websocket...")



        

