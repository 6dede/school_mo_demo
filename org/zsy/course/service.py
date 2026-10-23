import logging

from org.zsy.common.exception import BizException
from org.zsy.subject.dao import get_by_id_dao as get_subject_dao
from org.zsy.teacher.dao import get_by_id_dao as get_teacher_dao
from org.zsy.classroom.dao import get_by_id_dao as get_class_dao
from org.zsy.course.dao import (get_all_dao, get_by_id_dao, get_page_dao, insert_dao,
                                update_dao, delete_dao, count_refs_dao)

logger = logging.getLogger(__name__)


def _check_refs(subject_id, teacher_id, class_id):
    if not get_subject_dao(subject_id):
        raise BizException("学科不存在")
    if not get_teacher_dao(teacher_id):
        raise BizException("老师不存在")
    if not get_class_dao(class_id):
        raise BizException("班级不存在")


def get_all(class_id=None, teacher_id=None):
    return get_all_dao(class_id, teacher_id)


def get_page(page=1, page_size: int = 10, keyword='', class_id=None):
    rows, total = get_page_dao(page, page_size, keyword, class_id)
    logger.info(f"课程分页：第{page}页 每页{page_size}条 关键字={keyword} 共{total}条")
    return {"total": total, "page": page, "size": page_size, "rows": rows}


def get_one(course_id: int):
    row = get_by_id_dao(course_id)
    if not row:
        raise BizException("课程不存在")
    return row


def insert(name, subject_id, teacher_id, class_id, schedule_day, start_time, end_time):
    _check_refs(subject_id, teacher_id, class_id)
    newid = insert_dao(name, subject_id, teacher_id, class_id, schedule_day, start_time, end_time)
    logger.info(f"新增课程id={newid}")
    return newid


def update(course_id, data):
    if not get_by_id_dao(course_id):
        raise BizException("课程不存在")
    _check_refs(data['subject_id'], data['teacher_id'], data['class_id'])
    rowcount = update_dao(course_id, data)
    logger.info(f"修改课程id={course_id}")
    return rowcount


def delete(course_id: int):
    if not get_by_id_dao(course_id):
        raise BizException("课程不存在")
    refs = count_refs_dao(course_id)
    if refs['scores'] or refs['attendances']:
        raise BizException(
            f"该课程仍关联{refs['scores']}条成绩、{refs['attendances']}条考勤记录，请先处理关联数据")
    rowcount = delete_dao(course_id)
    logger.info(f"删除课程id={course_id}")
    return rowcount


def timetable(class_id: int):
    return get_all_dao(class_id=class_id)
