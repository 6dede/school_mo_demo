import pymysql
from dbutils.pooled_db import PooledDB


DB_CONFIG = {
    "host" : 'localhost',
    "port" :3306,
    "user" :'root',
    "password" : '123456',
    "charset" : 'utf8mb4',
    "cursorclass" : pymysql.cursors.DictCursor,
    "database" : "schaool_db_study",
    "cursorclass" : pymysql.cursors.DictCursor

}

pools = PooledDB(
    creator=pymysql,   #使用哪个驱动链接数据库
    mincached=5,       #连接池启动时首次连接个数
    maxcached=5,       #连接池空闲最多连接个数
    maxusage=1000,     #每个连接最多使用次数
    setsession=['set autocommit=1'],  #设置会话
    ping=1,            #探活，8小时断联
    blocking=True,     #配置数据库连接池都被占用时的策略：true:等待，false:异常报错
    maxconnections=10,
    **DB_CONFIG
)

def get_conn():
    return pools.connection()