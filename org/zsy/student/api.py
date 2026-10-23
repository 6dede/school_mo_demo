from typing import Literal, Optional

from fastapi import APIRouter
from pydantic import BaseModel, Field

from org.zsy.common.config import MAX_PAGE_SIZE
from org.zsy.common.response import ok, fall

from org.zsy.student.service import get_all,stu_one,delete,update,insert,get_page
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix='/student', tags=["学生管理"])


@router.get("/")
def home():
    return {"message": "欢迎进入校务管理系统"}

@router.get("/page")
def page(page:int=1,page_size:int=10,keyword:str=''):
    if page <= 0:
        return fall("页码必须大于0")
    if page_size <= 0 or page_size > MAX_PAGE_SIZE:
        return fall(f"每页条数必须在1~{MAX_PAGE_SIZE}之间")

    return ok(data=get_page(page, page_size,keyword=keyword))


@router.get("/all")
def getAll():
    '''查，获取所有学生信息'''


    return ok(data=get_all())


@router.get("/one")
def stuOne(student_id: int):
    if student_id <= 0:
        return fall("参数缺失或异常，无法查询学生信息")
    else:


        return ok(data=stu_one(student_id))


class studentAdd(BaseModel):
    name: str = Field(..., min_length=1, max_length=50, description="学生姓名")  # 必填项 ，1-50字符数，参考数据库字段
    # gerder: str=Field(...,min_length=1,max_length=10,description="性别")
    gerder: str = Field(..., min_length=1, max_length=10, description="性别")
    age: int = Field(18, ge=0, le=150, description="学生年龄")  # 选填项
    teacher_id: int = Field(..., ge=0, description="任课老师id")  # 必填项，0《=自增，无上限
    #teacher_no: str = Field(..., pattern=r"^2024\d{4}$", description="任课老师id", examples="20240001")  # 必填，设置正则表达式
    # 选填的两种方式
    # grade: str=Field("高二",ge=0,le=150,description="所在年级")
    grade: str = Field(..., min_length=1, max_length=20, description="所在年级")
    enrollment_date: str


class studentUpdate(BaseModel):
    id: int
    name: Optional[str] = Field(None, min_length=1, max_length=50, description="学生姓名")
    gerder: Optional[str] = Field(None, min_length=1, max_length=10)
    age: Optional[int] = Field(None, ge=0, le=150, description="学生年龄")
    teacher_id: Optional[int] = Field(None, ge=0, description="任课老师id")
    grade: Optional[str] = Field(None, min_length=1, max_length=20)
    enrollment_date: Optional[str] = None


@router.post("/add")
def insertone(stu: studentAdd):

    newid = insert(stu.name, stu.gerder, stu.age, stu.teacher_id, stu.grade, stu.enrollment_date)
    return ok(data={"id": newid}, msg="新增学生信息成功")


@router.put("/update")
def update_one(stu: studentUpdate):
    data = stu.model_dump(exclude_unset=True)
    data.pop('id', None)
    update(stu.id, data)
    return ok(msg="修改信息成功")


@router.delete("/delete")
def delete_one(stu_id: int):
    if stu_id <= 0:
        return fall("参数缺失或异常，无法删除学生信息")

    rowcount = delete(stu_id)
    return ok(msg=f"删除{rowcount}个学生{stu_id}成功")
