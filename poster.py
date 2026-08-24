"""
WordPress Auto News Poster
Парсит новости киберспорта и спорта, генерирует статьи через Groq, публикует на WordPress.
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
WP_URL      = os.environ["WP_URL"].rstrip("/")          # https://beteasy.ru
WP_USER     = os.environ["WP_USER"]                     # blogger
WP_APP_PASS = os.environ["WP_APP_PASS"]                 # Application Password
GROQ_API_KEY = os.environ["GROQ_API_KEY"]

# Сколько статей публиковать за один запуск
POSTS_PER_RUN = int(os.getenv("POSTS_PER_RUN", "3"))

# ── RSS-источники по категориям ────────────────────────────────────────────
RSS_FEEDS = {
    "Киберспорт": [
        "https://www.cybersport.ru/rss/all",
        "https://esports.ru/rss.xml",
        "https://dota2.ru/rss.xml",
    ],
    "Футбол": [
        "https://www.championat.com/rss/football/",
        "https://www.sports.ru/rss/football.xml",
        "https://www.goal.com/feeds/ru/news",
    ],
    "Баскетбол": [
        "https://www.championat.com/rss/basketball/",
        "https://www.sports.ru/rss/basketball.xml",
    ],
    "Хоккей": [
        "https://www.championat.com/rss/hockey/",
        "https://www.sports.ru/rss/hockey.xml",
    ],
    "Теннис": [
        "https://www.championat.com/rss/tennis/",
        "https://www.sports.ru/rss/tennis.xml",
    ],
}

# WordPress категории (slug → id) — будут созданы/найдены автоматически
CATEGORY_MAP: dict[str, int] = {}


# ══════════════════════════════════════════════════════════════════════════════
# 1. ПАРСИНГ RSS
# ══════════════════════════════════════════════════════════════════════════════

def fetch_news(max_per_category: int = 5) -> list[dict]:
    """Возвращает список новостей вида {title, summary, link, category}."""
    news_items: list[dict] = []

    for category, feeds in RSS_FEEDS.items():
        found = 0
        for url in feeds:
            if found >= max_per_category:
                break
            try:
                feed = feedparser.parse(url)
                for entry in feed.entries:
                    if found >= max_per_category:
                        break
                    title   = entry.get("title", "").strip()
                    summary = entry.get("summary", entry.get("description", "")).strip()
                    link    = entry.get("link", "")
                    # Чистим HTML-теги из summary
                    summary = re.sub(r"<[^>]+>", "", summary)[:1000]
                    if title and link:
                        news_items.append({
                            "title":    title,
                            "summary":  summary,
                            "link":     link,
                            "category": category,
                        })
                        found += 1
            except Exception as exc:
                log.warning("RSS %s: %s", url, exc)

    random.shuffle(news_items)
    return news_items


# ══════════════════════════════════════════════════════════════════════════════
# 2. ГЕНЕРАЦИЯ ТЕКСТА ЧЕРЕЗ GROQ
# ══════════════════════════════════════════════════════════════════════════════

GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"
GROQ_MODEL   = "llama3-70b-8192"

SYSTEM_PROMPT = (
    "Ты опытный спортивный журналист. Пишешь живые, интересные новостные статьи "
    "на русском языке для сайта о ставках на спорт и киберспорт. "
    "Тон: профессиональный, но доступный. "
    "Структура: вводный абзац с главным фактом, 2-3 абзаца с деталями и контекстом, "
    "краткий итог. Без воды и лишних слов. Только HTML: <p>, <b>, <ul>, <li>. "
    "Не добавляй заголовок — он передаётся отдельно."
)


def generate_article(news: dict) -> str | None:
    """Генерирует HTML-текст статьи через Groq API."""
    user_prompt = (
        f"Категория: {news['category']}\n"
        f"Заголовок новости: {news['title']}\n"
        f"Краткое описание: {news['summary']}\n"
        f"Источник: {news['link']}\n\n"
        "Напиши полноценную новостную статью на основе этих данных. "
        "Объём: 250-400 слов. Возвращай только HTML-контент статьи."
    )

    headers = {
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
        resp = requests.post(GROQ_API_URL, json=payload, headers=headers, timeout=60)
        resp.raise_for_status()
        content = resp.json()["choices"][0]["message"]["content"].strip()
        return content
    except Exception as exc:
        log.error("Groq error для '%s': %s", news["title"], exc)
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

    # Поиск существующей
    try:
        resp = requests.get(base, params={"search": name, "per_page": 5}, auth=auth, timeout=30)
        resp.raise_for_status()
        cats = resp.json()
        for cat in cats:
            if cat["name"].lower() == name.lower():
                CATEGORY_MAP[name] = cat["id"]
                return cat["id"]
    except Exception as exc:
        log.warning("Поиск категории '%s': %s", name, exc)

    # Создание новой
    try:
        resp = requests.post(base, json={"name": name}, auth=auth, timeout=30)
        resp.raise_for_status()
        cat_id = resp.json()["id"]
        CATEGORY_MAP[name] = cat_id
        log.info("Создана категория '%s' → id=%d", name, cat_id)
        return cat_id
    except Exception as exc:
        log.error("Создание категории '%s': %s", name, exc)
        return 1  # fallback: Uncategorized


def publish_post(news: dict, content: str) -> bool:
    """Публикует пост в WordPress. Возвращает True при успехе."""
    auth     = HTTPBasicAuth(WP_USER, WP_APP_PASS)
    endpoint = f"{WP_URL}/wp-json/wp/v2/posts"
    cat_id   = get_or_create_category(news["category"])

    # Добавляем ссылку на источник в конец статьи
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
        log.info("✅ Опубликован пост #%s: %s", post_id, post_url)
        return True
    except requests.HTTPError as exc:
        log.error("HTTP %s при публикации '%s': %s",
                  exc.response.status_code, news["title"], exc.response.text[:300])
        return False
    except Exception as exc:
        log.error("Ошибка публикации '%s': %s", news["title"], exc)
        return False


# ══════════════════════════════════════════════════════════════════════════════
# 4. ГЛАВНЫЙ ЦИКЛ
# ══════════════════════════════════════════════════════════════════════════════

def run() -> None:
    log.info("=== Запуск автопостинга (%s) ===", datetime.now().strftime("%Y-%m-%d %H:%M"))

    all_news  = fetch_news(max_per_category=5)
    published = 0

    for news in all_news:
        if published >= POSTS_PER_RUN:
            break

        log.info("→ Обрабатываем: [%s] %s", news["category"], news["title"])

        content = generate_article(news)
        if not content:
            continue

        success = publish_post(news, content)
        if success:
            published += 1

        # Пауза между запросами, чтобы не перегружать API
        time.sleep(3)

    log.info("=== Готово: опубликовано %d/%d статей ===", published, POSTS_PER_RUN)


if __name__ == "__main__":
    run()
