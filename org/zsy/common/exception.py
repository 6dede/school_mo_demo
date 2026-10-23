

CODE_FAIL=1
NOT_EXIST=100

class BizException(Exception):
    def __init__(self,msg="操作失败",code=CODE_FAIL):
        self.msg=msg
        self.code=code
        super().__init__(msg)