from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger

from .parser import send_daily_digest


def tasks_checker() -> AsyncIOScheduler:
    scheduler = AsyncIOScheduler(timezone="Europe/Moscow")

    scheduler.add_job(
        func=send_daily_digest,
        trigger=IntervalTrigger(seconds=10),
        id="send_daily_digest_job",
        name="Отправка новых материалов",
        replace_existing=True,
        max_instances=1,
        coalesce=True,
    )

    return scheduler
