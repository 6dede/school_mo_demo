from org.zsy.common.basedao import insert, execute, queray_all, queray_one


def ensure_table():
    '''初始化宿舍表'''
    execute(
        """CREATE TABLE IF NOT EXISTS dormitories (
            id INT AUTO_INCREMENT PRIMARY KEY,
            building VARCHAR(50) NOT NULL,
            room VARCHAR(20) NOT NULL,
            capacity INT NOT NULL,
            occupied INT NOT NULL DEFAULT 0,
            class_id INT NOT NULL,
            create_time DATETIME DEFAULT CURRENT_TIMESTAMP
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4"""
    )


DORM_SELECT = """
    select d.*, cl.name as class_name
    from dormitories d
    left join classes cl on cl.id=d.class_id
"""


def _where(keyword='', class_id=None):
    conds, args = [], []
    if keyword:
        conds.append("(d.building like %s or d.room like %s)")
        args.extend([f"%{keyword}%"] * 2)
    if class_id:
        conds.append("d.class_id=%s")
        args.append(class_id)
    return (" where " + " and ".join(conds)) if conds else "", args


def get_all_dao(class_id=None):
    cond, args = _where(class_id=class_id)
    return queray_all(DORM_SELECT + cond + " order by d.id desc", args or None)


def get_by_id_dao(dorm_id: int):
    return queray_one(DORM_SELECT + " where d.id=%s", dorm_id)


def get_page_dao(page: int, page_size: int, keyword='', class_id=None):
    cond, args = _where(keyword, class_id)
    count_sql = """
        select count(*) as total from dormitories d
        left join classes cl on cl.id=d.class_id
    """ + cond
    total = queray_one(count_sql, args or None)["total"]
    rows = queray_all(DORM_SELECT + cond + " order by d.id desc limit %s , %s",
                      [*args, (page - 1) * page_size, page_size])
    return rows, total


def insert_dao(building, room, capacity, occupied, class_id):
    sql = """insert into dormitories (building, room, capacity, occupied, class_id)
             values(%s,%s,%s,%s,%s)"""
    return insert(sql, (building, room, capacity, occupied, class_id))


DORM_UPDATE_FIELDS = ('building', 'room', 'capacity', 'occupied', 'class_id')


def update_dao(dorm_id: int, data: dict = None):
    if not data:
        return 0
    fields = [k for k in DORM_UPDATE_FIELDS if k in data]
    if not fields:
        return 0
    sql = f"update dormitories set {', '.join(f'{k}=%s' for k in fields)} where id=%s"
    return execute(sql, (*[data[k] for k in fields], dorm_id))


def delete_dao(dorm_id: int):
    return execute("delete from dormitories where id=%s", dorm_id)
