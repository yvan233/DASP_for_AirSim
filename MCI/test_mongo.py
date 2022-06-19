import pymongo

conn = pymongo.MongoClient(host= '127.0.0.1', port=9999)

# 创建或获取数据库
db = conn.get_database("test_db")
# db = client.test_db

coll = db.get_collection("table1")
post_data = {
    'name' : 'shilong',
    'item' : 'book1',
    'qty' : 18 }
coll.insert_one(post_data)

# post_data = {
#     'id' : '10',
#     'item' : 'book1',
#     'qty' : 18 }
# coll.insert_one(post_data)

# post_data = {
#     'id' : '7',
#     'item' : 'book1',
#     'qty' : 18 }
# coll.insert_one(post_data)

# find_post = coll.find().sort("id",-1)[0]
find_post = coll.find()

print([i for i in find_post])