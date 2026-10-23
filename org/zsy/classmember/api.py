from fastapi import APIRouter, Query
from pydantic import BaseModel, Field

from org.zsy.common.config import MAX_PAGE_SIZE
from org.zsy.common.response import ok
from org.zsy.classmember.service import get_all, get_one, get_page, insert, update, delete
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix='/classmember', tags=["分班管理"])


@router.get("/")
def home():
    return {"message": "欢迎进入分班管理模块"}


@router.get("/page")
def page(page: int = Query(1, gt=0), page_size: int = Query(10, gt=0, le=MAX_PAGE_SIZE),
         keyword: str = '', class_id: int = Query(None, gt=0)):
    return ok(data=get_page(page, page_size, keyword=keyword, class_id=class_id))


@router.get("/all")
def getAll(class_id: int = Query(None, gt=0)):
    return ok(data=get_all(class_id=class_id))


@router.get("/one")
def getOne(member_id: int = Query(gt=0)):
    return ok(data=get_one(member_id))


class memberAdd(BaseModel):
    class_id: int = Field(..., gt=0, description="班级id")
    student_id: int = Field(..., gt=0, description="学生id")
    join_date: str = Field(..., pattern=r'^\d{4}-\d{2}-\d{2}$', description="分班日期")


class memberUpdate(memberAdd):
    id: int


@router.post("/add")
def insertone(m: memberAdd):
    newid = insert(m.class_id, m.student_id, m.join_date)
    return ok(data={"id": newid}, msg="分班成功")


@router.put("/update")
def update_one(m: memberUpdate):
    data = m.model_dump(exclude_unset=True)
    data.pop('id', None)
    update(m.id, data)
    return ok(msg="修改分班信息成功")


@router.delete("/delete")
def delete_one(member_id: int = Query(gt=0)):
    rowcount = delete(member_id)
    return ok(msg=f"删除{rowcount}条分班记录{member_id}成功")
