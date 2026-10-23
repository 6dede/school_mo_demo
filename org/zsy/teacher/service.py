import logging

from org.zsy.common.exception import BizException
from org.zsy.teacher.dao import delete_dao,update_dao,insert_dao,get_by_id_dao,get_page_dao,count_course_dao
from org.zsy.teacher.dao import get_all_dao as get_teachers_dao
logger=logging.getLogger(__name__)
from org.zsy.student.dao import get_all_dao as get_students_dao


def get_all():
        '''查，获取所有老师信息'''

        res=get_teachers_dao()

        logger.info(f"查：{len(res)}条老师信息")
        return res

def tea_one(tea_id: int):



            tea = get_by_id_dao(tea_id)
            if tea:
                tea["student_list"]=get_students_dao(tea_id)
            logger.info(f"查询到{tea_id}条老师信息")
            return tea
def teacher_page(page:int,page_size:int,keyword:str):
    rows,total=get_page_dao(page,page_size,keyword)
    logger.info(f"分页查询：第{page}页 每页{page_size}条 关键字={keyword} 共{total}条")
    return {"total":total,"page":page,"size":page_size,"rows":rows}

def insert(name,gerder,age,subject,phone):

        newid = insert_dao(name,gerder,age,subject,phone)

        logger.info(f"增加{newid}老师信息")
        return newid

def update(tea_id, data=None):

        one=get_by_id_dao(tea_id)
        if one:
            rowcount = update_dao(tea_id, data)

            logger.info(f"改：{tea_id}老师信息")
            return rowcount
        else:
            raise BizException(msg="老师不存在",code=1000)

def delete(tea_id: int):


        one=get_by_id_dao(tea_id)
        if one:
            if get_students_dao(tea_id):
                raise BizException(msg="该老师名下还有学生，无法删除",code=1000)
            if count_course_dao(tea_id):
                raise BizException(msg="该老师仍有课程安排，无法删除",code=1000)
            rowcount = delete_dao(tea_id)

            logger.info(f"删除：一个老师信息{tea_id}")
            return rowcount
        else:
            raise BizException(msg="老师不存在",code=1000)
