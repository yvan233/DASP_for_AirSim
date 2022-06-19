import unreal
from datetime import datetime
from pymongo import MongoClient
from geo_change import ues2gps
import yaml
import os

yaml.warnings({'YAMLLoadWarning':False})

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
                unreal.log_error("读取GPS配置文件错误！请检查{}文件！".format(path))
                return False,{}    

    if option in cfg.keys():
        # 检测 GPS
        gps = cfg[option]

        if type(gps) is not dict:
            unreal.log_error("GPS配置文件错误！请检查{}文件中的GPS字段数据类型！".format(path))
            return False,{}

        if not (set(gps.keys()) == set(['lng0','lat0','alt0'])):
            unreal.log_error("GPS配置文件错误！请检查{}文件中的{}字典的各项是否正确！".format(path,option))
            return False,{}
        
        if not all([ ((type(gps[i]) is float) and (gps[i] >= 0 ))  for i in ['lng0','lat0','alt0'] ]):
            unreal.log_error("GPS配置文件错误！请检查{}文件中的{}字段数据类型！".format(path,option))
            return False,{}
        
        return True,gps
        
    else:
        unreal.log_error("找不到GPS配置文件！".format(path))
        return False,{}

if __name__ =="__main__":

    # UE 原点的GPS配置
    path = "E:\\shilong\\MCI_v0.3.4\\gps.conf"
    option = "GPS0"
    stat,gps = read_yaml(path=path,option=option)
    if stat:

        # 注意经纬高对应UE4 中 0,0,0 点的经纬高，且符合 WGS84 标准
        lng0,lat0,alt0 = gps["lng0"],gps["lat0"],gps["alt0"]
        
        # 储存UE静态Actors的数据库名称
        db_name = "UE_Static_Actors" 
        # 不需要读取的Actors
        pass_list = ['WorldSettings','Brush','','InstancedFoliageActor','AtmosphericFog','Starter_Background_Cue',
                       'BP_Sky_Sphere_C','LandscapeGizmoActiveActor','Minimal_Default_C','DefaultPhysicsVolume',
                       'Landscape'] 
        agent_list = ["MIS_A","TK_AI","TP_AI","SOL_A","MD_AI"]
        
        dt = datetime.now()
        ts = dt.strftime('%Y-%m-%d %H:%M:%S.%f') # 时间戳，考虑到与其它数据库统一，所以也多此一举加入了毫秒
        collection = dt.strftime('%Y-%m-%d %H:%M:%S') # 数据库 collection 的名字
        conn = MongoClient(host= '127.0.0.1', port=9999) # 连接 MongoDB数据库
        
        # 创建连接数据库与Collection
        db = conn.get_database(db_name)
        col = db.get_collection(collection)
        
        # 获取 UE 静态 Actor
        world = unreal.EditorLevelLibrary.get_editor_world()
        actors = unreal.GameplayStatics.get_all_actors_of_class(world, unreal.Actor)
        
        save_list = []
        spd = save_list.append
        for a in actors:
            name = str(a.get_fname())
            if name not in pass_list:
                if name[:5] in agent_list:
                    name = "_".join(str(a.get_fname()).split("_")[:-1])
                position = a.get_actor_location()
                rotation = a.get_actor_rotation()
                timestamp = int(datetime.strptime(ts,"%Y-%m-%d %H:%M:%S.%f").timestamp() * 1000)
                lng,lat,alt = ues2gps(position.x,position.y,position.z,lng0,lat0,alt0)
        
                out = {"NAME":name,"TIME":ts,"TIMESTAMP":timestamp,
                       "PX":position.x,"PY":position.y,"PZ":position.z,
                       "ROLL":rotation.roll,"PITCH":rotation.pitch,"YAW":rotation.yaw,
                       "LNG":lng,"LAT":lat,"ALT":alt,"REMARK":""}
                spd(out)
            else:
                pass
        
        # 数据插入数据库
        col.insert_many(save_list)
