from typing import Any, Dict, List

from binance.client import AsyncClient, Client

from src.api.base import APIBase, AsyncAPIBase


class AccountBase(APIBase):
     ...


class AsyncAccountBase(AsyncAPIBase):
     ...


class AccountInfo(AccountBase):
    def __init__(self, client: Client):
        self.client = client

    def __call__(self) -> Dict[str, Any]:
        """get the account information
        Retuens:
            Example::
            {
                'makerCommission': 0,
                'takerCommission': 0,
                'buyerCommission': 0,
                'sellerCommission': 0,
                'commissionRates': {'maker': '0.00000000',
                'taker': '0.00000000',
                'buyer': '0.00000000',
                'seller': '0.00000000'},
                'canTrade': True,
                'canWithdraw': True,
                'canDeposit': True,
                'brokered': False,
                'requireSelfTradePrevention': False,
                'preventSor': False,
                'updateTime': 1708867320778,
                'accountType': 'SPOT',
                'balances': [{'asset': 'ETH', 'free': '1.00000000', 'locked': '0.00000000'},
                {'asset': 'BTC', 'free': '1.00010000', 'locked': '0.00000000'},
                {'asset': 'LTC', 'free': '7.00000000', 'locked': '0.00000000'},
                {'asset': 'BNB', 'free': '1.00000000', 'locked': '0.00000000'},
                {'asset': 'USDT', 'free': '9994.80177800', 'locked': '0.00000000'},
                {'asset': 'TRX', 'free': '4027.00000000', 'locked': '0.00000000'},...
            }
        """
        return self.client.get_account()
    

class AssetBalance(AccountBase):
    
    def __init__(self, client: Client):
        self.client = client

    def __call__(self, asset: str) -> Dict[str, Any]:
        """get the asset balance
        Returns:
            Examples::
            {'asset': 'DOGE', 'free': 'XXXXX', 'locked': '0.00000000'}
        """

        return self.client.get_asset_balance(asset=asset)
    

class AccountStatus(AccountBase):
    def __init__(self, client: Client):
        self.client = client

    def __call__(self) -> Dict[str, str]:
        """get the status of account
        Returns:
            Example::
            {'data': "Normal"}
        """

        return self.client.get_account_status()
    

class AccountAPITradingStatus(AccountBase):

    def __init__(self, client: Client):
        self.client = client

    def __call__(self) -> Dict[str, Dict[str, Any]]:
        """
        Returns:
            Example::
            {'data': {
                'isLocked': False,
                'plannedRecoverTime': 0,
                'triggerCondition': {'UFR': 300, 'IFER': 150, 'GCR': 150},
                'updateTime': 0
            }}
        """

        return self.client.get_account_api_trading_status()
    

class AssetDetails(AccountBase):

    def __init__(self, client: Client):
        self.client = client

    def __call__(self) -> Dict[str, Dict[str, Any]]:
        """
        Returns:
            Examples
            {
                "DOGE":{
                    {'withdrawFee': '4',
                    'minWithdrawAmount': '60',
                    'withdrawStatus': True,
                    'depositStatus': True}
                },
                ...
            }
        """

        return self.client.get_asset_details()
    

class TradesGetter(AccountBase):

    def __init__(self, client: Client) -> None:
        super().__init__(client)

    def __call__(self, symbol: str) -> List[Dict[str, Any]]:
        """Get trades for a specific symbol.
        Returns:
            Example::
            [{
                'symbol': 'BTCUSDT',
                'id': 1319751,
                'orderId': 6565219,
                'orderListId': -1,
                'price': '51084.04000000',
                'qty': '0.00010000',
                'quoteQty': '5.10840400',
                'commission': '0.00000000',
                'commissionAsset': 'BTC',
                'time': 1708761151576,
                'isBuyer': True,
                'isMaker': False,
                'isBestMatch': True
            }]
        """

        return self.client.get_my_trades(symbol=symbol)
    

class TradeFeesGetter(AccountBase):

    def __init__(self, client: Client):
        self.client = client

    def __call__(self, symbol: str) -> List[Dict[str, str]]:
        """
        Returns:
            Example::
            [{'symbol': 'BTCUSDT', 'makerCommission': '0.001', 'takerCommission': '0.001'}]
        """

        fees = self.client.get_trade_fee(symbol=symbol)
    
        return fees
        

class ATradesGetter(AsyncAccountBase):

    def __init__(self, aclient: AsyncClient) -> None:
        super().__init__(aclient)

    async def __call__(self, symbol: str) -> List[Dict[str, Any]]:

        return await self.aclient.get_my_trades(symbol=symbol)
ATradesGetter.__call__.__doc__ = TradesGetter.__call__.__doc__
