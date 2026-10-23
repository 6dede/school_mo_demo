# 校务管理系统（教务管理模块）项目文档

> 代码范围：`org/`（后端）、`static/`（前端）

## 1. 项目概述

基于 **FastAPI + MySQL + Bootstrap 5** 的校务管理系统，包含用户认证、首页数据看板及 12 个业务管理模块：学生、老师、学科、班级、课程与课表、分班、成绩、考勤、奖惩、公告、缴费、宿舍。

- 后端采用 `api → service → dao` 分层，统一响应与全局异常处理。
- 前端为原生 JavaScript（IIFE）+ Bootstrap 5，侧边栏 + iframe 后台布局。
- 启动时自动建表，可通过种子脚本生成相互关联的演示数据。

**技术栈**

| 层次 | 技术 |
|---|---|
| Web 框架 | FastAPI、Uvicorn、Pydantic v2 |
| 数据访问 | PyMySQL、DBUtils PooledDB、DictCursor |
| 数据库 | MySQL（库名 `schaool_db_study`，utf8mb4） |
| 前端 | HTML5、Bootstrap 5、bootstrap-icons、原生 JS |
| 登录态 | 浏览器 `sessionStorage`（教学演示，非 JWT） |
| 密码存储 | PBKDF2-SHA256 + 随机盐，格式 `salt$digest` |

## 2. 目录结构

```text
py-104/
├── org/zsy/
│   ├── main.py                 # 入口、路由注册、静态资源挂载、全局异常
│   ├── common/
│   │   ├── config.py           # 数据库配置、日志、分页上限
│   │   ├── pool.py             # DBUtils 连接池
│   │   ├── basedao.py          # query_all/query_one/insert/execute
│   │   ├── response.py         # ok()/fall() 统一响应
│   │   ├── exception.py        # BizException 业务异常
│   │   ├── schema.py           # 统一初始化数据表
│   │   └── seed.py             # 演示数据脚本
│   ├── user/  student/  teacher/  subject/  classroom/
│   ├── course/  classmember/  score/  attendance/
│   ├── award/  notice/  payment/  dormitory/  dashboard/
└── static/
    ├── html/                   # 登录、注册、后台框架、业务页面
    ├── js/                     # common.js + 各模块脚本
    └── css/                    # admin.css、Bootstrap、图标库
```

每个业务模块固定包含：`__init__.py`、`dao.py`（建表与 SQL）、`service.py`（校验与业务逻辑）、`api.py`（路由与 Pydantic 校验）。

## 3. 系统架构

### 3.1 请求流程

```text
浏览器 → api.py（参数校验）→ service.py（业务校验 / BizException）
       → dao.py（参数化 SQL）→ basedao.py → 连接池 → MySQL
       → ok(data) / fall(msg) → {code, msg, data}
```

### 3.2 统一响应

```json
{ "code": 0, "msg": "success", "data": {} }
```

- `code = 0` 成功；`code = 1` 通用失败；`1000/1001` 业务异常。
- 参数校验错误和系统异常同样返回 HTTP 200，通过 `code/msg` 区分。
- 分页数据统一为 `{ total, page, size, rows }`。

### 3.3 数据层

- `basedao.py` 提供 `queray_all`、`queray_one`、`insert`、`execute`，全部参数化 SQL。
- `pool.py` 连接池：mincached/maxcached=5、maxconnections=10、自动探活。
- `common/schema.py::init_tables()` 在启动时调用各模块 `ensure_table()` 自动建表。
- 表间**无物理外键**，关联完整性由 service 层校验与删除保护保证。

### 3.4 跨模块联动

- 课程关联班级、学科、老师；课表中心按班级读取课程。
- 分班表连接学生与班级；成绩、考勤、奖惩、缴费通过学生关联班级。
- 首页看板实时聚合全部业务表。
- 列表接口通过 `LEFT JOIN` 输出 `student_name / class_name / course_name / teacher_name / subject_name`。
- 修改班级或学生姓名后，相关模块列表同步显示新名称。

### 3.5 删除保护

| 删除对象 | 拦截条件 |
|---|---|
| 班级 | 仍有关联课程、分班学生或宿舍 |
| 学生 | 仍有分班、成绩、考勤、奖惩或缴费记录 |
| 老师 | 名下仍有学生或课程 |
| 学科 | 仍被课程使用 |
| 课程 | 仍有成绩或考勤记录 |

## 4. 数据库设计

| 表名 | 说明 | 关键字段 |
|---|---|---|
| `users` | 系统用户 | id, username(唯一), password, nickname, create_time |
| `students` | 学生 | id, name, gerder, age, teacher_id(班主任), grade, enrollment_date, create_time, email |
| `teachers` | 老师 | id, name, gerder, age, subject, phone, create_time |
| `subjects` | 学科 | id, subject |
| `classes` | 班级 | id, name, address, create_time |
| `courses` | 课程 | id, name, subject_id, teacher_id, class_id, schedule_day, start_time, end_time, create_time |
| `class_students` | 分班记录 | id, class_id, student_id(唯一), join_date, create_time |
| `scores` | 成绩 | id, student_id, course_id, exam_name, score(0-100), create_time |
| `attendance` | 考勤 | id, student_id, course_id, status, attendance_date, remark, create_time |
| `awards` | 奖惩 | id, student_id, type, title, reason, record_date, create_time |
| `payments` | 缴费 | id, student_id, fee_type, amount, status, pay_date, create_time |
| `dormitories` | 宿舍 | id, building, room, capacity, occupied, class_id, create_time |
| `notices` | 公告 | id, title, content, publisher, publish_time |
| `students_copy2` | 历史备份表 | 结构与 `students` 一致，业务未使用 |

逻辑关系：

```text
teachers 1 ──< students（班主任）
classes  1 ──< class_students >── 1 students
classes  1 ──< courses >── 1 subjects
                    └── 1 teachers
students 1 ──< scores / attendance / awards / payments
courses  1 ──< scores / attendance
classes  1 ──< dormitories
```

## 5. 功能模块

### 5.1 用户认证

| 方法 | 路径 | 说明 |
|---|---|---|
| POST | `/user/register` | 注册：username(≥3)、password(≥6)、nickname |
| POST | `/user/login` | 登录，返回 `{id, username, nickname}` |

默认管理员 `admin / 123456`；演示账号 `jiaowu`、`zhengjiao`、`houqin`、`teacher01`，密码均为 `123456`。

### 5.2 业务模块

| 模块 | 前缀 | 分页筛选参数 | 删除参数 | 特殊接口 |
|---|---|---|---|---|
| 学生 | `/student` | `keyword` | `stu_id` | — |
| 老师 | `/teacher` | `keyword` | `tea_id` | — |
| 学科 | `/subject` | `keyword` | `sub_id` | — |
| 班级 | `/classroom` | `keyword` | `class_id` | — |
| 课程 | `/course` | `keyword, class_id` | `course_id` | `GET /course/timetable?class_id` |
| 分班 | `/classmember` | `keyword, class_id` | `member_id` | — |
| 成绩 | `/score` | `keyword, course_id` | `score_id` | `GET /score/all?student_id&course_id` |
| 考勤 | `/attendance` | `keyword, status, course_id` | `attendance_id` | `GET /attendance/all?student_id&course_id` |
| 奖惩 | `/award` | `keyword, type` | `award_id` | `GET /award/all?student_id` |
| 公告 | `/notice` | `keyword` | `notice_id` | — |
| 缴费 | `/payment` | `keyword, status` | `payment_id` | `GET /payment/all?student_id` |
| 宿舍 | `/dormitory` | `keyword, class_id` | `dorm_id` | `GET /dormitory/all?class_id` |

每个模块均提供：`GET /page`、`GET /all`、`GET /one`、`POST /add`、`PUT /update`、`DELETE /delete`。分页参数为 `page`、`page_size`（最大 100）。

示例：

```text
GET    /classroom/page?page=1&page_size=10&keyword=高一
GET    /classroom/all
GET    /classroom/one?class_id=1
POST   /classroom/add        {"name":"高一（1）班","address":"教学楼A101"}
PUT    /classroom/update     {"id":1,"name":"高一（1）班","address":"教学楼A101"}
DELETE /classroom/delete?class_id=1
```

### 5.3 首页看板

`GET /dashboard/overview` 返回：

| 字段 | 内容 |
|---|---|
| `counts` | 学生、老师、学科、班级、课程、已分班人数 |
| `score` | 成绩总数、平均分、及格率 |
| `attendance` | 总数及正常/迟到/缺勤/请假数量 |
| `payment` | 已缴金额、待缴笔数 |
| `awards` | 奖励/处分数量 |
| `dormitory` | 床位总数、已入住数 |
| `class_distribution` | 班级人数 Top 5 |
| `notices` | 最新 10 条公告 |

首页公告支持点击弹窗查看全文，正文按标准学校通知排版；公告列表可滚动。

## 6. 前端说明

### 6.1 页面清单

| 页面 | 脚本 | 说明 |
|---|---|---|
| `html/login.html` | `login.js` | 登录 |
| `html/register.html` | `register.js` | 注册 |
| `html/index.html` | `index.js` | 后台框架：侧边栏、面包屑、iframe |
| `html/welcome.html` | `welcome.js` | 数据看板、公告弹窗、快捷入口 |
| `html/student/list.html` | `student.js` | 学生管理 |
| `html/teacher/list.html` | `teacher.js` | 老师管理 |
| `html/subject/list.html` | `subject.js` | 学科管理 |
| `html/classroom/list.html` | `classroom.js` | 班级管理 |
| `html/course/list.html` | `course.js` | 课程管理 |
| `html/timetable/list.html` | `timetable.js` | 课表中心 |
| `html/classmember/list.html` | `classmember.js` | 分班管理 |
| `html/score/list.html` | `score.js` | 成绩管理 |
| `html/attendance/list.html` | `attendance.js` | 考勤管理 |
| `html/award/list.html` | `award.js` | 奖惩管理 |
| `html/notice/list.html` | `notice.js` | 公告管理 |
| `html/payment/list.html` | `payment.js` | 缴费管理 |
| `html/dormitory/list.html` | `dormitory.js` | 宿舍管理 |

### 6.2 公共脚本 `static/js/common.js`

全局对象 `App` 提供：

| 方法 | 作用 |
|---|---|
| `request(url, options)` | 封装 fetch，自动 JSON 序列化并校验 `code` |
| `toast(msg, type)` | 轻提示 |
| `confirm(msg)` | 确认框（Promise） |
| `renderPagination(el, options, onGo)` | 分页渲染 |
| `escapeHtml(value)` | HTML 转义 |
| `formatDateTime / toDateTimeLocal / toDate / today` | 日期时间处理 |
| `fillSelect(select, items, placeholder)` | 下拉框填充 |
| `gerderText / normalizeGerder / ensureOption` | 性别与历史值兼容 |
| `checkLogin / login / logout / adminName` | 登录态管理 |

### 6.3 交互约定

- 业务页加载时调用 `App.checkLogin()`，未登录跳转登录页。
- 通过 `window.parent.setBreadcrumb()` 同步父页面面包屑。
- 列表采用工具栏 + 表格 + 分页 + 模态框表单结构。
- 新增/修改成功后重新加载列表；删除前调用 `App.confirm`。

## 7. 运行与部署

### 7.1 环境准备

```bash
pip install fastapi uvicorn pymysql dbutils pydantic

# 创建数据库（表由程序自动创建）
mysql -uroot -p -e "CREATE DATABASE schaool_db_study DEFAULT CHARSET utf8mb4;"
```

数据库配置位于 `org/zsy/common/config.py` 的 `DB_CONFIG`；`common/pool.py` 中另有一份配置，修改时需保持同步。

### 7.2 启动服务

```bash
# 方式一：模块启动（默认 0.0.0.0:8002）
./.venv/Scripts/python.exe -m org.zsy.main

# 方式二：uvicorn 热更新启动
./.venv/Scripts/python.exe -m uvicorn org.zsy.main:app --host 0.0.0.0 --port 8002 --reload
```

访问 `http://localhost:8002/`（自动跳转登录页）；接口文档 `http://localhost:8002/docs`。

### 7.3 演示数据

```bash
./.venv/Scripts/python.exe -m org.zsy.common.seed
```

脚本可重复执行，检测到 `高一（1）班` 已存在时跳过。写入：5 个班级、5 个学科、6 位老师、10 名学生、10 条分班、15 门课程、30 条成绩、30 条考勤、8 条奖惩、20 条缴费、6 条公告、6 间宿舍、4 个演示用户、5 条备份学生快照。

## 8. 开发与扩展规范

1. 新增模块：创建 `dao.py / service.py / api.py`，在 `common/schema.py` 注册 `ensure_table()`。
2. 在 `main.py` 中导入并 `include_router()`。
3. SQL 一律参数化；分页查询返回 `(rows, total)`；引用校验失败抛出 `BizException`。
4. 前端新增 `static/html/<module>/list.html` 与 `static/js/<module>.js`，并在侧边栏、首页快捷入口登记。
5. 删除涉及关联数据时，在 service 层增加引用检查，避免孤立记录。
6. 保持统一响应 `{code, msg, data}`，错误提示使用中文。

## 9. 说明与限制

- `students_copy2` 为历史备份表，不参与业务逻辑。
- 登录态仅保存在 `sessionStorage`，未实现服务端 Token 校验与权限控制。
- 表间无物理外键，直接操作数据库时需自行保证关联完整性。
- `gerder` 为历史拼写，系统兼容 `man/woman` 与 `男/女`。
- 字段取值：考勤状态（正常/迟到/缺勤/请假）、奖惩类型（奖励/处分）、缴费状态（已缴费/未缴费）。
