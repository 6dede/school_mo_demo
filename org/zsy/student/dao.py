from datetime import datetime
from org.zsy.common.config import DB_CONFIG
from org.zsy.common.basedao import insert,execute,queray_all,queray_one
import pymysql

#insert,execute,queray_all,queray_one
def get_all_dao(tid=''):
        where,args='',[]
        if tid:
                where=" where teacher_id=%s"
                args.append(tid)
        sql=f"select * from students{where}"

        return queray_all(sql,args or None)

def get_tid_dao(tid:int):
        sql="select * from teachers where id=%s"
        return queray_all(sql, [tid])


def get_by_id_dao(student_id:int):

        sql = "select * from students where id=%s"

        return queray_one(sql,student_id)
def get_page_dao(page:int,page_size:int,keyword=''):
        where,args='',[]
        if keyword:
            where=" where name like %s"
            args.append(f"%{keyword}%")
        total=queray_one(f"select count(*) as total from students{where}",args or None)["total"]
        rows=queray_all(f"select * from students{where} order by id limit %s , %s",[*args,(page-1)*page_size,page_size])


        return rows,total

def insert_dao(name:str, gerder:str,age:int, teacher_id:int, grade:str, enrollment_date:datetime):

        sql = """insert into students (name,gerder,age,teacher_id,grade,enrollment_date) values(%s,%s,%s,%s,%s,%s)"""

        return insert(sql,(name,gerder,age,teacher_id,grade,enrollment_date))
STUDENT_UPDATE_FIELDS = ('name', 'gerder', 'age', 'teacher_id', 'grade', 'enrollment_date')


def update_dao(id:int, data:dict=None):
        if not data:
                sql = """update students set age=age+1 where id=%s"""
                return execute(sql,id)

        fields = [k for k in STUDENT_UPDATE_FIELDS if k in data]
        if not fields:
                return 0
        sql = f"update students set {', '.join(f'{k}=%s' for k in fields)} where id=%s"
        return execute(sql, (*[data[k] for k in fields], id))
def delete_dao(id:int):

        sql = "delete from students where id=%s"

        return execute(sql,id)


def count_refs_dao(student_id:int):
        '''统计学生被分班、成绩、考勤、奖惩、缴费引用的数量'''
        sql = """select
            (select count(*) from class_students where student_id=%s) as members,
            (select count(*) from scores where student_id=%s) as scores,
            (select count(*) from attendance where student_id=%s) as attendances,
            (select count(*) from awards where student_id=%s) as awards,
            (select count(*) from payments where student_id=%s) as payments"""
        return queray_one(sql, (student_id,) * 5)

if __name__=="__main__":
        rows, total = get_page_dao(1, 4,'s')
        print("total:", total)
        print("rows:", rows)
    # print(get_all_dao())
    # print(get_by_id_dao(1))
    # print(student.insert("喵喵喵",'man',22,2,'高二',datetime.now()))
    # print(student.update(1))
    # print(delete_dao(8))

