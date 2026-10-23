from typing import Literal, Optional

from fastapi import APIRouter
from pydantic import BaseModel, Field
from org.zsy.common.response import ok,fall

import logging
from org.zsy.teacher.service import delete,update,insert,tea_one,get_all,teacher_page
router=APIRouter(prefix="/teacher",tags=["老师管理"])
logger=logging.getLogger(__name__)


@router.get("/")
def home():
    return {"message":"欢迎进入教师管理系统"}
@router.get("/all")
def get_all_api():
    '''查，获取所有教师信息'''

    return ok(data=get_all())
@router.get("/page")
def get_page_api(page:int=1,page_size:int=10,keyword:str=''):
    return ok(data=teacher_page(page,page_size,keyword))

@router.get("/one")
def tea_one_api(tea_id:int):

    res=tea_one(tea_id)
    if res:
        logger.info("查询成功")
        return ok(data=res)
    else:
        return fall("未查询到")

class teacherAdd(BaseModel):
    name:str=Field(...,min_length=1,max_length=50,description="老师姓名")
    gerder:str=Field(...,min_length=1,max_length=10,description="性别")
    age:int=Field(18,ge=0,le=150,description="老师年龄")
    subject:str=Field(...,min_length=1,max_length=50,description="任教学科")
    phone:str=Field(..., pattern=r"^\d{9,11}$", description="电话号码",)

class teacherUpdate(BaseModel):
    id:int
    name:Optional[str]=Field(None,min_length=1,max_length=50,description="老师姓名")
    gerder:Optional[str]=Field(None,min_length=1,max_length=10)
    age:Optional[int]=Field(None,ge=0,le=150,description="老师年龄")
    subject:Optional[str]=Field(None,min_length=1,max_length=50)
    phone:Optional[str]=Field(None, pattern=r"^\d{9,11}$", description="电话号码")

@router.post("/add")
def insert_api(tea:teacherAdd):

    return ok(data=insert(tea.name,tea.gerder,tea.age,tea.subject,tea.phone))

@router.put("/update")
def update_api(stu:teacherUpdate):
    data = stu.model_dump(exclude_unset=True)
    data.pop('id', None)
    return ok(data=update(stu.id, data), msg="更新成功")

@router.delete("/delete")
def delete_api(tea_id:int):
    return ok(data=delete(tea_id), msg="删除成功")

