from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession, create_async_engine

# 数据库URL
ASYNC_DATABASE_URL = "mysql+aiomysql://root:123456@localhost:3306/news_app?charset=utf8mb4"

# 创建异步引擎
async_engine = create_async_engine(
    ASYNC_DATABASE_URL,  # 传入数据库连接 URL
    echo=True,  # 可选：开启 SQL 日志输出，便于调试
    pool_size=10,  # 设置连接池中保持的持久连接数为 10
    max_overflow=20  # 设置连接池允许创建的额外连接数最大为 20
)

# 创建异步会话工厂
AsyncSessionLocal = async_sessionmaker(
    bind=async_engine,  # 绑定到之前创建的异步引擎
    class_=AsyncSession,  # 指定会话类为 AsyncSession
    expire_on_commit=False  # 提交后不使对象属性过期，保持数据可访问
)

# 依赖项，用于获取数据库会话
async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session  # 将会话对象产出给调用者，暂停函数执行直到请求结束
            await session.commit()  # 如果无异常，提交事务
        except Exception:
            await session.rollback()  # 发生异常时回滚事务
            raise  # 重新抛出异常以便上层处理
        finally:
            await session.close()  # 关闭会话，释放资源
