import logging

from org.zsy.common.exception import BizException
from org.zsy.classroom.dao import get_by_id_dao as get_class_dao
from org.zsy.dormitory.dao import get_all_dao, get_by_id_dao, get_page_dao, insert_dao, update_dao, delete_dao

logger = logging.getLogger(__name__)


def _check(class_id, capacity, occupied):
    if not get_class_dao(class_id):
        raise BizException("班级不存在")
    if occupied < 0 or occupied > capacity:
        raise BizException("入住人数需在 0 ~ 床位容量之间")


def get_all(class_id=None):
    return get_all_dao(class_id)


def get_page(page=1, page_size: int = 10, keyword='', class_id=None):
    rows, total = get_page_dao(page, page_size, keyword, class_id)
    logger.info(f"宿舍分页：第{page}页 每页{page_size}条 共{total}条")
    return {"total": total, "page": page, "size": page_size, "rows": rows}


def get_one(dorm_id: int):
    row = get_by_id_dao(dorm_id)
    if not row:
        raise BizException("宿舍不存在")
    return row


def insert(building, room, capacity, occupied, class_id):
    _check(class_id, capacity, occupied)
    newid = insert_dao(building, room, capacity, occupied, class_id)
    logger.info(f"新增宿舍id={newid}")
    return newid


def update(dorm_id, data):
    if not get_by_id_dao(dorm_id):
        raise BizException("宿舍不存在")
    _check(data['class_id'], data['capacity'], data['occupied'])
    rowcount = update_dao(dorm_id, data)
    logger.info(f"修改宿舍id={dorm_id}")
    return rowcount


def delete(dorm_id: int):
    if not get_by_id_dao(dorm_id):
        raise BizException("宿舍不存在")
    rowcount = delete_dao(dorm_id)
    logger.info(f"删除宿舍id={dorm_id}")
    return rowcount
