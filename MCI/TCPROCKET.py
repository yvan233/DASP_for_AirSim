import socket # 导入 socket 模块
from threading import Thread
from numpy import frombuffer,uint32,float32
import json

import time
import sqlite3
from datetime import datetime
from geo_change import *

class TCPROCKET:
    def __init__(self, ip, port, cur, conn, lng0, lat0,alt0 ,len = 4*18+16,record=True):
        self.ip = ip
        self.port = port
        self.cur = cur
        self.conn = conn
        self.lng0 = lng0
        self.lat0 = lat0
        self.alt0 = alt0
        self.len = len
        self.record = record
        self.address = (ip, port) # 绑定地址
        self.g_socket_server = None # 负责监听的socket
        self.g_conn_pool = [] # 连接池
        self.start()


    def start(self):
        """
        初始化服务端
        """
        self.g_socket_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # 创建 socket 对象
        self.g_socket_server.bind(self.address)
        self.g_socket_server.listen(5) # 最大等待数（有很多人理解为最大连接数，其实是错误的）
        # print("服务端已启动，等待客户端连接...")

        self.thread = Thread(target=self.accept_client)
        self.thread.setDaemon(True)
        self.thread.start()

    def accept_client(self):
        """
        接收新连接
        """
        while True:
            client, _ = self.g_socket_server.accept()  # 阻塞，等待客户端连接
            # 加入连接池
            self.g_conn_pool.append(client)
            # 给每个客户端创建一个独立的线程进行管理
            thread = Thread(target=self.message_handle, args=(client,))
            # 设置成守护线程
            thread.setDaemon(True)
            thread.start()    
    
    def message_handle(self,client):
        """
        消息处理
        """
        msg0 = {"msg":"连接服务器成功!"}
        msg0 =json.dumps(msg0)
        client.sendall(msg0.encode(encoding='utf8'))
        print("有一个客户端已上线，通讯地址（{}:{}）。".format(self.ip,self.port))
        
        while True:
            bytes = client.recv(self.len)
                # print(self.ip,self.port)
            if len(bytes) == 0:
                client.close()
                # 删除连接
                self.g_conn_pool.remove(client)
                print("有客户端已下线，通讯地址（{}:{}）。".format(self.ip,self.port))
                break
            # try:
            # print(len(bytes))
            length = frombuffer(bytes, dtype=uint32,count=1)
            # 整型只有4个数，所以计数只读4个数
            id = frombuffer(bytes, dtype=uint32,offset=4*1,count=1)
            dtime = frombuffer(bytes, dtype=uint32,count=7,offset=4*2)

            # 1个uint8是4个字节，所以4个时间整数数要移动4*4
            possition = frombuffer(bytes, dtype=float32,offset=4*9,count=3)
            rotation = frombuffer(bytes, dtype=float32,offset=4*12,count =3)
            origin_coordinate = frombuffer(bytes, dtype=float32,offset=4*15,count =3)
            # dtime(年月日时分秒毫秒),坐标(xyz),旋转(rpy),原点坐标(xyz)
            # print(length,id,dtime,possition,rotation,origin_coordinate)
            name = frombuffer(bytes,dtype='S1',offset=4*18,count=length[0]-4*18) # 解析string 字节型数据
            name = "".join([i.decode() for i in name])
            
            # 时间戳
            timestamp = int(datetime.strptime('{}-{}-{} {}:{}:{}.{}'.format(*dtime),"%Y-%m-%d %H:%M:%S.%f").timestamp() * 1000)

            insert = []
            insert.extend(id)
            insert.extend(id)
            insert.extend([name])
            insert.extend([self.ip])
            insert.extend([self.port])
            insert.extend(dtime)
            insert.extend([timestamp])
            
            # 坐标转gps
            #-------------------------------------------0
            dx,dy,dz = possition
            ox,oy,oz = origin_coordinate
            sx,sy,sz = ued2ues(dx,dy,dz,ox,oy,oz)
            # print(insert)
            insert.extend([sx,sy,sz]) # UE 静态坐标系
            insert.extend(rotation)
            # print((sx,sy,sz,self.lng0,self.lat0,self.alt0))
            lng,lat,alt = ues2gps(sx,sy,sz,self.lng0,self.lat0,self.alt0)
            insert.extend([lng,lat,alt])

            #-------------------------------------------1

            # print("INSERT INTO ID{} (ID,NAME,IP,PORT,TIME,TIMESTAMP,PX,PY,PZ,ROLL,PITCH,YOW,OX,OY,OZ) VALUES ( {}, '{}','{}', {}, '{}-{}-{} {}:{}:{}.{}',{}, {}, {}, {}, {}, {}, {}, {}, {}, {} )".format(*insert))
            time.sleep(0.000000001) # TODO: sqlite3 的一个bug，需要停一下才行，回头可以想个更好的办法
            # self.cur.execute("INSERT INTO ID{} (ID,NAME,IP,PORT,TIME,TIMESTAMP,PX,PY,PZ,ROLL,PITCH,YOW,OX,OY,OZ) VALUES ( {}, '{}','{}', {}, '{}-{}-{} {}:{}:{}.{}',{}, {}, {}, {}, {}, {}, {}, {}, {}, {} )".format(*insert))
            self.cur.execute("INSERT INTO ID{} (ID,NAME,IP,PORT,TIME,TIMESTAMP,PX,PY,PZ,ROLL,PITCH,YOW,LNG,LAT,ALT) VALUES ( {}, '{}','{}', {}, '{}-{}-{} {}:{}:{}.{}',{}, {}, {}, {}, {}, {}, {}, {}, {}, {} )".format(*insert))
            self.conn.commit()
            

    
    def send(self,msg):
        msg = json.dumps(msg)
        index = 0
        if len(self.g_conn_pool) == 0:
            return {"stat":1,"msg":"通讯地址（{}:{}）没有上线，请稍后再试".format(self.ip,self.port)}
        else:
            self.g_conn_pool[int(index)].sendall(msg.encode(encoding='utf8'))
            return {"stat":0,"msg":""}


def init_info(host,hport,db,db_table,length=64):

    conn = sqlite3.connect(db, check_same_thread=False)
    cur = conn.cursor()
    time.sleep(1)
    try:
        cur.execute('''CREATE TABLE {} (
                           NAME CHAR(50) PRIMARY KEY NOT NULL,
                           ID INT NOT NULL,
                           IP CHAR(50) NOT NULL,
                           PORT INT NOT NULL,
                           OX REAL NOT NULL,
                           OY REAL NOT NULL,
                           OZ REAL NOT NULL
                           );'''.format(db_table))
        conn.commit()
    except:
        conn.close()
        return {},False,[]

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # print((host, hport))
    server.bind((host, hport))
    server.listen(1) # 接收的连接数
    client, address = server.accept() 
    name_dict = {}
    while True: 
        bytes = client.recv(length)
        # print(len(bytes))
        #####################
        if len(bytes) == 0:
            conn.close()
            client.close()
            # print(name_dict)
            return name_dict,True,[ox.item(),oy.item(),oz.item()]
    
        id = frombuffer(bytes, dtype=uint32,offset=4*1,count=1)
        port = frombuffer(bytes, dtype=uint32,offset=4*2,count=1)
        ip_length = frombuffer(bytes, dtype=uint32,offset=4*3,count=1)
        ip = frombuffer(bytes,dtype='S1',offset=4*4,count=ip_length[0])
        ip = "".join([i.decode() for i in ip])
        name_length = frombuffer(bytes, dtype=uint32,offset=4*4+ip_length[0],count=1)
        name = frombuffer(bytes,dtype='S1',offset=4*5+ip_length[0],count=name_length[0])
        name = "".join([i.decode() for i in name])
        origin_coordinate = frombuffer(bytes, dtype=float32,offset=4*5+ip_length[0]+name_length[0],count =3)
        ox,oy,oz = origin_coordinate
        name_dict[name] = [id[0].item(), ip, port[0].item()]
        # print(name,id[0],ip,port[0],ox,oy,oz)
        
        cur.execute("INSERT INTO {} (NAME,ID,IP,PORT,OX,OY,OZ) VALUES ( '{}', {},'{}', {}, {}, {}, {} )".format(
            db_table,name,id[0],ip,port[0],ox,oy,oz))
        conn.commit()
        # print(1111111111)



if __name__ == '__main__':
    
    print("test")