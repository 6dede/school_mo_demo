import hashlib
import secrets

from org.zsy.common.basedao import execute, insert, queray_one


def ensure_table():
    '''初始化用户表，并写入默认管理员 admin/123456'''
    execute(
        """CREATE TABLE IF NOT EXISTS users (
            id INT AUTO_INCREMENT PRIMARY KEY,
            username VARCHAR(50) NOT NULL UNIQUE,
            password VARCHAR(255) NOT NULL,
            nickname VARCHAR(50) DEFAULT NULL,
            create_time DATETIME DEFAULT CURRENT_TIMESTAMP
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4"""
    )
    if not get_by_username('admin'):
        create_user('admin', '123456', '管理员')


def hash_password(password, salt=None):
    salt = salt or secrets.token_hex(8)
    digest = hashlib.pbkdf2_hmac(
        'sha256', password.encode('utf-8'), salt.encode('utf-8'), 100000
    ).hex()
    return f'{salt}${digest}'


def verify_password(password, stored):
    try:
        salt = stored.split('$', 1)[0]
    except (AttributeError, ValueError):
        return False
    return secrets.compare_digest(hash_password(password, salt), stored)


def get_by_username(username):
    return queray_one('select * from users where username=%s', username)


def create_user(username, password, nickname=''):
    sql = 'insert into users (username,password,nickname) values(%s,%s,%s)'
    return insert(sql, (username, hash_password(password), nickname or username))
