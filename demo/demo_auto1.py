# 自动控制demo
import time
import socket
import sys
sys.path.insert(1,".") # 把上一级目录加入搜索路径
from DASP.control import ControlMixin
from DaspCarClient import DaspCarClient,get_image,get_lidar

if __name__ == '__main__':
    Controlmixin = ControlMixin("Pc") # 控制函数集合
    DAPPname = "Airsim"
    rootnode = "Car0" # 根节点ID
    print("开始任务："+DAPPname)
    Controlmixin.StartTask(DAPPname,rootnode)

    time.sleep(5)
    host = socket.gethostbyname(socket.gethostname())
    remote_ip = host
    
    # 初始化客户端实例,与服务器端建立连接
    client = DaspCarClient(host)

    # 获取车辆状态
    state = client.get_state()
    print("车辆状态",state)  

    # 开始记录数据
    print("start record")
    client.start_record()

    # 读取碰撞信息
    collision = client.get_collision()
    if collision["has_collided"]:
        print (f"collision with {collision['object_name']}")

    # 获取图像
    img = get_image(remote_ip)
    # print(img)

    # 获取雷达
    lidar = get_lidar(remote_ip)
    # print(lidar)

    # 前进
    action = {"throttle": 1,"steering": 0,"brake": 0}
    client.do_action(action)
    print("前进",action)
    time.sleep(3)

    # 转向
    action = {"throttle": 1,"steering": 50,"brake": 0}
    client.do_action(action)
    print("右转",action)
    time.sleep(1.3)

    # 前进
    action = {"throttle": 1,"steering": 0,"brake": 0}
    client.do_action(action)
    print("前进",action)
    time.sleep(2)

    # 后退
    action = {"throttle": -1,"steering": 0,"brake": 0}
    client.do_action(action)
    print("后退",action)
    time.sleep(2.5)

    # 刹车
    action = {"throttle": 0,"steering": 0,"brake": 1}
    client.do_action(action)
    print("刹车",action)
    time.sleep(2)

    # 重置
    print("reset")
    client.reset()

    # 结束记录数据
    print("stop record")
    client.stop_record()