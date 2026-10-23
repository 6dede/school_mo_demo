from pathlib import Path
from urllib.request import Request

from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from starlette.responses import JSONResponse

from org.zsy.common.exception import BizException
from org.zsy.teacher.api import router as teaRouter
from org.zsy.student.api import router as stuRouter
from org.zsy.subject.api import router as subRouter
from org.zsy.classroom.api import router as classRouter
from org.zsy.course.api import router as courseRouter
from org.zsy.score.api import router as scoreRouter
from org.zsy.attendance.api import router as attendanceRouter
from org.zsy.classmember.api import router as memberRouter
from org.zsy.notice.api import router as noticeRouter
from org.zsy.award.api import router as awardRouter
from org.zsy.payment.api import router as paymentRouter
from org.zsy.dormitory.api import router as dormRouter
from org.zsy.dashboard.api import router as dashboardRouter
from org.zsy.user.api import router as userRouter
from org.zsy.common.schema import init_tables
import uvicorn
import logging
from org.zsy.common.response import fall
app = FastAPI(title='教务管理Api',description='用于校务管理系统中教务管理模块')
app.include_router(teaRouter)
app.include_router(stuRouter)
app.include_router(subRouter)
app.include_router(classRouter)
app.include_router(courseRouter)
app.include_router(scoreRouter)
app.include_router(attendanceRouter)
app.include_router(memberRouter)
app.include_router(noticeRouter)
app.include_router(awardRouter)
app.include_router(paymentRouter)
app.include_router(dormRouter)
app.include_router(dashboardRouter)
app.include_router(userRouter)

# 初始化各业务模块数据表及默认管理员
init_tables()

# 静态资源目录：项目根/static
STATIC_DIR = Path(__file__).resolve().parents[2] / "static"
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

logger=logging.getLogger(__name__)


@app.get("/", include_in_schema=False)
def index():
    return RedirectResponse(url="/static/html/login.html")
@app.exception_handler(RequestValidationError)
async def validation_handler(request:Request,exc:RequestValidationError):
    logger.error(f"请求{request.url.path} 参数错误：{exc}")
    err=exc.errors()[0] if exc.errors() else {}
    return JSONResponse(status_code=200,content=fall(f"参数错误：{err.get('msg','请检查提交')}"))

@app.exception_handler(BizException)
async def biz_handler(request:Request,exc:BizException):
    logger.warning(f"请求{request.url.path} 业务异常：{exc.msg}")

    return JSONResponse(status_code=200,content=fall(exc.msg,code=exc.code))

@app.exception_handler(Exception)
async def gplobal_exception_handler(request: Request, exc: Exception):
        logger.error(f"请求{request.url.path} 系统异常：{exc}")

        return JSONResponse(status_code=200,content=fall(f"服务器异常：{exc}",code=500))
if __name__ == "__main__":
    uvicorn.run("org.zsy.main:app", host="0.0.0.0", port=8002, reload=False)








# @app.get("/")
# def home():
#     return {"message":"欢迎进入校务管理系统"}
#
# if __name__ == "__main__":
#     uvicorn.run("main:app", host="127.0.0.1", port=8004)
