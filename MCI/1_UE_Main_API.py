# import sqlite3
from pymongo import MongoClient
from TCPSOCKET import TCPSOCKET,init_info
import os
from flask import Flask,jsonify,request
from flask_cors import CORS
from gevent import monkey
from gevent import pywsgi
import joblib
from loguru import logger
import ctypes
import warnings
import yaml

from geo_change import *

yaml.warnings({'YAMLLoadWarning':False})

warnings.filterwarnings("ignore")
logger.add('runtime.log', rotation = "100 MB", retention = "30 days")


def read_yaml(path="gps.conf",option="GPS0"):
    '''
    读 yaml 文件，提供 UE 静态系下 0,0,0 点的经纬高
    '''
    if os.path.exists(path):
        try:
            with open(path,'r',encoding='utf-8') as f:
                cfg = f.read()
                cfg = yaml.load(cfg,Loader=yaml.FullLoader)
        except:
                return False,{}    

    if option in cfg.keys():
        # 检测 GPS
        gps = cfg[option]

        if type(gps) is not dict:
            return False,{}

        if not (set(gps.keys()) == set(['lng0','lat0','alt0'])):
            return False,{}
        
        if not all([ ((type(gps[i]) is float) and (gps[i] >= 0 ))  for i in ['lng0','lat0','alt0'] ]):
            return False,{}
        
        return True,gps
        
    else:
        return False,{}

# UE4 静态坐标系 0,0,0 坐标对应的经纬度定位全局变量，高德地图拾取到的坐标转为wgs84 gps坐标
# lng0, lat0 = gcj02_to_wgs84(116.174646, 40.055388)
# alt0 = 150. # 北京平均海拔

# 原点 GPS 初始化自动获取
#-----------------------------------------------0
# path = "E:\\shilong\\MCI_v0.3.4\\gps.conf" # 环保园
path = "C:\\Users\\shilong\Desktop\\MCI_v0.3.4\\MCI_v0.3.4\\gps.conf"
option = "GPS0"
stat,gps = read_yaml(path=path,option=option)
if stat:
    # 注意经纬高对应UE4 中 0,0,0 点的经纬高，且符合 WGS84 标准
    lng0,lat0,alt0 = gps["lng0"],gps["lat0"],gps["alt0"]
    print(lng0,lat0,alt0)
else:
    raise Exception("gps.conf 文件配置错误！请检查！")
#-----------------------------------------------1

monkey.patch_all()
app = Flask(__name__)

# 0. 切换镜头接口
#-----------------------------------------------------------------------------------------------------------------------------0
# 启动记录数据与智体通讯接口
@app.route('/api/start_service_camera', methods= ['POST'])
def start_service_camera():
    input = request.get_json()
    
    data = input["data"]
    start = data["start"]
    db = ""
    ip = "127.0.0.1"
    port = 9998
    info_dict = {}
    info_dict2 = {}
    if start: 
        info_dict2["tcpsocket"] = TCPSOCKET(ip, port, db, lng0, lat0,alt0,record=False)
        info_dict["tcpsocket"] = id(info_dict2["tcpsocket"])
        joblib.dump(info_dict,'camera_info_dict.pkl')
        
        out = {"stat":0,"msg":"Success!"}
    else:
        out =  {"stat":1,"msg":"目前start只支持设为1，不能为别的，如有需要可联系工程师！"}
    
    return jsonify(out)

# 初始化切换镜头服务
@app.route('/api/control_camera', methods=['POST'])
def control_camera():
    input = request.get_json()

    if os.path.exists('camera_info_dict.pkl'):
        info_dict = joblib.load('camera_info_dict.pkl')
    else:
        out =  {"stat":1,"msg":"请先与接口“/api/start_service_camera”进行通讯！"}
        return jsonify(out)
    
    client = info_dict["tcpsocket"]
    print(ctypes.cast(client, ctypes.py_object).value.send(input))
    
    out = {"stat":0,"msg":"Success!"}
    return jsonify(out)
#-----------------------------------------------------------------------------------------------------------------------------1

#-----------------------------------------------------------------------------------------------------------------------------1

# 1. 坦克接口
#-----------------------------------------------------------------------------------------------------------------------------0
# 初始化服务接口
@app.route('/api/start_service_tank', methods= ['POST'])
def start_service_tank():
    # input = request.get_data(as_text=True)
    input = request.get_json()
    # print(input)
    data = input["data"]
    host = data["host"]
    port = data["port"]
    task = data["task"]+"_init_tank" #
    db_table = "init_tank" # 
    info_dict,stat,origin_coordinate = init_info(host,port,task,db_table)
    if not stat:
        out = {"stat":1,"msg":"数据通讯错误！","data":{}}
        return jsonify(out)

    joblib.dump(info_dict, 'tank_info_dict.pkl')
    joblib.dump(origin_coordinate,"origin_coordinate.pkl")

    out = {"stat":0,"msg":"Success!","data":{"origin_coordinate":origin_coordinate,"info_dict":info_dict}}
    return jsonify(out)

# 启动记录数据与智体通讯接口
@app.route('/api/record_data_tank', methods= ['POST'])
def data_record_tank():
    input = request.get_json()
    
    data = input["data"]

    record_all = data["record_all"]
    task = data["task"]+"_record_tank"

    if os.path.exists('tank_info_dict.pkl') and os.path.exists("origin_coordinate.pkl"):
        info_dict = joblib.load('tank_info_dict.pkl')
        origin_coordinate = joblib.load('origin_coordinate.pkl')
    else:
        out =  {"stat":1,"msg":"请先与接口“/api/start_service_tank”进行通讯！"}
        return jsonify(out)

    # MongoDB
    conn = MongoClient(host= '127.0.0.1', port=9999)

    # 创建数据库 MongoDB
    db = conn.get_database(task)

    info_dict2 = {}
    if record_all:
        for name in info_dict.keys():
            ip = info_dict[name][1]
            port = info_dict[name][2]
            info_dict2[name] = TCPSOCKET(ip, port, db, lng0, lat0,alt0,record=True)
            info_dict[name].append(id(info_dict2[name]))
        
        joblib.dump(info_dict,'tank_info_dict.pkl')
        
        out = {"stat":0,"msg":"Success!"}
    else:
        out =  {"stat":1,"msg":"目前record_all只支持设为1，不能为别的，如有需要可联系工程师！"}
    
    return jsonify(out)

# Tank 智体控制接口
@app.route('/api/control_tank', methods=['POST'])
def control_tank():
    input = request.get_json()

    data = input["data"]

    if os.path.exists('tank_info_dict.pkl') and os.path.exists("origin_coordinate.pkl"):
        info_dict = joblib.load('tank_info_dict.pkl')
        origin_coordinate = joblib.load('origin_coordinate.pkl')
    else:
        out =  {"stat":1,"msg":"请先与接口“/api/start_service_tank”进行通讯！"}
        return jsonify(out)
    
    for name in data.keys():
        if len(info_dict[name]) == 4:
            # 对经纬高转换，变成UE4动态坐标的xyz
            #------------------------------------0
            if not data[name]["data"]["option"]:
                destination = data[name]["data"]["destination"]
                ox,oy,oz = origin_coordinate
                lng,lat,alt = destination["lng"],destination["lat"],destination["alt"]
                data[name]["data"]["destination"]["xc"],data[name]["data"]["destination"]["yc"] ,data[name]["data"]["destination"]["zc"] = gps2ued(lng,lat,alt,lng0,lat0,alt0,ox,oy,oz)
                print([lng0,lat0,alt0],[lng,lat,alt],[ox,oy,oz])
                # print("经纬高变换xyz:",data)
            #------------------------------------1
            ctypes.cast(info_dict[name][3], ctypes.py_object).value.send(data[name])
        else:
            out = {"stat":1,"msg":"请先与接口“/api/record_data_tank”进行通讯！"}
            return jsonify(out)
            

    out = {"stat":0,"msg":"Success!"}
    return jsonify(out)
#-----------------------------------------------------------------------------------------------------------------------------1


# 2. 导弹接口
#-----------------------------------------------------------------------------------------------------------------------------0
# 初始化服务接口
@app.route('/api/start_service_missile', methods= ['POST'])
def start_service_missile():
    # input = request.get_data(as_text=True)
    input = request.get_json()
    # print(input)
    data = input["data"]
    host = data["host"]
    port = data["port"]
    task = data["task"]+"_init_missile" # 
    db_table = "init_missile" 
    info_dict,stat,origin_coordinate = init_info(host,port,task,db_table)
    if not stat:
        out = {"stat":1,"msg":"数据通讯错误！","data":{}}
        return jsonify(out)

    joblib.dump(info_dict, 'missile_info_dict.pkl')
    joblib.dump(origin_coordinate,"origin_coordinate2.pkl")

    out = {"stat":0,"msg":"Success!","data":{"origin_coordinate":origin_coordinate,"info_dict":info_dict}}
    return jsonify(out)

# 启动记录数据与智体通讯接口
@app.route('/api/record_data_missile', methods= ['POST'])
def data_record_missile():
    input = request.get_json()
    
    data = input["data"]
    record_all = data["record_all"]
    task = data["task"]+"_record_missile"

    if os.path.exists('missile_info_dict.pkl') and os.path.exists('origin_coordinate2.pkl'):
        info_dict = joblib.load('missile_info_dict.pkl')
        origin_coordinate = joblib.load('origin_coordinate2.pkl')
    else:
        out =  {"stat":1,"msg":"请先与接口“/api/start_service_missile”进行通讯！"}
        return jsonify(out)

    # MongoDB
    conn = MongoClient(host= '127.0.0.1', port=9999)

    # 创建数据库 MongoDB
    db = conn.get_database(task)

    info_dict2 = {}
    if record_all:
        for name in info_dict.keys():
            ip = info_dict[name][1]
            port = info_dict[name][2]
            info_dict2[name] = TCPSOCKET(ip, port, db,lng0,lat0,alt0,record=True)
            info_dict[name].append(id(info_dict2[name]))
        
        joblib.dump(info_dict,'missile_info_dict.pkl')
        
        out = {"stat":0,"msg":"Success!"}
    else:
        out =  {"stat":1,"msg":"目前record_all只支持设为1，不能为别的，如有需要可联系工程师！"}
    
    return jsonify(out)

# Missile 智体控制接口
@app.route('/api/control_missile', methods= ['POST'])
def control_missile():
    input = request.get_json()

    data = input["data"]

    if os.path.exists('missile_info_dict.pkl') and os.path.exists("origin_coordinate2.pkl"):
        info_dict = joblib.load('missile_info_dict.pkl')
        origin_coordinate = joblib.load('origin_coordinate2.pkl')
    else:
        out =  {"stat":1,"msg":"请先与接口“/api/start_service_missile”进行通讯！"}
        return jsonify(out)
    
    for name in data.keys():
        if len(info_dict[name]) == 4:
            # 对经纬高转换，变成UE4动态坐标的xyz
            #------------------------------------0
            if not data[name]["data"]["option"]:
                destination = data[name]["data"]["destination"]
                ox,oy,oz = origin_coordinate
                lng,lat,alt = destination["lng"],destination["lat"],destination["alt"]
                data[name]["data"]["destination"]["xc"],data[name]["data"]["destination"]["yc"] ,data[name]["data"]["destination"]["zc"] = gps2ued(lng,lat,alt,lng0,lat0,alt0,ox,oy,oz)
                # print("经纬高变换xyz:",data)
            #------------------------------------1
            ctypes.cast(info_dict[name][3], ctypes.py_object).value.send(data[name])
        else:
            out = {"stat":1,"msg":"请先与接口“/api/record_data_missile”进行通讯！"}
            return jsonify(out)

    out = {"stat":0,"msg":"Success!"}
    return jsonify(out)
#-----------------------------------------------------------------------------------------------------------------------------1

# 3. 士兵接口
#-----------------------------------------------------------------------------------------------------------------------------0
# 初始化服务接口
@app.route('/api/start_service_solider', methods= ['POST'])
def start_service_solider():
    # input = request.get_data(as_text=True)
    input = request.get_json()
    # print(input)
    data = input["data"]
    host = data["host"]
    port = data["port"]
    task = data["task"]+"_init_solider" # 
    db_table = "init_solider"
    info_dict,stat,origin_coordinate = init_info(host,port,task,db_table)
    if not stat:
        out = {"stat":1,"msg":"数据通讯错误！","data":{}}
        return jsonify(out)

    joblib.dump(info_dict, 'solider_info_dict.pkl')
    joblib.dump(origin_coordinate,"origin_coordinate3.pkl")

    out = {"stat":0,"msg":"Success!","data":{"origin_coordinate":origin_coordinate,"info_dict":info_dict}}
    return jsonify(out)

# 启动记录数据与智体通讯接口
@app.route('/api/record_data_solider', methods= ['POST'])
def data_record_solider():
    input = request.get_json()
    
    data = input["data"]

    record_all = data["record_all"]
    task = data["task"]+"_record_solider"

    if os.path.exists('solider_info_dict.pkl') and os.path.exists("origin_coordinate3.pkl"):
        info_dict = joblib.load('solider_info_dict.pkl')
        origin_coordinate = joblib.load('origin_coordinate3.pkl')
    else:
        out =  {"stat":1,"msg":"请先与接口“/api/start_service_solider”进行通讯！"}
        return jsonify(out)

    # MongoDB
    conn = MongoClient(host= '127.0.0.1', port=9999)

    # 创建数据库 MongoDB
    db = conn.get_database(task)

    info_dict2 = {}
    if record_all:
        for name in info_dict.keys():
            ip = info_dict[name][1]
            port = info_dict[name][2]
            info_dict2[name] = TCPSOCKET(ip, port, db,lng0, lat0,alt0,record=True)
            info_dict[name].append(id(info_dict2[name]))
        
        joblib.dump(info_dict,'solider_info_dict.pkl')
        
        out = {"stat":0,"msg":"Success!"}
    else:
        out =  {"stat":1,"msg":"目前record_all只支持设为1，不能为别的，如有需要可联系工程师！"}
    
    return jsonify(out)

# 士兵 智体控制接口
@app.route('/api/control_solider', methods=['POST'])
def control_solider():
    input = request.get_json()

    data = input["data"]

    if os.path.exists('solider_info_dict.pkl') and os.path.exists("origin_coordinate3.pkl"):
        info_dict = joblib.load('solider_info_dict.pkl')
        origin_coordinate = joblib.load('origin_coordinate3.pkl')
    else:
        out =  {"stat":1,"msg":"请先与接口“/api/start_service_solider”进行通讯！"}
        return jsonify(out)
    
    for name in data.keys():
        if len(info_dict[name]) == 4:
            # 对经纬高转换，变成UE4动态坐标的xyz
            #------------------------------------0
            if not data[name]["data"]["option"]:
                destination = data[name]["data"]["destination"]
                ox,oy,oz = origin_coordinate
                lng,lat,alt = destination["lng"],destination["lat"],destination["alt"]
                data[name]["data"]["destination"]["xc"],data[name]["data"]["destination"]["yc"] ,data[name]["data"]["destination"]["zc"] = gps2ued(lng,lat,alt,lng0,lat0,alt0,ox,oy,oz)
                # print("经纬高变换xyz:",data)
            #------------------------------------1
            ctypes.cast(info_dict[name][3], ctypes.py_object).value.send(data[name])
        else:
            out = {"stat":1,"msg":"请先与接口“/api/record_data_solider”进行通讯！"}
            return jsonify(out)
            

    out = {"stat":0,"msg":"Success!"}
    return jsonify(out)
#-----------------------------------------------------------------------------------------------------------------------------1

# 4. 特朗普接口
#-----------------------------------------------------------------------------------------------------------------------------0
# 初始化服务接口
@app.route('/api/start_service_trump', methods= ['POST'])
def start_service_trump():
    # input = request.get_data(as_text=True)
    input = request.get_json()
    # print(input)
    data = input["data"]
    host = data["host"]
    port = data["port"]
    task = data["task"]+"_init_trump" # 
    db_table = "init_trump"
    
    info_dict,stat,origin_coordinate = init_info(host,port,task,db_table)
    if not stat:
        out = {"stat":1,"msg":"数据通讯错误！","data":{}}
        return jsonify(out)

    joblib.dump(info_dict, 'trump_info_dict.pkl')
    joblib.dump(origin_coordinate,"origin_coordinate4.pkl")

    out = {"stat":0,"msg":"Success!","data":{"origin_coordinate":origin_coordinate,"info_dict":info_dict}}
    return jsonify(out)

# 启动记录数据与智体通讯接口
@app.route('/api/record_data_trump', methods= ['POST'])
def data_record_trump():
    input = request.get_json()
    
    data = input["data"]

    record_all = data["record_all"]
    task = data["task"]+"_record_trump"

    if os.path.exists('trump_info_dict.pkl') and os.path.exists("origin_coordinate4.pkl"):
        info_dict = joblib.load('trump_info_dict.pkl')
        origin_coordinate = joblib.load('origin_coordinate4.pkl')
    else:
        out =  {"stat":1,"msg":"请先与接口“/api/start_service_trump”进行通讯！"}
        return jsonify(out)

    # MongoDB
    conn = MongoClient(host= '127.0.0.1', port=9999)

    # 创建数据库 MongoDB
    db = conn.get_database(task)

    info_dict2 = {}
    if record_all:
        for name in info_dict.keys():
            ip = info_dict[name][1]
            port = info_dict[name][2]
            info_dict2[name] = TCPSOCKET(ip, port, db,lng0, lat0,alt0,record=True)
            info_dict[name].append(id(info_dict2[name]))
        
        joblib.dump(info_dict,'trump_info_dict.pkl')
        
        out = {"stat":0,"msg":"Success!"}
    else:
        out =  {"stat":1,"msg":"目前record_all只支持设为1，不能为别的，如有需要可联系工程师！"}
    
    return jsonify(out)

# 特朗普 智体控制接口
@app.route('/api/control_trump', methods=['POST'])
def control_trump():
    input = request.get_json()

    data = input["data"]

    if os.path.exists('trump_info_dict.pkl') and os.path.exists("origin_coordinate4.pkl"):
        info_dict = joblib.load('trump_info_dict.pkl')
        origin_coordinate = joblib.load('origin_coordinate4.pkl')
    else:
        out =  {"stat":1,"msg":"请先与接口“/api/start_service_trump”进行通讯！"}
        return jsonify(out)
    
    for name in data.keys():
        if len(info_dict[name]) == 4:
            # 对经纬高转换，变成UE4动态坐标的xyz
            #------------------------------------0
            if not data[name]["data"]["option"]:
                destination = data[name]["data"]["destination"]
                ox,oy,oz = origin_coordinate
                lng,lat,alt = destination["lng"],destination["lat"],destination["alt"]
                data[name]["data"]["destination"]["xc"],data[name]["data"]["destination"]["yc"] ,data[name]["data"]["destination"]["zc"] = gps2ued(lng,lat,alt,lng0,lat0,alt0,ox,oy,oz)
                # print([lng0,lat0,alt0],[lng,lat,alt],[ox,oy,oz]) ###############
                # sx,sy,sz = ued2ues(data[name]["data"]["destination"]["xc"],data[name]["data"]["destination"]["yc"] ,data[name]["data"]["destination"]["zc"],ox,oy,oz) #################
                # print([sx,sy,sz],[data[name]["data"]["destination"]["xc"],data[name]["data"]["destination"]["yc"] ,data[name]["data"]["destination"]["zc"]])###############
                # print("经纬高变换xyz:",data)
            #------------------------------------1
            ctypes.cast(info_dict[name][3], ctypes.py_object).value.send(data[name])
        else:
            out = {"stat":1,"msg":"请先与接口“/api/record_data_trump”进行通讯！"}
            return jsonify(out)
            

    out = {"stat":0,"msg":"Success!"}
    return jsonify(out)
#-----------------------------------------------------------------------------------------------------------------------------1

# 5. 拦截弹接口
#-----------------------------------------------------------------------------------------------------------------------------0
# 初始化服务接口
@app.route('/api/start_service_md', methods= ['POST'])
def start_service_md():
    # input = request.get_data(as_text=True)
    input = request.get_json()
    # print(input)
    data = input["data"]
    host = data["host"]
    port = data["port"]
    task = data["task"]+"_init_md" # 
    db_table = "init_md"
    info_dict,stat,origin_coordinate = init_info(host,port,task,db_table)
    if not stat:
        out = {"stat":1,"msg":"数据通讯错误！","data":{}}
        return jsonify(out)

    joblib.dump(info_dict, 'md_info_dict.pkl')
    joblib.dump(origin_coordinate,"origin_coordinate5.pkl")

    out = {"stat":0,"msg":"Success!","data":{"origin_coordinate":origin_coordinate,"info_dict":info_dict}}
    return jsonify(out)

# 启动记录数据与智体通讯接口
@app.route('/api/record_data_md', methods= ['POST'])
def data_record_md():
    input = request.get_json()
    
    data = input["data"]
    record_all = data["record_all"]
    task = data["task"]+"_record_md"

    if os.path.exists('md_info_dict.pkl') and os.path.exists('origin_coordinate5.pkl'):
        info_dict = joblib.load('md_info_dict.pkl')
        origin_coordinate = joblib.load('origin_coordinate5.pkl')
    else:
        out =  {"stat":1,"msg":"请先与接口“/api/start_service_md”进行通讯！"}
        return jsonify(out)

    # conn = sqlite3.connect(task, check_same_thread=False)
    # cur = conn.cursor()
     
    # MongoDB
    conn = MongoClient(host= '127.0.0.1', port=9999)

    # 创建数据库 MongoDB
    db = conn.get_database(task)

    info_dict2 = {}
    if record_all:
        for name in info_dict.keys():
            ip = info_dict[name][1]
            port = info_dict[name][2]
            info_dict2[name] = TCPSOCKET(ip, port, db, lng0,lat0,alt0,record=True)
            info_dict[name].append(id(info_dict2[name]))
        
        joblib.dump(info_dict,'md_info_dict.pkl')
        
        out = {"stat":0,"msg":"Success!"}
    else:
        out =  {"stat":1,"msg":"目前record_all只支持设为1，不能为别的，如有需要可联系工程师！"}
    
    return jsonify(out)

# 拦截弹 智体控制接口
@app.route('/api/control_md', methods= ['POST'])
def control_md():
    input = request.get_json()

    data = input["data"]

    if os.path.exists('md_info_dict.pkl') and os.path.exists("origin_coordinate5.pkl"):
        info_dict = joblib.load('md_info_dict.pkl')
        origin_coordinate = joblib.load('origin_coordinate5.pkl')
    else:
        out =  {"stat":1,"msg":"请先与接口“/api/start_service_md”进行通讯！"}
        return jsonify(out)
    
    for name in data.keys():
        if len(info_dict[name]) == 4:
            # 对经纬高转换，变成UE4动态坐标的xyz
            #------------------------------------0
            if not data[name]["data"]["option"]:
                destination = data[name]["data"]["destination"]
                ox,oy,oz = origin_coordinate
                lng,lat,alt = destination["lng"],destination["lat"],destination["alt"]
                data[name]["data"]["destination"]["xc"],data[name]["data"]["destination"]["yc"] ,data[name]["data"]["destination"]["zc"] = gps2ued(lng,lat,alt,lng0,lat0,alt0,ox,oy,oz)
                # print("经纬高变换xyz:",data)
            #------------------------------------1
            ctypes.cast(info_dict[name][3], ctypes.py_object).value.send(data[name])
        else:
            out = {"stat":1,"msg":"请先与接口“/api/record_data_md”进行通讯！"}
            return jsonify(out)

    out = {"stat":0,"msg":"Success!"}
    return jsonify(out)
#-----------------------------------------------------------------------------------------------------------------------------1



if __name__ == '__main__':
    
    # from werkzeug.debug import DebuggedApplication
    # dapp = DebuggedApplication( app, evalex= True)
    CORS(app, supports_credentials=True) # 支持跨域通讯
    server = pywsgi.WSGIServer(('0.0.0.0', 5000), app, log = None, error_log=logger)
    server.serve_forever()
    # app.run(host='0.0.0.0',debug=True) # 调试的时候可以启用这个把前两条注销掉即可

