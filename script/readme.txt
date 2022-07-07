使用说明：
1. 启动run.bat脚本，运行程序
2. 运行start.py
   AirSimCarAgent.py中包含是否手动控制的选项
3. 进入cyber的docker环境（修改两个脚本下的host IP）
   bazel run //path/demo:imu_talker
   bazel run //path/demo:points_talker
4. 录制cyberbag 
   cyber_recorder record -a
5. 回放cyberbag
   cyber_recorder play -f -loop 20220707170512.record.00000