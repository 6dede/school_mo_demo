from fastapi import APIRouter
from pydantic import BaseModel, Field

from org.zsy.common.response import ok
from org.zsy.user.service import login, register

router = APIRouter(prefix='/user', tags=['用户管理'])


class RegisterModel(BaseModel):
    username: str = Field(..., min_length=3, max_length=50, description='用户名')
    password: str = Field(..., min_length=6, max_length=64, description='密码')
    nickname: str = Field('', max_length=50, description='昵称')


class LoginModel(BaseModel):
    username: str = Field(..., min_length=1, max_length=50)
    password: str = Field(..., min_length=1, max_length=64)


@router.post('/register')
def register_api(data: RegisterModel):
    return ok(data=register(data.username, data.password, data.nickname), msg='注册成功')


@router.post('/login')
def login_api(data: LoginModel):
    return ok(data=login(data.username, data.password), msg='登录成功')
