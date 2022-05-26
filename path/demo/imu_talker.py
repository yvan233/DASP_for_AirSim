#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Module for points talker."""
from DaspCarClient import DaspCarClient

import time
import socket
import struct
import traceback
from threading import Thread
import numpy as np
import json
from cyber.python.cyber_py3 import cyber
from modules.drivers.proto.imu_pb2 import ImuMsg
from modules.common.proto.header_pb2 import Header
from modules.common.proto.geometry_pb2 import Point3D

def get_imu(writer, host = "0.0.0.0", port = 5003):
    count = 0
    headerSize = 16
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((host, port))
    server.listen(10) #接收的连接数
    conn, addr = server.accept()
    print('Connected by {}:{}'.format(addr[0], addr[1]))
    # FIFO消息队列
    dataBuffer = bytes()
    with conn:
        while not cyber.is_shutdown():
            try:
                data = conn.recv(1024)
            except Exception as e:
                # 发送端进程被杀掉
                break
            if data == b"":
                # 发送端close()
                break
            if data:
                # 把数据存入缓冲区，类似于push数据
                dataBuffer += data
                while True:
                    if len(dataBuffer) < headerSize:
                        break  #数据包小于消息头部长度，跳出小循环
                    # 读取包头
                    headPack = struct.unpack("!IIQ", dataBuffer[:headerSize])
                    bodySize = headPack[1]
                    if len(dataBuffer) < headerSize+bodySize :
                        break  #数据包不完整，跳出小循环
                    # 读取消息正文的内容
                    body = dataBuffer[headerSize:headerSize+bodySize]
                    # 数据处理
                    count = count + 1
                    thread = Thread(target=MessageHandle, args=(headPack, body, writer, count,))
                    # 设置成守护线程
                    thread.daemon = True
                    thread.start()    
        
                    # 数据出列
                    dataBuffer = dataBuffer[headerSize+bodySize:]

def MessageHandle(headPack, body, writer, count):
    try:
        if headPack[0] == 1:
            data = json.loads(body.decode())
            msg = data2msg(count, data)
            print("=" * 80)
            print("write msg -> %s" % msg.header)
            writer.write(msg)
        else:
            info = "暂未提供POST以外的接口"
            print(info)
    except Exception as e:
        print(traceback.format_exc())


def data2msg(count, data):
    msg = ImuMsg()
    head = msg.header
    head.timestamp_sec = data["timestamp"]/1e9
    head.frame_id = "base_link"
    msg.msg_cnt = count
    
    acc = msg.acc
    acc.x = data["acc"][0]
    acc.y = data["acc"][1]
    acc.z = data["acc"][2]

    gyro = msg.gyro
    gyro.x = data["gyro"][0]
    gyro.y = data["gyro"][1]
    gyro.z = data["gyro"][2]

    attitude = msg.attitude
    attitude.x = data["attitude"][0]
    attitude.y = data["attitude"][1]
    attitude.z = data["attitude"][2]   

    return msg

if __name__ == '__main__':
    host = "192.168.1.4"
    remote_ip = "0.0.0.0"
    cyber.init("points_talker_sample")
    test_node = cyber.Node("IMU_talker")
    writer = test_node.create_writer("/minirobo/driver/ins/imu_data", ImuMsg, 6)

    client = DaspCarClient(host, port = 5001)

    thread = Thread(target=get_imu, args=(writer, remote_ip, 5003,))
    thread.daemon = True
    thread.start()    

    # 开始记录数据
    print("start upload")
    parameter = {"type": "imu","IP": host,"port": 5003}
    client.start_upload(parameter)

    thread.join() 
