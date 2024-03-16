# Deep Learning Trainer

## Interface and Abstract Class
There are three interfaces and one abstract class for custom training

* IMetric : define the various metrics
* ICallbacks : define the four different actions when training
* IEarlyStop : define the custom earlystopping conditon
* Trainer : inherit this class to define the training step and validation loop. Also accept the custom 
'Metric'、'Callback' and 'Earlystop' class and they need to be the arguments of 'start_to_train' method(callback function)