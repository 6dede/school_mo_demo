import logging

from org.zsy.common.exception import BizException
from org.zsy.user.dao import create_user, get_by_username, verify_password

logger = logging.getLogger(__name__)


def register(username, password, nickname=''):
    username = (username or '').strip()
    nickname = (nickname or '').strip()
    if len(username) < 3:
        raise BizException('用户名至少 3 个字符')
    if len(password) < 6:
        raise BizException('密码至少 6 位')
    if get_by_username(username):
        raise BizException('用户名已存在', code=1001)

    user_id = create_user(username, password, nickname)
    logger.info(f'注册用户：{username}')
    return {'id': user_id, 'username': username, 'nickname': nickname or username}


def login(username, password):
    user = get_by_username((username or '').strip())
    if not user or not verify_password(password, user['password']):
        raise BizException('用户名或密码错误', code=1001)

    logger.info(f'用户登录：{user["username"]}')
    return {
        'id': user['id'],
        'username': user['username'],
        'nickname': user['nickname'] or user['username'],
    }
