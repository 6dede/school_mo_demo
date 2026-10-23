import logging

from org.zsy.common.exception import BizException
from org.zsy.student.dao import get_by_id_dao as get_student_dao
from org.zsy.course.dao import get_by_id_dao as get_course_dao
from org.zsy.attendance.dao import get_all_dao, get_by_id_dao, get_page_dao, insert_dao, update_dao, delete_dao

logger = logging.getLogger(__name__)
STATUSES = ('正常', '迟到', '缺勤', '请假')


def _check_refs(student_id, course_id, status):
    if not get_student_dao(student_id):
        raise BizException("学生不存在")
    if not get_course_dao(course_id):
        raise BizException("课程不存在")
    if status not in STATUSES:
        raise BizException("考勤状态不正确")


def get_all(student_id=None, course_id=None):
    return get_all_dao(student_id, course_id)


def get_page(page=1, page_size: int = 10, keyword='', status=None, course_id=None):
    rows, total = get_page_dao(page, page_size, keyword, status, course_id)
    logger.info(f"考勤分页：第{page}页 每页{page_size}条 关键字={keyword} 共{total}条")
    return {"total": total, "page": page, "size": page_size, "rows": rows}


def get_one(attendance_id: int):
    row = get_by_id_dao(attendance_id)
    if not row:
        raise BizException("考勤记录不存在")
    return row


def insert(student_id, course_id, status, attendance_date, remark=''):
    _check_refs(student_id, course_id, status)
    newid = insert_dao(student_id, course_id, status, attendance_date, remark)
    logger.info(f"新增考勤id={newid}")
    return newid


def update(attendance_id, data):
    if not get_by_id_dao(attendance_id):
        raise BizException("考勤记录不存在")
    _check_refs(data['student_id'], data['course_id'], data['status'])
    rowcount = update_dao(attendance_id, data)
    logger.info(f"修改考勤id={attendance_id}")
    return rowcount


def delete(attendance_id: int):
    if not get_by_id_dao(attendance_id):
        raise BizException("考勤记录不存在")
    rowcount = delete_dao(attendance_id)
    logger.info(f"删除考勤id={attendance_id}")
    return rowcount
