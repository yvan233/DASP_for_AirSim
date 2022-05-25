import ctypes
import joblib
import os
import sqlite3
import warnings

from flask import Flask,jsonify,request
from flask_cors import CORS
from gevent import monkey
from gevent import pywsgi
from loguru import logger
from geo_change import *
from TCPROCKET import TCPROCKET,init_info

warnings.filterwarnings("ignore")
logger.add('runtime.log', rotation = "100 MB", retention = "30 days")

# UE4 静态坐标系 0,0,0 坐标对应的经纬度定位全局变量，高德地图拾取到的坐标转为wgs84 gps坐标
lng0, lat0 = gcj02_to_wgs84(116.174646, 40.055388)
alt0 = 150. # 北京平均海拔

monkey.patch_all()
app = Flask(__name__)

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
    db = data["db"]
    # length = data["length"]
    db_table = data["db_table"]
    
    info_dict,stat,origin_coordinate = init_info(host,port,db,db_table)
    if not stat:
        out = {"stat":1,"msg":"初始化数据库表{}是之前任务已创建的表，请为本次任务的指定新的表名或新建数据库！".format(db_table),"data":{}}
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
    db = data["db"]

    if os.path.exists('tank_info_dict.pkl') and os.path.exists("origin_coordinate.pkl"):
        info_dict = joblib.load('tank_info_dict.pkl')
        origin_coordinate = joblib.load('origin_coordinate.pkl')
    else:
        out =  {"stat":1,"msg":"请先与接口“/api/start_service_tank”进行通讯！"}
        return jsonify(out)

    conn = sqlite3.connect(db, check_same_thread=False)
    cur = conn.cursor()

    info_dict2 = {}
    if record_all:
        for name in info_dict.keys():
            ip = info_dict[name][1]
            port = info_dict[name][2]
            info_dict2[name] = TCPROCKET(ip, port, cur, conn,lng0, lat0,alt0,record=True)
            info_dict[name].append(id(info_dict2[name]))
        
        joblib.dump(info_dict,'tank_info_dict.pkl')
        
        out = {"stat":0,"msg":"Success!"}
    else:
        out =  {"stat":1,"msg":"目前record_all只支持设为True，不能为False，如有需要可联系工程师！"}
    
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
    db = data["db"]
    db_table = data["db_table"]
    info_dict,stat,origin_coordinate = init_info(host,port,db,db_table)
    if not stat:
        out = {"stat":1,"msg":"初始化数据库表{}是之前任务已创建的表，请为本次任务的指定新的表名！".format(db_table),"data":{}}
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
    db = data["db"]

    if os.path.exists('missile_info_dict.pkl') and os.path.exists('origin_coordinate2.pkl'):
        info_dict = joblib.load('missile_info_dict.pkl')
        origin_coordinate = joblib.load('origin_coordinate2.pkl')
    else:
        out =  {"stat":1,"msg":"请先与接口“/api/start_service_missile”进行通讯！"}
        return jsonify(out)

    conn = sqlite3.connect(db, check_same_thread=False)
    cur = conn.cursor()

    info_dict2 = {}
    if record_all:
        for name in info_dict.keys():
            ip = info_dict[name][1]
            port = info_dict[name][2]
            info_dict2[name] = TCPROCKET(ip, port, cur, conn,lng0,lat0,alt0,record=True)
            info_dict[name].append(id(info_dict2[name]))
        
        joblib.dump(info_dict,'missile_info_dict.pkl')
        
        out = {"stat":0,"msg":"Success!"}
    else:
        out =  {"stat":1,"msg":"目前record_all只支持设为True，不能为False，如有需要可联系工程师！"}
    
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
    db = data["db"]
    # length = data["length"]
    db_table = data["db_table"]
    
    info_dict,stat,origin_coordinate = init_info(host,port,db,db_table)
    if not stat:
        out = {"stat":1,"msg":"初始化数据库表{}是之前任务已创建的表，请为本次任务的指定新的表名！".format(db_table),"data":{}}
        return jsonify(out)

    joblib.dump(info_dict, 'solider_info_dict.pkl')
    joblib.dump(origin_coordinate,"origin_coordinate.pkl")

    out = {"stat":0,"msg":"Success!","data":{"origin_coordinate":origin_coordinate,"info_dict":info_dict}}
    return jsonify(out)

# 启动记录数据与智体通讯接口
@app.route('/api/record_data_solider', methods= ['POST'])
def data_record_solider():
    input = request.get_json()
    
    data = input["data"]

    record_all = data["record_all"]
    db = data["db"]

    if os.path.exists('solider_info_dict.pkl') and os.path.exists("origin_coordinate.pkl"):
        info_dict = joblib.load('solider_info_dict.pkl')
        origin_coordinate = joblib.load('origin_coordinate.pkl')
    else:
        out =  {"stat":1,"msg":"请先与接口“/api/start_service_solider”进行通讯！"}
        return jsonify(out)

    conn = sqlite3.connect(db, check_same_thread=False)
    cur = conn.cursor()

    info_dict2 = {}
    if record_all:
        for name in info_dict.keys():
            ip = info_dict[name][1]
            port = info_dict[name][2]
            info_dict2[name] = TCPROCKET(ip, port, cur, conn,lng0, lat0,alt0,record=True)
            info_dict[name].append(id(info_dict2[name]))
        
        joblib.dump(info_dict,'solider_info_dict.pkl')
        
        out = {"stat":0,"msg":"Success!"}
    else:
        out =  {"stat":1,"msg":"目前record_all只支持设为True，不能为False，如有需要可联系工程师！"}
    
    return jsonify(out)

# 士兵 智体控制接口
@app.route('/api/control_solider', methods=['POST'])
def control_solider():
    input = request.get_json()

    data = input["data"]

    if os.path.exists('solider_info_dict.pkl') and os.path.exists("origin_coordinate.pkl"):
        info_dict = joblib.load('solider_info_dict.pkl')
        origin_coordinate = joblib.load('origin_coordinate.pkl')
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
    db = data["db"]
    # length = data["length"]
    db_table = data["db_table"]
    
    info_dict,stat,origin_coordinate = init_info(host,port,db,db_table)
    if not stat:
        out = {"stat":1,"msg":"初始化数据库表{}是之前任务已创建的表，请为本次任务的指定新的表名！".format(db_table),"data":{}}
        return jsonify(out)

    joblib.dump(info_dict, 'trump_info_dict.pkl')
    joblib.dump(origin_coordinate,"origin_coordinate.pkl")

    out = {"stat":0,"msg":"Success!","data":{"origin_coordinate":origin_coordinate,"info_dict":info_dict}}
    return jsonify(out)

# 启动记录数据与智体通讯接口
@app.route('/api/record_data_trump', methods= ['POST'])
def data_record_trump():
    input = request.get_json()
    
    data = input["data"]

    record_all = data["record_all"]
    db = data["db"]

    if os.path.exists('trump_info_dict.pkl') and os.path.exists("origin_coordinate.pkl"):
        info_dict = joblib.load('trump_info_dict.pkl')
        origin_coordinate = joblib.load('origin_coordinate.pkl')
    else:
        out =  {"stat":1,"msg":"请先与接口“/api/start_service_trump”进行通讯！"}
        return jsonify(out)

    conn = sqlite3.connect(db, check_same_thread=False)
    cur = conn.cursor()

    info_dict2 = {}
    if record_all:
        for name in info_dict.keys():
            ip = info_dict[name][1]
            port = info_dict[name][2]
            info_dict2[name] = TCPROCKET(ip, port, cur, conn,lng0, lat0,alt0,record=True)
            info_dict[name].append(id(info_dict2[name]))
        
        joblib.dump(info_dict,'trump_info_dict.pkl')
        
        out = {"stat":0,"msg":"Success!"}
    else:
        out =  {"stat":1,"msg":"目前record_all只支持设为True，不能为False，如有需要可联系工程师！"}
    
    return jsonify(out)

# 特朗普 智体控制接口
@app.route('/api/control_trump', methods=['POST'])
def control_trump():
    input = request.get_json()

    data = input["data"]

    if os.path.exists('trump_info_dict.pkl') and os.path.exists("origin_coordinate.pkl"):
        info_dict = joblib.load('trump_info_dict.pkl')
        origin_coordinate = joblib.load('origin_coordinate.pkl')
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
                # print("经纬高变换xyz:",data)
            #------------------------------------1
            ctypes.cast(info_dict[name][3], ctypes.py_object).value.send(data[name])
        else:
            out = {"stat":1,"msg":"请先与接口“/api/record_data_trump”进行通讯！"}
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

