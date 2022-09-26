from gino import Gino
from .log import logger
import asyncio
from configs.config import config

# 全局数据库连接对象
db: Gino = Gino()


async def init():
    i_bind = f"{config['db_type']}://{config['db_user']}:{config['db_password']}@{config['db_address']}:{config['db_port']}/{config['db_name']}"
    while True:
        try:
            await db.set_bind(i_bind)
            await db.gino.create_all()
            logger.info('Database loaded successfully!')
            break
        except Exception as e:
            logger.error(f'数据库连接错误.... e: {e}')
            await asyncio.sleep(1)
            continue


async def disconnect():
    await db.pop_bind().close()