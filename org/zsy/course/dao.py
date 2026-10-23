from org.zsy.common.basedao import insert, execute, queray_all, queray_one


def ensure_table():
    '''初始化课程表'''
    execute(
        """CREATE TABLE IF NOT EXISTS courses (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(50) NOT NULL,
            subject_id INT NOT NULL,
            teacher_id INT NOT NULL,
            class_id INT NOT NULL,
            schedule_day VARCHAR(10) NOT NULL,
            start_time VARCHAR(5) NOT NULL,
            end_time VARCHAR(5) NOT NULL,
            create_time DATETIME DEFAULT CURRENT_TIMESTAMP
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4"""
    )


COURSE_SELECT = """
    select c.*, s.subject as subject_name, t.name as teacher_name, cl.name as class_name
    from courses c
    left join subjects s on s.id=c.subject_id
    left join teachers t on t.id=c.teacher_id
    left join classes cl on cl.id=c.class_id
"""
COURSE_ORDER = "FIELD(c.schedule_day,'周一','周二','周三','周四','周五','周六','周日'), c.start_time, c.id"


def _where(keyword='', class_id=None):
    conds, args = [], []
    if keyword:
        conds.append("(c.name like %s or s.subject like %s or t.name like %s or cl.name like %s)")
        args.extend([f"%{keyword}%"] * 4)
    if class_id:
        conds.append("c.class_id=%s")
        args.append(class_id)
    return (" where " + " and ".join(conds)) if conds else "", args


def get_all_dao(class_id=None, teacher_id=None):
    if teacher_id:
        return queray_all(COURSE_SELECT + " where c.teacher_id=%s order by " + COURSE_ORDER, teacher_id)
    cond, args = _where(class_id=class_id)
    return queray_all(COURSE_SELECT + cond + " order by " + COURSE_ORDER, args or None)


def get_by_id_dao(course_id: int):
    return queray_one(COURSE_SELECT + " where c.id=%s", course_id)


def get_page_dao(page: int, page_size: int, keyword='', class_id=None):
    cond, args = _where(keyword, class_id)
    count_sql = """
        select count(*) as total from courses c
        left join subjects s on s.id=c.subject_id
        left join teachers t on t.id=c.teacher_id
        left join classes cl on cl.id=c.class_id
    """ + cond
    total = queray_one(count_sql, args or None)["total"]
    rows = queray_all(COURSE_SELECT + cond + " order by " + COURSE_ORDER + " limit %s , %s",
                      [*args, (page - 1) * page_size, page_size])
    return rows, total


def insert_dao(name, subject_id, teacher_id, class_id, schedule_day, start_time, end_time):
    sql = """insert into courses (name, subject_id, teacher_id, class_id, schedule_day, start_time, end_time)
             values(%s,%s,%s,%s,%s,%s,%s)"""
    return insert(sql, (name, subject_id, teacher_id, class_id, schedule_day, start_time, end_time))


COURSE_UPDATE_FIELDS = ('name', 'subject_id', 'teacher_id', 'class_id', 'schedule_day', 'start_time', 'end_time')


def update_dao(course_id: int, data: dict = None):
    if not data:
        return 0
    fields = [k for k in COURSE_UPDATE_FIELDS if k in data]
    if not fields:
        return 0
    sql = f"update courses set {', '.join(f'{k}=%s' for k in fields)} where id=%s"
    return execute(sql, (*[data[k] for k in fields], course_id))


def delete_dao(course_id: int):
    return execute("delete from courses where id=%s", course_id)


def count_refs_dao(course_id: int):
    '''统计课程被成绩、考勤引用的数量'''
    sql = """select
        (select count(*) from scores where course_id=%s) as scores,
        (select count(*) from attendance where course_id=%s) as attendances"""
    return queray_one(sql, (course_id, course_id))
