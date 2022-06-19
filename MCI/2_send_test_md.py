from aifc import Error
import requests
import json
import time

from geo_change import *

# import sqlite3
from pymongo import MongoClient

'''
说明：本部分请参考接口文档，里面有详细说明
'''

task_name = "task_A_202205292026"
db_name_init = task_name+"_init_missile"
db_collection_init = "init_missile"
db_name_record = task_name+"_record_missile"

md_init_ip = "127.0.0.1"
md_init_port = 10005

# 二、拦截弹通讯与控制
#-----------------------------------------------------------------------------------0
# 1. 与初始化接口通讯
# 注意：端口是10005
data_json = {"data":{"host":md_init_ip,"port":md_init_port,"task":task_name}} 
head = {"Content-Type": "application/json; charset=UTF-8", 'Connection': 'close'}
url ="http://127.0.0.1:5000/api/start_service_md"
r = requests.post(url,json=data_json,headers=head)
if r.status_code == 200:
    data0 = json.loads(r.text)
    print(data0)

time.sleep(5)


# 2. 与拦截弹数据存储接口通讯
data_json = {"data":{"task":task_name,"record_all":1}} 
head = {"Content-Type": "application/json; charset=UTF-8", 'Connection': 'close'}
url ="http://127.0.0.1:5000/api/record_data_md"
r = requests.post(url,json=data_json,headers=head)
if r.status_code == 200:
    data = json.loads(r.text)
    print(data)


'''
  说明：前两步在UE4运行前就发送，执行完成之后，可以在任意时刻发送下方的控制命令
'''

time.sleep(5)

# 3. 与拦截弹控制接口通讯
# 先瞄准某个位置------------------------------------0

target0 = "MIS_AI"
target1 = "MIS_AI2"

# 通过初始化数据库读取目标的id
# db_name0 = "missile_init.db"
# conn0 = sqlite3.connect("./{}".format(db_name0), check_same_thread=False)
# cursor0 = conn0.cursor()
# cursor0.execute("select * from {} where NAME=?".format(task_name),("{}".format(target0),))
# id0 = cursor0.fetchall()[0][1]
# cursor0.execute("select * from {} where NAME=?".format(task_name),("{}".format(target1),))
# id1 = cursor0.fetchall()[0][1]
# print(id0,id1)
# conn0.close()

# 连接数据库 MongoDB
conn = MongoClient(host= '127.0.0.1', port=9999)

# 创建数据库与collection MongoDB
db = conn.get_database(db_name_init)
col = db.get_collection(db_collection_init)

id0 = col.find({"NAME":target0})[0]["ID"]
id1 = col.find({"NAME":target1})[0]["ID"]
print(id0,id1)
# 读取目标当前位置
db = conn.get_database(db_name_record)
col0 = db["ID{}".format(id0)]
out0 = col0.find().sort("TIMESTAMP",-1)[0]
lng0,lat0,alt0 = out0["LNG"],out0["LAT"],out0["ALT"]

col1 = db["ID{}".format(id1)]
out1 = col1.find().sort("TIMESTAMP",-1)[0]
lng1,lat1,alt1 = out1["LNG"],out1["LAT"],out1["ALT"]
#--------------------------------------------------1

data_json = {"data":{"MD_AI":{"data":{"option":0,"destination":{"lng":lng0,"lat":lat0,"alt":alt0}}},'MD_AI2':{"data":{"option":0,"destination":{"lng":lng1,"lat":lat1,"alt":alt1}}}}}
head = {"Content-Type": "application/json; charset=UTF-8", 'Connection': 'close'}
url ="http://127.0.0.1:5000/api/control_md"
r = requests.post(url,json=data_json,headers=head)
if r.status_code == 200:
    data = json.loads(r.text)
    print(data)

time.sleep(1.5)

data_json = {"data":{"MD_AI":{"data":{"option":1}},'MD_AI2':{"data":{"option":1}}}}
head = {"Content-Type": "application/json; charset=UTF-8", 'Connection': 'close'}
url ="http://127.0.0.1:5000/api/control_md"
r = requests.post(url,json=data_json,headers=head)
# if r.status_code == 200:
#     data = json.loads(r.text)
#     print(data)

while True:
    # 实时获取对方导弹位置
    out0 = col0.find().sort("TIMESTAMP",-1)[0]
    # print(out0)
    lng0,lat0,alt0 = out0["LNG"],out0["LAT"],out0["ALT"]
    
    out1 = col1.find().sort("TIMESTAMP",-1)[0]
    lng1,lat1,alt1 = out1["LNG"],out1["LAT"],out1["ALT"]
    
    data_json = {"data":{"MD_AI":{"data":{"option":0,"destination":{"lng":lng0,"lat":lat0,"alt":alt0}}},'MD_AI2':{"data":{"option":0,"destination":{"lng":lng1,"lat":lat1,"alt":alt1}}}}}
    head = {"Content-Type": "application/json; charset=UTF-8", 'Connection': 'close'}
    url ="http://127.0.0.1:5000/api/control_md"
    r = requests.post(url,json=data_json,headers=head)
    if r.status_code != 200:
        break
    # 未来这块还需要在处理一下，让它正常退出循环

print("拦截弹控制完毕！")
#-----------------------------------------------------------------------------------1