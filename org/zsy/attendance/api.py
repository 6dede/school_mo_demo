from typing import Literal
from fastapi import APIRouter, Query
from pydantic import BaseModel, Field

from org.zsy.common.config import MAX_PAGE_SIZE
from org.zsy.common.response import ok
from org.zsy.attendance.service import get_all, get_one, get_page, insert, update, delete
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix='/attendance', tags=["考勤管理"])


@router.get("/")
def home():
    return {"message": "欢迎进入考勤管理模块"}


@router.get("/page")
def page(page: int = Query(1, gt=0), page_size: int = Query(10, gt=0, le=MAX_PAGE_SIZE),
         keyword: str = '', status: str = '', course_id: int = Query(None, gt=0)):
    return ok(data=get_page(page, page_size, keyword=keyword, status=status or None, course_id=course_id))


@router.get("/all")
def getAll(student_id: int = Query(None, gt=0), course_id: int = Query(None, gt=0)):
    return ok(data=get_all(student_id=student_id, course_id=course_id))


@router.get("/one")
def getOne(attendance_id: int = Query(gt=0)):
    return ok(data=get_one(attendance_id))


class attendanceAdd(BaseModel):
    student_id: int = Field(..., gt=0, description="学生id")
    course_id: int = Field(..., gt=0, description="课程id")
    status: Literal['正常', '迟到', '缺勤', '请假'] = Field(..., description="考勤状态")
    attendance_date: str = Field(..., pattern=r'^\d{4}-\d{2}-\d{2}$', description="考勤日期")
    remark: str = Field('', max_length=200, description="备注")


class attendanceUpdate(attendanceAdd):
    id: int


@router.post("/add")
def insertone(a: attendanceAdd):
    newid = insert(a.student_id, a.course_id, a.status, a.attendance_date, a.remark)
    return ok(data={"id": newid}, msg="新增考勤成功")


@router.put("/update")
def update_one(a: attendanceUpdate):
    data = a.model_dump(exclude_unset=True)
    data.pop('id', None)
    update(a.id, data)
    return ok(msg="修改考勤成功")


@router.delete("/delete")
def delete_one(attendance_id: int = Query(gt=0)):
    rowcount = delete(attendance_id)
    return ok(msg=f"删除{rowcount}条考勤{attendance_id}成功")
