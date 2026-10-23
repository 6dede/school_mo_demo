import logging

from org.zsy.common.config import MAX_PAGE_SIZE
from org.zsy.common.exception import BizException
from org.zsy.subject.dao import (get_all_dao, get_by_id_dao, get_page_dao, insert_dao,
                                 update_dao, delete_dao, count_course_dao)
from org.zsy.teacher.dao import get_all_dao as get_tea_dao, count_dao as count_tea_dao
logger=logging.getLogger(__name__)



def get_all(subject=''):
    '''获取所有学科信息'''
    res = get_all_dao()

    return res



def get_page(page=1, page_size: int = 10, keyword=''):
    pages = max(1, int(page))
    size = min(max(1, int(page_size)), MAX_PAGE_SIZE)
    rows, total = get_page_dao(page, page_size, keyword)
    logger.info(f"分页查询：第{page}页 每页{page_size}条 关键字={keyword} 共{total}条")
    return {"total": total, "page": page, "size": page_size, "rows": rows}


def sub_one(subject_id: int):
    sub = get_by_id_dao(subject_id)
    if not sub:
        raise BizException("学科不存在")
    tealist = get_tea_dao(sub["subject"]) or []
    sub["teacherList"] = tealist
    sub["count"] = len(tealist)
    logger.info(f"查询id={subject_id}的学科信息")
    return sub


def insert(subject):
    newid = insert_dao(subject)
    logger.info(f"新增学科id={newid}")
    return newid


def update(sub_id, subject):
    one = get_by_id_dao(sub_id)
    if one:
        rowcount = update_dao(sub_id, subject)
        logger.info(f"修改：id={sub_id}学科信息")
        return rowcount
    else:
        raise BizException("学科不存在")


def delete(sub_id: int):
    one = get_by_id_dao(sub_id)
    if one:
        if count_course_dao(sub_id):
            raise BizException("该学科仍有课程使用，无法删除")
        rowcount = delete_dao(sub_id)
        logger.info(f"删除：学科id={sub_id}")
        return rowcount
    else:
        raise BizException("学科不存在")
