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
from cyber.python.cyber_py3 import cyber
from modules.drivers.proto.pointcloud_pb2 import PointXYZIT,PointCloud
from modules.common.proto.header_pb2 import Header


def get_lidar(writer, host = "0.0.0.0", port = 5002):
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
            time_stamp = headPack[2]
            points = np.frombuffer(body, dtype=np.dtype('f4'))
            points = np.reshape(points, (int(points.shape[0]/3), 3)) # reshape array of floats to array of [X,Y,Z]
            msg = points2PointCloud(count, time_stamp, points)
            print("=" * 80)
            print("write msg -> %s" % msg.header)
            writer.write(msg)
        else:
            info = "暂未提供POST以外的接口"
            print(info)
    except Exception as e:
        print(traceback.format_exc())

def points2PointCloud(count, time_stamp, points):
    msg = PointCloud()
    head = msg.header
    head.timestamp_sec = time_stamp/1e9
    head.lidar_timestamp = time_stamp
    head.frame_id = "rslidar_16"
    head.sequence_num = count
    msg.measurement_time = time_stamp/1e9
    for point in points:
        p = PointXYZIT()
        # 转换坐标
        p.x = point[0]
        p.y = -point[1]
        p.z = -point[2]
        msg.point.append(p)
    return msg


if __name__ == '__main__':
    host = "192.168.1.4"
    remote_ip = "0.0.0.0"
    cyber.init("points_talker_sample")
    test_node = cyber.Node("points_talker")
    writer = test_node.create_writer("/apollo/sensor/rs16/PointCloud2", PointCloud, 6)

    client = DaspCarClient(host)

    thread = Thread(target=get_lidar, args=(writer, remote_ip, 5002,))
    thread.daemon = True
    thread.start()    

    # 开始记录数据
    print("start upload")
    parameter = {"type": "lidar","IP": host,"port": 5002}
    client.start_upload(parameter)

    thread.join() 
