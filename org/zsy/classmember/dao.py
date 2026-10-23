from org.zsy.common.basedao import insert, execute, queray_all, queray_one


def ensure_table():
    '''初始化分班表，一个学生只能属于一个班级'''
    execute(
        """CREATE TABLE IF NOT EXISTS class_students (
            id INT AUTO_INCREMENT PRIMARY KEY,
            class_id INT NOT NULL,
            student_id INT NOT NULL,
            join_date DATE NOT NULL,
            create_time DATETIME DEFAULT CURRENT_TIMESTAMP,
            UNIQUE KEY uk_student (student_id)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4"""
    )


MEMBER_SELECT = """
    select cs.*, st.name as student_name, st.gerder, st.age, cl.name as class_name
    from class_students cs
    left join students st on st.id=cs.student_id
    left join classes cl on cl.id=cs.class_id
"""


def _where(keyword='', class_id=None):
    conds, args = [], []
    if keyword:
        conds.append("(st.name like %s or cl.name like %s)")
        args.extend([f"%{keyword}%"] * 2)
    if class_id:
        conds.append("cs.class_id=%s")
        args.append(class_id)
    return (" where " + " and ".join(conds)) if conds else "", args


def get_all_dao(class_id=None):
    cond, args = _where(class_id=class_id)
    return queray_all(MEMBER_SELECT + cond + " order by cs.id desc", args or None)


def get_by_id_dao(member_id: int):
    return queray_one(MEMBER_SELECT + " where cs.id=%s", member_id)


def get_by_student_dao(student_id: int):
    return queray_one(MEMBER_SELECT + " where cs.student_id=%s", student_id)


def get_page_dao(page: int, page_size: int, keyword='', class_id=None):
    cond, args = _where(keyword, class_id)
    count_sql = """
        select count(*) as total from class_students cs
        left join students st on st.id=cs.student_id
        left join classes cl on cl.id=cs.class_id
    """ + cond
    total = queray_one(count_sql, args or None)["total"]
    rows = queray_all(MEMBER_SELECT + cond + " order by cs.id desc limit %s , %s",
                      [*args, (page - 1) * page_size, page_size])
    return rows, total


def insert_dao(class_id, student_id, join_date):
    sql = """insert into class_students (class_id, student_id, join_date) values(%s,%s,%s)"""
    return insert(sql, (class_id, student_id, join_date))


MEMBER_UPDATE_FIELDS = ('class_id', 'student_id', 'join_date')


def update_dao(member_id: int, data: dict = None):
    if not data:
        return 0
    fields = [k for k in MEMBER_UPDATE_FIELDS if k in data]
    if not fields:
        return 0
    sql = f"update class_students set {', '.join(f'{k}=%s' for k in fields)} where id=%s"
    return execute(sql, (*[data[k] for k in fields], member_id))


def delete_dao(member_id: int):
    return execute("delete from class_students where id=%s", member_id)
