"""
The TrainBase  class is only for CPU training. If training the model with GPU, inherit the DDPTrainBase class
"""

import os 
import time
from abc import ABCMeta, abstractmethod
from typing import Dict, Optional, Any
from tqdm import tqdm

import numpy as np
import dill
import torch
from torch.utils.data import DataLoader
from torch.utils.tensorboard import SummaryWriter
import torch.distributed as dist


from src.minner.dl.earlystopping import IEarlyStop
from src.minner.dl.metrics import IMetric, NullMetric
from src.minner.dl.tensorboard import TensorBoard
from src.minner.dl.abstract.callback import NullCallback, ICallbacks


class TrainBase(metaclass=ABCMeta):


    def __init__(self, 
                 model,
                 optimizer,
                 lr_scheduler,
                 *args, **kwargs) -> None:
        
        self.model = model
        self.optimizer = optimizer
        self.lr_scheduler = lr_scheduler

        self.epoch_loss = None


    @abstractmethod
    def train_step(self, X_batch, y_batch=None, *args, **kwargs):
        """define the training step  per batch"""
        raise NotImplemented("not implemented")
    
    
    @abstractmethod
    def start_to_train(*args, **kwargs):
        raise NotImplemented("not implemented")
    

    def validation_loop(self, epoch):
        """ return the loss value of an epoch if override this method
        """
        return None
    

    def count_model_parameters(self) -> None:

        num_parameters = 0
        parameters = self.model.parameters()
        for parameter in parameters:
            num_parameters += parameter.numel()
        print(f'number of parameters: {num_parameters}')

    
    def save_model(self, 
                   model_path: Optional[str], 
                   epoch: int, 
                   checkpoint: Dict[str, Any]) -> None:
        if model_path is not None:
            if self.lr_scheduler is not None:
                    checkpoint.update({'lr_scheduler': self.lr_scheduler})
            checkpoint.update({"Epoch": epoch})

            torch.save(checkpoint, f'{model_path}.pkl', pickle_module=dill)

        
class Trainer(TrainBase):


    def __init__(self, 
                 model, 
                 optimizer,
                 lr_scheduler=None,
                 metrics=NullMetric(),
                 *args, **keargs) -> None:
        
        super().__init__(model, optimizer, lr_scheduler, metrics)


    def start_to_train(self, 
                       train_data_loader: DataLoader,
                       epochs: int,
                       tb_path: str,
                       ckpt_path: Optional[str] = None,
                       earlystopping: Optional[IEarlyStop] = None,
                       callback: ICallbacks = NullCallback(),
                       metrics: IMetric = NullMetric()
                        ) -> None:
        
        if earlystopping is not None and not issubclass(earlystopping.__class__, IEarlyStop):
            raise ValueError("Earlystopping object must the subclass of IEarlyStop interface")
        
        if  not issubclass(metrics.__class__, IMetric):
            raise ValueError("train_metric object must be the subclass of IMetric")
        
        train_metric = metrics
        self.count_model_parameters()

        writer = SummaryWriter(tb_path)

        TRAINSTEP_PER_EPOCH = len(train_data_loader)

        for epoch in range(1, epochs+1):
            ep_start_time = time.time()
            running_loss = 0
            print(f'------------EPOCH {epoch} start------------')
            
            self.model.train()

            callback.on_epoch_start(epoch)
            for X_batch, y_batch in train_data_loader:

                callback.on_batch_start()
                
                loss, y_pred = self.train_step(X_batch=X_batch, 
                                               y_batch=y_batch)
                
                running_loss += loss

                
                train_metric.calculate_metric(y_batch, y_pred)
                callback.on_batch_end()

            self.epoch_loss = running_loss / TRAINSTEP_PER_EPOCH
            print(f"Training Epoch Loss :  {self.epoch_loss}")
            
            train_tb = TensorBoard(writer, model=self.model)
            train_tb.start_to_write(metrics=train_metric,
                                   step=epoch,
                                   loss=self.epoch_loss,
                                   histogram=True,
                                   optimizer=self.optimizer)
            epoch_val_loss = self.validation_loop(epoch=epoch)

            print(f'------------Saving model for epoch {epoch}------------')
            model_path = ckpt_path + f'_model_epoch{epoch}' if ckpt_path is not None \
                        else None
            if model_path is not None and not os.path.exists(ckpt_path):
                os.makedirs(ckpt_path)

            # https://zhuanlan.zhihu.com/p/136902153
            #TODO: be a config params
            checkpoint = {'model': self.model,
                          'model_state_dict': self.model.state_dict(),
                          'optimizer_state_dict': self.optimizer.state_dict(),
                            }
            self.save_model(model_path=model_path,
                            epoch=epoch,
                            checkpoint=checkpoint)
            
            callback.on_epoch_end(epoch, train_metric, self.epoch_loss, self.model, epoch_val_loss)

            if epoch_val_loss is not None and earlystopping is not None:
                if earlystopping(val_loss=epoch_val_loss, 
                                 train_epoch_loss=self.epoch_loss,
                                 metrics=train_metric
                                 ):
                    print(f'*********** EarlyStopping at epoch {epoch}***********')
                    break            
            train_metric.reset()

            print(f'------------Epoch {epoch} finished, cost {round(time.time() - ep_start_time, 3)} seconds------------')


#TODO: Need to be tested on GPU device
class DDPTrainer(TrainBase):

    def __init__(self, 
                model, 
                optimizer,
                lr_scheduler=None,
                *args, **keargs) -> None:
    
        self.world_size = dist.get_world_size()


    def start_to_train(self, 
                       train_data_loader: DataLoader,
                       epochs: int,
                       tb_path: str,
                       local_rank: int,
                       sampler,
                       ckpt_path: Optional[str] = None,
                       earlystopping: Optional[IEarlyStop] = None,
                       callback: ICallbacks = NullCallback(),
                       metrics: IMetric = NullMetric()
                        ) -> None:
        
        if earlystopping is not None and not issubclass(earlystopping.__class__, IEarlyStop):
            raise ValueError("Earlystopping object must the subclass of IEarlyStop interface")
        
        if  not issubclass(metrics.__class__, IMetric):
            raise ValueError("train_metric object must be the subclass of IMetric")        
        
        train_metric = metrics
        # master rank
        if dist.get_rank() == 0: 
            self.count_model_parameters()
            writer = SummaryWriter(tb_path)

        TRAINSTEP_PER_EPOCH = len(train_data_loader)
        for epoch in range(1, epochs+1):
            running_loss = 0

            print(f'------------Train local rank:{local_rank}, Train epoch:{epoch} start training------------')

            sampler.set_epoch(epoch)
            self.model.train()
            # TODO:make sure if it's correct , because this method will run on all ranks  
            callback.on_epoch_start(epoch)
            for X_batch, y_batch in train_data_loader:
                                         
                callback.on_batch_start()
                loss, y_pred = self.train_step(X_batch=X_batch, 
                                               y_batch=y_batch)
                
                running_loss += loss

                
                y_true = self.gather_all(y_batch.to(dist.get_rank()))
                y_true = torch.cat(y_true)
                y_pred = self.gather_all(y_pred.to(dist.get_rank()))
                y_pred = torch.cat(y_pred)
                if dist.get_rank() == 0:
                    train_metric.calculate_metric(y_true.cpu(), y_pred.cpu())
                dist.barrier()
                callback.on_batch_end()

            rank_epoch_loss = running_loss / TRAINSTEP_PER_EPOCH
            print(f"------rank_{dist.get_rank()} Epoch loss : {rank_epoch_loss}------")
            self.epoch_loss = self.reduce_sum_all(rank_epoch_loss)

            if dist.get_rank() == 0:
                epoch_loss = self.epoch_loss.cpu().numpy() / self.world_size

                train_tb = TensorBoard(writer, model=self.model)
                train_tb.start_to_write(metrics=train_metric,
                                        step=epoch,
                                        loss=self.epoch_loss,
                                        histogram=True,
                                        optimizer=self.optimizer)

                epoch_val_loss = self.validation_loop(epoch=epoch)

            
                print(f'------------Saving model for epoch {epoch}------------')
                model_path = ckpt_path + f'_model_epoch{epoch}' if ckpt_path is not None \
                        else None
                if model_path is not None and not os.path.exists(ckpt_path):
                    os.makedirs(ckpt_path)

                #TODO: be a config params
                checkpoint = {
                              'model_state_dict': self.model.state_dict(),
                              'optimizer_state_dict': self.optimizer.state_dict(),
                                }
                self.save_model(model_path=model_path,
                                epoch=epoch,
                                checkpoint=checkpoint)

                callback.on_epoch_end(epoch, train_metric, self.epoch_loss, epoch_val_loss)
                
                if epoch_val_loss is not None and earlystopping is not None:
                    if earlystopping(val_loss=epoch_val_loss, 
                                     train_epoch_loss=epoch_loss,
                                     metrics=train_metric):
                        print(f'*********** EarlyStopping at epoch {epoch}***********')
                        break
                self.train_metric.reset()
            print(f'------------Epoch {epoch} of RANK{dist.get_rank()} finished------------')
            dist.barrier()
        print("=======Finished Training=======")


    def gather_all(self, value_tensor):
        
        tensor_list = [torch.zeros_like(value_tensor).to(dist.get_rank()) for _ in range(self.world_size)]
        dist.all_gather(tensor_list, value_tensor)
        return tensor_list


    def reduce_sum_all(self, value_tensor):
        if not isinstance(value_tensor, torch.Tensor):
            value_tensor = torch.tensor(value_tensor).to(dist.get_rank())
        
        dist.all_reduce(value_tensor, op=dist.ReduceOp.SUM)

        return value_tensor


