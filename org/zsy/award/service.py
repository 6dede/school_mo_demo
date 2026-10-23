import logging

from org.zsy.common.exception import BizException
from org.zsy.student.dao import get_by_id_dao as get_student_dao
from org.zsy.award.dao import get_all_dao, get_by_id_dao, get_page_dao, insert_dao, update_dao, delete_dao

logger = logging.getLogger(__name__)


def _check_student(student_id):
    if not get_student_dao(student_id):
        raise BizException("学生不存在")


def get_all(student_id=None):
    return get_all_dao(student_id)


def get_page(page=1, page_size: int = 10, keyword='', type=None):
    rows, total = get_page_dao(page, page_size, keyword, type)
    logger.info(f"奖惩分页：第{page}页 每页{page_size}条 共{total}条")
    return {"total": total, "page": page, "size": page_size, "rows": rows}


def get_one(award_id: int):
    row = get_by_id_dao(award_id)
    if not row:
        raise BizException("奖惩记录不存在")
    return row


def insert(student_id, type, title, reason, record_date):
    _check_student(student_id)
    newid = insert_dao(student_id, type, title, reason, record_date)
    logger.info(f"新增奖惩id={newid}")
    return newid


def update(award_id, data):
    if not get_by_id_dao(award_id):
        raise BizException("奖惩记录不存在")
    _check_student(data['student_id'])
    rowcount = update_dao(award_id, data)
    logger.info(f"修改奖惩id={award_id}")
    return rowcount


def delete(award_id: int):
    if not get_by_id_dao(award_id):
        raise BizException("奖惩记录不存在")
    rowcount = delete_dao(award_id)
    logger.info(f"删除奖惩id={award_id}")
    return rowcount
