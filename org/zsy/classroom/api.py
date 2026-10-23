from fastapi import APIRouter, Query
from pydantic import BaseModel, Field

from org.zsy.common.config import MAX_PAGE_SIZE
from org.zsy.common.response import ok
from org.zsy.classroom.service import get_all, get_one, delete, update, insert, get_page
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix='/classroom', tags=["班级管理"])


@router.get("/")
def home():
    return {"message": "欢迎进入班级管理模块"}


@router.get("/page")
def page(page: int = Query(1, gt=0), page_size: int = Query(10, gt=0, le=MAX_PAGE_SIZE), keyword: str = ''):
    return ok(data=get_page(page, page_size, keyword=keyword))


@router.get("/all")
def getAll():
    '''获取所有班级信息'''
    return ok(data=get_all())


@router.get("/one")
def getOne(class_id: int = Query(gt=0)):
    return ok(data=get_one(class_id))


class classAdd(BaseModel):
    name: str = Field(..., min_length=1, max_length=50, description="班级名称")  # 必填班级名称
    address: str = Field(..., min_length=1, max_length=200, description="班级地址")  # 必填班级地址


class classUpdate(BaseModel):
    id: int
    name: str = Field(..., min_length=1, max_length=50, description="班级名称")
    address: str = Field(..., min_length=1, max_length=200, description="班级地址")


@router.post("/add")
def insertone(cls: classAdd):
    newid = insert(cls.name, cls.address)
    return ok(data={"id": newid}, msg="新增班级信息成功")


@router.put("/update")
def update_one(cls: classUpdate):
    rowcount = update(cls.id, cls.name, cls.address)
    return ok(msg="修改班级信息成功")


@router.delete("/delete")
def delete_one(class_id: int = Query(gt=0)):
    rowcount = delete(class_id)
    return ok(msg=f"删除{rowcount}个班级{class_id}成功")
