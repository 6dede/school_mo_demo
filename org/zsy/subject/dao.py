from datetime import datetime
from org.zsy.common.config import DB_CONFIG
from org.zsy.common.basedao import insert, execute, queray_all, queray_one
from org.zsy.teacher.dao import get_all_dao as get_tea_dao
import pymysql


def get_all_dao():
    sql = "select * from subjects"
    return queray_all(sql)


def get_by_id_dao(subject_id: int,totea=''):


    sql = "select * from subjects where id=%s"
    return queray_one(sql, subject_id)



def get_page_dao(page: int, page_size: int, keyword=''):
    where, args = '', []
    if keyword:
        where = " where subject like %s"
        args.append(f"%{keyword}%")
    total = queray_one(f"select count(*) as total from subjects{where}", args or None)["total"]
    rows = queray_all(f"select * from subjects{where} order by id limit %s , %s",
                      [*args, (page - 1) * page_size, page_size])
    return rows, total


def insert_dao(subject: str):
    sql = """insert into subjects (subject) values(%s)"""
    return insert(sql, (subject,))


def update_dao(id: int, subject: str):
    sql = """update subjects set subject=%s where id=%s"""
    return execute(sql, (subject, id))


def delete_dao(id: int):
    sql = "delete from subjects where id=%s"
    return execute(sql, id)


def count_course_dao(subject_id: int):
    '''统计学科被课程引用的数量'''
    sql = "select count(*) as total from courses where subject_id=%s"
    return queray_one(sql, subject_id)["total"]


if __name__ == "__main__":
    rows, total = get_page_dao(1, 4, 's')
    print("total:", total)
    print("rows:", rows)
    # print(get_all_dao())
    # print(get_by_id_dao(1))
    # print(insert_dao("数学"))
    # print(update_dao(1,"高等数学"))
    # print(delete_dao(1))
