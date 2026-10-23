import logging

from org.zsy import teacher
from org.zsy.common.config import MAX_PAGE_SIZE
from org.zsy.common.exception import BizException
from org.zsy.student.dao import (get_all_dao, get_by_id_dao, get_page_dao, insert_dao,
                                  update_dao, delete_dao, count_refs_dao)
logger=logging.getLogger(__name__)
from org.zsy.teacher.dao import get_by_id_dao as get_teacher_dao


def get_all():
        '''查，获取所有学生信息'''

        res=get_all_dao()

        logger.info(f"查：{len(res)}条学生信息")
        return res


def get_page(page=1,page_size:int=10,keyword=''):
    pages=max(1,int(page))
    size=min(max(1,int(page_size)),MAX_PAGE_SIZE)
    rows,total=get_page_dao(page,page_size,keyword)
    logger.info(f"分页查：第{page}页 每页{page_size}条 关键字={keyword} 共{total}条")
    return {"total":total,"page":page,"size":page_size ,"rows":rows}

def stu_one(student_id: int):



            stu = get_by_id_dao(student_id)
            logger.info(f"查询到{student_id}条学生信息")
            if not stu:
                raise BizException("学生不存在")
            return stu

def insert(name,gerder,age,teacher_id,grade,enrollment_date):
        tea=get_teacher_dao(teacher_id)
        if tea:
            newid = insert_dao(name, gerder, age,teacher_id,grade, enrollment_date)

            logger.info(f"增加{newid}学生信息")
            return newid
        else:

            raise BizException(msg="老师不存在",code=1000)

def update(stu_id, data=None):

        one=get_by_id_dao(stu_id)
        if one:
            rowcount = update_dao(stu_id, data)

            logger.info(f"改：{stu_id}学生信息")
            return rowcount
        else:
            raise BizException("学生不存在")

def delete(stu_id: int):


        one=get_by_id_dao(stu_id)
        if one:
            refs = count_refs_dao(stu_id)
            if any(refs.values()):
                raise BizException(
                    f"该学生仍关联{refs['members']}条分班、{refs['scores']}条成绩、"
                    f"{refs['attendances']}条考勤、{refs['awards']}条奖惩、{refs['payments']}条缴费记录，请先处理关联数据")
            rowcount = delete_dao(stu_id)

            logger.info(f"删除：一个学生信息{stu_id}")
            return rowcount
        else:
            raise BizException("学生不存在")
