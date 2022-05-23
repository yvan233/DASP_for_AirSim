import airsim
import numpy as np
import os
import time
import cv2
import csv
import sys
import struct
import socket
from threading import Thread

class AirSimCarAgent():
    """
    AirSimCarAgent用于在AirSim模拟器上实现车辆的控制，并记录控制过程中的图片，以及车辆的状态和碰撞信息。
    实现的功能包括：
        1. 初始化AirSim模拟器
        2. 获取车辆的状态信息
        3. 获取车辆的碰撞信息
        4. 控制车辆
        5. 获取图像数据
        6. 获取雷达数据
        7. 记录车辆的控制过程
        8. 停止记录
        9. 重置车辆
    """
    def __init__(self, ip = "", vehicle_name = "", control_flag = False):
        image_size = (84, 84, 1)  # image shape for default gym env
        ## name
        self.name = vehicle_name
        self.record_flag = False
        self.upload_video_flag = False
        self.upload_lidar_flag = False
        self.header = ['timestamp', 'position', 'orientation', 'speed', 'throttle', 'steering', 'brake', 
            'linear_velocity', 'linear_acceleration', 'angular_velocity', 'angular_acceleration']
        self.connect(ip, control_flag)

    def connect(self, ip, control_flag):
        # 连接AirSim模拟器
        self.car = airsim.CarClient(ip=ip)
        self.car.confirmConnection()
        self.car.enableApiControl(True,self.name) if not control_flag else self.car.enableApiControl(False,self.name)
        self.car.armDisarm(True,self.name) if not control_flag else self.car.enableApiControl(False,self.name)
        time.sleep(0.01)

    def get_car_state(self):
        # 获取车辆状态
        DIG = 4
        State = self.car.getCarState(self.name)
        action = self.car.getCarControls(self.name)
        kinematics = State.kinematics_estimated
        state = {
            "timestamp":str(State.timestamp)[:-6],
            "position":[round(i,DIG) for i in kinematics.position.to_numpy_array().tolist()],
            "orientation":[round(i,DIG) for i in kinematics.orientation.to_numpy_array().tolist()],
            "speed": round(State.speed,DIG),
            "throttle":round(action.throttle,DIG),
            "steering":round(action.steering*50,DIG),
            "brake":round(action.brake,DIG),
            "linear_velocity":[round(i,DIG) for i in kinematics.linear_velocity.to_numpy_array().tolist()],
            "linear_acceleration":[round(i,DIG) for i in kinematics.linear_acceleration.to_numpy_array().tolist()],
            "angular_velocity":[round(i,DIG) for i in kinematics.angular_velocity.to_numpy_array().tolist()],
            "angular_acceleration":[round(i,DIG) for i in kinematics.angular_acceleration.to_numpy_array().tolist()]
        }
        return state

    def get_collision(self):
        # 获取车辆碰撞信息
        collision_info = self.car.simGetCollisionInfo(self.name)
        info = {
            "has_collided":collision_info.has_collided,
            "object_name": collision_info.object_name,
        }
        return info

    def reset(self):
        # 重置车辆
        self.car.reset()

    def do_action(self, action):
        # 控制车辆
        car_controls = airsim.CarControls()
        car_controls.throttle = action["throttle"]
        car_controls.steering = action["steering"]/50
        car_controls.brake = action["brake"]
        if action["throttle"] < 0:
            car_controls.is_manual_gear = True
            car_controls.manual_gear = -1
        self.car.setCarControls(car_controls, self.name)

    def get_image(self):
        # 获取车辆图像
        img_response = self.car.simGetImage("0", airsim.ImageType.Scene, self.name)
        np_response_image = np.asarray(bytearray(img_response), dtype="uint8")
        decoded_frame = cv2.imdecode(np_response_image, cv2.IMREAD_COLOR)
        # cv2.imwrite("result.jpg", decoded_frame)
        ret, image = cv2.imencode('.jpg', decoded_frame)
        # 解码
        # imgstring = np.asarray(bytearray(data), dtype="uint8")
        # image = cv2.imdecode(imgstring, cv2.IMREAD_COLOR)
        return image

    def get_lidar(self):
        # 获取车辆雷达数据
        lidar_data = self.car.getLidarData("Lidar1", self.name)
        if (len(lidar_data.point_cloud) < 3):
            print("No points received from Lidar data")
            return lidar_data.time_stamp, np.array([])
        else:
            points = np.array(lidar_data.point_cloud, dtype=np.dtype('f4'))
            # data = points.tobytes()
            # 解码
            # points = np.asarray(bytearray(data), dtype=np.dtype('f4'))
            # points =  np.reshape(points, (int(points.shape[0]/3), 3)) # reshape array of floats to array of [X,Y,Z]
            return lidar_data.time_stamp, points


    def startRecording(self, rootpath = "D:/Qiyuan/Record"):
        # 开始记录
        timelabel = time.strftime("%Y-%m-%d-%H-%M-%S", time.localtime(time.time()))
        self.path = os.path.join(rootpath, timelabel)
        os.system('mkdir "%s"' %self.path) 
        os.system('mkdir "%s"' %self.path+"/pointcloud") 
        os.system('mkdir "%s"' %self.path+"/image") 
        with open(self.path+'/record.csv', 'a', newline='',encoding='utf-8') as f: 
            writer = csv.DictWriter(f,fieldnames=self.header) 
            writer.writeheader()  # 写入列名
        self.record_flag = True
        
    def stopRecording(self):
        # 停止记录
        self.record_flag = False

    def startUpload(self, parameter):
        type = parameter["type"]
        remote_ip = parameter["IP"]
        port = parameter["port"]
        # 开始上传
        if type == "video":
            self.upload_video_flag = True
            self.video_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.video_socket.connect((remote_ip, port))
        elif type == "lidar":
            self.upload_lidar_flag = True
            self.lidar_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.lidar_socket.connect((remote_ip, port))
        else:
            pass

    def stopUpload(self, parameter):
        type = parameter["type"]
        # 停止上传
        if type == "video":
            self.upload_video_flag = False
            self.video_socket.close()
        elif type == "lidar":
            self.upload_lidar_flag = False
            self.lidar_socket.close()
        else:
            pass
    
    def updateVideo(self):
        # 记录及上传视频数据
        while True:
            if self.record_flag or self.upload_video_flag:
                image = self.get_image()
                state = self.get_car_state()
                time_stamp = state["timestamp"]
                if self.upload_video_flag:
                    self.sendallAddHead(self.video_socket, image.tobytes(), time_stamp)
                if self.record_flag:
                    filepath = os.path.join(self.path, "image/img_" + time_stamp+".jpg")
                    cv2.imwrite(filepath, image)

    def updateLidar(self):
        # 记录及上传雷达数据
        while True:
            if self.record_flag or self.upload_lidar_flag:
                time_stamp, lidar_data = self.get_lidar()
                if self.upload_lidar_flag and lidar_data.size:
                    self.sendallAddHead(self.video_socket, lidar_data.tobytes(), time_stamp)
                if self.record_flag:
                    filepath = os.path.join(self.path, "pointcloud/pointcloud_" + time_stamp)
                    np.save(filepath, lidar_data)

    def updateState(self):
        # 记录状态信息
        while True:
            if self.record_flag:
                state = self.get_car_state()
                filepath = os.path.join(self.path, "record.csv")
                with open(filepath, 'a', newline='',encoding='utf-8-sig') as f: 
                    writer = csv.DictWriter(f,fieldnames=self.header) 
                    writer.writerow(state) 

    def sendallAddHead(self, socket, data:bytes, time_stamp, methods = 1):
        '''
        为发送的数据添加methods和length报头
            POST: methods = 1
            REFUSE: methods = 9
        '''
        body = data
        header = [methods, body.__len__(), time_stamp]
        headPack = struct.pack("!IIQ" , *header)
        socket.sendall(headPack+body)

if __name__ == '__main__':
    # 开启udp视频流
    UE_ip = "127.0.0.1"
    remote_ip = "127.0.0.1"

    record = AirSimCarAgent(ip = UE_ip)
    thread = Thread(target=record.upload_video_lidar, args = (remote_ip,), daemon=True)
    thread.start()
    record.startRecording()

    car = AirSimCarAgent(ip = UE_ip, vehicle_name= "Escaper")
    print(car.get_car_state())
    print(car.get_collision())
    # 前进
    action = {
        "throttle": 1,
        "steering": 30,
        "brake": 0
    }
    car.do_action(action)
    time.sleep(3)
    # 后退
    action = {
        "throttle": -1,
        "steering": 50,
        "brake": 0
    }
    car.do_action(action)
    time.sleep(3)
    # 刹车
    action = {
        "throttle": 0,
        "steering": 0,
        "brake": 1
    }
    car.do_action(action)
    time.sleep(2)
    car.reset()

    record.stopRecording()