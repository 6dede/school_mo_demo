from fastapi import APIRouter, Query
from pydantic import BaseModel, Field

from org.zsy.common.config import MAX_PAGE_SIZE
from org.zsy.common.response import ok
from org.zsy.course.service import get_all, get_one, get_page, insert, update, delete, timetable
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix='/course', tags=["课程与课表"])


@router.get("/")
def home():
    return {"message": "欢迎进入课程管理模块"}


@router.get("/page")
def page(page: int = Query(1, gt=0), page_size: int = Query(10, gt=0, le=MAX_PAGE_SIZE),
         keyword: str = '', class_id: int = Query(None, gt=0)):
    return ok(data=get_page(page, page_size, keyword=keyword, class_id=class_id))


@router.get("/all")
def getAll(class_id: int = Query(None, gt=0), teacher_id: int = Query(None, gt=0)):
    return ok(data=get_all(class_id=class_id, teacher_id=teacher_id))


@router.get("/one")
def getOne(course_id: int = Query(gt=0)):
    return ok(data=get_one(course_id))


@router.get("/timetable")
def getTimetable(class_id: int = Query(gt=0)):
    return ok(data=timetable(class_id))


class courseAdd(BaseModel):
    name: str = Field(..., min_length=1, max_length=50, description="课程名称")
    subject_id: int = Field(..., gt=0, description="学科id")
    teacher_id: int = Field(..., gt=0, description="老师id")
    class_id: int = Field(..., gt=0, description="班级id")
    schedule_day: str = Field(..., pattern=r'^周[一二三四五六日]$', description="上课星期")
    start_time: str = Field(..., pattern=r'^\d{2}:\d{2}$', description="开始时间")
    end_time: str = Field(..., pattern=r'^\d{2}:\d{2}$', description="结束时间")


class courseUpdate(courseAdd):
    id: int


@router.post("/add")
def insertone(course: courseAdd):
    newid = insert(course.name, course.subject_id, course.teacher_id, course.class_id,
                   course.schedule_day, course.start_time, course.end_time)
    return ok(data={"id": newid}, msg="新增课程成功")


@router.put("/update")
def update_one(course: courseUpdate):
    data = course.model_dump(exclude_unset=True)
    data.pop('id', None)
    update(course.id, data)
    return ok(msg="修改课程成功")


@router.delete("/delete")
def delete_one(course_id: int = Query(gt=0)):
    rowcount = delete(course_id)
    return ok(msg=f"删除{rowcount}个课程{course_id}成功")
