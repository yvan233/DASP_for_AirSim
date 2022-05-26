# 启动流程
1. wsl
2. cd apollo
3. (bash docker/scripts/dev_start.sh)
4. bash docker/scripts/dev_into.sh
5. DASP: python .\script\start.py
6. apollo: bazel run //path/demo:points_talker
7. apollo: bazel run //path/demo:imu_talker
8. apollo: cyber_recorder record -a
9. 操作小车，完成数据生成