from org.zsy.common.basedao import queray_all, queray_one


def overview_dao():
    '''汇总各模块数据，供首页看板使用'''
    counts = {}
    for key, table in (
        ('students', 'students'), ('teachers', 'teachers'), ('subjects', 'subjects'),
        ('classes', 'classes'), ('courses', 'courses'), ('assignments', 'class_students'),
    ):
        counts[key] = queray_one(f"select count(*) as total from {table}")["total"]

    score_row = queray_one(
        "select count(*) as total, avg(score) as avg_score, "
        "ifnull(sum(case when score>=60 then 1 else 0 end),0) as pass_count from scores"
    )
    score_total = score_row['total']
    score_avg = round(float(score_row['avg_score']), 1) if score_row['avg_score'] is not None else 0
    pass_rate = round(float(score_row['pass_count']) / score_total * 100, 1) if score_total else 0

    attendance = {'正常': 0, '迟到': 0, '缺勤': 0, '请假': 0}
    for row in queray_all("select status, count(*) as total from attendance group by status"):
        attendance[row['status']] = row['total']
    attendance_total = sum(attendance.values())

    paid = queray_one("select ifnull(sum(amount),0) as amount from payments where status='已缴费'")['amount']
    unpaid = queray_one("select count(*) as total from payments where status='未缴费'")['total']

    awards = {'奖励': 0, '处分': 0}
    for row in queray_all("select type, count(*) as total from awards group by type"):
        awards[row['type']] = row['total']

    dorm = queray_one(
        "select ifnull(sum(capacity),0) as capacity, ifnull(sum(occupied),0) as occupied from dormitories"
    )

    class_dist = queray_all(
        """select cl.name, count(cs.id) as total
           from classes cl left join class_students cs on cs.class_id=cl.id
           group by cl.id, cl.name order by total desc, cl.id limit 5"""
    )

    notices = queray_all(
        "select id, title, publisher, publish_time from notices order by publish_time desc, id desc limit 10"
    )

    return {
        'counts': counts,
        'score': {'total': score_total, 'average': score_avg, 'pass_rate': pass_rate},
        'attendance': {'total': attendance_total, **attendance},
        'payment': {'paid_amount': float(paid), 'unpaid_count': unpaid},
        'awards': awards,
        'dormitory': {'capacity': dorm['capacity'], 'occupied': dorm['occupied']},
        'class_distribution': class_dist,
        'notices': notices,
    }
