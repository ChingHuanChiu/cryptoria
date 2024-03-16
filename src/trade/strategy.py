# generate the next signal
import random
from typing import Literal
from abc import ABCMeta, abstractmethod

from src.api.endpoint.account import AssetBalance

class StrategyBase(metaclass=ABCMeta):

    @abstractmethod
    def get_signal(self, **kwargs) -> Literal["0", "1", "-1"]:
        raise NotImplemented("Not Implemented")
    
    def is_buy(self, signal: str) -> bool:

        return signal == "1"
    
    def is_sell(self, signal: str) -> bool:

        return signal == "-1"
    

class AIStrategy(StrategyBase):

    def __init__(self, model_path: str, asset: str) -> None:
        
        self.model = self.load_model(model_path)
        self.asset = asset

    def get_signal(self, **kwargs):
        """the following strategy:
        1. without further position averaging
        2. without short selling
        """

        balance_info = AssetBalance(asset=self.asset)
        signal = self.model(**kwargs)

        if balance_info is not None:
            if self.is_buy(signal):
                return "0"
            
            return signal

        else:
            return "0"
         
    @staticmethod
    def load_model(model_path):
        """TODO: load model 
        """
        ...
        

class MockStrategy(StrategyBase):

    def get_signal(self, **kwargs) -> str:

        signal = random.choice(["0", "1", "-1"])
        return signal

        
        