import logging

from org.zsy.common.exception import BizException
from org.zsy.notice.dao import get_all_dao, get_by_id_dao, get_page_dao, insert_dao, update_dao, delete_dao

logger = logging.getLogger(__name__)


def get_all(limit=20):
    return get_all_dao(limit)


def get_page(page=1, page_size: int = 10, keyword=''):
    rows, total = get_page_dao(page, page_size, keyword)
    logger.info(f"公告分页：第{page}页 每页{page_size}条 共{total}条")
    return {"total": total, "page": page, "size": page_size, "rows": rows}


def get_one(notice_id: int):
    row = get_by_id_dao(notice_id)
    if not row:
        raise BizException("公告不存在")
    return row


def insert(title, content, publisher):
    newid = insert_dao(title, content, publisher)
    logger.info(f"发布公告id={newid}")
    return newid


def update(notice_id, data):
    if not get_by_id_dao(notice_id):
        raise BizException("公告不存在")
    rowcount = update_dao(notice_id, data)
    logger.info(f"修改公告id={notice_id}")
    return rowcount


def delete(notice_id: int):
    if not get_by_id_dao(notice_id):
        raise BizException("公告不存在")
    rowcount = delete_dao(notice_id)
    logger.info(f"删除公告id={notice_id}")
    return rowcount
