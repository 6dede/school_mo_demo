from fastapi import APIRouter, Query
from pydantic import BaseModel, Field

from org.zsy.common.config import MAX_PAGE_SIZE
from org.zsy.common.response import ok
from org.zsy.score.service import get_all, get_one, get_page, insert, update, delete
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix='/score', tags=["成绩管理"])


@router.get("/")
def home():
    return {"message": "欢迎进入成绩管理模块"}


@router.get("/page")
def page(page: int = Query(1, gt=0), page_size: int = Query(10, gt=0, le=MAX_PAGE_SIZE),
         keyword: str = '', course_id: int = Query(None, gt=0)):
    return ok(data=get_page(page, page_size, keyword=keyword, course_id=course_id))


@router.get("/all")
def getAll(course_id: int = Query(None, gt=0), student_id: int = Query(None, gt=0)):
    return ok(data=get_all(course_id=course_id, student_id=student_id))


@router.get("/one")
def getOne(score_id: int = Query(gt=0)):
    return ok(data=get_one(score_id))


class scoreAdd(BaseModel):
    student_id: int = Field(..., gt=0, description="学生id")
    course_id: int = Field(..., gt=0, description="课程id")
    exam_name: str = Field(..., min_length=1, max_length=50, description="考试名称")
    score: float = Field(..., ge=0, le=100, description="分数")


class scoreUpdate(scoreAdd):
    id: int


@router.post("/add")
def insertone(sc: scoreAdd):
    newid = insert(sc.student_id, sc.course_id, sc.exam_name, sc.score)
    return ok(data={"id": newid}, msg="录入成绩成功")


@router.put("/update")
def update_one(sc: scoreUpdate):
    data = sc.model_dump(exclude_unset=True)
    data.pop('id', None)
    update(sc.id, data)
    return ok(msg="修改成绩成功")


@router.delete("/delete")
def delete_one(score_id: int = Query(gt=0)):
    rowcount = delete(score_id)
    return ok(msg=f"删除{rowcount}条成绩{score_id}成功")
