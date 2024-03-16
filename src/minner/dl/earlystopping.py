
from typing import Any


from src.minner.dl.metrics import IMetric



class IEarlyStop:

    def __call__(self, val_loss, train_epoch_loss, metrics: IMetric = None) -> Any:
        pass


class WorseValLossEarlyStopping(IEarlyStop):
    

    def __init__(self, tolerance: int) -> None:
        self.tolerance = tolerance
        self.patient = 0
        self.pre_val_loss = 0


    def __call__(self, val_loss, train_epoch_loss, metrics = None) -> bool:
        """early stop when validation loss is worse than previous validation loss with 'tolerance' times consecutively
        """

        if val_loss <= self.pre_val_loss:
            self.patient = 0
        
        else:
            self.patient += 1
            
        self.pre_val_loss = val_loss

        if self.patient == self.tolerance:
            return True
        return False