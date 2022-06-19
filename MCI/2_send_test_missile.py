from aifc import Error
import requests
import json
import time

from geo_change import *

'''
说明：本部分请参考接口文档，里面有详细说明
'''

task_name = "task_A_202205292026"

missile_init_ip = "127.0.0.1"
missile_init_port = 10002

# 二、导弹通讯与控制
#-----------------------------------------------------------------------------------0
# 1. 与初始化接口通讯
# 注意：端口是10002
data_json = {"data":{"host":missile_init_ip,"port":missile_init_port,"task":task_name}} 
head = {"Content-Type": "application/json; charset=UTF-8", 'Connection': 'close'}
url ="http://127.0.0.1:5000/api/start_service_missile"
r = requests.post(url,json=data_json,headers=head)
if r.status_code == 200:
    data = json.loads(r.text)
    print(data)

time.sleep(5)
print(r.status_code)
print(data)
# 获取 动态UE4坐标系的原点坐标
if data != None:    
    if data["stat"] == 0:
        ox,oy,oz = data["data"]["origin_coordinate"]
    else:
        raise Exception("返回状态错误！")
else:
    raise Exception("返回状态错误！")

# 将UE静态坐标转为GPS坐标，假设UE原点对应的高德火星坐标是116.174646, 40.055388
# https://lbs.amap.com/tools/picker

# sx1,sy1,sz1 = -539670.000000,15820.000000,300.00000
# sx2,sy2,sz2 = 6000.0,6000.0,0.0
# lng0, lat0 = gcj02_to_wgs84(116.174646, 40.055388)
# alt0 = 150. # 北京平均海拔

# lng1,lat1,alt1 = ues2gps(sx1,sy1,sz1,lng0,lat0,alt0)
# lng2,lat2,alt2 = ues2gps(sx2,sy2,sz2,lng0,lat0,alt0)
lng1,lat1,alt1 = 116.168297539873,40.053015051946,157.126980113759 # 椅子的位置

# 将UE动态坐标转GPS坐标 -3000.0,3000.0,500.0  -6000.0,-6000.0,500.0
# dx1,dy1,dz1 = -3000.0,3000.0,500.0
dx2,dy2,dz2 = -6000.0,-6000.0,500.0

# lng3,lat3,alt3 = ued2gps(dx1,dy1,dz1,ox,oy,oz,lng0,lat0,alt0)
# lng4,lat4,alt4 = ued2gps(dx2,dy2,dz2,ox,oy,oz,lng0,lat0,alt0)

lng4,lat4,alt4 = 116.115708882407,40.0669490404869,173.935998552175 # 跨海大桥的尽头

# 2. 与导弹数据存储接口通讯
data_json = {"data":{"task":task_name,"record_all":1}} 
head = {"Content-Type": "application/json; charset=UTF-8", 'Connection': 'close'}
url ="http://127.0.0.1:5000/api/record_data_missile"
r = requests.post(url,json=data_json,headers=head)
if r.status_code == 200:
    data = json.loads(r.text)
    print(data)


'''
  说明：前两步在UE4运行前就发送，执行完成之后，可以在任意时刻发送下方的控制命令
'''

time.sleep(5)

# 3. 与导弹控制接口通讯
# data_json = {"data":{"MIS_AI":{"data":{"option":0,"destination":{"xc":-3000.0,"yc":3000.0,"zc":500.0}}},'MIS_AI2':{"data":{"option":0,"destination":{"xc":-3000.0,"yc":3000.0,"zc":500.0}}}}}
data_json = {"data":{"MIS_AI":{"data":{"option":0,"destination":{"lng":lng1,"lat":lat1,"alt":alt1}}},'MIS_AI2':{"data":{"option":0,"destination":{"lng":lng1,"lat":lat1,"alt":alt1}}}}}
head = {"Content-Type": "application/json; charset=UTF-8", 'Connection': 'close'}
url ="http://127.0.0.1:5000/api/control_missile"
r = requests.post(url,json=data_json,headers=head)
if r.status_code == 200:
    data = json.loads(r.text)
    print(data)

time.sleep(2)

data_json = {"data":{"MIS_AI":{"data":{"option":1}},'MIS_AI2':{"data":{"option":1}}}}
head = {"Content-Type": "application/json; charset=UTF-8", 'Connection': 'close'}
url ="http://127.0.0.1:5000/api/control_missile"
r = requests.post(url,json=data_json,headers=head)
if r.status_code == 200:
    data = json.loads(r.text)
    print(data)

time.sleep(5)
data_json = {"data":{"MIS_AI3":{"data":{"option":0,"destination":{"lng":lng4,"lat":lat4,"alt":alt4}}}}}
head = {"Content-Type": "application/json; charset=UTF-8", 'Connection': 'close'}
url ="http://127.0.0.1:5000/api/control_missile"
r = requests.post(url,json=data_json,headers=head)
if r.status_code == 200:
    data = json.loads(r.text)
    print(data)
time.sleep(5)
data_json = {"data":{"MIS_AI3":{"data":{"option":1}}}}
head = {"Content-Type": "application/json; charset=UTF-8", 'Connection': 'close'}
url ="http://127.0.0.1:5000/api/control_missile"
r = requests.post(url,json=data_json,headers=head)
if r.status_code == 200:
    data = json.loads(r.text)
    print(data)
#-----------------------------------------------------------------------------------1