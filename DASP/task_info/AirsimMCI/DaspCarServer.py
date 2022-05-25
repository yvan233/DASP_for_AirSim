import socket
import traceback
import json
import time
from threading import Thread
from .AirSimCarAgent import AirSimCarAgent

class DaspCarServer():
    def __init__(self, host = "localhost", port = 5000, UE_ip = "", vehicle_name = "", remote_ip = ""):
        self.host = host
        self.port = port
        self.car = AirSimCarAgent(ip = UE_ip, vehicle_name= vehicle_name)
        self.record = AirSimCarAgent(ip = UE_ip)
        self.thread = Thread(target=self.record.upload_video_lidar, args = (remote_ip,), daemon=True)

    def run(self):
        self.thread.start()
        while True:
            try:
                server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                server.bind((self.host, self.port))
                server.listen(10) #接收的连接数
                conn, addr = server.accept()
                print(f'Connected by {addr[0]}:{addr[1]}')
                with conn:
                    while True:
                        pack = self.recv(conn)
                        # 发送端close()
                        if pack == b"":
                            print(f'{addr[0]}:{addr[1]} disconnect')
                            break
                        else:
                            # 数据处理
                            thread = Thread(target=self.MessageHandle, args = (pack, conn), )    
                            thread.start()
            except ConnectionResetError:
                pass
            
    def MessageHandle(self, pack, sock):
        """
        数据处理函数
        pack:{"Methods","Data"}
        Methods: "Control", "Get"
        """
        try:
            if pack["Method"] == "Control":
                action = pack['Data']
                self.car.do_action(action)
                self.send(sock, "Control OK")
            elif pack["Method"] == "Get state":
                state = self.car.get_car_state()
                self.send(sock, "State Data", state)
            elif pack["Method"] == "Get collision":
                collision = self.car.get_collision()
                self.send(sock, "Collision Data", collision)
            elif pack["Method"] == "Reset":
                self.car.reset()
                self.send(sock, "Reset OK")
            elif pack["Method"] == "Start record":
                path = pack['Data']
                self.record.startRecording(path)
                self.send(sock, "Start OK")
            elif pack["Method"] == "Stop record":
                self.record.stopRecording()
                self.send(sock, "Stop OK")
            else:
                info = "请根据提供的接口发送请求"
                self.send(sock, "REFUSE", info)
        except Exception as e:
            print(f"通信服务器执行出错：{traceback.format_exc()}")

    def send(self, sock, method, data = ""):
        pack = {
                "Method":method,
                "Data":data
            }
        pack = json.dumps(pack)
        sock.sendall(pack.encode())
        time.sleep(0.01)

    def recv(self, sock):
        pack = sock.recv(1024)
        if pack:
            pack = json.loads(pack.decode())
        return pack

if __name__ == '__main__':
    # 开启udp视频流
    host = socket.gethostbyname(socket.gethostname())
    remote_ip = host
    UE_ip = "59.66.17.186"
    server = DaspCarServer(host, UE_ip = UE_ip, vehicle_name = "Escaper", remote_ip = remote_ip)
    server.run()