from binance.client import AsyncClient, Client


class ClientGetter:
    
    _CLIENT = None

    @classmethod
    def get(cls, 
            api_key: str,
            api_secret: str,
            testnet: str,
            tld: str = "com") -> Client:

        if cls._CLIENT is None:
            client = Client(api_key=api_key, 
                            api_secret=api_secret, 
                            testnet=eval(testnet),
                            tld=tld)
            cls._CLIENT = client
        return cls._CLIENT


class AsyncClientGetter:
    
    _ACLIENT = None

    @classmethod
    async def aget(cls,
                   api_key: str,
                   api_secret: str,
                   testnet: str,
                   tld: str = "com") -> AsyncClient:
        if cls._ACLIENT is None:
            aclient = await AsyncClient.create(api_key, 
                                               api_secret, 
                                               testnet=eval(testnet),
                                               tld=tld)
            cls._ACLIENT = aclient

        return cls._ACLIENT