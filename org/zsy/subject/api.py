from typing import Literal
from fastapi import APIRouter, Query
from pydantic import BaseModel, Field

from org.zsy.common.config import MAX_PAGE_SIZE
from org.zsy.common.response import ok
from org.zsy.subject.service import get_all, sub_one, delete, update, insert, get_page
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix='/subject', tags=["学科管理"])


@router.get("/")
def home():
    return {"message": "欢迎进入学科管理模块"}


@router.get("/page")
def page(page: int = Query(1, gt=0), page_size: int = Query(10, gt=0, le=MAX_PAGE_SIZE), keyword: str = ''):
    return ok(data=get_page(page, page_size, keyword=keyword))


@router.get("/all")
def getAll():
    '''获取所有学科信息'''
    return ok(data=get_all())


@router.get("/one")
def subOne(subject_id: int = Query(gt=0)):
    return ok(data=sub_one(subject_id))


class subjectAdd(BaseModel):
    subject: str = Field(..., min_length=1, max_length=50, description="学科名称")  # 必填学科名称


class subjectUpdate(BaseModel):
    id: int
    subject: str = Field(..., min_length=1, max_length=50, description="学科名称")


@router.post("/add")
def insertone(sub: subjectAdd):
    newid = insert(sub.subject)
    return ok(data={"id": newid}, msg="新增学科信息成功")


@router.put("/update")
def update_one(sub: subjectUpdate):
    rowcount = update(sub.id, sub.subject)
    return ok(msg="修改学科信息成功")


@router.delete("/delete")
def delete_one(sub_id: int = Query(gt=0)):
    rowcount = delete(sub_id)
    return ok(msg=f"删除{rowcount}个学科{sub_id}成功")
