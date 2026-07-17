from contextlib import asynccontextmanager
from config_data import config
import asyncpg

dbname = config.DB_NAME
user = config.DB_USER
password = config.DB_PASSWORD
host = config.DB_HOST


@asynccontextmanager
async def db_connection():
    """Контекстный менеджер для асинхронного подключения к базе данных."""
    conn = await asyncpg.connect(
        database=dbname, user=user, password=password, host=host
    )
    try:
        yield conn
    finally:
        await conn.close()


async def init_db():
    async with db_connection() as conn:
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS users (
                telegram_id BIGINT PRIMARY KEY
            );
        """)


async def add_user(telegram_id):
    async with db_connection() as conn:
        sql = """
            INSERT INTO users (telegram_id)
            VALUES ($1)
            ON CONFLICT (telegram_id) DO NOTHING;
        """
        await conn.execute(sql, telegram_id)


async def all_users() -> list[int]:
    async with db_connection() as conn:
        rows = await conn.fetch("""
            SELECT telegram_id
            FROM users
        """)

        return [int(row["telegram_id"]) for row in rows]
