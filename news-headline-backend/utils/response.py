from typing import Any
from fastapi.encoders import jsonable_encoder
from starlette.responses import JSONResponse

# 成功响应结果
def success_response(message: str = "success", data: Any = None):
   content = {
       "code": 200,
       "message":message,
       "data":data
   }
   # 目标:把任何的 FastAPI、Pydantic、ORM对象 都要正常响应 + code、 message、 data
   return JSONResponse(content=jsonable_encoder(content))