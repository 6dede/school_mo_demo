'''统一初始化各业务模块数据表'''
from org.zsy.user.dao import ensure_table as ensure_user_table
from org.zsy.classroom.dao import ensure_table as ensure_class_table
from org.zsy.course.dao import ensure_table as ensure_course_table
from org.zsy.score.dao import ensure_table as ensure_score_table
from org.zsy.attendance.dao import ensure_table as ensure_attendance_table
from org.zsy.classmember.dao import ensure_table as ensure_member_table
from org.zsy.notice.dao import ensure_table as ensure_notice_table
from org.zsy.award.dao import ensure_table as ensure_award_table
from org.zsy.payment.dao import ensure_table as ensure_payment_table
from org.zsy.dormitory.dao import ensure_table as ensure_dormitory_table


def init_tables():
    for ensure in (
        ensure_user_table,
        ensure_class_table,
        ensure_course_table,
        ensure_score_table,
        ensure_attendance_table,
        ensure_member_table,
        ensure_notice_table,
        ensure_award_table,
        ensure_payment_table,
        ensure_dormitory_table,
    ):
        ensure()
