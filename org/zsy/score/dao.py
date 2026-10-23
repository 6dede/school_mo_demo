from org.zsy.common.basedao import insert, execute, queray_all, queray_one


def ensure_table():
    '''初始化成绩表'''
    execute(
        """CREATE TABLE IF NOT EXISTS scores (
            id INT AUTO_INCREMENT PRIMARY KEY,
            student_id INT NOT NULL,
            course_id INT NOT NULL,
            exam_name VARCHAR(50) NOT NULL,
            score DECIMAL(5,1) NOT NULL,
            create_time DATETIME DEFAULT CURRENT_TIMESTAMP
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4"""
    )


SCORE_SELECT = """
    select sc.*, st.name as student_name, c.name as course_name,
           s.subject as subject_name, cl.name as class_name
    from scores sc
    left join students st on st.id=sc.student_id
    left join courses c on c.id=sc.course_id
    left join subjects s on s.id=c.subject_id
    left join class_students cs on cs.student_id=sc.student_id
    left join classes cl on cl.id=cs.class_id
"""


def _where(keyword='', course_id=None):
    conds, args = [], []
    if keyword:
        conds.append("(st.name like %s or c.name like %s or sc.exam_name like %s)")
        args.extend([f"%{keyword}%"] * 3)
    if course_id:
        conds.append("sc.course_id=%s")
        args.append(course_id)
    return (" where " + " and ".join(conds)) if conds else "", args


def get_all_dao(course_id=None, student_id=None):
    if student_id:
        return queray_all(SCORE_SELECT + " where sc.student_id=%s order by sc.id desc", student_id)
    cond, args = _where(course_id=course_id)
    return queray_all(SCORE_SELECT + cond + " order by sc.id desc", args or None)


def get_by_id_dao(score_id: int):
    return queray_one(SCORE_SELECT + " where sc.id=%s", score_id)


def get_page_dao(page: int, page_size: int, keyword='', course_id=None):
    cond, args = _where(keyword, course_id)
    count_sql = """
        select count(*) as total from scores sc
        left join students st on st.id=sc.student_id
        left join courses c on c.id=sc.course_id
    """ + cond
    total = queray_one(count_sql, args or None)["total"]
    rows = queray_all(SCORE_SELECT + cond + " order by sc.id desc limit %s , %s",
                      [*args, (page - 1) * page_size, page_size])
    return rows, total


def insert_dao(student_id, course_id, exam_name, score):
    sql = """insert into scores (student_id, course_id, exam_name, score) values(%s,%s,%s,%s)"""
    return insert(sql, (student_id, course_id, exam_name, score))


SCORE_UPDATE_FIELDS = ('student_id', 'course_id', 'exam_name', 'score')


def update_dao(score_id: int, data: dict = None):
    if not data:
        return 0
    fields = [k for k in SCORE_UPDATE_FIELDS if k in data]
    if not fields:
        return 0
    sql = f"update scores set {', '.join(f'{k}=%s' for k in fields)} where id=%s"
    return execute(sql, (*[data[k] for k in fields], score_id))


def delete_dao(score_id: int):
    return execute("delete from scores where id=%s", score_id)
