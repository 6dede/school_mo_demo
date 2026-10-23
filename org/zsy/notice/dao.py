from org.zsy.common.basedao import insert, execute, queray_all, queray_one


def ensure_table():
    '''初始化公告表'''
    execute(
        """CREATE TABLE IF NOT EXISTS notices (
            id INT AUTO_INCREMENT PRIMARY KEY,
            title VARCHAR(100) NOT NULL,
            content TEXT NOT NULL,
            publisher VARCHAR(50) NOT NULL,
            publish_time DATETIME DEFAULT CURRENT_TIMESTAMP
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4"""
    )


def get_all_dao(limit=20):
    return queray_all("select * from notices order by publish_time desc, id desc limit %s", (limit,))


def get_by_id_dao(notice_id: int):
    return queray_one("select * from notices where id=%s", notice_id)


def get_page_dao(page: int, page_size: int, keyword=''):
    where, args = '', []
    if keyword:
        where = " where title like %s or content like %s"
        args.extend([f"%{keyword}%"] * 2)
    total = queray_one(f"select count(*) as total from notices{where}", args or None)["total"]
    rows = queray_all(f"select * from notices{where} order by publish_time desc, id desc limit %s , %s",
                      [*args, (page - 1) * page_size, page_size])
    return rows, total


def insert_dao(title, content, publisher):
    sql = """insert into notices (title, content, publisher) values(%s,%s,%s)"""
    return insert(sql, (title, content, publisher))


NOTICE_UPDATE_FIELDS = ('title', 'content', 'publisher')


def update_dao(notice_id: int, data: dict = None):
    if not data:
        return 0
    fields = [k for k in NOTICE_UPDATE_FIELDS if k in data]
    if not fields:
        return 0
    sql = f"update notices set {', '.join(f'{k}=%s' for k in fields)} where id=%s"
    return execute(sql, (*[data[k] for k in fields], notice_id))


def delete_dao(notice_id: int):
    return execute("delete from notices where id=%s", notice_id)
