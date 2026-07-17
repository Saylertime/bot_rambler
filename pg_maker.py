from contextlib import asynccontextmanager
import asyncpg
from config_data import config


@asynccontextmanager
async def db_connection():
    conn = await asyncpg.connect(
        database=config.DB_NAME,
        user=config.DB_USER,
        password=config.DB_PASSWORD,
        host=config.DB_HOST,
    )
    try:
        yield conn
    finally:
        await conn.close()


async def init_db():
    async with db_connection() as conn:
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS chats (
                chat_id BIGINT PRIMARY KEY,
                chat_type VARCHAR(20) NOT NULL,
                title TEXT,
                is_active BOOLEAN NOT NULL DEFAULT TRUE
            );
        """)


async def add_chat(
    chat_id: int,
    chat_type: str,
    title: str | None = None,
):
    async with db_connection() as conn:
        await conn.execute("""
            INSERT INTO chats (
                chat_id,
                chat_type,
                title,
                is_active
            )
            VALUES ($1, $2, $3, TRUE)
            ON CONFLICT (chat_id)
            DO UPDATE SET
                chat_type = EXCLUDED.chat_type,
                title = EXCLUDED.title,
                is_active = TRUE;
        """, chat_id, chat_type, title)


async def remove_chat(chat_id: int):
    async with db_connection() as conn:
        await conn.execute("""
            UPDATE chats
            SET is_active = FALSE
            WHERE chat_id = $1;
        """, chat_id)


async def all_chats() -> list[int]:
    async with db_connection() as conn:
        rows = await conn.fetch("""
            SELECT chat_id
            FROM chats
            WHERE is_active = TRUE;
        """)

        return [row["chat_id"] for row in rows]