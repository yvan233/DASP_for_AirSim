# 启动系统并运行分布式算法
from threading import Thread
from moniter import moniter
import time 
import sys
sys.path.insert(1,".") # 把上一级目录加入搜索路径
from DASP.module import Node
from DASP.control import ControlMixin

nodeNum = 2  # 节点数量
rootnode = "Car0" # 根节点ID
nodelist = [] # 节点进程列表
Controlmixin = ControlMixin("Pc") # 控制函数集合

# 启动监控脚本
t = Thread(target=moniter,)    
t.start()

# 启动节点进程
for i in range(nodeNum):
    node = Node(i+1,mode = False)
    nodelist.append(node)

time.sleep(2)
DAPPname = "Airsim"
print("开始任务："+DAPPname)
Controlmixin.StartTask(DAPPname,rootnode)