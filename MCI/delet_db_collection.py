import pymongo
 
myclient = pymongo.MongoClient("mongodb://localhost:9999/")
db = myclient["UE_Static_Actors"]
cs = db.list_collection_names()
for c in cs:
    mycol = db[c]
    mycol.drop()