from typing import Any
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel


# 分页接口统一返回结构
class PageResult(BaseModel):
    code: int = 200
    message: str = "success"
    data: Any = None

    @classmethod
    def page(cls, list_data: Any = None, total: int = 0, has_more: bool = False):
        """
        分页列表响应
        :param list_data: 当前页数据列表
        :param total: 数据总条数
        :param has_more: 是否还有更多数据
        :return: 统一分页响应对象
        """
        return cls(
            code=200,
            message="success",
            data={
                "list": jsonable_encoder(list_data),
                "total": total,
                "hasMore": has_more
            }
        )
