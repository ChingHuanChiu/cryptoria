import sys
import warnings  
warnings.filterwarnings("ignore")  
sys.path.append("../..")

from torch.utils.data import Dataset, DataLoader
import pandas as pd
import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim
from torch.utils.tensorboard import SummaryWriter
from torch.utils.data import Dataset, DataLoader
from transformers import get_cosine_schedule_with_warmup
from sklearn.preprocessing import MinMaxScaler


from src.minner.dl.abstract.train import Trainer
from src.minner.dl.tensorboard import TensorBoard
from src.minner.dl.metrics import ClassificationTorchMetric
from src.minner.dl.earlystopping import WorseValLossEarlyStopping


class MyModel(nn.Module):

    def __init__(self):
        super().__init__()
        self.fc1 = nn.Linear(5, 4)
        self.fc2 = nn.Linear(4, 2)

    
    def forward(self, inps):
        x = F.relu(self.fc1(inps))
        x = self.fc2(x)
        return x


class DummyDataset(Dataset):


    def __init__(self, data: pd.DataFrame):

        self.data = data

    
    def __len__(self):

        return self.data.shape[0]


    def __getitem__(self, idx):

        data = self.data.iloc[idx,  :]
        x, y = data[["Open", "High", "Low", "Adj Close", "Volume" ]].values,\
            data["label"]
        
        return torch.Tensor(x), torch.Tensor(np.array(y))


class MyTrainer(Trainer):

    def __init__(self, 
                 model,
                 optimizer,
                 lr_scheduler, 
                 val_dataloader, 
                 ):
        super().__init__(model, optimizer, lr_scheduler)

        self.val_dataloader = val_dataloader
        self.loss_fn = nn.CrossEntropyLoss()

    
    def train_step(self, X_batch, y_batch):
        
        logits = self.model(X_batch)

        y_hat = torch.argmax(F.softmax(logits), dim=-1)
        loss = self.loss_fn(logits, y_batch.long())

        self.optimizer.zero_grad()
        loss.backward()
        self.optimizer.step()
        self.lr_scheduler.step()

        return loss, y_hat
    

    def validation_loop(self, epoch):
        VALSTEP_PER_EPOCH = len(self.val_dataloader)
        val_running_loss = 0
        val_writer = SummaryWriter('../storage/tb/val/test1/')
        val_tb = TensorBoard(val_writer)
        val_metric = ClassificationTorchMetric()
        self.model.eval()
        with torch.no_grad():
            for X_val, y_val in self.val_dataloader:

                val_logits = self.model(X_val)

                val_y_hat = torch.argmax(F.softmax(val_logits), dim=-1)

                val_running_loss += self.loss_fn(val_logits, y_val.long())
        
                val_metric.calculate_metric(y_val, val_y_hat)
        epoch_val_loss = val_running_loss / VALSTEP_PER_EPOCH
        print(f"Validation Epoch Loss :  {self.epoch_loss}")

        val_tb.start_to_write(metrics=val_metric,
                              loss=epoch_val_loss,
                              step=epoch)
        val_metric.reset()

        return epoch_val_loss
    

def main():

    df = pd.read_csv("../storage/data/BTC-USD.csv").drop("Date", 1)
    df["label"] = np.where(df["Adj Close"].pct_change() >= 0, 1, 0).astype(int)

    scaler = MinMaxScaler()
    minmax_df = pd.DataFrame(scaler.fit_transform(df[["Open", "High", "Low", "Adj Close", "Volume" ]].values), 
                             columns=["Open", "High", "Low", "Adj Close", "Volume" ])
    minmax_df["label"] = df.label

    length_df = minmax_df.shape[0]
    split_point = int(0.7*length_df)
    train_data = minmax_df.iloc[:split_point, :]
    train_dataset = DummyDataset(data=train_data)
    train_loader = DataLoader(train_dataset, batch_size=32)

    val_data = minmax_df.iloc[split_point:, :].reset_index()
    val_dataset = DummyDataset(data=val_data)
    val_loader = DataLoader(val_dataset, batch_size=32)

    model = MyModel()
    EPOCHS = 3
    optimizer = torch.optim.Adam(model.parameters(), lr=0.001)
    lr_scheduler = get_cosine_schedule_with_warmup(
                                                    optimizer=optimizer,
                                                    num_warmup_steps=100,
                                                    num_training_steps=EPOCHS *len(train_loader)
                                                  )
    trainer = MyTrainer(
                        model=model,
                        optimizer=optimizer,
                        lr_scheduler=lr_scheduler,
                        val_dataloader=val_loader,
                        )
    

    trainer.start_to_train(train_data_loader=train_loader,
                           epochs=EPOCHS,
                           ckpt_path="../storage/model/test1/",
                           tb_path="../storage/tb/train/test1/",
                           earlystopping=WorseValLossEarlyStopping(3), 
                           metrics=ClassificationTorchMetric())


if __name__ == '__main__':

    main() 

        
                
                
