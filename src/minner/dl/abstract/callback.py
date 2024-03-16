
import mlflow

class ICallbacks:
    """various behavior in start_to_train method of TrainBase class 
    """

    def on_epoch_start(self, epoch) -> None:
        pass


    def on_epoch_end(self, epoch, metrics, loss, model, val_loss) -> None:

        pass


    def on_batch_start(self) -> None:

        pass


    def on_batch_end(self) -> None:

        pass


class NullCallback(ICallbacks):
    pass


class MLFlowTrackCallback(ICallbacks):


    def on_epoch_end(self, epoch, metrics, loss, model, val_loss) -> None:
        """self.metrics and self.epoch_loss are the attritube of TrainBase Class
        """
        for name, result in metrics.get_result().items():
            if isinstance(result, (int, float)):
                mlflow.log_metric(name, result, epoch)
        mlflow.log_metric("epoch_Loss", loss, epoch)
        mlflow.pytorch.log_model(model, "model")
            
        