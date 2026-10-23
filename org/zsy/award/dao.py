from org.zsy.common.basedao import insert, execute, queray_all, queray_one


def ensure_table():
    '''初始化奖惩表'''
    execute(
        """CREATE TABLE IF NOT EXISTS awards (
            id INT AUTO_INCREMENT PRIMARY KEY,
            student_id INT NOT NULL,
            type VARCHAR(10) NOT NULL,
            title VARCHAR(100) NOT NULL,
            reason VARCHAR(200) DEFAULT NULL,
            record_date DATE NOT NULL,
            create_time DATETIME DEFAULT CURRENT_TIMESTAMP
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4"""
    )


AWARD_SELECT = """
    select a.*, st.name as student_name, cl.name as class_name
    from awards a
    left join students st on st.id=a.student_id
    left join class_students cs on cs.student_id=a.student_id
    left join classes cl on cl.id=cs.class_id
"""


def _where(keyword='', type=None):
    conds, args = [], []
    if keyword:
        conds.append("(st.name like %s or a.title like %s)")
        args.extend([f"%{keyword}%"] * 2)
    if type:
        conds.append("a.type=%s")
        args.append(type)
    return (" where " + " and ".join(conds)) if conds else "", args


def get_all_dao(student_id=None):
    if student_id:
        return queray_all(AWARD_SELECT + " where a.student_id=%s order by a.record_date desc, a.id desc", student_id)
    return queray_all(AWARD_SELECT + " order by a.record_date desc, a.id desc")


def get_by_id_dao(award_id: int):
    return queray_one(AWARD_SELECT + " where a.id=%s", award_id)


def get_page_dao(page: int, page_size: int, keyword='', type=None):
    cond, args = _where(keyword, type)
    count_sql = """
        select count(*) as total from awards a
        left join students st on st.id=a.student_id
    """ + cond
    total = queray_one(count_sql, args or None)["total"]
    rows = queray_all(AWARD_SELECT + cond + " order by a.record_date desc, a.id desc limit %s , %s",
                      [*args, (page - 1) * page_size, page_size])
    return rows, total


def insert_dao(student_id, type, title, reason, record_date):
    sql = """insert into awards (student_id, type, title, reason, record_date) values(%s,%s,%s,%s,%s)"""
    return insert(sql, (student_id, type, title, reason, record_date))


AWARD_UPDATE_FIELDS = ('student_id', 'type', 'title', 'reason', 'record_date')


def update_dao(award_id: int, data: dict = None):
    if not data:
        return 0
    fields = [k for k in AWARD_UPDATE_FIELDS if k in data]
    if not fields:
        return 0
    sql = f"update awards set {', '.join(f'{k}=%s' for k in fields)} where id=%s"
    return execute(sql, (*[data[k] for k in fields], award_id))


def delete_dao(award_id: int):
    return execute("delete from awards where id=%s", award_id)
