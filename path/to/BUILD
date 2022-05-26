load("@rules_python//python:defs.bzl", "py_library")

package(default_visibility = ["//visibility:public"])

py_binary(
    name = "my_demo",
    srcs = ["my_demo.py"],
    deps = [
        "//cyber/python/cyber_py3:cyber",
    ],
)

py_binary(
    name = "talker",
    srcs = ["talker.py"],
    deps = [
        "//modules/common/proto:header_py_pb2",
        "//modules/drivers/proto:pointcloud_py_pb2",
        "//cyber/python/cyber_py3:cyber",
    ],
)