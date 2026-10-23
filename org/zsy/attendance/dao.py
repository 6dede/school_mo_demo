from org.zsy.common.basedao import insert, execute, queray_all, queray_one


def ensure_table():
    '''初始化考勤表'''
    execute(
        """CREATE TABLE IF NOT EXISTS attendance (
            id INT AUTO_INCREMENT PRIMARY KEY,
            student_id INT NOT NULL,
            course_id INT NOT NULL,
            status VARCHAR(10) NOT NULL,
            attendance_date DATE NOT NULL,
            remark VARCHAR(200) DEFAULT NULL,
            create_time DATETIME DEFAULT CURRENT_TIMESTAMP
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4"""
    )


ATTENDANCE_SELECT = """
    select a.*, st.name as student_name, c.name as course_name, cl.name as class_name
    from attendance a
    left join students st on st.id=a.student_id
    left join courses c on c.id=a.course_id
    left join class_students cs on cs.student_id=a.student_id
    left join classes cl on cl.id=cs.class_id
"""


def _where(keyword='', status=None, course_id=None):
    conds, args = [], []
    if keyword:
        conds.append("(st.name like %s or c.name like %s)")
        args.extend([f"%{keyword}%"] * 2)
    if status:
        conds.append("a.status=%s")
        args.append(status)
    if course_id:
        conds.append("a.course_id=%s")
        args.append(course_id)
    return (" where " + " and ".join(conds)) if conds else "", args


def get_all_dao(student_id=None, course_id=None):
    if student_id:
        return queray_all(ATTENDANCE_SELECT + " where a.student_id=%s order by a.attendance_date desc, a.id desc", student_id)
    cond, args = _where(course_id=course_id)
    return queray_all(ATTENDANCE_SELECT + cond + " order by a.attendance_date desc, a.id desc", args or None)


def get_by_id_dao(attendance_id: int):
    return queray_one(ATTENDANCE_SELECT + " where a.id=%s", attendance_id)


def get_page_dao(page: int, page_size: int, keyword='', status=None, course_id=None):
    cond, args = _where(keyword, status, course_id)
    count_sql = """
        select count(*) as total from attendance a
        left join students st on st.id=a.student_id
        left join courses c on c.id=a.course_id
    """ + cond
    total = queray_one(count_sql, args or None)["total"]
    rows = queray_all(ATTENDANCE_SELECT + cond + " order by a.attendance_date desc, a.id desc limit %s , %s",
                      [*args, (page - 1) * page_size, page_size])
    return rows, total


def insert_dao(student_id, course_id, status, attendance_date, remark=''):
    sql = """insert into attendance (student_id, course_id, status, attendance_date, remark)
             values(%s,%s,%s,%s,%s)"""
    return insert(sql, (student_id, course_id, status, attendance_date, remark))


ATTENDANCE_UPDATE_FIELDS = ('student_id', 'course_id', 'status', 'attendance_date', 'remark')


def update_dao(attendance_id: int, data: dict = None):
    if not data:
        return 0
    fields = [k for k in ATTENDANCE_UPDATE_FIELDS if k in data]
    if not fields:
        return 0
    sql = f"update attendance set {', '.join(f'{k}=%s' for k in fields)} where id=%s"
    return execute(sql, (*[data[k] for k in fields], attendance_id))


def delete_dao(attendance_id: int):
    return execute("delete from attendance where id=%s", attendance_id)
