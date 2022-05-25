import sqlite3
import pandas as pd
from datetime import datetime
import os

db_name = "tank_record.db"
id = 0
conn = sqlite3.connect("./MCIP_v0.3.2/{}".format(db_name), check_same_thread=False)

# 方法一：利用 pandas 读取数据库数据
# df = pd.read_sql_query("select * from ID0 order by TIMESTAMP desc limit 10",conn) # 对 xxx_record.db 适用
# df = pd.read_sql("select * from task2",conn) # 对 init.db 适用
# print(df)

# 方法二：利用游标读取 数据库数据
cursor = conn.cursor()
cursor.execute("select * from ID{} order by TIMESTAMP desc limit 1".format(id))
# cursor.execute("select * from ID0 where TIME=? order by TIME  desc limit 10 ",("2022-5-9 1:16:41.86",))
tables = cursor.fetchall()
print(tables)
conn.close()