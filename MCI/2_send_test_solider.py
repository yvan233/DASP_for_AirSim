import requests
import json
import time

from geo_change import *

'''
说明：本部分请参考接口文档，里面有详细说明
'''

task_name =  "task_A_202205292026"

solider_init_ip = "127.0.0.1"
solider_init_port = 10003

# 二、士兵通讯与控制
#-----------------------------------------------------------------------------------0
# 1. 与初始化接口通讯
# 注意：端口是10003
data_json = {"data":{"host":solider_init_ip,"port":solider_init_port,"task":task_name}} 
head = {"Content-Type": "application/json; charset=UTF-8", 'Connection': 'close'}
url ="http://127.0.0.1:5000/api/start_service_solider"
r = requests.post(url,json=data_json,headers=head)
if r.status_code == 200:
    data = json.loads(r.text)
    print(data)

time.sleep(5)

# 获取 动态UE4坐标系的原点坐标
ox,oy,oz = data["data"]["origin_coordinate"]

# 将UE静态坐标转为GPS坐标，假设UE原点对应的高德火星坐标是116.174646, 40.055388
# https://lbs.amap.com/tools/picker
# sx1,sy1,sz1 = 0.0,0.0,0.0
# sx2,sy2,sz2 = 1322.0,2115.0,0.0
# lng0, lat0 = gcj02_to_wgs84(116.174646, 40.055388)
# alt0 = 150. # 北京平均海拔

# lng1,lat1,alt1 = ues2gps(sx1,sy1,sz1,lng0,lat0,alt0)
# lng2,lat2,alt2 = ues2gps(sx2,sy2,sz2,lng0,lat0,alt0)

lng1,lat1,alt1 = 116.168518814716,40.0535735160858,157.015943688916 # 某个start
lng2,lat2,alt2 = 116.168297539873,40.053015051946,157.126980113759 # 椅子


# 2. 与士兵数据存储接口通讯
data_json = {"data":{"task":task_name,"record_all":1}} 
head = {"Content-Type": "application/json; charset=UTF-8", 'Connection': 'close'}
url ="http://127.0.0.1:5000/api/record_data_solider"
r = requests.post(url,json=data_json,headers=head)
if r.status_code == 200:
    data = json.loads(r.text)
    print(data)


'''
  说明：前两步在UE4运行前就发送，执行完成之后，可以在任意时刻发送下方的控制命令
'''

time.sleep(5)

# 3. 与士兵控制接口通讯(往前走是N，往右走是E)，以下是对各个士兵的各种控制示例，详见api文档

# data_json = {"data":{"MIS_AI":{"data":{"option":0,"destination":{"xc":-3000.0,"yc":3000.0,"zc":500.0}}},'MIS_AI2':{"data":{"option":0,"destination":{"xc":-3000.0,"yc":3000.0,"zc":500.0}}}}}
data_json = {"data":{"SOL_AI":{"data":{"option":0,"destination":{"lng":lng2,"lat":lat2,"alt":alt2}}},'SOL_AI2':{"data":{"option":0,"destination":{"lng":lng2,"lat":lat2,"alt":alt2}}},"SOL_AI3":{"data":{"option":1,"control":{"forward":1.0,"right":0.0}}}}}
head = {"Content-Type": "application/json; charset=UTF-8", 'Connection': 'close'}
url ="http://127.0.0.1:5000/api/control_solider"
r = requests.post(url,json=data_json,headers=head)
if r.status_code == 200:
    data = json.loads(r.text)
    print(data)

time.sleep(2)

data_json = {"data":{"SOL_AI3":{"data":{"option":1,"control":{"forward":0.,"right":0.}}}}}
head = {"Content-Type": "application/json; charset=UTF-8", 'Connection': 'close'}
url ="http://127.0.0.1:5000/api/control_solider"
r = requests.post(url,json=data_json,headers=head)
if r.status_code == 200:
    data = json.loads(r.text)
    print(data)

time.sleep(10)

data_json = {"data":{"SOL_AI3":{"data":{"option":1,"control":{"forward":0.0,"right":1.0}}},'SOL_AI2':{"data":{"option":2}},"SOL_AI":{"data":{"option":0,"destination":{"lng":lng1,"lat":lat1,"alt":alt1}}}}}
head = {"Content-Type": "application/json; charset=UTF-8", 'Connection': 'close'}
url ="http://127.0.0.1:5000/api/control_solider"
r = requests.post(url,json=data_json,headers=head)
if r.status_code == 200:
    data = json.loads(r.text)
    print(data)

time.sleep(10)

data_json = {"data":{"SOL_AI3":{"data":{"option":1,"control":{"forward":1.0,"right":0.0}}},'SOL_AI2':{"data":{"option":1,"control":{"forward":1.0,"right":0.0}}}}}
head = {"Content-Type": "application/json; charset=UTF-8", 'Connection': 'close'}
url ="http://127.0.0.1:5000/api/control_solider"
r = requests.post(url,json=data_json,headers=head)
if r.status_code == 200:
    data = json.loads(r.text)
    print(data)

time.sleep(2)
data_json = {"data":{'SOL_AI2':{"data":{"option":3}}}}
head = {"Content-Type": "application/json; charset=UTF-8", 'Connection': 'close'}
url ="http://127.0.0.1:5000/api/control_solider"
r = requests.post(url,json=data_json,headers=head)
if r.status_code == 200:
    data = json.loads(r.text)
    print(data)
#-----------------------------------------------------------------------------------1