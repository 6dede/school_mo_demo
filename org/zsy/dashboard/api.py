from fastapi import APIRouter

from org.zsy.common.response import ok
from org.zsy.dashboard.service import overview

router = APIRouter(prefix='/dashboard', tags=["首页看板"])


@router.get("/overview")
def get_overview():
    return ok(data=overview())
