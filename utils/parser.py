import asyncio
from pathlib import Path

import requests
from bs4 import BeautifulSoup

from loader import bot
from pg_maker import all_users


HEADERS = {"User-Agent": "Mozilla/5.0"}
URL = "https://sci.rambler.ru/"
SEEN_FILE = Path("seen_links.txt")


def load_seen_links() -> set[str]:
    if not SEEN_FILE.exists():
        return set()

    with SEEN_FILE.open("r", encoding="utf-8") as file:
        return {line.strip() for line in file if line.strip()}


def save_seen_links(links: set[str]) -> None:
    with SEEN_FILE.open("w", encoding="utf-8") as file:
        file.write("\n".join(sorted(links)))


def fetch_rambler() -> list[tuple[str, str]]:
    response = requests.get(
        URL,
        headers=HEADERS,
        timeout=20,
    )
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")

    seen_links = load_seen_links()
    found_links = set()
    new_articles = []

    for tag in soup.find_all("a", href=True):
        href = tag["href"]

        if not href.startswith("https://sci.rambler.ru/"):
            continue

        title = tag.get_text(" ", strip=True)

        if not title or href in found_links:
            continue

        found_links.add(href)

        if href not in seen_links:
            new_articles.append((title, href))

    # Сохраняем всю историю, а не только ссылки с текущей страницы
    seen_links.update(found_links)
    save_seen_links(seen_links)

    return new_articles


async def send_daily_digest() -> None:
    # requests блокирует event loop, поэтому запускаем парсер в отдельном потоке
    news = await asyncio.to_thread(fetch_rambler)
    chat_ids = await all_users()

    for chat_id in chat_ids:
        for title, link in news:
            text = f"{title}\n{link}"
            await bot.send_message(chat_id, text)
