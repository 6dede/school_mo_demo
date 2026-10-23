import logging
from datetime import datetime

from org.zsy.common.exception import BizException
from org.zsy.student.dao import get_by_id_dao as get_student_dao
from org.zsy.payment.dao import get_all_dao, get_by_id_dao, get_page_dao, insert_dao, update_dao, delete_dao

logger = logging.getLogger(__name__)


def _check_student(student_id):
    if not get_student_dao(student_id):
        raise BizException("学生不存在")


def _normalize(data):
    if data.get('status') == '已缴费':
        if not data.get('pay_date'):
            data['pay_date'] = datetime.now().strftime('%Y-%m-%d')
    else:
        data['pay_date'] = None
    return data


def get_all(student_id=None):
    return get_all_dao(student_id)


def get_page(page=1, page_size: int = 10, keyword='', status=None):
    rows, total = get_page_dao(page, page_size, keyword, status)
    logger.info(f"缴费分页：第{page}页 每页{page_size}条 共{total}条")
    return {"total": total, "page": page, "size": page_size, "rows": rows}


def get_one(payment_id: int):
    row = get_by_id_dao(payment_id)
    if not row:
        raise BizException("缴费记录不存在")
    return row


def insert(student_id, fee_type, amount, status, pay_date=None):
    _check_student(student_id)
    data = _normalize({'status': status, 'pay_date': pay_date})
    newid = insert_dao(student_id, fee_type, amount, status, data['pay_date'])
    logger.info(f"新增缴费id={newid}")
    return newid


def update(payment_id, data):
    if not get_by_id_dao(payment_id):
        raise BizException("缴费记录不存在")
    _check_student(data['student_id'])
    rowcount = update_dao(payment_id, _normalize(data))
    logger.info(f"修改缴费id={payment_id}")
    return rowcount


def delete(payment_id: int):
    if not get_by_id_dao(payment_id):
        raise BizException("缴费记录不存在")
    rowcount = delete_dao(payment_id)
    logger.info(f"删除缴费id={payment_id}")
    return rowcount
