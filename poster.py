"""
WordPress Auto News Poster
Парсит новости киберспорта и спорта, генерирует статьи на русском через Groq,
публикует на WordPress.
"""

import os
import re
import time
import random
import logging
import requests
import feedparser
from datetime import datetime, timezone
from requests.auth import HTTPBasicAuth

# ── Настройка логирования ──────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
log = logging.getLogger(__name__)

# ── Конфигурация из переменных окружения ───────────────────────────────────
WP_URL       = os.environ["WP_URL"].rstrip("/")
WP_USER      = os.environ["WP_USER"]
WP_APP_PASS  = os.environ["WP_APP_PASS"]
GROQ_API_KEY = os.environ["GROQ_API_KEY"]
POSTS_PER_RUN = int(os.getenv("POSTS_PER_RUN", "3"))

# ── Заголовки браузера для RSS-запросов ────────────────────────────────────
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept": "application/rss+xml, application/xml, text/xml, */*",
    "Accept-Language": "ru-RU,ru;q=0.9,en;q=0.8",
}

# ── RSS-источники ──────────────────────────────────────────────────────────
RSS_FEEDS = {
    "Киберспорт": [
        "https://dotesports.com/dota-2/feed",
        "https://dotesports.com/counter-strike/feed",
        "https://www.hltv.org/rss/news",
        "https://dotesports.com/feed",
        "https://www.cybersport.ru/rss/all",
        "https://cyber.sports.ru/rss.xml",
    ],
    "Футбол": [
        "https://feeds.bbci.co.uk/sport/football/rss.xml",
        "https://www.espn.com/espn/rss/soccer/news",
        "https://www.football-espana.net/feed",
        "https://www.sports.ru/rss/football.xml",
        "https://www.championat.com/rss/football/",
    ],
    "Баскетбол": [
        "https://feeds.bbci.co.uk/sport/basketball/rss.xml",
        "https://www.espn.com/espn/rss/nba/news",
        "https://www.sports.ru/rss/basketball.xml",
        "https://www.championat.com/rss/basketball/",
    ],
    "Хоккей": [
        "https://www.espn.com/espn/rss/nhl/news",
        "https://www.nhl.com/rss/news.xml",
        "https://www.sports.ru/rss/hockey.xml",
        "https://www.championat.com/rss/hockey/",
        "https://www.khl.ru/news/rss/",
    ],
    "Теннис": [
        "https://feeds.bbci.co.uk/sport/tennis/rss.xml",
        "https://www.espn.com/espn/rss/tennis/news",
        "https://www.sports.ru/rss/tennis.xml",
        "https://www.championat.com/rss/tennis/",
    ],
}

CATEGORY_MAP: dict[str, int] = {}


# ══════════════════════════════════════════════════════════════════════════════
# 1. ПАРСИНГ RSS
# ══════════════════════════════════════════════════════════════════════════════

def fetch_rss(url: str) -> list:
    """Загружает RSS с браузерными заголовками, возвращает список записей."""
    try:
        resp = requests.get(url, headers=HEADERS, timeout=15)
        log.info("RSS %s → HTTP %s, %d bytes", url, resp.status_code, len(resp.content))
        if resp.status_code != 200:
            log.warning("RSS %s → нет ответа (HTTP %s)", url, resp.status_code)
            return []
        feed = feedparser.parse(resp.content)
        log.info("RSS %s → найдено записей: %d", url, len(feed.entries))
        return feed.entries
    except Exception as exc:
        log.warning("RSS %s → ошибка: %s", url, exc)
        return []


def fetch_news(max_per_category: int = 5) -> list[dict]:
    """Возвращает список новостей {title, summary, link, category}."""
    news_items: list[dict] = []

    for category, feeds in RSS_FEEDS.items():
        found = 0
        log.info("=== Категория: %s ===", category)
        for url in feeds:
            if found >= max_per_category:
                break
            entries = fetch_rss(url)
            for entry in entries:
                if found >= max_per_category:
                    break
                title   = entry.get("title", "").strip()
                summary = entry.get("summary", entry.get("description", "")).strip()
                link    = entry.get("link", "")
                summary = re.sub(r"<[^>]+>", "", summary)[:1000]
                if title and link:
                    news_items.append({
                        "title":    title,
                        "summary":  summary,
                        "link":     link,
                        "category": category,
                    })
                    found += 1
                    log.info("  + [%s] %s", category, title[:80])
        log.info("Итого для '%s': %d новостей", category, found)

    log.info("Всего собрано новостей: %d", len(news_items))
    random.shuffle(news_items)
    return news_items


# ══════════════════════════════════════════════════════════════════════════════
# 2. ГЕНЕРАЦИЯ ТЕКСТА ЧЕРЕЗ GROQ
# ══════════════════════════════════════════════════════════════════════════════

GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"
GROQ_MODEL   = "openai/gpt-oss-20b"

SYSTEM_PROMPT = (
    "Ты опытный спортивный журналист. Пишешь ТОЛЬКО на русском языке. "
    "Пишешь живые, интересные новостные статьи для сайта о ставках на спорт и киберспорт. "
    "Тон: профессиональный, но доступный. "
    "Структура: вводный абзац с главным фактом, 2-3 абзаца с деталями и контекстом, "
    "краткий итог. Без воды и лишних слов. "
    "Используй только HTML теги: <p>, <b>, <ul>, <li>. "
    "Не добавляй заголовок — он передаётся отдельно. "
    "Если исходная новость на английском — переведи и изложи на русском языке."
)


def generate_article(news: dict) -> str | None:
    """Генерирует HTML-текст статьи через Groq API."""
    user_prompt = (
        f"Категория: {news['category']}\n"
        f"Заголовок новости: {news['title']}\n"
        f"Краткое описание: {news['summary']}\n"
        f"Источник: {news['link']}\n\n"
        "Напиши полноценную новостную статью на РУССКОМ ЯЗЫКЕ на основе этих данных. "
        "Объём: 250-400 слов. Возвращай только HTML-контент статьи без заголовка."
    )

    groq_headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type":  "application/json",
    }
    payload = {
        "model":       GROQ_MODEL,
        "messages":    [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user",   "content": user_prompt},
        ],
        "temperature": 0.7,
        "max_tokens":  1024,
    }

    try:
        resp = requests.post(GROQ_API_URL, json=payload, headers=groq_headers, timeout=60)
        resp.raise_for_status()
        content = resp.json()["choices"][0]["message"]["content"].strip()
        log.info("Groq сгенерировал %d символов для '%s'", len(content), news["title"][:50])
        return content
    except Exception as exc:
        log.error("Groq ошибка для '%s': %s", news["title"], exc)
        return None


# ══════════════════════════════════════════════════════════════════════════════
# 3. WORDPRESS REST API
# ══════════════════════════════════════════════════════════════════════════════

def get_or_create_category(name: str) -> int:
    """Возвращает ID категории WordPress, создаёт если не существует."""
    if name in CATEGORY_MAP:
        return CATEGORY_MAP[name]

    auth = HTTPBasicAuth(WP_USER, WP_APP_PASS)
    base = f"{WP_URL}/wp-json/wp/v2/categories"

    try:
        resp = requests.get(base, params={"search": name, "per_page": 5}, auth=auth, timeout=30)
        resp.raise_for_status()
        for cat in resp.json():
            if cat["name"].lower() == name.lower():
                CATEGORY_MAP[name] = cat["id"]
                log.info("Найдена категория '%s' → id=%d", name, cat["id"])
                return cat["id"]
    except Exception as exc:
        log.warning("Поиск категории '%s': %s", name, exc)

    try:
        resp = requests.post(base, json={"name": name}, auth=auth, timeout=30)
        resp.raise_for_status()
        cat_id = resp.json()["id"]
        CATEGORY_MAP[name] = cat_id
        log.info("Создана категория '%s' → id=%d", name, cat_id)
        return cat_id
    except Exception as exc:
        log.error("Создание категории '%s': %s", name, exc)
        return 1


def publish_post(news: dict, content: str) -> bool:
    """Публикует пост в WordPress."""
    auth     = HTTPBasicAuth(WP_USER, WP_APP_PASS)
    endpoint = f"{WP_URL}/wp-json/wp/v2/posts"
    cat_id   = get_or_create_category(news["category"])

    footer = (
        f'<p><small>Источник: <a href="{news["link"]}" '
        f'target="_blank" rel="nofollow noopener">{news["link"]}</a></small></p>'
    )

    post_data = {
        "title":      news["title"],
        "content":    content + footer,
        "status":     "publish",
        "categories": [cat_id],
        "date":       datetime.now(timezone.utc).isoformat(),
    }

    try:
        resp = requests.post(endpoint, json=post_data, auth=auth, timeout=30)
        resp.raise_for_status()
        post_id  = resp.json().get("id")
        post_url = resp.json().get("link")
        log.info("ОПУБЛИКОВАН пост #%s: %s", post_id, post_url)
        return True
    except requests.HTTPError as exc:
        log.error("HTTP %s при публикации '%s': %s",
                  exc.response.status_code, news["title"], exc.response.text[:500])
        return False
    except Exception as exc:
        log.error("Ошибка публикации '%s': %s", news["title"], exc)
        return False


# ══════════════════════════════════════════════════════════════════════════════
# 4. ГЛАВНЫЙ ЦИКЛ
# ══════════════════════════════════════════════════════════════════════════════

def run() -> None:
    log.info("=== Запуск автопостинга (%s) ===", datetime.now().strftime("%Y-%m-%d %H:%M"))
    log.info("WordPress URL: %s", WP_URL)
    log.info("Пользователь: %s", WP_USER)

    all_news  = fetch_news(max_per_category=5)
    published = 0

    if not all_news:
        log.error("Новости не найдены! Все RSS-ленты недоступны.")
        return

    for news in all_news:
        if published >= POSTS_PER_RUN:
            break

        log.info("→ Обрабатываем: [%s] %s", news["category"], news["title"])

        content = generate_article(news)
        if not content:
            log.warning("Groq не вернул контент, пропускаем")
            continue

        success = publish_post(news, content)
        if success:
            published += 1

        time.sleep(3)

    log.info("=== Готово: опубликовано %d/%d статей ===", published, POSTS_PER_RUN)


if __name__ == "__main__":
    run()
