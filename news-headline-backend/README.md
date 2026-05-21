# News Headline Backend

新闻资讯应用后端服务，基于 FastAPI 框架开发，提供新闻浏览、用户认证、收藏管理和浏览历史等功能。采用前后端分离架构，前端（Vue/React）通过 RESTful API 与本服务交互。

## 技术栈

- **Python 3.12**
- **FastAPI** — 异步 Web 框架
- **SQLAlchemy 2.0** — 异步 ORM
- **MySQL** — 关系型数据库（通过 aiomysql 异步驱动连接）
- **Redis** — 缓存中间件（通过 redis.asyncio 异步客户端连接）
- **Passlib + bcrypt** — 密码加密
- **Pydantic v2** — 请求数据校验与响应序列化
- **Uvicorn** — ASGI 服务器

## 项目结构

```
news-headline-backend/
├── main.py                  # 应用入口，创建 FastAPI 实例、注册路由和中间件
├── requirements.txt         # 项目依赖
│
├── config/                  # 配置层
│   ├── db_confing.py        # 数据库连接配置（异步引擎、会话工厂、依赖注入）
│   └── cache_conf.py        # Redis 连接配置及通用缓存读写方法
│
├── models/                  # ORM 模型层（对应数据库表结构）
│   ├── news.py              # News 新闻表 / Category 分类表
│   ├── users.py             # User 用户表 / UserToken 令牌表
│   ├── favorite.py          # Favorite 收藏表
│   └── history.py           # History 浏览历史表
│
├── schemas/                 # Pydantic 模型层（请求/响应数据校验）
│   ├── base.py              # 通用基础模型 NewsItemBase
│   ├── users.py             # 用户相关：注册、登录、更新信息、修改密码
│   ├── favorite.py          # 收藏相关：添加、列表、状态检查
│   └── history.py           # 历史记录：添加、列表
│
├── routers/                 # 路由层（API 接口定义）
│   ├── news.py              # /api/news — 新闻分类、列表、详情、相关推荐
│   ├── users.py             # /api/user — 注册、登录、用户信息、修改密码
│   ├── favorite.py          # /api/favorite — 收藏状态、添加、取消、列表、清空
│   └── history.py           # /api/history — 添加、列表、删除、清空
│
├── crud/                    # 数据操作层（数据库 CRUD 封装）
│   ├── news.py              # 新闻查询、浏览量更新、相关推荐
│   ├── users.py             # 用户注册、认证、Token 管理、信息更新
│   ├── favorite.py          # 收藏增删查、列表联表查询
│   └── history.py           # 历史记录增删查、清空
│
├── cache/                   # 缓存层（Redis 缓存策略）
│   └── news_cache.py        # 新闻分类、列表、详情、相关推荐的缓存读写
│
├── common/                  # 公共模块
│   ├── result.py            # 统一响应结构 Result
│   └── page_result.py       # 分页响应结构 PageResult
│
├── utils/                   # 工具模块
│   ├── auth.py              # Token 认证依赖注入（get_current_user）
│   ├── security.py          # 密码加密与验证（bcrypt）
│   ├── response.py          # 成功响应封装 success_response
│   ├── exception.py         # 全局异常处理器（HTTP、数据库、兜底）
│   └── exception_handlers.py # 异常处理器注册
│
├── db/
│   └── database.sql         # 数据库建表 SQL 脚本（含测试数据）
│
└── .venv/                   # 虚拟环境（不提交到 Git）
```

## 环境准备

### 1. 安装 MySQL

确保本地已安装 MySQL 5.7+ 或 8.0，并创建数据库：

```sql
CREATE DATABASE IF NOT EXISTS news_app DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

然后导入建表脚本和测试数据：

```bash
mysql -u root -p news_app < db/database.sql
```

### 2. 安装 Redis

确保本地已安装并启动 Redis 服务，默认端口 6379。

Windows 用户可从 [https://github.com/tporadowski/redis/releases](https://github.com/tporadowski/redis/releases) 下载安装。

### 3. 创建虚拟环境并安装依赖

```bash
# 创建虚拟环境
python -m venv .venv

# 激活虚拟环境
# Windows PowerShell:
.\.venv\Scripts\Activate.ps1
# Windows CMD:
.\.venv\Scripts\activate.bat
# macOS / Linux:
source .venv/bin/activate

# 安装依赖
pip install -r requirements.txt
```

### 4. 修改配置

数据库和 Redis 的连接信息需要根据你的本地环境修改：

`config/db_confing.py` — 修改数据库连接地址、用户名、密码：

```python
ASYNC_DATABASE_URL = "mysql+aiomysql://root:你的密码@localhost:3306/news_app?charset=utf8mb4"
```

`config/cache_conf.py` — 修改 Redis 连接地址（如果 Redis 不在本机或端口不是 6379）：

```python
REDIS_HOST = "localhost"
REDIS_PORT = 6379
```

## 运行项目

```bash
# 确保虚拟环境已激活
uvicorn main:app --reload
```

启动成功后，控制台会显示：

```
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Started reloader process
```

## API 文档

项目启动后，浏览器访问以下地址查看自动生成的交互式 API 文档：

- **Swagger UI**：`http://127.0.0.1:8000/docs`
- **ReDoc**：`http://127.0.0.1:8000/redoc`

在 Swagger UI 中可以直接测试每个接口，包括需要 Token 认证的接口（点击 Authorize 按钮输入 Token）。

## API 接口总览

### 新闻模块 `/api/news`

| 方法 | 路径 | 说明 | 是否需要登录 |
|------|------|------|:------:|
| GET | `/api/news/categories` | 获取新闻分类列表 | 否 |
| GET | `/api/news/list?categoryId=&page=&pageSize=` | 获取新闻列表（分页） | 否 |
| GET | `/api/news/detail?id=` | 获取新闻详情（浏览量+1） | 否 |

### 用户模块 `/api/user`

| 方法 | 路径 | 说明 | 是否需要登录 |
|------|------|------|:------:|
| POST | `/api/user/register` | 用户注册 | 否 |
| POST | `/api/user/login` | 用户登录 | 否 |
| GET | `/api/user/info` | 获取当前用户信息 | 是 |
| PUT | `/api/user/update` | 修改用户信息 | 是 |
| PUT | `/api/user/password` | 修改密码 | 是 |

### 收藏模块 `/api/favorite`

| 方法 | 路径 | 说明 | 是否需要登录 |
|------|------|------|:------:|
| GET | `/api/favorite/check?newsId=` | 检查是否已收藏 | 是 |
| POST | `/api/favorite/add` | 添加收藏 | 是 |
| DELETE | `/api/favorite/remove?newsId=` | 取消收藏 | 是 |
| GET | `/api/favorite/list?page=&pageSize=` | 获取收藏列表（分页） | 是 |
| DELETE | `/api/favorite/clear` | 清空收藏列表 | 是 |

### 浏览历史模块 `/api/history`

| 方法 | 路径 | 说明 | 是否需要登录 |
|------|------|------|:------:|
| POST | `/api/history/add` | 添加浏览历史 | 是 |
| GET | `/api/history/list?page=&pageSize=` | 获取历史列表（分页） | 是 |
| DELETE | `/api/history/delete/{news_id}` | 删除单条历史 | 是 |
| DELETE | `/api/history/clear` | 清空全部历史 | 是 |

### 认证方式

需要登录的接口在请求头中携带 Token：

```
Authorization: Bearer <token>
```

Token 在注册或登录成功后返回，有效期 7 天。

## 统一响应格式

所有接口返回统一的 JSON 结构：

```json
{
  "code": 200,
  "message": "success",
  "data": {}
}
```

分页接口的 `data` 结构：

```json
{
  "list": [],
  "total": 100,
  "hasMore": true
}
```

## 缓存策略

项目使用 Redis 作为缓存层，减少数据库查询压力，各类型数据的缓存过期时间不同：

| 数据类型 | 缓存 Key 格式 | 过期时间 |
|----------|--------------|---------|
| 新闻分类 | `news:categories` | 2 小时 |
| 新闻列表 | `news_list:{分类ID}:{页码}:{每页数量}` | 30 分钟 |
| 新闻详情 | `news:detail:{新闻ID}` | 5 分钟 |
| 相关推荐 | `news:related:{新闻ID}:{分类ID}` | 30 分钟 |

## 数据库表结构

| 表名 | 说明 |
|------|------|
| `user` | 用户信息（用户名、密码、头像、性别等） |
| `user_token` | 用户登录令牌（UUID，7天过期） |
| `news_category` | 新闻分类 |
| `news` | 新闻内容（标题、正文、封面、浏览量等） |
| `favorite` | 收藏记录（用户 + 新闻唯一约束） |
| `history` | 浏览历史（重复浏览更新时间） |

详细的建表语句和测试数据见 `db/database.sql`。

## 全局异常处理

项目注册了四层异常处理器，从具体到通用逐级捕获：

1. `HTTPException` — 业务层主动抛出的异常
2. `IntegrityError` — 数据库完整性约束错误（用户名重复、外键不存在等）
3. `SQLAlchemyError` — 其他数据库操作错误
4. `Exception` — 兜底，捕获所有未处理的异常

开发模式下（`DEBUG_MODE = True`），错误响应会包含详细堆栈信息，方便调试。
