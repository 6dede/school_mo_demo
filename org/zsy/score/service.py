import logging

from org.zsy.common.exception import BizException
from org.zsy.student.dao import get_by_id_dao as get_student_dao
from org.zsy.course.dao import get_by_id_dao as get_course_dao
from org.zsy.score.dao import get_all_dao, get_by_id_dao, get_page_dao, insert_dao, update_dao, delete_dao

logger = logging.getLogger(__name__)


def _check_refs(student_id, course_id):
    if not get_student_dao(student_id):
        raise BizException("学生不存在")
    if not get_course_dao(course_id):
        raise BizException("课程不存在")


def get_all(course_id=None, student_id=None):
    return get_all_dao(course_id, student_id)


def get_page(page=1, page_size: int = 10, keyword='', course_id=None):
    rows, total = get_page_dao(page, page_size, keyword, course_id)
    logger.info(f"成绩分页：第{page}页 每页{page_size}条 关键字={keyword} 共{total}条")
    return {"total": total, "page": page, "size": page_size, "rows": rows}


def get_one(score_id: int):
    row = get_by_id_dao(score_id)
    if not row:
        raise BizException("成绩记录不存在")
    return row


def insert(student_id, course_id, exam_name, score):
    _check_refs(student_id, course_id)
    newid = insert_dao(student_id, course_id, exam_name, score)
    logger.info(f"录入成绩id={newid}")
    return newid


def update(score_id, data):
    if not get_by_id_dao(score_id):
        raise BizException("成绩记录不存在")
    _check_refs(data['student_id'], data['course_id'])
    rowcount = update_dao(score_id, data)
    logger.info(f"修改成绩id={score_id}")
    return rowcount


def delete(score_id: int):
    if not get_by_id_dao(score_id):
        raise BizException("成绩记录不存在")
    rowcount = delete_dao(score_id)
    logger.info(f"删除成绩id={score_id}")
    return rowcount
