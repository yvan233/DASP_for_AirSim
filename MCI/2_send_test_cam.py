import requests
import json
import time

'''
说明：本部分请参考接口文档，里面有详细说明
'''


data_json = {"data":{"start":1}}
head = {"Content-Type": "application/json; charset=UTF-8", 'Connection': 'close'}
url ="http://127.0.0.1:5000/api/start_service_camera"
r = requests.post(url,json=data_json,headers=head)
if r.status_code == 200:
    data = json.loads(r.text)
    print(data)

time.sleep(20)
print("切换UE")
# 切换
data_json = {"data":{"option":0,"cname":"CameraActor"}}
head = {"Content-Type": "application/json; charset=UTF-8", 'Connection': 'close'}
url ="http://127.0.0.1:5000/api/control_camera"
r = requests.post(url,json=data_json,headers=head)
if r.status_code == 200:
    data = json.loads(r.text)
    print(data)

time.sleep(5)
print("切换AirSim")
# 切换
data_json = {"data":{"option":1,"cname":"test1_car_camera_driver"}}
head = {"Content-Type": "application/json; charset=UTF-8", 'Connection': 'close'}
url ="http://127.0.0.1:5000/api/control_camera"
r = requests.post(url,json=data_json,headers=head)
if r.status_code == 200:
    data = json.loads(r.text)
    print(data)