import pymysql

from org.zsy.common.pool import get_conn

def queray_all(sql,args=None):
    """查询所有"""
    with get_conn() as conn:
        with conn.cursor() as cursor:
            cursor.execute(sql,args)
            return cursor.fetchall()

def queray_one(sql,args=None):
    """查询所有"""
    with get_conn() as conn:
        with conn.cursor() as cursor:
            cursor.execute(sql,args)
            return cursor.fetchone()


def execute(sql,args=None):
    conn = get_conn()
    try:
        with conn.cursor() as cursor:
            cursor.execute(sql,args)
            rowcount=cursor.rowcount
        conn.commit()
        return rowcount
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()


def insert(sql,args=None):
    conn = get_conn()
    try:
        with conn.cursor() as cursor:
            cursor.execute(sql,args)
            new_id=cursor.lastrowid
        conn.commit()
        return new_id
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()

if __name__ == '__main__':


    sql_insert="insert into students (name,gerder,age,teacher_id,grade,enrollment_date) values(%s,%s,%s,%s,%s,%s)"
    insert_id=insert(sql_insert,["mmm", "男", 13, 2, "高一", "2026-10-15 14:20:20"])
    print(insert_id)
    sql_delete="delete from students where id=%s"
    sql_update="update students set grade=%s where id=%s"
    print(execute(sql_delete, [14]))
    print(execute(sql_update, ["高三",insert_id]))
