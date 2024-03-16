import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)
from typing import List, Any
from abc import ABCMeta, abstractmethod

import pandas as pd
import pandas_ta as ta
import numpy as np

from src.config import FEATURE_COLUMNS, TIMESERIES_WINDOWS_SIZE
# queue 預留100跟K棒計算技術指標(不從database 拿)
class FeatureBase(metaclass=ABCMeta):

    def __init__(self, data_queue: List[List[Any]]) -> None:
        self.current_df = pd.DataFrame(data_queue, columns=FEATURE_COLUMNS)
        self.current_df.set_index(FEATURE_COLUMNS[0], inplace=True)
        # self.current_df.index =  pd.to_datetime(self.current_df.index)

    @abstractmethod
    def make(self, *args, **kwargs) -> Any:

        pass


class RNNFeature(FeatureBase):

    def __init__(self, data_queue: List[List[Any]]) -> None:
        super().__init__(data_queue)        

    @abstractmethod
    def make(self) -> np.array:

        array_data = self.current_df.values
        
        return array_data[-TIMESERIES_WINDOWS_SIZE: ]
        

class TechincalFeature(FeatureBase):
    
    def __init__(self, data_queue: List[List[Any]]) -> None:
        
        super().__init__(data_queue)

    def make(self, event_time, o, h, l, c, v) -> List[float]:
        new_df = pd.DataFrame(
            [[event_time, o, h, l, c, v]], 
            columns=FEATURE_COLUMNS[: 6]
        )
        new_df.set_index(FEATURE_COLUMNS[0], inplace=True)
        new_df = new_df.astype(dict(zip(FEATURE_COLUMNS[1: 6], ['float32']*5)))
     
        selected_df = self.current_df[FEATURE_COLUMNS[1:6]]

        tmp_df = pd.concat(objs=[selected_df, new_df], axis=0)
        self.make_all_indicator_from_ta(tmp_df)
        res_df = tmp_df
        result = res_df.values[-1].tolist()
        result.insert(0, event_time)

        return result
    
    @staticmethod
    def make_all_indicator_from_ta(df) -> None:
        """make the indicator data with pandas_ta , which is inplace operation
        """

        AllStrategy = ta.Strategy(
            name="All",
            description="All the indicators with their default settings. Pandas TA default.",
            ta=None,
        )
        df.ta.cores = 4
        df.ta.strategy(AllStrategy)






    






