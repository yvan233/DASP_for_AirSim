#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Module for example of talker."""

import time
import numpy as np
from cyber.python.cyber_py3 import cyber
from modules.drivers.proto.pointcloud_pb2 import PointXYZIT,PointCloud
from modules.common.proto.header_pb2 import Header

def points2PointCloud(count, time_stamp, points):
    msg = PointCloud()
    head = msg.header
    head.timestamp_sec = time_stamp/1e9
    head.frame_id = "UE4"
    head.sequence_num = count
    msg.frame_id = "UE4"
    msg.measurement_time = time_stamp/1e9
    for point in points:
        p = PointXYZIT()
        p.x = point[0]
        p.y = point[1]
        p.z = point[2]
        msg.point.append(p)
        
    return msg

def test_talker_class():
    """
    Test talker.
    """
    a = np.array([[1,3,4],[1,3,5],[1,3,6]])
    test_node = cyber.Node("node_name2")
    count = 0
    timestamp  = 1501011020134567888
    writer = test_node.create_writer("UE4/sensor/PointCloud", PointCloud, 6)
    while not cyber.is_shutdown():
        time.sleep(0.1)
        timestamp = timestamp + 1e7
        count = count + 1
        msg = points2PointCloud(count, timestamp, a)
        print("=" * 80)
        print("write msg -> %s" % msg.header)
        writer.write(msg)


if __name__ == '__main__':
    cyber.init("talker_sample")
    test_talker_class()
    cyber.shutdown()
