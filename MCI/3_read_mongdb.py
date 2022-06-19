from pymongo import MongoClient

task_name = "task_A_202205292026"

db_name_init = task_name+"_init_missile"
db_collection_init = "init_missile"
db_name_record = task_name+"_record_missile"

target0 = "MIS_AI"
target1 = "MIS_AI2"


# 连接数据库 MongoDB
conn = MongoClient(host= '127.0.0.1', port=9999)

# 创建数据库与collection MongoDB
db = conn.get_database(db_name_init)
col = db.get_collection(db_collection_init)

id0 = col.find({"NAME":target0})[0]["ID"]
id1 = col.find({"NAME":target1})[0]["ID"]

print(id0,id1)

# 读取目标当前位置
db = conn.get_database(db_name_record)
col0 = db["ID{}".format(id0)]
out0 = col0.find().sort("TIMESTAMP",-1)[0]
lng0,lat0,alt0 = out0["LNG"],out0["LAT"],out0["ALT"]

col1 = db["ID{}".format(id1)]
out1 = col1.find().sort("TIMESTAMP",-1)[0]
lng1,lat1,alt1 = out1["LNG"],out1["LAT"],out1["ALT"]