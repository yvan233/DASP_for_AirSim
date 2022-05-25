import sqlite3
import os
import shutil
import datetime

# 0. 将原来生成的数据库转移到特定文件夹中，文件夹由当前操作的时间点，内容为此时间之前的数据库数据
filefold = "./MCI/backup/" + datetime.datetime.now().strftime('%Y_%m_%d_%H_%M_%S')+"/"
print(filefold)

files = os.listdir("./MCI/")
tomove_files = [f for f in files if f.endswith(".pkl") or f.endswith(".db")]

if len(tomove_files) != 0:
    os.mkdir(filefold)
    for f in tomove_files:
        shutil.move("./MCI/"+f,filefold+f)
else:
    pass

# 1. tank数据库的构建
#-----------------------------------------------------------------------------------------------------------------------0
tank_init_db = './MCI/tank_init.db' # 这个数据库是记录初始化时各个坦克的名称、ID、通讯地址之间的关系，不需要变更
# tank_init_table = "task1" # 每次任务，需要给各个坦克的名称、ID、通讯地址之间的关系建立一个新表
tank_record_db = './MCI/tank_record.db' # 这个数据库是个坦克实况的数据记录，对不同的任务可以创建新的数据库，表的名称需要根据不同任务换
tank_num = 3 # n为坦克个数，会自动为各个ID的坦克实况创建数据记录表，大于实际个数也可以

conn = sqlite3.connect(tank_init_db)
print ("{}数据库创建或连接成功".format(tank_init_db))
conn.close()

# 创建坦克实况数据记录表
conn = sqlite3.connect(tank_record_db)
print ("{}数据库创建或连接成功".format(tank_record_db))
c = conn.cursor()
for i in range(tank_num):
    try:
        c.execute('''CREATE TABLE ID{} (
                               ID INT NOT NULL,
                               NAME CHAR(50) NOT NULL,
                               IP CHAR(50) NOT NULL,
                               PORT INT NOT NULL,
                               TIME CHAR(50) PRIMARY KEY NOT NULL,
                               TIMESTAMP INT NOT NULL,
                               PX REAL NOT NULL, 
                               PY REAL NOT NULL, 
                               PZ REAL NOT NULL,
                               ROLL REAL NOT NULL, 
                               PITCH REAL NOT NULL, 
                               YOW REAL NOT NULL, 
                               LNG REAL NOT NULL,
                               LAT REAL NOT NULL,
                               ALT REAL NOT NULL
                               );'''.format(i))
        print ("{}数据表创建成功".format(tank_record_db))
    except:
        print ("错误！{}数据表创建失败，已存在该表！".format(tank_record_db))


conn.commit()
conn.close()
#-----------------------------------------------------------------------------------------------------------------------1

# 2. 导弹数据库的构建
#-----------------------------------------------------------------------------------------------------------------------0
missile_init_db = './MCI/missile_init.db' # 这个数据库是记录初始化时各个导弹的名称、ID、通讯地址之间的关系，不需要变更
missile_record_db = './MCI/missile_record.db' # 这个数据库是个导弹实况的数据记录，对不同的任务可以创建新的数据库，表的名称需要根据不同任务换
missile_num = 3 # n为导弹个数，会自动为各个ID的导弹实况创建数据记录表，大于实际个数也可以

conn = sqlite3.connect(missile_init_db)
print ("{}数据库创建或连接成功".format(missile_init_db))
conn.close()

# 创建导弹实况数据记录表
conn = sqlite3.connect(missile_record_db)
print ("{}数据库创建或连接成功".format(missile_record_db))
c = conn.cursor()
for i in range(missile_num):
    try:
        c.execute('''CREATE TABLE ID{} (
                               ID INT NOT NULL,
                               NAME CHAR(50) NOT NULL,
                               IP CHAR(50) NOT NULL,
                               PORT INT NOT NULL,
                               TIME CHAR(50) PRIMARY KEY NOT NULL,
                               TIMESTAMP INT NOT NULL,
                               PX REAL NOT NULL, 
                               PY REAL NOT NULL, 
                               PZ REAL NOT NULL,
                               ROLL REAL NOT NULL, 
                               PITCH REAL NOT NULL, 
                               YOW REAL NOT NULL, 
                               LNG REAL NOT NULL,
                               LAT REAL NOT NULL,
                               ALT REAL NOT NULL
                               );'''.format(i))
        print ("{}数据表创建成功".format(missile_record_db))
    except:
        print ("错误！{}数据表创建失败，已存在该表！".format(missile_record_db))


conn.commit()
conn.close()
#-----------------------------------------------------------------------------------------------------------------------1


# 3. solider 数据库的构建
#-----------------------------------------------------------------------------------------------------------------------0
solider_init_db = './MCI/solider_init.db' # 这个数据库是记录初始化时各个坦克的名称、ID、通讯地址之间的关系，不需要变更
# tank_init_table = "task1" # 每次任务，需要给各个坦克的名称、ID、通讯地址之间的关系建立一个新表
solider_record_db = './MCI/solider_record.db' # 这个数据库是个坦克实况的数据记录，对不同的任务可以创建新的数据库，表的名称需要根据不同任务换
solider_num = 3 # n为坦克个数，会自动为各个ID的坦克实况创建数据记录表，大于实际个数也可以

# 如果数据库或表已经存在的话，创建冲突会报错

conn = sqlite3.connect(solider_init_db)
print ("{}数据库创建或连接成功".format(solider_init_db))
conn.close()

# 创建坦克实况数据记录表
conn = sqlite3.connect(solider_record_db)
print ("{}数据库创建或连接成功".format(solider_record_db))
c = conn.cursor()
for i in range(solider_num):
    try:
        c.execute('''CREATE TABLE ID{} (
                               ID INT NOT NULL,
                               NAME CHAR(50) NOT NULL,
                               IP CHAR(50) NOT NULL,
                               PORT INT NOT NULL,
                               TIME CHAR(50) PRIMARY KEY NOT NULL,
                               TIMESTAMP INT NOT NULL,
                               PX REAL NOT NULL, 
                               PY REAL NOT NULL, 
                               PZ REAL NOT NULL,
                               ROLL REAL NOT NULL, 
                               PITCH REAL NOT NULL, 
                               YOW REAL NOT NULL, 
                               LNG REAL NOT NULL,
                               LAT REAL NOT NULL,
                               ALT REAL NOT NULL
                               );'''.format(i))

        print ("{}数据表创建成功".format(solider_record_db))
    except:
        print ("错误！{}数据表创建失败，已存在该表！".format(solider_record_db))

conn.commit()
conn.close()
#-----------------------------------------------------------------------------------------------------------------------1

# 4. trump 数据库的构建
#-----------------------------------------------------------------------------------------------------------------------0
trump_init_db = './MCI/trump_init.db' # 这个数据库是记录初始化时各个坦克的名称、ID、通讯地址之间的关系，不需要变更
# tank_init_table = "task1" # 每次任务，需要给各个坦克的名称、ID、通讯地址之间的关系建立一个新表
trump_record_db = './MCI/trump_record.db' # 这个数据库是个坦克实况的数据记录，对不同的任务可以创建新的数据库，表的名称需要根据不同任务换
trump_num = 3 # n为坦克个数，会自动为各个ID的坦克实况创建数据记录表，大于实际个数也可以

conn = sqlite3.connect(trump_init_db)
print ("{}数据库创建或连接成功".format(trump_init_db))
conn.close()

# 创建坦克实况数据记录表
conn = sqlite3.connect(trump_record_db)
print ("{}数据库创建或连接成功".format(trump_record_db))
c = conn.cursor()
for i in range(trump_num):
    try:
        c.execute('''CREATE TABLE ID{} (
                               ID INT NOT NULL,
                               NAME CHAR(50) NOT NULL,
                               IP CHAR(50) NOT NULL,
                               PORT INT NOT NULL,
                               TIME CHAR(50) PRIMARY KEY NOT NULL,
                               TIMESTAMP INT NOT NULL,
                               PX REAL NOT NULL, 
                               PY REAL NOT NULL, 
                               PZ REAL NOT NULL,
                               ROLL REAL NOT NULL, 
                               PITCH REAL NOT NULL, 
                               YOW REAL NOT NULL, 
                               LNG REAL NOT NULL,
                               LAT REAL NOT NULL,
                               ALT REAL NOT NULL
                               );'''.format(i))
        print ("{}数据表创建成功".format(trump_record_db))
    except:
        print ("错误！{}数据表创建失败，已存在该表！".format(trump_record_db))
        


conn.commit()
conn.close()
#-----------------------------------------------------------------------------------------------------------------------1