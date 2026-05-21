from typing import Any
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel


# 统一接口返回结构
class Result(BaseModel):
    code: int = 200
    message: str = "success"
    data: Any = None

    @classmethod
    def success(cls, data: Any = None, message: str = "success"):
        # jsonable_encoder 会把 SQLAlchemy ORM 对象、datetime 等类型
        # 转换成 FastAPI 可以正常返回的 JSON 数据
        return cls(
            code=200,
            message=message,
            data=jsonable_encoder(data)
        )

    @classmethod
    def error(cls, message: str = "error", code: int = 500, data: Any = None):
        # 失败响应统一走这里，方便前端按 code/message/data 处理
        return cls(
            code=code,
            message=message,
            data=jsonable_encoder(data)
        )
