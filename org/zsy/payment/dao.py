from org.zsy.common.basedao import insert, execute, queray_all, queray_one


def ensure_table():
    '''初始化缴费表'''
    execute(
        """CREATE TABLE IF NOT EXISTS payments (
            id INT AUTO_INCREMENT PRIMARY KEY,
            student_id INT NOT NULL,
            fee_type VARCHAR(50) NOT NULL,
            amount DECIMAL(10,2) NOT NULL,
            status VARCHAR(10) NOT NULL,
            pay_date DATE DEFAULT NULL,
            create_time DATETIME DEFAULT CURRENT_TIMESTAMP
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4"""
    )


PAYMENT_SELECT = """
    select p.*, st.name as student_name, cl.name as class_name
    from payments p
    left join students st on st.id=p.student_id
    left join class_students cs on cs.student_id=p.student_id
    left join classes cl on cl.id=cs.class_id
"""


def _where(keyword='', status=None):
    conds, args = [], []
    if keyword:
        conds.append("(st.name like %s or p.fee_type like %s)")
        args.extend([f"%{keyword}%"] * 2)
    if status:
        conds.append("p.status=%s")
        args.append(status)
    return (" where " + " and ".join(conds)) if conds else "", args


def get_all_dao(student_id=None):
    if student_id:
        return queray_all(PAYMENT_SELECT + " where p.student_id=%s order by p.id desc", student_id)
    return queray_all(PAYMENT_SELECT + " order by p.id desc")


def get_by_id_dao(payment_id: int):
    return queray_one(PAYMENT_SELECT + " where p.id=%s", payment_id)


def get_page_dao(page: int, page_size: int, keyword='', status=None):
    cond, args = _where(keyword, status)
    count_sql = """
        select count(*) as total from payments p
        left join students st on st.id=p.student_id
    """ + cond
    total = queray_one(count_sql, args or None)["total"]
    rows = queray_all(PAYMENT_SELECT + cond + " order by p.id desc limit %s , %s",
                      [*args, (page - 1) * page_size, page_size])
    return rows, total


def insert_dao(student_id, fee_type, amount, status, pay_date):
    sql = """insert into payments (student_id, fee_type, amount, status, pay_date)
             values(%s,%s,%s,%s,%s)"""
    return insert(sql, (student_id, fee_type, amount, status, pay_date))


PAYMENT_UPDATE_FIELDS = ('student_id', 'fee_type', 'amount', 'status', 'pay_date')


def update_dao(payment_id: int, data: dict = None):
    if not data:
        return 0
    fields = [k for k in PAYMENT_UPDATE_FIELDS if k in data]
    if not fields:
        return 0
    sql = f"update payments set {', '.join(f'{k}=%s' for k in fields)} where id=%s"
    return execute(sql, (*[data[k] for k in fields], payment_id))


def delete_dao(payment_id: int):
    return execute("delete from payments where id=%s", payment_id)
