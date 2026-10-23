from typing import Literal, Optional
from fastapi import APIRouter, Query
from pydantic import BaseModel, Field

from org.zsy.common.config import MAX_PAGE_SIZE
from org.zsy.common.response import ok
from org.zsy.payment.service import get_all, get_one, get_page, insert, update, delete
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix='/payment', tags=["缴费管理"])


@router.get("/")
def home():
    return {"message": "欢迎进入缴费管理模块"}


@router.get("/page")
def page(page: int = Query(1, gt=0), page_size: int = Query(10, gt=0, le=MAX_PAGE_SIZE),
         keyword: str = '', status: str = ''):
    return ok(data=get_page(page, page_size, keyword=keyword, status=status or None))


@router.get("/all")
def getAll(student_id: int = Query(None, gt=0)):
    return ok(data=get_all(student_id=student_id))


@router.get("/one")
def getOne(payment_id: int = Query(gt=0)):
    return ok(data=get_one(payment_id))


class paymentAdd(BaseModel):
    student_id: int = Field(..., gt=0, description="学生id")
    fee_type: str = Field(..., min_length=1, max_length=50, description="费用类型")
    amount: float = Field(..., gt=0, description="金额")
    status: Literal['未缴费', '已缴费'] = Field('未缴费', description="缴费状态")
    pay_date: Optional[str] = Field(None, pattern=r'^\d{4}-\d{2}-\d{2}$', description="缴费日期")


class paymentUpdate(paymentAdd):
    id: int


@router.post("/add")
def insertone(p: paymentAdd):
    newid = insert(p.student_id, p.fee_type, p.amount, p.status, p.pay_date)
    return ok(data={"id": newid}, msg="新增缴费记录成功")


@router.put("/update")
def update_one(p: paymentUpdate):
    data = p.model_dump(exclude_unset=True)
    data.pop('id', None)
    update(p.id, data)
    return ok(msg="修改缴费记录成功")


@router.delete("/delete")
def delete_one(payment_id: int = Query(gt=0)):
    rowcount = delete(payment_id)
    return ok(msg=f"删除{rowcount}条缴费记录{payment_id}成功")
