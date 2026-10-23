
""""
全局统一响应处理
"""
#业务状态
CODE_OK=0 #成功
CODE_FALL=1 #通用失败

def ok(msg="success",data=None):
    #返回成功，code固定为0
    return {"code":CODE_OK,"msg":msg,"data":data}
def fall(msg="操作失败",code=CODE_FALL,data=None):
    #返回失败，默认code为1
    return {"code":code,"msg":msg,"data":data}