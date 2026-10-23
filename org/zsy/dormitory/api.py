from fastapi import APIRouter, Query
from pydantic import BaseModel, Field

from org.zsy.common.config import MAX_PAGE_SIZE
from org.zsy.common.response import ok
from org.zsy.dormitory.service import get_all, get_one, get_page, insert, update, delete
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix='/dormitory', tags=["宿舍管理"])


@router.get("/")
def home():
    return {"message": "欢迎进入宿舍管理模块"}


@router.get("/page")
def page(page: int = Query(1, gt=0), page_size: int = Query(10, gt=0, le=MAX_PAGE_SIZE),
         keyword: str = '', class_id: int = Query(None, gt=0)):
    return ok(data=get_page(page, page_size, keyword=keyword, class_id=class_id))


@router.get("/all")
def getAll(class_id: int = Query(None, gt=0)):
    return ok(data=get_all(class_id=class_id))


@router.get("/one")
def getOne(dorm_id: int = Query(gt=0)):
    return ok(data=get_one(dorm_id))


class dormAdd(BaseModel):
    building: str = Field(..., min_length=1, max_length=50, description="宿舍楼")
    room: str = Field(..., min_length=1, max_length=20, description="房间号")
    capacity: int = Field(..., gt=0, description="床位容量")
    occupied: int = Field(0, ge=0, description="入住人数")
    class_id: int = Field(..., gt=0, description="所属班级id")


class dormUpdate(dormAdd):
    id: int


@router.post("/add")
def insertone(d: dormAdd):
    newid = insert(d.building, d.room, d.capacity, d.occupied, d.class_id)
    return ok(data={"id": newid}, msg="新增宿舍成功")


@router.put("/update")
def update_one(d: dormUpdate):
    data = d.model_dump(exclude_unset=True)
    data.pop('id', None)
    update(d.id, data)
    return ok(msg="修改宿舍成功")


@router.delete("/delete")
def delete_one(dorm_id: int = Query(gt=0)):
    rowcount = delete(dorm_id)
    return ok(msg=f"删除{rowcount}个宿舍{dorm_id}成功")
