import logging

from org.zsy.common.config import MAX_PAGE_SIZE
from org.zsy.common.exception import BizException
from org.zsy.classroom.dao import (get_all_dao, get_by_id_dao, get_page_dao, insert_dao,
                                   update_dao, delete_dao, count_refs_dao)

logger = logging.getLogger(__name__)


def get_all():
    '''获取所有班级信息'''
    res = get_all_dao()
    logger.info(f"查：{len(res)}条班级信息")
    return res


def get_page(page=1, page_size: int = 10, keyword=''):
    rows, total = get_page_dao(page, page_size, keyword)
    logger.info(f"分页查询：第{page}页 每页{page_size}条 关键字={keyword} 共{total}条")
    return {"total": total, "page": page, "size": page_size, "rows": rows}


def get_one(class_id: int):
    cls = get_by_id_dao(class_id)
    if not cls:
        raise BizException("班级不存在")
    logger.info(f"查询id={class_id}的班级信息")
    return cls


def insert(name, address):
    newid = insert_dao(name, address)
    logger.info(f"新增班级id={newid}")
    return newid


def update(class_id, name, address):
    one = get_by_id_dao(class_id)
    if not one:
        raise BizException("班级不存在")
    rowcount = update_dao(class_id, {"name": name, "address": address})
    logger.info(f"修改：id={class_id}班级信息")
    return rowcount


def delete(class_id: int):
    one = get_by_id_dao(class_id)
    if not one:
        raise BizException("班级不存在")
    refs = count_refs_dao(class_id)
    if refs['courses'] or refs['members'] or refs['dorms']:
        raise BizException(
            f"该班级仍关联{refs['courses']}门课程、{refs['members']}名学生、{refs['dorms']}间宿舍，请先处理关联数据")
    rowcount = delete_dao(class_id)
    logger.info(f"删除：班级id={class_id}")
    return rowcount
