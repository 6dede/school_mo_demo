import logging

from org.zsy.common.exception import BizException
from org.zsy.student.dao import get_by_id_dao as get_student_dao
from org.zsy.classroom.dao import get_by_id_dao as get_class_dao
from org.zsy.classmember.dao import (get_all_dao, get_by_id_dao, get_by_student_dao,
                                     get_page_dao, insert_dao, update_dao, delete_dao)

logger = logging.getLogger(__name__)


def _check_refs(class_id, student_id):
    if not get_class_dao(class_id):
        raise BizException("班级不存在")
    if not get_student_dao(student_id):
        raise BizException("学生不存在")


def get_all(class_id=None):
    return get_all_dao(class_id)


def get_page(page=1, page_size: int = 10, keyword='', class_id=None):
    rows, total = get_page_dao(page, page_size, keyword, class_id)
    logger.info(f"分班分页：第{page}页 每页{page_size}条 关键字={keyword} 共{total}条")
    return {"total": total, "page": page, "size": page_size, "rows": rows}


def get_one(member_id: int):
    row = get_by_id_dao(member_id)
    if not row:
        raise BizException("分班记录不存在")
    return row


def insert(class_id, student_id, join_date):
    _check_refs(class_id, student_id)
    existing = get_by_student_dao(student_id)
    if existing:
        raise BizException(f"该学生已分入{existing['class_name'] or '其他班级'}")
    newid = insert_dao(class_id, student_id, join_date)
    logger.info(f"新增分班记录id={newid}")
    return newid


def update(member_id, data):
    if not get_by_id_dao(member_id):
        raise BizException("分班记录不存在")
    _check_refs(data['class_id'], data['student_id'])
    existing = get_by_student_dao(data['student_id'])
    if existing and existing['id'] != member_id:
        raise BizException(f"该学生已分入{existing['class_name'] or '其他班级'}")
    rowcount = update_dao(member_id, data)
    logger.info(f"修改分班记录id={member_id}")
    return rowcount


def delete(member_id: int):
    if not get_by_id_dao(member_id):
        raise BizException("分班记录不存在")
    rowcount = delete_dao(member_id)
    logger.info(f"删除分班记录id={member_id}")
    return rowcount
