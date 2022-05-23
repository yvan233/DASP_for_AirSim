import cv2
import socket
import json
import time
import numpy as np
import struct

class DaspCarClient():
    def __init__(self, host = "localhost", port = 5000):
        self.host = host
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((host, port))

    def send(self, method, data = ""):
        pack = {
                "Method":method,
                "Data":data
            }
        pack = json.dumps(pack)
        self.sock.sendall(pack.encode())
        time.sleep(0.01)

    def recv(self):
        pack = self.sock.recv(1024)
        if pack:
            pack = json.loads(pack.decode())
        return pack

    def get_state(self):
        self.send("Get state")
        data = self.recv()
        return data["Data"]
        
    def get_collision(self):
        self.send("Get collision")
        data = self.recv()
        return data["Data"]

    def do_action(self, action):
        self.send("Control", action)
        data = self.recv()
        return data["Method"]

    def reset(self):
        self.send("Reset")
        data = self.recv()
        return data["Method"]

    def start_record(self, path =  "D:/Qiyuan/Record"):
        self.send("Start record", path)
        data = self.recv()
        return data["Method"]

    def stop_record(self):
        self.send("Stop record")
        data = self.recv()
        return data["Method"]

    def start_upload(self, parameter):
        # parameter = {"type": "video","IP": 127.0.0.1,"port": 5001}
        self.send("Start upload", parameter)
        data = self.recv()
        return data["Method"]

    def stop_upload(self, parameter):
        # parameter = {"type": "video"}
        self.send("Stop upload", parameter)
        data = self.recv()
        return data["Method"]

def get_image(remote_ip = "127.0.0.1", port = 5001):
    """
    获取图像数据
    """
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((remote_ip, 5001))
    data, address = sock.recvfrom(65535)
    imgstring = np.asarray(bytearray(data), dtype="uint8")
    image = cv2.imdecode(imgstring, cv2.IMREAD_COLOR)
    sock.close()
    return image

def get_video(self, host, port, adjID = ""):
    """
    长连接循环接收数据框架
    """
    while True:
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.bind((host, port))
        server.listen(1) #接收的连接数
        conn, addr = server.accept()
        print('Connected by {}:{}'.format(addr[0], addr[1]))
        # FIFO消息队列
        dataBuffer = bytes()
        with conn:
            while True:
                try:
                    data = conn.recv(1024)
                except Exception as e:
                    # 发送端进程被杀掉
                    self.RecvDisconnectHandle(addr, adjID)
                    break
                if data == b"":
                    # 发送端close()
                    self.RecvDisconnectHandle(addr, adjID)
                    break
                if data:
                    # 把数据存入缓冲区，类似于push数据
                    dataBuffer += data
                    while True:
                        if len(dataBuffer) < self.headerSize:
                            break  #数据包小于消息头部长度，跳出小循环
                        # 读取包头
                        headPack = struct.unpack(self.headformat, dataBuffer[:self.headerSize])
                        bodySize = headPack[1]
                        if len(dataBuffer) < self.headerSize+bodySize :
                            break  #数据包不完整，跳出小循环
                        # 读取消息正文的内容
                        body = dataBuffer[self.headerSize:self.headerSize+bodySize]
                        body = body.decode()
                        body = json.loads(body)
                        # 数据处理
                        self.MessageHandle(headPack, body, conn)
                        # 数据出列
                        dataBuffer = dataBuffer[self.headerSize+bodySize:]

def get_lidar(remote_ip = "127.0.0.1", port = 5002):
    """
    获取雷达数据
    """
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((remote_ip, 5002))
    data, address = sock.recvfrom(65535)
    points = np.frombuffer(data, dtype=np.dtype('f4'))
    points = np.reshape(points, (int(points.shape[0]/3), 3)) # reshape array of floats to array of [X,Y,Z]
    sock.close()
    return points
