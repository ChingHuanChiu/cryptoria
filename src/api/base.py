from abc import ABCMeta, abstractmethod
from typing import Any

from binance.client import AsyncClient, Client


class APIBase(metaclass=ABCMeta):

    def __init__(self, client: Client) -> None:
        if not isinstance(client, Client):
            raise TypeError("client must be *Client* object")
        
        self.client = client

    @abstractmethod
    def __call__(self, *args: Any, **kwds: Any) -> Any:
        raise NotImplementedError("Not Implemented !")


class AsyncAPIBase(metaclass=ABCMeta):

    def __init__(self, aclient: AsyncClient) -> None:
        if not isinstance(aclient, AsyncClient):
            raise TypeError("client must be *AsyncClient* object")
        self.aclient = aclient
        
    @abstractmethod
    async def __call__(self, *args: Any, **kwds: Any) -> Any:
        raise NotImplementedError("Not Implemented !")