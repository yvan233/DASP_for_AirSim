load("@rules_python//python:defs.bzl", "py_library")

package(default_visibility = ["//visibility:public"])

py_binary(
    name = "points_talker",
    srcs = ["points_talker.py"],
    deps = [
        "//modules/common/proto:header_py_pb2",
        "//modules/drivers/proto:pointcloud_py_pb2",
        "//cyber/python/cyber_py3:cyber",
        ":DaspCarClient",
    ],
)

py_binary(
    name = "imu_talker",
    srcs = ["imu_talker.py"],
    deps = [
        "//modules/common/proto:header_py_pb2",
        "//modules/common/proto:geometry_py_pb2",
        "//modules/drivers/proto:imu_py_pb2",
        "//cyber/python/cyber_py3:cyber",
        ":DaspCarClient",
    ],
)

py_binary(
    name = "DaspCarClient",
    srcs = ["DaspCarClient.py"],
)