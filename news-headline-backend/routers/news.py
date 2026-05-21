from fastapi import APIRouter
from fastapi.params import Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from common.result import Result
from common.page_result import PageResult
from crud import news
from config.db_confing import get_db

# 创建新闻模块路由
# prefix：当前文件下所有接口都会自动加上 /api/news 前缀
# tags：接口文档 Swagger 中显示的分组名称
router = APIRouter(prefix="/api/news", tags=["news"])


@router.get("/categories", response_model=Result)
async def get_categories(skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db)):
    """
    获取新闻分类
    :param db: 数据库异步会话
    :param skip: 跳过的数据条数，用于分页查询
    :param limit: 每次查询的数据条数，用于分页查询
    :return: 统一格式的新闻分类列表响应
    """
    # skip：跳过多少条数据；limit：最多返回多少条数据，用于分页查询

    # 调用 crud 层查询新闻分类列表
    categories = await news.get_categories(db, skip, limit)

    return Result.success(categories)


@router.get("/list", response_model=PageResult)
async def get_new_list(
        category_id: int = Query(..., alias="categoryId"),
        page: int = 1,
        page_size: int = Query(10, alias="pageSize", le=100),
        db: AsyncSession = Depends(get_db)
):
    """
    获取新闻列表
    :param category_id: 新闻分类 ID
    :param page: 当前页码
    :param page_size: 每页数据条数
    :param db: 数据库异步会话
    :return: 分页格式的新闻列表响应
    """
    offset = (page - 1) * page_size
    news_list = await news.get_news_list(db, category_id, offset, page_size)

    total = await news.get_news_count(db, category_id)

    # （跳过的 + 当前列表里面的数量）< 总量
    has_more = (offset + len(news_list)) < total

    return PageResult.page(
        list_data=news_list,
        total=total,
        has_more=has_more
    )


@router.get("/detail", response_model=Result)
async def get_news_detail(
        news_id: int = Query(..., alias="id"),
        db: AsyncSession = Depends(get_db)
):
    """
    获取新闻详情
    :param news_id:
    :param db:
    :return:
    """
    news_detail = await news.get_news_detail(db, news_id)

    if news_detail is None:
        return Result.error(code=404,data="该新闻不存在")

    # 新闻浏览量 + 1
    news_res = await news.increase_new_views(db, news_id)

    if not news_res:
        return Result.error(code=404, data="更新浏览量失败")

    # 新闻详情-相关推荐
    related_news = await news.get_related_news(
        db,
        news_detail.id,
        news_detail.category_id
    )

    data = {
        "id": news_detail.id,
        "title": news_detail.title,
        "description": news_detail.description,
        "content": news_detail.content,
        "image": news_detail.image,
        "author": news_detail.author,
        "publishTime": news_detail.publish_time,
        "categoryId": news_detail.category_id,
        "views": news_detail.views + 1,
        "relatedNews": related_news
    }

    return Result.success(data)
