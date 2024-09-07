import time
print("テストモード...計測を開始します")
start = time.time()
import os
from inference.Seq2Seq import Learning  
import torch_directml
#Batch_sizeは2のn乗でないといけない
batch_size = 16
APP_dir = os.path.dirname(os.path.dirname(__file__))
device=torch_directml.device()
os.chdir(os.path.join(APP_dir, "model/Learning_test_model/Lerarning"))

with open("input.txt", "r", encoding="utf-8") as f:
    inputs = f.readlines()
with open("output.txt", "r", encoding="utf-8") as f:
    outputs = f.readlines()

model=Learning(inputs,outputs,device=device,batch_size=batch_size,lr=0.01,epochs=100)
end=time.time()
time_diff = end - start
print(time_diff)
