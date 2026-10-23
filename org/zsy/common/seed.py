'''
演示数据初始化：为所有业务表写入相互关联的数据

运行方式（项目根目录）：
    ./.venv/Scripts/python.exe -m org.zsy.common.seed

说明：
    1. 数据按“班级 -> 学生/分班 -> 课程 -> 成绩/考勤/奖惩/缴费”链路关联；
    2. 脚本可重复执行，检测到演示班级已存在时自动跳过；
    3. students_copy2 为历史备份表，同步写入 5 条快照数据。
'''
from datetime import date

import pymysql

from org.zsy.common.config import DB_CONFIG
from org.zsy.common.schema import init_tables
from org.zsy.user.dao import hash_password

SEED_CLASS = '高一（1）班'

CLASSES = [
    ('高一（1）班', '教学楼A101'),
    ('高一（2）班', '教学楼A102'),
    ('高二（1）班', '教学楼B201'),
    ('高二（2）班', '教学楼B202'),
    ('高三（1）班', '教学楼C301'),
]

NEW_SUBJECTS = ['英语', '化学', '生物', '历史', '地理']

TEACHERS = [
    ('陈静', '女', 32, '英语', '13800001001'),
    ('刘洋', '男', 29, '生物', '13800001002'),
    ('孙悦', '女', 35, '历史', '13800001003'),
    ('周涛', '男', 31, '地理', '13800001004'),
    ('吴敏', '女', 28, '化学', '13800001005'),
    ('郑凯', '男', 33, '音乐', '13800001006'),
]

# (姓名, 性别, 年龄, 班主任, 年级, 班级, 入学日期, 三门课成绩)
STUDENTS = [
    ('林晓', '女', 16, '陈静', '高一', '高一（1）班', '2026-09-01', [92, 88, 95]),
    ('张伟', '男', 16, '陈静', '高一', '高一（1）班', '2026-09-01', [78, 85, 90]),
    ('陈晨', '女', 16, '孙悦', '高一', '高一（2）班', '2026-09-01', [85, 91, 76]),
    ('周杰', '男', 16, '吴敏', '高一', '高一（2）班', '2026-09-01', [66, 72, 80]),
    ('王芳', '女', 17, '刘洋', '高二', '高二（1）班', '2025-09-01', [94, 89, 97]),
    ('李强', '男', 17, '刘洋', '高二', '高二（1）班', '2025-09-01', [58, 64, 71]),
    ('刘敏', '女', 17, '孙悦', '高二', '高二（2）班', '2025-09-01', [88, 93, 84]),
    ('吴静', '女', 17, '吴敏', '高二', '高二（2）班', '2025-09-01', [75, 81, 69]),
    ('赵磊', '男', 18, '周涛', '高三', '高三（1）班', '2024-09-01', [90, 86, 92]),
    ('孙雨', '女', 18, '周涛', '高三', '高三（1）班', '2024-09-01', [82, 79, 88]),
]

# (课程名, 学科, 任课老师, 班级, 星期, 开始, 结束)
COURSES = [
    ('语文', '语文', '张老师', '高一（1）班', '周一', '08:00', '09:40'),
    ('数学', '数学', '赵老师', '高一（1）班', '周二', '08:00', '09:40'),
    ('英语', '英语', '陈静', '高一（1）班', '周三', '10:00', '11:40'),
    ('数学', '数学', '赵老师', '高一（2）班', '周一', '08:00', '09:40'),
    ('英语', '英语', '陈静', '高一（2）班', '周二', '10:00', '11:40'),
    ('物理', '物理', '万老师', '高一（2）班', '周三', '08:00', '09:40'),
    ('语文', '语文', '张老师', '高二（1）班', '周一', '10:00', '11:40'),
    ('化学', '化学', '吴敏', '高二（1）班', '周二', '08:00', '09:40'),
    ('生物', '生物', '刘洋', '高二（1）班', '周四', '08:00', '09:40'),
    ('数学', '数学', '赵老师', '高二（2）班', '周一', '10:00', '11:40'),
    ('物理', '物理', '万老师', '高二（2）班', '周二', '08:00', '09:40'),
    ('历史', '历史', '孙悦', '高二（2）班', '周三', '08:00', '09:40'),
    ('语文', '语文', '张老师', '高三（1）班', '周一', '08:00', '09:40'),
    ('数学', '数学', '赵老师', '高三（1）班', '周二', '10:00', '11:40'),
    ('英语', '英语', '陈静', '高三（1）班', '周四', '08:00', '09:40'),
]

ATTENDANCE_PATTERNS = [
    ['正常', '正常', '正常'],
    ['正常', '迟到', '正常'],
    ['正常', '正常', '请假'],
    ['迟到', '正常', '正常'],
    ['正常', '缺勤', '正常'],
]

AWARDS = [
    ('林晓', '奖励', '三好学生', '期末综合评定优秀', '2026-09-30'),
    ('王芳', '奖励', '学习标兵', '月考年级前十', '2026-10-08'),
    ('赵磊', '奖励', '竞赛一等奖', '校数学竞赛第一名', '2026-09-25'),
    ('刘敏', '奖励', '优秀班干部', '班级工作突出', '2026-10-10'),
    ('孙雨', '奖励', '进步之星', '月考进步20名', '2026-10-15'),
    ('周杰', '奖励', '体育之星', '校运动会800米冠军', '2026-10-16'),
    ('张伟', '处分', '警告处分', '连续迟到三次', '2026-10-09'),
    ('李强', '处分', '通报批评', '上课纪律问题', '2026-10-11'),
]

NOTICES = [
    ('关于开展2026年秋季运动会的通知',
     '为全面贯彻党的教育方针，增强学生体质，丰富校园文化生活，经学校研究，定于2026年10月28日至30日举行秋季运动会。现将有关事项通知如下：\n'
     '一、比赛时间：10月28日至30日，每天上午8:00开始。\n'
     '二、比赛地点：学校田径场。\n'
     '三、参赛办法：以班级为单位报名，每班每项目限报2人，每人限报2项。\n'
     '四、请各班班主任于10月24日前将报名表交至体育组。\n'
     '请各班高度重视，认真组织训练，确保运动会安全有序进行。',
     '教务处', '2026-10-08 09:00:00'),
    ('期中考试安排通知',
     '根据学校教学工作计划，本学期期中考试定于11月5日至7日进行。现将考试安排通知如下：\n'
     '一、考试科目：语文、数学、英语、物理、化学、生物、历史、地理。\n'
     '二、考试时间：上午8:00至10:00，下午14:30至16:30。\n'
     '三、各年级组要统筹安排复习进度，不得提前结束课程。\n'
     '四、监考教师须提前15分钟到达考场，严格履行监考职责。\n'
     '请各班级做好考前动员，严肃考风考纪。',
     '教务处', '2026-10-12 10:30:00'),
    ('关于评选三好学生的通知',
     '为表彰先进、树立典型，促进学生德智体美劳全面发展，学校决定开展本学期三好学生评选工作。现将有关事项通知如下：\n'
     '一、评选条件：思想品德好、学习表现好、身体锻炼好，无违纪记录。\n'
     '二、评选比例：各班按班级人数的15%推荐。\n'
     '三、评选程序：学生自评、班级评议、年级审核、学校公示。\n'
     '四、请各班于10月25日前将推荐名单及相关材料报政教处。',
     '政教处', '2026-10-14 14:00:00'),
    ('校园安全教育活动安排',
     '为进一步增强全体师生安全防范意识，提高应急避险能力，学校定于本周五下午15:00开展消防疏散演练。现将有关安排通知如下：\n'
     '一、演练内容：火灾报警、紧急疏散、灭火器使用演示。\n'
     '二、演练地点：各教学楼及学校操场。\n'
     '三、各班班主任为本班疏散引导第一责任人，须全程跟班。\n'
     '四、演练期间请保持安静，按指定路线有序撤离，严禁拥挤推搡。',
     '保卫处', '2026-10-15 08:30:00'),
    ('图书馆新书上架公告',
     '为满足广大师生阅读需求，图书馆近期采购新书500册，涵盖文学、历史、科学、艺术等类别，现已完成编目上架。欢迎广大师生前来借阅。\n'
     '开放时间：周一至周五 8:30至17:30。\n'
     '借阅规则：每次限借2册，借期30天，可续借一次。',
     '图书馆', '2026-10-18 16:00:00'),
    ('冬季作息时间调整通知',
     '根据季节变化和学校工作实际，自2026年11月1日起，学校执行冬季作息时间。现将有关事项通知如下：\n'
     '一、上午上课时间调整为8:00，下午上课时间调整为14:30。\n'
     '二、各年级组要提前调整课表和值班安排。\n'
     '三、班主任要及时通知学生和家长，做好作息衔接。\n'
     '四、后勤部门要保障供暖和照明正常运行。',
     '校办公室', '2026-10-20 11:00:00'),
]

DORMITORIES = [
    ('1号楼', '101', 6, 2, '高一（1）班'),
    ('1号楼', '102', 6, 2, '高一（2）班'),
    ('2号楼', '201', 4, 2, '高二（1）班'),
    ('2号楼', '202', 4, 2, '高二（2）班'),
    ('3号楼', '301', 6, 2, '高三（1）班'),
    ('3号楼', '302', 6, 0, '高三（1）班'),
]

USERS = [
    ('jiaowu', '123456', '教务主任'),
    ('zhengjiao', '123456', '政教主任'),
    ('houqin', '123456', '后勤主管'),
    ('teacher01', '123456', '陈静老师'),
]


def _insert(cur, sql, args):
    cur.execute(sql, args)
    return cur.lastrowid


def seed_demo_data():
    init_tables()

    conn = pymysql.connect(**DB_CONFIG)
    try:
        with conn.cursor() as cur:
            cur.execute('select id from classes where name=%s', (SEED_CLASS,))
            if cur.fetchone():
                print('演示数据已存在，跳过初始化')
                return False

            # 1. 班级
            class_ids = {}
            for name, address in CLASSES:
                class_ids[name] = _insert(
                    cur, 'insert into classes (name, address) values(%s, %s)', (name, address))

            # 2. 学科（复用已有学科）
            subject_ids = {}
            cur.execute('select id, subject from subjects order by id')
            for row in cur.fetchall():
                subject_ids.setdefault(row['subject'], row['id'])
            for name in NEW_SUBJECTS:
                if name not in subject_ids:
                    subject_ids[name] = _insert(
                        cur, 'insert into subjects (subject) values(%s)', (name,))

            # 3. 老师（复用已有老师）
            teacher_ids = {}
            cur.execute('select id, name from teachers order by id')
            for row in cur.fetchall():
                teacher_ids.setdefault(row['name'], row['id'])
            for name, gerder, age, subject, phone in TEACHERS:
                if name not in teacher_ids:
                    teacher_ids[name] = _insert(
                        cur,
                        'insert into teachers (name, gerder, age, subject, phone) values(%s,%s,%s,%s,%s)',
                        (name, gerder, age, subject, phone))

            # 4. 学生 + 分班
            student_ids = {}
            for name, gerder, age, teacher_name, grade, class_name, enroll, _score in STUDENTS:
                student_ids[name] = _insert(
                    cur,
                    'insert into students (name, gerder, age, teacher_id, grade, enrollment_date) '
                    'values(%s,%s,%s,%s,%s,%s)',
                    (name, gerder, age, teacher_ids[teacher_name], grade, enroll))
                _insert(
                    cur,
                    'insert into class_students (class_id, student_id, join_date) values(%s,%s,%s)',
                    (class_ids[class_name], student_ids[name], enroll))

            # 5. 课程（课表中心按班级读取）
            class_courses = {}
            for name, subject_name, teacher_name, class_name, day, start, end in COURSES:
                course_id = _insert(
                    cur,
                    'insert into courses (name, subject_id, teacher_id, class_id, schedule_day, '
                    'start_time, end_time) values(%s,%s,%s,%s,%s,%s,%s)',
                    (name, subject_ids[subject_name], teacher_ids[teacher_name],
                     class_ids[class_name], day, start, end))
                class_courses.setdefault(class_name, []).append(course_id)

            # 6. 成绩 + 考勤（依赖学生与课程）
            for index, (name, _g, _a, _t, _grade, class_name, _e, scores) in enumerate(STUDENTS):
                for course_id, score in zip(class_courses[class_name], scores):
                    _insert(
                        cur,
                        'insert into scores (student_id, course_id, exam_name, score) '
                        'values(%s,%s,%s,%s)',
                        (student_ids[name], course_id, '第一次月考', score))

                pattern = ATTENDANCE_PATTERNS[index % len(ATTENDANCE_PATTERNS)]
                for offset, course_id in enumerate(class_courses[class_name]):
                    status = pattern[offset]
                    remark = ''
                    if status == '迟到':
                        remark = '迟到10分钟'
                    elif status == '缺勤':
                        remark = '未请假缺勤'
                    elif status == '请假':
                        remark = '病假'
                    _insert(
                        cur,
                        'insert into attendance (student_id, course_id, status, attendance_date, remark) '
                        'values(%s,%s,%s,%s,%s)',
                        (student_ids[name], course_id, status,
                         date(2026, 10, 12 + offset * 2), remark))

            # 7. 奖惩
            for name, award_type, title, reason, record_date in AWARDS:
                _insert(
                    cur,
                    'insert into awards (student_id, type, title, reason, record_date) '
                    'values(%s,%s,%s,%s,%s)',
                    (student_ids[name], award_type, title, reason, record_date))

            # 8. 缴费（每名学生：学费已缴 + 住宿费部分未缴）
            for index, student in enumerate(STUDENTS):
                name = student[0]
                _insert(
                    cur,
                    'insert into payments (student_id, fee_type, amount, status, pay_date) '
                    'values(%s,%s,%s,%s,%s)',
                    (student_ids[name], '学费（2026秋季）', 1200.00, '已缴费', '2026-09-05'))
                if index % 2 == 0:
                    _insert(
                        cur,
                        'insert into payments (student_id, fee_type, amount, status, pay_date) '
                        'values(%s,%s,%s,%s,%s)',
                        (student_ids[name], '住宿费（2026秋季）', 400.00, '已缴费', '2026-09-06'))
                else:
                    _insert(
                        cur,
                        'insert into payments (student_id, fee_type, amount, status, pay_date) '
                        'values(%s,%s,%s,%s,%s)',
                        (student_ids[name], '住宿费（2026秋季）', 400.00, '未缴费', None))

            # 9. 公告
            for title, content, publisher, publish_time in NOTICES:
                _insert(
                    cur,
                    'insert into notices (title, content, publisher, publish_time) '
                    'values(%s,%s,%s,%s)',
                    (title, content, publisher, publish_time))

            # 10. 宿舍
            for building, room, capacity, occupied, class_name in DORMITORIES:
                _insert(
                    cur,
                    'insert into dormitories (building, room, capacity, occupied, class_id) '
                    'values(%s,%s,%s,%s,%s)',
                    (building, room, capacity, occupied, class_ids[class_name]))

            # 11. 系统用户
            for username, password, nickname in USERS:
                cur.execute('select id from users where username=%s', (username,))
                if not cur.fetchone():
                    _insert(
                        cur,
                        'insert into users (username, password, nickname) values(%s,%s,%s)',
                        (username, hash_password(password), nickname))

            # 12. 历史备份表：写入 5 条学生快照
            cur.execute(
                'insert into students_copy2 (name, gerder, age, teacher_id, grade, enrollment_date) '
                'select name, gerder, age, teacher_id, grade, enrollment_date '
                'from students where id in (%s,%s,%s,%s,%s)',
                tuple(student_ids[name] for name in list(student_ids)[:5]))

        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()

    print('演示数据初始化完成：')
    print('  班级 %d 个、学科 %d 个、老师 %d 人、学生 %d 人、分班 %d 条'
          % (len(CLASSES), len(NEW_SUBJECTS), len(TEACHERS), len(STUDENTS), len(STUDENTS)))
    print('  课程 %d 门、成绩 %d 条、考勤 %d 条、奖惩 %d 条'
          % (len(COURSES), len(STUDENTS) * 3, len(STUDENTS) * 3, len(AWARDS)))
    print('  缴费 %d 条、公告 %d 条、宿舍 %d 间、用户 %d 个'
          % (len(STUDENTS) * 2, len(NOTICES), len(DORMITORIES), len(USERS)))
    return True


if __name__ == '__main__':
    seed_demo_data()
