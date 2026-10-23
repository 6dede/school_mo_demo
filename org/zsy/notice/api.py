from fastapi import APIRouter, Query
from pydantic import BaseModel, Field

from org.zsy.common.config import MAX_PAGE_SIZE
from org.zsy.common.response import ok
from org.zsy.notice.service import get_all, get_one, get_page, insert, update, delete
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix='/notice', tags=["公告管理"])


@router.get("/")
def home():
    return {"message": "欢迎进入公告管理模块"}


@router.get("/page")
def page(page: int = Query(1, gt=0), page_size: int = Query(10, gt=0, le=MAX_PAGE_SIZE), keyword: str = ''):
    return ok(data=get_page(page, page_size, keyword=keyword))


@router.get("/all")
def getAll():
    return ok(data=get_all())


@router.get("/one")
def getOne(notice_id: int = Query(gt=0)):
    return ok(data=get_one(notice_id))


class noticeAdd(BaseModel):
    title: str = Field(..., min_length=1, max_length=100, description="公告标题")
    content: str = Field(..., min_length=1, description="公告内容")
    publisher: str = Field('管理员', min_length=1, max_length=50, description="发布人")


class noticeUpdate(noticeAdd):
    id: int


@router.post("/add")
def insertone(n: noticeAdd):
    newid = insert(n.title, n.content, n.publisher)
    return ok(data={"id": newid}, msg="发布公告成功")


@router.put("/update")
def update_one(n: noticeUpdate):
    data = n.model_dump(exclude_unset=True)
    data.pop('id', None)
    update(n.id, data)
    return ok(msg="修改公告成功")


@router.delete("/delete")
def delete_one(notice_id: int = Query(gt=0)):
    rowcount = delete(notice_id)
    return ok(msg=f"删除{rowcount}条公告{notice_id}成功")
