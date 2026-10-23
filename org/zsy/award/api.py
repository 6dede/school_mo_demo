from typing import Literal
from fastapi import APIRouter, Query
from pydantic import BaseModel, Field

from org.zsy.common.config import MAX_PAGE_SIZE
from org.zsy.common.response import ok
from org.zsy.award.service import get_all, get_one, get_page, insert, update, delete
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix='/award', tags=["奖惩管理"])


@router.get("/")
def home():
    return {"message": "欢迎进入奖惩管理模块"}


@router.get("/page")
def page(page: int = Query(1, gt=0), page_size: int = Query(10, gt=0, le=MAX_PAGE_SIZE),
         keyword: str = '', type: str = ''):
    return ok(data=get_page(page, page_size, keyword=keyword, type=type or None))


@router.get("/all")
def getAll(student_id: int = Query(None, gt=0)):
    return ok(data=get_all(student_id=student_id))


@router.get("/one")
def getOne(award_id: int = Query(gt=0)):
    return ok(data=get_one(award_id))


class awardAdd(BaseModel):
    student_id: int = Field(..., gt=0, description="学生id")
    type: Literal['奖励', '处分'] = Field(..., description="类型")
    title: str = Field(..., min_length=1, max_length=100, description="奖惩标题")
    reason: str = Field('', max_length=200, description="原因")
    record_date: str = Field(..., pattern=r'^\d{4}-\d{2}-\d{2}$', description="记录日期")


class awardUpdate(awardAdd):
    id: int


@router.post("/add")
def insertone(a: awardAdd):
    newid = insert(a.student_id, a.type, a.title, a.reason, a.record_date)
    return ok(data={"id": newid}, msg="新增奖惩成功")


@router.put("/update")
def update_one(a: awardUpdate):
    data = a.model_dump(exclude_unset=True)
    data.pop('id', None)
    update(a.id, data)
    return ok(msg="修改奖惩成功")


@router.delete("/delete")
def delete_one(award_id: int = Query(gt=0)):
    rowcount = delete(award_id)
    return ok(msg=f"删除{rowcount}条奖惩记录{award_id}成功")
