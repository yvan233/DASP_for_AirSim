from pymap3d import ned2geodetic,geodetic2ned

import json
import requests
import math
from math import radians, cos, sin, asin, sqrt
import folium
import os

# 总体包括两部分：
# 第一部分是UE-AirSim-GIS坐标系间的转换，
# 第二部分是WGS84坐标系（标准GPS坐标系）-火星坐标系（国测局坐标系）-bd09坐标系（百度坐标系）等GPS坐标系之间的转换与GPS导航功能

# 一、第一部分：这一部分包含了UE（静态与动态）坐标系-AirSim坐标系-GIS坐标系之间的各种转换函数

# 参考资料
# https://forums.unrealengine.com/t/which-axis-is-north/27650/8
# https://docs.unrealengine.com/4.27/zh-CN/BuildingWorlds/Georeferencing/
# https://view.inews.qq.com/a/20211025A0CM8S00
# https://blog.csdn.net/qq_33641919/article/details/101003978?utm_medium=distribute.pc_aggpage_search_result.none-task-blog-2~aggregatepage~first_rank_ecpm_v1~rank_v31_ecpm-1-101003978-null-null.pc_agg_new_rank&utm_term=ned%E5%9D%90%E6%A0%87%E7%B3%BB&spm=1000.2123.3001.4430

# 说明
# UE4 采用的是左手系 ENU 坐标系，x：东，y：南，z：上，但是本次不这么干，x对地图北，y对地图东，z对地图上
# UE4 坐标系分为两种：编辑模式下的左手 ENU 坐标系，暂时简称静态坐标系；启动后的左手 ENU 坐标系，坐标原点是 start player 0，简称动态坐标系。
# AirSim 坐标系采用的是 右手 NED 坐标系，原点是 start player 0，x：北，y：东，z：下，与修改后的UE4 坐标一致

# 1. UE 静态坐标（启动运行前的UE场景编辑坐标）的转换

def ues2gps(sx,sy,sz,lon0,lat0,h0):
    '''
    说明：UE静态坐标转GPS（WGS84）坐标，UE x轴对应北，y轴对应东，z轴指向U天顶
    输入：
     - sx: float，ue 静态坐标x分量
     - sy: float，ue 静态坐标y分量
     - sz: float，ue 静态坐标z分量
     - lon0: float，静态坐标原点的经度
     - lat0: float，静态坐标原点的纬度
     - h0: float，静态坐标原点的高程
    输出：
     - lon: float，经度
     - lat: float，纬度
     - alt: float，高程
    '''
    lat,lon,alt = ned2geodetic(sx/100.,sy/100.,-sz/100.,lat0,lon0,h0)
    
    return lon,lat,alt

def gps2ues(lon,lat,h,lon0,lat0,h0):
    '''
    说明：GPS（WGS84）坐标转UE静态坐标
    输入：
     - lat: float，纬度
     - lon: float，经度
     - h: float，高程
     - lon0: float，静态坐标原点的经度
     - lat0: float，静态坐标原点的纬度
     - h0: float，静态坐标原点的高程
    输出：
     - sx: float，东E
     - sy: float，北N
     - sz: float，天U
    '''
    sx,sy,sz = geodetic2ned(lat,lon,h,lat0,lon0,h0)
    sx *= 100.
    sy *= 100.
    sz *= -100.
    return sx,sy,sz

def ues2ued(sx,sy,sz,ox,oy,oz):
    """
    ue 静态坐标转 ue 动态坐标（运行启动后的以player start 0为原点）
    输入值：
     - sx:float，静态坐标系坐标x分量
     - sy:float，静态坐标系坐标y分量
     - sz:float，静态坐标系坐标z分量
     - ox:float，静态坐标系player start 0为原点坐标的x分量
     - oy:float，静态坐标系player start 0为原点坐标的y分量
     - oz:float，静态坐标系player start 0为原点坐标的z分量
    返回值：
     - dx: float，动态坐标系坐标的x分量
     - dy: float，动态坐标系坐标的y分量 
     - dz: float，动态坐标系坐标的z分量 
    """
    dx,dy,dz = sx-ox,sy-oy,sz-oz

    return dx,dy,dz

def ues2airsim(sx,sy,sz,ox,oy,oz):
    """
    ue 静态坐标转 AirSim坐标
    输入值：
     - sx:float，静态坐标系坐标x分量
     - sy:float，静态坐标系坐标y分量
     - sz:float，静态坐标系坐标z分量
     - ox:float，AirSim系player start 0为原点坐标的x分量
     - oy:float，AirSim系player start 0为原点坐标的y分量
     - oz:float，AirSim系player start 0为原点坐标的z分量
    返回值：
     - dx: float，动态坐标系坐标的x分量
     - dy: float，动态坐标系坐标的y分量 
     - dz: float，动态坐标系坐标的z分量 
    """
    ax,ay,az = sx-ox,sy-oy,oz-sz
    ax /= 100.
    ay /= 100.
    az /= 100.
    return ax,ay,az

# 2. UE 动态坐标（UE 启动运行后的坐标系）的转换

def ued2ues(dx,dy,dz,ox,oy,oz):
    """
    ue 动态坐标转 ue 静态坐标
    输入值：
     - dx:float，动态坐标系坐标x分量
     - dy:float，动态坐标系坐标y分量
     - dz:float，动态坐标系坐标z分量
     - ox:float，静态坐标系player start 0为原点坐标的x分量
     - oy:float，静态坐标系player start 0为原点坐标的y分量
     - oz:float，静态坐标系player start 0为原点坐标的z分量
    返回值：
     - sx: float，静态坐标系坐标的x分量
     - sy: float，静态坐标系坐标的y分量 
     - sz: float，静态坐标系坐标的z分量
    """
    sx,sy,sz = ox+dx,oy+dy,oz+dz

    return sx,sy,sz

def ued2airsim(dx,dy,dz):
    """
    ue 静态坐标转 ue 动态坐标（运行启动后的以player start 0为原点）
    输入值：
     - dx:float，动态坐标系坐标x分量
     - dy:float，动态坐标系坐标y分量
     - dz:float，动态坐标系坐标z分量
     - ox:float，静态坐标系player start 0为原点坐标的x分量
     - oy:float，静态坐标系player start 0为原点坐标的y分量
     - oz:float，静态坐标系player start 0为原点坐标的z分量
    返回值：
     - ax: float，AirSim坐标系坐标的x分量
     - ay: float，AirSim坐标系坐标的y分量 
     - az: float，AirSim坐标系坐标的z分量
    """
    ax,ay,az = dx,dy,-dz
    ax /= 100.
    ay /= 100.
    az /= 100.
    return ax,ay,az

def ued2gps(dx,dy,dz,ox,oy,oz,lon0,lat0,h0):
    '''
    说明：UE动态坐标转GPS（WGS84）坐标
    输入：
     - dx: float，ue 动态坐标x分量
     - dy: float，ue 动态坐标y分量
     - dz: float，ue 动态坐标z分量
     - ox:float，静态坐标系player start 0为原点坐标的x分量
     - oy:float，静态坐标系player start 0为原点坐标的y分量
     - oz:float，静态坐标系player start 0为原点坐标的z分量
     - lon0: float，静态坐标原点的经度
     - lat0: float，静态坐标原点的纬度
     - h0: float，静态坐标原点的高程
    输出：
     - lon: float，经度
     - lat: float，纬度
     - alt: float，高程
    '''
    sx,sy,sz = ued2ues(dx,dy,dz,ox,oy,oz)
    lat,lon,alt = ned2geodetic(sx/100.,sy/100.,-sz/100.,lat0,lon0,h0)
    
    return lon,lat,alt

def gps2ued(lon,lat,h,lon0,lat0,h0,ox,oy,oz):
    '''
    说明：GPS（WGS84）坐标转UE动态坐标
    输入：
     - lat: float，纬度
     - lon: float，经度
     - h: float，高程
     - lon0: float，静态坐标原点的经度
     - lat0: float，静态坐标原点的纬度
     - h0: float，静态坐标原点的高程
     - ox:float，静态坐标系player start 0为原点坐标的x分量
     - oy:float，静态坐标系player start 0为原点坐标的y分量
     - oz:float，静态坐标系player start 0为原点坐标的z分量
    输出：
     - dx: float，东E
     - dy: float，北N
     - dz: float，天U
    '''
    sx,sy,sz = geodetic2ned(lat,lon,h,lat0,lon0,h0)
    sx *= 100.
    sy *= 100.
    sz *= -100.
    dx,dy,dz = ues2ued(sx,sy,sz,ox,oy,oz)
    
    return dx,dy,dz

# 3. AirSim坐标（UE 启动运行后的坐标系）的转换

'''
隐藏功能：AirSim 有 GPS传感器，只需要在 settings.json 中将player start 0 的 经纬度坐标填入脚本，就可以获取 GPS 传感器的定位数据。
'''

def airsim2ues(ax,ay,az,ox,oy,oz):
    """
    AirSim坐标转 ue 静态坐标（运行启动前编辑状态的环境ENU坐标）
    输入值：
     - ax:float，AirSim坐标系坐标x分量
     - ay:float，AirSim坐标系坐标y分量
     - az:float，AirSim坐标系坐标z分量
     - ox:float，静态坐标系player start 0为原点坐标的x分量
     - oy:float，静态坐标系player start 0为原点坐标的y分量
     - oz:float，静态坐标系player start 0为原点坐标的z分量
    返回值：
     - sx: float，静态坐标系坐标的x分量
     - sy: float，静态坐标系坐标的y分量 
     - sz: float，静态坐标系坐标的z分量
    """
    sx,sy,sz = ox+ax*100.,oy+ay*100.,oz-az*100.

    return sx,sy,sz

def airsim2ued(ax,ay,az):
    """
    AirSim坐标转 ue 动态坐标（运行启动后的NED坐标）
    输入值：
     - ax:float，AirSim坐标系坐标x分量
     - ay:float，AirSim坐标系坐标y分量
     - az:float，AirSim坐标系坐标z分量
    返回值：
     - dx: float，动态坐标系坐标的x分量
     - dy: float，动态坐标系坐标的y分量 
     - dz: float，动态坐标系坐标的z分量
    """
    dx,dy,dz = ax*100., ay*100., -az*100.

    return dx,dy,dz

def arisim2gps(ax,ay,az,ox,oy,oz,lon0,lat0,h0):
    '''
    说明：AirSim坐标转GPS（WGS84）坐标
    输入：
     - ax: float，AriSim坐标x分量
     - ay: float，AriSim坐标y分量
     - az: float，AriSim坐标z分量
     - ox:float，静态坐标系player start 0为原点坐标的x分量
     - oy:float，静态坐标系player start 0为原点坐标的y分量
     - oz:float，静态坐标系player start 0为原点坐标的z分量
     - lon0: float，静态坐标原点的经度
     - lat0: float，静态坐标原点的纬度
     - h0: float，静态坐标原点的高程
    输出：
     - lon: float，经度
     - lat: float，纬度
     - alt: float，高程
    '''
    sx,sy,sz = airsim2ues(ax,ay,az,ox,oy,oz)
    lat,lon,alt = ned2geodetic(sx/100.,sy/100.,-sz/100.,lat0,lon0,h0)
    
    return lon,lat,alt

def gps2airsim(lon,lat,h,lon0,lat0,h0,ox,oy,oz):
    '''
    说明：GPS（WGS84）坐标转UE动态坐标，UE x轴对应E东，-y轴对应N北，z轴指向U天顶
    输入：
     - lat: float，纬度
     - lon: float，经度
     - h: float，高程
     - lon0: float，静态坐标原点的经度
     - lat0: float，静态坐标原点的纬度
     - h0: float，静态坐标原点的高程
     - ox:float，静态坐标系player start 0为原点坐标的x分量
     - oy:float，静态坐标系player start 0为原点坐标的y分量
     - oz:float，静态坐标系player start 0为原点坐标的z分量
    输出：
     - ax: float，东E
     - ay: float，北N
     - az: float，天U
    '''

    sx,sy,sz = geodetic2ned(lat,lon,h,lat0,lon0,h0)
    sx *= 100.
    sy *= 100.
    sz *= -100.
    ax,ay,az = ues2airsim(sx,sy,sz,ox,oy,oz)
    
    return ax,ay,az

# 第二部分：WGS84-火星-bd09等GPS坐标系之间的转换与GPS导航功能

# CGCS2000：2000国家大地坐标系(CGCS 2000) 与 WGS84差别极小可以认为是同一种坐标系
# https://baijiahao.baidu.com/s?id=1710928153676892779&wfr=spider&for=pc

pi = 3.1415926535897932384626  # π
x_pi = pi * 3000.0 / 180.0
a = 6378245.0  # 长半轴
ee = 0.00669342162296594323  # 偏心率平方

def gcj02_to_bd09(lng, lat):
    """
    火星坐标系(GCJ-02)转百度坐标系(BD-09)
    谷歌、高德——>百度
    :param lng:火星坐标经度
    :param lat:火星坐标纬度
    :return:
    """
    z = math.sqrt(lng * lng + lat * lat) + 0.00002 * math.sin(lat * x_pi)
    theta = math.atan2(lat, lng) + 0.000003 * math.cos(lng * x_pi)
    bd_lng = z * math.cos(theta) + 0.0065
    bd_lat = z * math.sin(theta) + 0.006
    return [bd_lng, bd_lat]


def bd09_to_gcj02(bd_lon, bd_lat):
    """
    百度坐标系(BD-09)转火星坐标系(GCJ-02)
    百度——>谷歌、高德
    :param bd_lat:百度坐标纬度
    :param bd_lon:百度坐标经度
    :return:转换后的坐标列表形式
    """
    x = bd_lon - 0.0065
    y = bd_lat - 0.006
    z = math.sqrt(x * x + y * y) - 0.00002 * math.sin(y * x_pi)
    theta = math.atan2(y, x) - 0.000003 * math.cos(x * x_pi)
    gg_lng = z * math.cos(theta)
    gg_lat = z * math.sin(theta)
    return [gg_lng, gg_lat]


def wgs84_to_gcj02(lng, lat):
    """
    WGS84转GCJ02(火星坐标系)
    :param lng:WGS84坐标系的经度
    :param lat:WGS84坐标系的纬度
    :return:
    """
    if out_of_china(lng, lat):  # 判断是否在国内
        return [lng, lat]
    dlat = _transformlat(lng - 105.0, lat - 35.0)
    dlng = _transformlng(lng - 105.0, lat - 35.0)
    radlat = lat / 180.0 * pi
    magic = math.sin(radlat)
    magic = 1 - ee * magic * magic
    sqrtmagic = math.sqrt(magic)
    dlat = (dlat * 180.0) / ((a * (1 - ee)) / (magic * sqrtmagic) * pi)
    dlng = (dlng * 180.0) / (a / sqrtmagic * math.cos(radlat) * pi)
    mglat = lat + dlat
    mglng = lng + dlng
    return [mglng, mglat]

def gcj02_to_wgs84(lng, lat):
    """
    GCJ02(火星坐标系)转GPS84
    :param lng:火星坐标系的经度
    :param lat:火星坐标系纬度
    :return:
    """
    if out_of_china(lng, lat):
        return [lng, lat]
    dlat = _transformlat(lng - 105.0, lat - 35.0)
    dlng = _transformlng(lng - 105.0, lat - 35.0)
    radlat = lat / 180.0 * pi
    magic = math.sin(radlat)
    magic = 1 - ee * magic * magic
    sqrtmagic = math.sqrt(magic)
    dlat = (dlat * 180.0) / ((a * (1 - ee)) / (magic * sqrtmagic) * pi)
    dlng = (dlng * 180.0) / (a / sqrtmagic * math.cos(radlat) * pi)
    mglat = lat + dlat
    mglng = lng + dlng
    return [lng * 2 - mglng, lat * 2 - mglat]

def bd09_to_wgs84(bd_lon, bd_lat):
    """
    百度bd09坐标系转wgs84坐标系
    """
    lon, lat = bd09_to_gcj02(bd_lon, bd_lat)
    return gcj02_to_wgs84(lon, lat)

def wgs84_to_bd09(lon, lat):
    """
    wgs84坐标系转百度bd09坐标系
    """
    lon, lat = wgs84_to_gcj02(lon, lat)
    return gcj02_to_bd09(lon, lat)

def geodistance(lng1,lat1,lng2,lat2):
    """
    计算两个经纬度坐标之间的距离，返回单位是 m
    """
    lng1, lat1, lng2, lat2 = map(radians, [float(lng1), float(lat1), float(lng2), float(lat2)]) # 经纬度转换成弧度
    dlon = lng2-lng1
    dlat = lat2-lat1
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2 
    distance = 2*asin(sqrt(a))*6371393 # 地球平均半径，6371393 m
    distance = round(distance,3)
    return distance

def _transformlat(lng, lat):
    ret = -100.0 + 2.0 * lng + 3.0 * lat + 0.2 * lat * lat + \
          0.1 * lng * lat + 0.2 * math.sqrt(math.fabs(lng))
    ret += (20.0 * math.sin(6.0 * lng * pi) + 20.0 *
            math.sin(2.0 * lng * pi)) * 2.0 / 3.0
    ret += (20.0 * math.sin(lat * pi) + 40.0 *
            math.sin(lat / 3.0 * pi)) * 2.0 / 3.0
    ret += (160.0 * math.sin(lat / 12.0 * pi) + 320 *
            math.sin(lat * pi / 30.0)) * 2.0 / 3.0
    return ret

def _transformlng(lng, lat):
    ret = 300.0 + lng + 2.0 * lat + 0.1 * lng * lng + \
          0.1 * lng * lat + 0.1 * math.sqrt(math.fabs(lng))
    ret += (20.0 * math.sin(6.0 * lng * pi) + 20.0 *
            math.sin(2.0 * lng * pi)) * 2.0 / 3.0
    ret += (20.0 * math.sin(lng * pi) + 40.0 *
            math.sin(lng / 3.0 * pi)) * 2.0 / 3.0
    ret += (150.0 * math.sin(lng / 12.0 * pi) + 300.0 *
            math.sin(lng / 30.0 * pi)) * 2.0 / 3.0
    return ret

def out_of_china(lng, lat):
    """
    判断是否在国内，不在国内不做偏移
    :param lng:
    :param lat:
    :return:
    """
    return not (lng > 73.66 and lng < 135.05 and lat > 3.86 and lat < 53.55)



def draw_gps(locations,color,name):
    """
    绘制gps轨迹图
    :param locations: list, 需要绘制轨迹的经纬度信息，格式为[[lon1,lat1], [lon2,lat2], ...]
    :param color: str, 轨迹颜色
    :param name: str, 轨迹图保存文件名
    :return: None
    """
    # 将location转为纬经度形式
    locations = [(i[1],i[0]) for i in locations]

    m = folium.Map(locations[0], zoom_start=15, attr='default')  # 中心区域的确定

    folium.PolyLine(  # polyline方法为将坐标用线段形式连接起来
        locations,  # 将坐标点连接起来
        weight=3,  # 线的粗度为3
        color=color,  # 线的颜色
        opacity=0.8  # 线的透明度
    ).add_to(m)  # 将这条线添加到刚才的区域 m 内

    # 起始点，结束点
    folium.Marker(locations[0], popup='<b>Starting Point</b>').add_to(m)
    folium.Marker(locations[-1], popup='<b>End Point</b>').add_to(m)

    m.save(os.path.join('./','{}.HTML'.format(name)))  # 将结果以HTML形式保存到指定路径

class NAV:

    def __init__(self, api_key):
        self.api_key = api_key

    def amap_driving(self,origin,destination):
        """
        利用高德服务做路径规划
        :param: 请求的参数
        :return: 规划的 gps 路径
        """
        params = {
            "key":self.api_key,
            "origin":origin,
            "destination":destination,
            "strategy": 2,
            "output": "json",
            "extensions":"base"
            } # "waypoints":""

        url = "https://restapi.amap.com/v3/direction/driving?"
        r = requests.post(url=url,params=params)
        if r.status_code == 200:
            data = json.loads(r.text)
            paths = self.amap2gps_paths(data)

        return paths

    def amap2gps_paths(self,data_dict):
        '''
        对高德的图路径规划数据进行转换，变换成gps坐标数据，方便UE使用
        返回值是经纬度list序列
        '''
        paths = data_dict["route"]["paths"][0]["steps"]
        paths_list = []
        plapd = paths_list.append
        for i in range(len(paths)):
            path = paths[i]["polyline"]
            plapd(path)
    
        paths_list = ";".join(paths_list).split(";")
        # print(paths_list)
        paths_new = []
        pnapd = paths_new.append
        for p in paths_list:
            p = p.split(",")
            lng, lat = float(p[0]),float(p[1])
            lng, lat = gcj02_to_wgs84(lng, lat)
    
            pnapd((lng,lat)) # 高德坐标是经纬
        
        return paths_new  


if __name__ == '__main__':

    lng = 121.513782 # 经度
    lat = 31.3003 # 纬度

    result1 = gcj02_to_bd09(lng, lat)
    result2 = bd09_to_gcj02(lng, lat)
    result3 = wgs84_to_gcj02(lng, lat)
    result4 = gcj02_to_wgs84(lng, lat)
    result5 = bd09_to_wgs84(lng, lat)
    result6 = wgs84_to_bd09(lng, lat)

    nav = NAV('7db86f1b5f684ab95a6b2a0a362e7a0b')  # 这里填写你的高德api的key key_gn	7db86f1b5f684ab95a6b2a0a362e7a0b
    result7 = nav.amap_driving("116.481028,39.989643","116.434446,39.90816")
    
    print(result1, result2, result3, result4, result5, result6, result7)
    
    # 画导航图
    draw_gps(result7,'red',"abc") #,'orange')