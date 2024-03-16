from abc import ABCMeta, abstractmethod
from typing import Dict, Union

from torchmetrics.classification import Accuracy, Recall, Precision, F1Score


class IMetric(metaclass=ABCMeta):

    @abstractmethod
    def calculate_metric(self, y_true, y_pred) -> None:
        raise NotImplemented("not implemented")


    @abstractmethod
    def reset(self):
        raise NotImplemented("not implemented")


    @abstractmethod
    def get_result(self) -> Dict[str, Union[float, int]]:
        """
        return a dictionary of result of metrics
        """

        raise NotImplemented("not implemented")


class NullMetric(IMetric):
    """Null Object
    """

    def calculate_metric(self, y_true, y_pred) -> None:

        return None

    def reset(self):

        return None

    
    def get_result(self):

        return None


class ClassificationTorchMetric(IMetric):


    def __init__(self, 
                 task: str = "multiclass",
                 average: str = "micro",
                 num_classes: int = 2
                 ) -> None:
        """
        @param task:  'binary', 'multiclass' or multilabel
        """

        self.accuracy = Accuracy(task=task, average=average, num_classes=num_classes)
        self.recall = Recall(task=task, average=average, num_classes=num_classes)
        self.precision = Precision(task=task, average=average, num_classes=num_classes)
        self.f1 = F1Score(task=task, num_classes=num_classes)


    def calculate_metric(self, y_true, y_pred) -> None:

        for name, metric in self._iter_attribute():
            metric(y_pred, y_true)
            setattr(self, name, metric)


    def reset(self) -> None:

        for _, metric in self._iter_attribute():

            metric.reset()


    def get_result(self):

        result = dict()

        for name, metric in self._iter_attribute():

            result[name] = metric.compute().item()
        
        return result


    def _iter_attribute(self):

        for name, metric in self.__dict__.items():
            yield name, metric



