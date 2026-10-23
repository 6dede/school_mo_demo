import pymysql
from org.zsy.common.config import DB_CONFIG
from org.zsy.common.basedao import insert,execute,queray_all,queray_one



def get_all_dao(subject=''):
    where, args = '', []
    if subject:
        where = " where subject=%s"
        args.append(subject)
    sql = f"select * from teachers{where}"
    return queray_all(sql, args or None)
def count_dao(subject=''):
#     sql = "select count(*) from teachers where subject=%s"
#     res=queray_one(sql,subject)["COUNT"]
#     print("查询结果：", res)
#     return res
    sql = "select count(*) as cnt from teachers where subject=%s"
    res = queray_one(sql,subject)
    if not res:
        return 0
    return res["cnt"]

def get_by_id_dao(teacher_id:int):

        sql = "select * from teachers where id=%s"

        return queray_one(sql,teacher_id)


def get_page_dao(page: int, page_size: int,keyword=''):
    where,args='',[]
    if keyword:
        where=f"where name like %s"
        args.append(f"%{keyword}%")
    total=queray_one(f"select count(*) as total from teachers {where} ",args or None)["total"]
    rows=queray_all(f"select * from teachers {where} limit %s,%s ",[*args,(page-1)*page_size,page_size])

    return rows,total

def insert_dao(name,gerder,age,subject,phone):

        sql = """insert into teachers (name,gerder,age,subject,phone) values
            (%s,%s,%s,%s,%s)"""

        return insert(sql,(name,gerder,age,subject,phone))
TEACHER_UPDATE_FIELDS = ('name', 'gerder', 'age', 'subject', 'phone')


def update_dao( id:int, data:dict=None):
        if not data:
                sql = """update teachers set age=age+1 where id=%s"""
                return execute(sql,id)

        fields = [k for k in TEACHER_UPDATE_FIELDS if k in data]
        if not fields:
                return 0
        sql = f"update teachers set {', '.join(f'{k}=%s' for k in fields)} where id=%s"
        return execute(sql, (*[data[k] for k in fields], id))
def delete_dao( id:int):

        sql = "delete from teachers where id=%s"

        return execute(sql,id)


def count_course_dao(teacher_id:int):
        '''统计老师被课程引用的数量'''
        sql = "select count(*) as total from courses where teacher_id=%s"
        return queray_one(sql, teacher_id)["total"]

if __name__=="__main__":

    print(get_all_dao())
    print(get_by_id_dao(1))
    print(insert_dao("老王","man",23,"音乐","19832761992"))
    print(update_dao(1))
    print(delete_dao(7))