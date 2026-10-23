from org.zsy.common.basedao import insert, execute, queray_all, queray_one


def ensure_table():
    '''初始化班级表，id 自增，创建时间默认当前时间'''
    execute(
        """CREATE TABLE IF NOT EXISTS classes (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(50) NOT NULL,
            address VARCHAR(200) NOT NULL,
            create_time DATETIME DEFAULT CURRENT_TIMESTAMP
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4"""
    )


def get_all_dao():
    sql = "select * from classes order by id"
    return queray_all(sql)


def get_by_id_dao(class_id: int):
    sql = "select * from classes where id=%s"
    return queray_one(sql, class_id)


def get_page_dao(page: int, page_size: int, keyword=''):
    where, args = '', []
    if keyword:
        where = " where name like %s or address like %s"
        args.extend([f"%{keyword}%", f"%{keyword}%"])
    total = queray_one(f"select count(*) as total from classes{where}", args or None)["total"]
    rows = queray_all(f"select * from classes{where} order by id limit %s , %s",
                      [*args, (page - 1) * page_size, page_size])
    return rows, total


def insert_dao(name: str, address: str):
    sql = """insert into classes (name, address) values(%s,%s)"""
    return insert(sql, (name, address))


CLASS_UPDATE_FIELDS = ('name', 'address')


def update_dao(class_id: int, data: dict = None):
    if not data:
        return 0
    fields = [k for k in CLASS_UPDATE_FIELDS if k in data]
    if not fields:
        return 0
    sql = f"update classes set {', '.join(f'{k}=%s' for k in fields)} where id=%s"
    return execute(sql, (*[data[k] for k in fields], class_id))


def delete_dao(class_id: int):
    sql = "delete from classes where id=%s"
    return execute(sql, class_id)


def count_refs_dao(class_id: int):
    '''统计班级被课程、分班、宿舍引用的数量'''
    sql = """select
        (select count(*) from courses where class_id=%s) as courses,
        (select count(*) from class_students where class_id=%s) as members,
        (select count(*) from dormitories where class_id=%s) as dorms"""
    return queray_one(sql, (class_id, class_id, class_id))


if __name__ == "__main__":
    rows, total = get_page_dao(1, 4, '')
    print("total:", total)
    print("rows:", rows)
    # print(get_all_dao())
    # print(get_by_id_dao(1))
    # print(insert_dao("高一(1)班", "教学楼101"))
    # print(update_dao(1, {"name": "高一(2)班", "address": "教学楼102"}))
    # print(delete_dao(1))
