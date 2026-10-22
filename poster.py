"""
WordPress Auto News Poster
Парсит новости киберспорта и спорта, генерирует статьи на русском через Groq,
загружает картинку, добавляет внутреннюю SEO-перелинковку и публикует на WordPress.
"""

import os
import re
import time
import random
import logging
import requests
import feedparser
import json
from datetime import datetime, timezone
from requests.auth import HTTPBasicAuth
from urllib.parse import urlparse

# ── Настройка логирования ──────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
log = logging.getLogger(__name__)

# ── Конфигурация из переменных окружения ───────────────────────────────────
WP_URL        = os.environ["WP_URL"].rstrip("/")
WP_USER       = os.environ["WP_USER"]
WP_APP_PASS   = os.environ["WP_APP_PASS"]
GROQ_API_KEY  = os.environ["GROQ_API_KEY"]
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

# ── RSS-источники (международные - доступны с GitHub) ──────────────────────
RSS_FEEDS = {
    "Киберспорт": [
        "https://cybersport.ru/rss/materials",
        "https://www.cybersport.ru/rss/materials",
        "https://dotesports.com/dota-2/feed",
        "https://dotesports.com/counter-strike/feed",
        "https://www.hltv.org/rss/news",
    ],
    "Футбол": [
        "https://www.championat.com/rss/news/football/",
        "https://feeds.bbci.co.uk/sport/football/rss.xml",
        "https://www.espn.com/espn/rss/soccer/news",
        "https://www.goal.com/feeds/en/news",
    ],
    "Баскетбол": [
        "https://feeds.bbci.co.uk/sport/basketball/rss.xml",
        "https://www.espn.com/espn/rss/nba/news",
        "https://www.nbcsports.com/rss/nbcsports/sections/nba/headlines/",
    ],
    "Хоккей": [
        "https://www.espn.com/espn/rss/nhl/news",
        "https://www.nhl.com/rss/news.xml",
        "https://feeds.bbci.co.uk/sport/winter-sports/rss.xml",
    ],
    "Теннис": [
        "https://feeds.bbci.co.uk/sport/tennis/rss.xml",
        "https://www.espn.com/espn/rss/tennis/news",
        "https://www.atptour.com/en/media/rss-feed/xml-feed",
    ],
}

CATEGORY_MAP: dict[str, int] = {}
CATEGORY_URLS: dict[str, str] = {}

# ── Файл истории опубликованных новостей ──────────────────────────────────
PUBLISHED_HISTORY_FILE = "/tmp/published_news.json"

# Сколько внутренних ссылок вставлять в текст и в блок «Читайте также»
INLINE_LINKS_COUNT = 2
RELATED_BLOCK_COUNT = 3


def wp_auth() -> HTTPBasicAuth:
    return HTTPBasicAuth(WP_USER, WP_APP_PASS)


def load_published_history() -> set:
    """Загружает набор уже опубликованных ссылок из файла."""
    try:
        if os.path.exists(PUBLISHED_HISTORY_FILE):
            with open(PUBLISHED_HISTORY_FILE, "r") as f:
                data = json.load(f)
                log.info("Загружена история: %d опубликованных ссылок", len(data.get("links", [])))
                return set(data.get("links", []))
    except Exception as exc:
        log.warning("Ошибка загрузки истории: %s", exc)
    return set()


def save_published_history(published_links: set) -> None:
    """Сохраняет набор опубликованных ссылок в файл."""
    try:
        data = {
            "links": list(published_links),
            "updated": datetime.now(timezone.utc).isoformat(),
        }
        with open(PUBLISHED_HISTORY_FILE, "w") as f:
            json.dump(data, f, indent=2)
        log.info("История сохранена: %d ссылок", len(published_links))
    except Exception as exc:
        log.warning("Ошибка сохранения истории: %s", exc)


# ══════════════════════════════════════════════════════════════════════════════
# 0. ВНУТРЕННИЕ СТРАНИЦЫ САЙТА (для SEO-перелинковки)
# ══════════════════════════════════════════════════════════════════════════════

def _strip_html(text: str) -> str:
    return re.sub(r"<[^>]+>", "", text or "").strip()


def fetch_internal_content() -> dict:
    """
    Собирает реальные внутренние URL с WordPress:
    - опубликованные посты
    - страницы
    - архивы категорий
    """
    auth = wp_auth()
    result = {
        "posts": [],
        "pages": [],
        "categories": [],
    }

    try:
        resp = requests.get(
            f"{WP_URL}/wp-json/wp/v2/posts",
            params={"per_page": 50, "status": "publish", "_fields": "id,title,link,categories,excerpt"},
            auth=auth,
            timeout=30,
        )
        resp.raise_for_status()
        for item in resp.json():
            title = _strip_html(item.get("title", {}).get("rendered", ""))
            link = item.get("link", "")
            if title and link:
                result["posts"].append({
                    "id": item.get("id"),
                    "title": title,
                    "url": link,
                    "categories": item.get("categories", []),
                    "excerpt": _strip_html(item.get("excerpt", {}).get("rendered", "")),
                })
        log.info("Внутренние посты для перелинковки: %d", len(result["posts"]))
    except Exception as exc:
        log.warning("Не удалось получить посты для перелинковки: %s", exc)

    try:
        resp = requests.get(
            f"{WP_URL}/wp-json/wp/v2/pages",
            params={"per_page": 30, "status": "publish", "_fields": "id,title,link"},
            auth=auth,
            timeout=30,
        )
        resp.raise_for_status()
        for item in resp.json():
            title = _strip_html(item.get("title", {}).get("rendered", ""))
            link = item.get("link", "")
            if title and link:
                result["pages"].append({"id": item.get("id"), "title": title, "url": link})
        log.info("Внутренние страницы для перелинковки: %d", len(result["pages"]))
    except Exception as exc:
        log.warning("Не удалось получить страницы для перелинковки: %s", exc)

    try:
        resp = requests.get(
            f"{WP_URL}/wp-json/wp/v2/categories",
            params={"per_page": 50, "hide_empty": False, "_fields": "id,name,link,slug"},
            auth=auth,
            timeout=30,
        )
        resp.raise_for_status()
        for item in resp.json():
            name = item.get("name", "")
            link = item.get("link", "")
            if name and link:
                result["categories"].append({
                    "id": item.get("id"),
                    "name": name,
                    "url": link,
                    "slug": item.get("slug", ""),
                })
                CATEGORY_URLS[name] = link
        log.info("Категории для перелинковки: %d", len(result["categories"]))
    except Exception as exc:
        log.warning("Не удалось получить категории для перелинковки: %s", exc)

    return result


def _tokenize(text: str) -> set[str]:
    words = re.findall(r"[а-яёa-z0-9]{4,}", (text or "").lower())
    stop = {
        "этот", "этого", "эта", "это", "для", "или", "как", "что", "при", "после",
        "будет", "были", "был", "была", "также", "более", "всех", "своей", "своих",
        "which", "that", "with", "from", "have", "been", "this", "their", "about",
    }
    return {w for w in words if w not in stop}


def select_related_links(news: dict, internal: dict, exclude_url: str | None = None, limit: int = 5) -> list[dict]:
    """Подбирает только реально релевантные внутренние страницы.
    Требует пересечение слов >= 2 или совпадение категории + 1 слово.
    Не добирает случайные посты."""
    news_tokens = _tokenize(news.get("title", "") + " " + news.get("summary", "") + " " + news.get("category", ""))
    news_cat = (news.get("category") or "").lower()
    scored: list[tuple[int, dict]] = []

    for post in internal.get("posts", []):
        if exclude_url and post["url"] == exclude_url:
            continue
        tokens = _tokenize(post["title"] + " " + post.get("excerpt", ""))
        overlap = len(news_tokens & tokens)
        score = overlap
        # Бонус за ту же категорию
        post_title_lower = post["title"].lower()
        if news_cat and news_cat in post_title_lower:
            score += 4
        # Требуем минимум 2 общих слова ИЛИ категорию + 1 слово
        if overlap < 2 and not (news_cat and news_cat in post_title_lower and overlap >= 1):
            continue
        scored.append((score, {"title": post["title"], "url": post["url"], "type": "post"}))

    # Страницы — только если есть пересечение
    for page in internal.get("pages", []):
        if exclude_url and page["url"] == exclude_url:
            continue
        tokens = _tokenize(page["title"])
        overlap = len(news_tokens & tokens)
        if overlap < 1:
            continue
        score = overlap + 1
        scored.append((score, {"title": page["title"], "url": page["url"], "type": "page"}))

    scored.sort(key=lambda x: x[0], reverse=True)

    picked: list[dict] = []
    seen = set()
    for score, item in scored:
        if item["url"] in seen:
            continue
        if score < 2:
            continue
        seen.add(item["url"])
        picked.append(item)
        if len(picked) >= limit:
            break

    log.info("Подобрано релевантных ссылок: %d (мин. скор 2)", len(picked))
    return picked


def _is_internal_url(url: str) -> bool:
    try:
        host = urlparse(url).netloc.lower().replace("www.", "")
        site = urlparse(WP_URL).netloc.lower().replace("www.", "")
        return bool(host) and host == site
    except Exception:
        return False


def inject_inline_links(content: str, related: list[dict], category_name: str, category_url: str | None) -> str:
    """
    Вставляет 1-2 естественные внутренние ссылки в HTML:
    1) первое упоминание названия категории → архив категории
    2) первое подходящее слово из заголовка связанной статьи → эта статья
    Не трогает уже существующие <a> теги.
    """
    if not content:
        return content

    # Не вставляем ссылки внутрь существующих якорей
    protected = []

    def _stash(m):
        protected.append(m.group(0))
        return f"___LINK_{len(protected) - 1}___"

    working = re.sub(r"<a\b[^>]*>.*?</a>", _stash, content, flags=re.I | re.S)

    inserted = 0

    if category_name and category_url and _is_internal_url(category_url):
        pattern = re.compile(re.escape(category_name), re.I)
        match = pattern.search(working)
        if match:
            linked = f'<a href="{category_url}">{match.group(0)}</a>'
            working = working[:match.start()] + linked + working[match.end():]
            inserted += 1
            log.info("Вставлена ссылка на категорию: %s", category_url)

    for item in related:
        if inserted >= INLINE_LINKS_COUNT:
            break
        title = item.get("title", "").strip()
        url = item.get("url", "")
        if not title or not url or not _is_internal_url(url):
            continue

        # Берём значимый кусок заголовка (2-4 слова) как анкор
        words = [w for w in re.findall(r"[А-Яа-яЁёA-Za-z0-9\-]{3,}", title) if len(w) > 3]
        if len(words) < 2:
            continue
        anchor_candidates = [
            " ".join(words[:4]),
            " ".join(words[:3]),
            " ".join(words[:2]),
            words[0],
        ]

        for anchor in anchor_candidates:
            if len(anchor) < 4:
                continue
            pattern = re.compile(re.escape(anchor), re.I)
            match = pattern.search(working)
            if not match:
                continue
            # Не ставим ссылку в заголовочные теги
            before = working[max(0, match.start() - 40):match.start()].lower()
            if any(tag in before for tag in ("<h1", "<h2", "<h3", "<title")):
                continue
            linked = f'<a href="{url}">{match.group(0)}</a>'
            working = working[:match.start()] + linked + working[match.end():]
            inserted += 1
            log.info("Вставлена внутренняя ссылка: '%s' → %s", match.group(0), url)
            break

    def _restore(m):
        return protected[int(m.group(1))]

    working = re.sub(r"___LINK_(\d+)___", _restore, working)
    return working


def build_related_block(related: list[dict], category_name: str, category_url: str | None) -> str:
    """HTML-блок «Читайте также» в конце статьи."""
    items = []
    for item in related[:RELATED_BLOCK_COUNT]:
        url = item.get("url", "")
        title = item.get("title", "")
        if url and title and _is_internal_url(url):
            items.append(f'<li><a href="{url}">{title}</a></li>')

    if category_url and _is_internal_url(category_url) and category_name:
        items.append(f'<li><a href="{category_url}">Все новости: {category_name}</a></li>')

    if not items:
        return ""

    return (
        '<h3>Читайте также</h3>'
        '<ul>'
        + "".join(items)
        + "</ul>"
    )


# ══════════════════════════════════════════════════════════════════════════════
# 1. ПАРСИНГ RSS
# ══════════════════════════════════════════════════════════════════════════════

def get_image_from_entry(entry) -> str | None:
    """Извлекает URL картинки из RSS-записи."""
    media = entry.get("media_content", [])
    if media and isinstance(media, list):
        for m in media:
            url = m.get("url", "")
            if url and any(url.lower().endswith(ext) for ext in (".jpg", ".jpeg", ".png", ".webp")):
                return url

    thumb = entry.get("media_thumbnail", [])
    if thumb and isinstance(thumb, list):
        url = thumb[0].get("url", "")
        if url:
            return url

    for enc in entry.get("enclosures", []):
        if enc.get("type", "").startswith("image/"):
            return enc.get("href") or enc.get("url")

    for field in ("summary", "description", "content"):
        text = ""
        val = entry.get(field, "")
        if isinstance(val, list):
            text = " ".join(v.get("value", "") for v in val if isinstance(v, dict))
        elif isinstance(val, str):
            text = val
        if text:
            m = re.search(r'<img[^>]+src=["\']([^"\']+)["\']', text)
            if m:
                return m.group(1)

    return None


def get_openverse_image(query: str) -> str | None:
    """Openverse — бесплатный поиск картинок без ключа."""
    try:
        resp = requests.get(
            "https://api.openverse.org/v1/images/",
            params={"q": query[:80], "page_size": 3, "license_type": "commercial"},
            headers=HEADERS,
            timeout=15,
        )
        if resp.status_code == 200:
            data = resp.json()
            for result in data.get("results", []):
                url = result.get("url") or result.get("thumbnail")
                if url and url.startswith("http"):
                    log.info("Openverse: найдена картинка")
                    return url
    except Exception as exc:
        log.warning("Openverse ошибка: %s", exc)
    return None


def get_wikimedia_image(query: str) -> str | None:
    """Wikimedia Commons — поиск без ключа."""
    try:
        resp = requests.get(
            "https://commons.wikimedia.org/w/api.php",
            params={
                "action": "query",
                "format": "json",
                "generator": "search",
                "gsrsearch": query[:60],
                "gsrlimit": 3,
                "prop": "imageinfo",
                "iiprop": "url",
                "iiurlwidth": 1200,
            },
            headers=HEADERS,
            timeout=15,
        )
        if resp.status_code == 200:
            data = resp.json()
            pages = data.get("query", {}).get("pages", {})
            for page in pages.values():
                info = page.get("imageinfo", [])
                if info:
                    url = info[0].get("thumburl") or info[0].get("url")
                    if url and url.startswith("http"):
                        log.info("Wikimedia: найдена картинка")
                        return url
    except Exception as exc:
        log.warning("Wikimedia ошибка: %s", exc)
    return None


def get_unsplash_image(query: str, category: str) -> str | None:
    """Получает URL картинки с Unsplash через Search API или fallback."""
    try:
        search_terms = query.lower()
        search_terms = re.sub(r"[^\w\s]", " ", search_terms)
        words = search_terms.split()[:2]
        search_query = " ".join(words) if words else category

        resp = requests.get(
            "https://api.unsplash.com/search/photos",
            params={
                "query": search_query,
                "per_page": 1,
                "orientation": "landscape",
            },
            timeout=10,
        )

        if resp.status_code == 200:
            data = resp.json()
            if data.get("results"):
                image_url = data["results"][0]["urls"]["regular"]
                log.info("Unsplash найдена картинка для '%s'", search_query)
                return image_url
    except Exception as exc:
        log.warning("Unsplash API ошибка: %s", exc)

    static_images = {
        "Киберспорт": "https://images.unsplash.com/photo-1542751371-adc38448a05e?w=1200&h=800&fit=crop",
        "Футбол": "https://images.unsplash.com/photo-1574629810360-7efbbe195018?w=1200&h=800&fit=crop",
        "Баскетбол": "https://images.unsplash.com/photo-1546519638-68e109498ffc?w=1200&h=800&fit=crop",
        "Хоккей": "https://images.unsplash.com/photo-1515703407324-5f753afd8be8?w=1200&h=800&fit=crop",
        "Теннис": "https://images.unsplash.com/photo-1554068865-24cecd4e34b8?w=1200&h=800&fit=crop",
    }
    image_url = static_images.get(category)
    if image_url:
        log.info("Используем статическую картинку для категории '%s'", category)
    return image_url


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


def fetch_news(max_per_category: int = 5, published_links: set = None) -> list[dict]:
    """Возвращает список новостей. Пропускает уже опубликованные."""
    if published_links is None:
        published_links = set()

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

                if link in published_links:
                    log.info("  ~ [%s] уже опубликовано: %s", category, title[:80])
                    continue

                if title and link:
                    # Openverse → Wikimedia → Unsplash static → RSS
                    search_q = title.split()[:4]
                    search_q = " ".join(search_q) if search_q else category
                    image_url = get_openverse_image(search_q)
                    if not image_url:
                        image_url = get_wikimedia_image(search_q)
                    if not image_url:
                        image_url = get_unsplash_image(title, category)
                    if not image_url:
                        image_url = get_image_from_entry(entry)

                    news_items.append({
                        "title":     title,
                        "summary":   summary,
                        "link":      link,
                        "category":  category,
                        "image_url": image_url,
                    })
                    found += 1
                    log.info("  + [%s] %s", category, title[:80])
        log.info("Итого для '%s': %d новостей", category, found)

    log.info("Всего собрано новостей: %d", len(news_items))
    random.shuffle(news_items)
    return news_items


# ══════════════════════════════════════════════════════════════════════════════
# 2. ЗАГРУЗКА КАРТИНКИ В WORDPRESS
# ══════════════════════════════════════════════════════════════════════════════


def generate_image_prompt(title: str, summary: str, category: str) -> str:
    """Генерирует промпт для картинки через Groq."""
    groq_headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": GROQ_MODEL,
        "messages": [
            {
                "role": "user",
                "content": (
                    "Напиши короткий промпт на английском (15-25 слов) для генерации реалистичной спортивной фотографии. "
                    "Тема: " + title + ". Категория: " + category + ". "
                    "Описание: " + (summary[:200] if summary else "") + ". "
                    "Стиль: professional sports photography, dynamic, high quality, no text, no logos. "
                    "Верни ТОЛЬКО промпт, без кавычек и пояснений."
                ),
            }
        ],
        "temperature": 0.6,
        "max_tokens": 80,
    }
    try:
        resp = requests.post(GROQ_API_URL, json=payload, headers=groq_headers, timeout=30)
        resp.raise_for_status()
        prompt = resp.json()["choices"][0]["message"]["content"].strip().strip('"').strip("'")
        prompt = re.sub(r"^(prompt|image prompt)\s*:\s*", "", prompt, flags=re.I).strip()
        if len(prompt) < 10:
            prompt = f"professional sports photography, {category}, dynamic action, high quality"
        log.info("Промпт для картинки: %s", prompt[:80])
        return prompt
    except Exception as exc:
        log.warning("Не удалось сгенерировать промпт: %s", exc)
        return f"professional sports photography, {category}, dynamic action, high quality"


def generate_ai_image_url(prompt: str) -> str | None:
    """Генерирует URL картинки через Pollinations.ai. Возвращает URL или None."""
    try:
        from urllib.parse import quote
        encoded = quote(prompt[:180])
        url = f"https://image.pollinations.ai/prompt/{encoded}?width=1200&height=800&nologo=true"
        # Не проверяем HEAD — сразу возвращаем URL, скачивание проверит позже
        log.info("AI-картинка URL подготовлен")
        return url
    except Exception as exc:
        log.warning("Ошибка подготовки AI-картинки: %s", exc)
    return None


def upload_image_to_wp(image_url: str, title: str, category: str = "") -> int | None:
    """Скачивает картинку и загружает в медиабиблиотеку WordPress. Возвращает media ID.
    Если AI-картинка не скачалась — пробует Unsplash."""
    auth = wp_auth()
    try:
        img_resp = requests.get(image_url, headers=HEADERS, timeout=20, allow_redirects=True)
        if img_resp.status_code != 200:
            log.warning("Не удалось скачать картинку %s: HTTP %s", image_url[:80], img_resp.status_code)
            # Fallback на Unsplash если это был AI
            if "pollinations" in (image_url or "").lower() and category:
                fallback = get_unsplash_image(title, category)
                if fallback and fallback != image_url:
                    log.info("Пробуем Unsplash fallback")
                    return upload_image_to_wp(fallback, title, category)
            return None

        content_type = img_resp.headers.get("Content-Type", "image/jpeg").split(";")[0].strip()
        if not content_type.startswith("image/"):
            log.warning("URL вернул не картинку, а %s", content_type)
            return None

        ext = "jpg"
        if "png" in content_type:
            ext = "png"
        elif "webp" in content_type:
            ext = "webp"

        safe_title = re.sub(r"[^\w\s-]", "", title)[:50].strip().replace(" ", "-").lower()
        filename = f"{safe_title}.{ext}"

        # ASCII-only filename to avoid latin-1 header errors
        safe_name = re.sub(r"[^a-z0-9\-]", "-", transliterate(title).lower())[:50].strip("-") or "news"
        upload_headers = {
            "Content-Disposition": f'attachment; filename="{safe_name}.jpg"',
            "Content-Type": content_type,
        }
        resp = requests.post(
            f"{WP_URL}/wp-json/wp/v2/media",
            data=img_resp.content,
            headers=upload_headers,
            auth=auth,
            timeout=30,
        )
        resp.raise_for_status()
        media_id = resp.json().get("id")
        log.info("Картинка загружена: media_id=%s", media_id)
        return media_id
    except Exception as exc:
        log.warning("Ошибка загрузки картинки: %s", exc)
        return None


# ══════════════════════════════════════════════════════════════════════════════
# 3. ГЕНЕРАЦИЯ ТЕКСТА ЧЕРЕЗ GROQ
# ══════════════════════════════════════════════════════════════════════════════

GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"
GROQ_MODEL   = "openai/gpt-oss-20b"

SYSTEM_PROMPT = (
    "Ты опытный спортивный журналист. ВСЕГДА пишешь ТОЛЬКО на русском языке. "
    "Пишешь ОРИГИНАЛЬНЫЕ новости: не пересказывай источник дословно, а создавай свой текст на основе фактов. "
    "Пишешь живые, интересные новостные статьи для спортивного сайта. "
    "Тон: профессиональный, но доступный. "
    "Структура: вводный абзац с главным фактом, 2-3 абзаца с деталями и контекстом, краткий итог. "
    "Без воды и лишних слов. Используй только HTML теги: <p>, <b>, <ul>, <li>, <a>. "
    "Не добавляй заголовок — он передаётся отдельно. "
    "Не выдумывай ссылки. Если даны внутренние страницы сайта — можешь обернуть подходящее слово в <a href=\"URL\">анкор</a>, "
    "но только используя URL из списка. Не больше двух ссылок в тексте."
)


def translate_title_to_russian(title: str) -> str:
    """Переводит заголовок на русский язык через Groq."""
    groq_headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type":  "application/json",
    }
    payload = {
        "model":       GROQ_MODEL,
        "messages":    [
            {
                "role": "user",
                "content": (
                    "Переведи этот заголовок на русский язык, сохраняя суть. "
                    "Верни ТОЛЬКО перевод, без кавычек и без объяснений:\n\n" + title
                ),
            },
        ],
        "temperature": 0.5,
        "max_tokens":  150,
    }

    try:
        resp = requests.post(GROQ_API_URL, json=payload, headers=groq_headers, timeout=30)
        resp.raise_for_status()
        translated = resp.json()["choices"][0]["message"]["content"].strip().strip('"').strip("'")
        # Убираем префиксы вроде "Перевод:"
        translated = re.sub(r"^(перевод|title|заголовок)\s*:\s*", "", translated, flags=re.I).strip()
        if not translated or len(translated) < 5:
            return title
        log.info("Заголовок переведён: '%s' → '%s'", title[:50], translated[:50])
        return translated
    except Exception as exc:
        log.warning("Ошибка перевода заголовка: %s, используем оригинал", exc)
        return title


def extract_focus_keyword(title: str, summary: str) -> str:
    """Извлекает фокусный ключевик из заголовка (первые 2-3 слова)."""
    stop_words = {
        "the", "a", "an", "and", "or", "in", "at", "to", "for", "of", "is", "are",
        "was", "were", "be", "been", "и", "в", "на", "по", "за", "от", "до", "из",
    }

    words = title.lower().split()
    keywords = [w.strip(".,!?:;—-") for w in words[:6] if w.strip(".,!?:;—-") not in stop_words and len(w) > 2]

    if keywords:
        focus_keyword = " ".join(keywords[:3])
        log.info("Фокусный ключевик: '%s'", focus_keyword)
        return focus_keyword

    return title[:50]


def generate_article(news: dict, related: list[dict] | None = None) -> str | None:
    """Генерирует HTML-текст статьи через Groq API."""
    related = related or []
    links_hint = ""
    if related:
        lines = "\n".join(f"- {item['title']}: {item['url']}" for item in related[:5])
        links_hint = (
            "\n\nВнутренние страницы этого сайта (используй ТОЛЬКО эти URL, не выдумывай):\n"
            f"{lines}\n"
            "Если уместно, оберни 1-2 естественных словосочетания в ссылку <a href=\"URL\">текст</a>. "
            "Не ставь ссылки списком в конце — это будет добавлено отдельно."
        )

    user_prompt = (
        f"Категория: {news['category']}\n"
        f"Заголовок новости: {news['title']}\n"
        f"Краткое описание: {news['summary']}\n"
        f"Источник: {news['link']}\n\n"
        "Напиши ОРИГИНАЛЬНУЮ новостную статью на русском языке по этой теме. "
        "Не копируй текст источника — перескажи факты своими словами, добавь контекст и анализ. "
        "Объём: 280-450 слов. Возвращай только HTML-контент статьи без заголовка."
        + links_hint
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
        log.info("Groq: сгенерировано %d символов для '%s'", len(content), news["title"][:50])
        return content
    except Exception as exc:
        log.error("Groq ошибка для '%s': %s", news["title"], exc)
        return None


def sanitize_external_invented_links(content: str, allowed_urls: set[str]) -> str:
    """Удаляет ВСЕ выдуманные Groq ссылки. Оставляет только внутренние из белого списка."""
    def _repl(m):
        href = m.group(1)
        inner = m.group(2)
        if href in allowed_urls or _is_internal_url(href):
            return m.group(0)
        # Оставляем текст, убираем плохую ссылку
        return inner

    return re.sub(r'<a\s+[^>]*href=["\']([^"\']+)["\'][^>]*>(.*?)</a>', _repl, content, flags=re.I | re.S)


# ══════════════════════════════════════════════════════════════════════════════
# 4. WORDPRESS REST API
# ══════════════════════════════════════════════════════════════════════════════

def get_or_create_category(name: str) -> int:
    """Возвращает ID категории WordPress, создаёт если не существует."""
    if name in CATEGORY_MAP:
        return CATEGORY_MAP[name]

    auth = wp_auth()
    base = f"{WP_URL}/wp-json/wp/v2/categories"

    try:
        resp = requests.get(base, params={"search": name, "per_page": 5}, auth=auth, timeout=30)
        resp.raise_for_status()
        for cat in resp.json():
            if cat["name"].lower() == name.lower():
                CATEGORY_MAP[name] = cat["id"]
                if cat.get("link"):
                    CATEGORY_URLS[name] = cat["link"]
                log.info("Найдена категория '%s' → id=%d", name, cat["id"])
                return cat["id"]
    except Exception as exc:
        log.warning("Поиск категории '%s': %s", name, exc)

    try:
        resp = requests.post(base, json={"name": name}, auth=auth, timeout=30)
        resp.raise_for_status()
        cat_id = resp.json()["id"]
        CATEGORY_MAP[name] = cat_id
        if resp.json().get("link"):
            CATEGORY_URLS[name] = resp.json()["link"]
        log.info("Создана категория '%s' → id=%d", name, cat_id)
        return cat_id
    except Exception as exc:
        log.error("Создание категории '%s': %s", name, exc)
        return 1

def transliterate(text: str) -> str:
    """Транслитерация русского текста в латиницу."""
    if not text:
        return ""

    # Простая транслитерация (можно расширить)
    translit = {
        "а": "a", "б": "b", "в": "v", "г": "g", "д": "d", "е": "e",
        "ё": "yo", "ж": "zh", "з": "z", "и": "i", "й": "y", "к": "k",
        "л": "l", "м": "m", "н": "n", "о": "o", "п": "p", "р": "r",
        "с": "s", "т": "t", "у": "u", "ф": "f", "х": "kh", "ц": "ts",
        "ч": "ch", "ш": "sh", "щ": "shch", "ъ": "", "ы": "y", "ь": "",
        "э": "e", "ю": "yu", "я": "ya",
        "А": "A", "Б": "B", "В": "V", "Г": "G", "Д": "D", "Е": "E",
        "Ё": "Yo", "Ж": "Zh", "З": "Z", "И": "I", "Й": "Y", "К": "K",
        "Л": "L", "М": "M", "Н": "N", "О": "O", "П": "P", "Р": "R",
        "С": "S", "Т": "T", "У": "U", "Ф": "F", "Х": "Kh", "Ц": "Ts",
        "Ч": "Ch", "Ш": "Sh", "Щ": "Shch", "Ъ": "", "Ы": "Y", "Ь": "",
        "Э": "E", "Ю": "Yu", "Я": "Ya",
    }

    result = []
    for char in text:
        result.append(translit.get(char, char))

    # Убираем лишние пробелы и делаем безопасный slug
    slug = "".join(result).lower()
    slug = re.sub(r"[^a-z0-9\-]", "-", slug)
    slug = re.sub(r"-+", "-", slug)
    slug = slug.strip("-")

    return slug or "news"


def publish_post(news: dict, content: str, related: list[dict]) -> bool:
    """Публикует пост с транслитерированным slug."""
    auth     = wp_auth()
    endpoint = f"{WP_URL}/wp-json/wp/v2/posts"
    cat_id   = get_or_create_category(news["category"])
    cat_url  = CATEGORY_URLS.get(news["category"])

    russian_title = translate_title_to_russian(news["title"])

    if not russian_title or russian_title.strip() == "" or len(russian_title) < 5:
        log.warning("Заголовок не переведён или слишком короткий: '%s', пропускаем", russian_title)
        return False

    if not re.search(r"[А-Яа-яЁё]", russian_title):
        log.warning("Заголовок без кириллицы, пропускаем: '%s'", russian_title)
        return False

    focus_keyword = extract_focus_keyword(russian_title, news["summary"])

    media_id = None
    if news.get("image_url"):
        media_id = upload_image_to_wp(news["image_url"], russian_title, news.get("category", ""))

    allowed_urls = {item["url"] for item in related if item.get("url")}
    if cat_url:
        allowed_urls.add(cat_url)
    allowed_urls.add(news["link"])

    content = sanitize_external_invented_links(content, allowed_urls)
    content = inject_inline_links(content, related, news["category"], cat_url)
    related_block = build_related_block(related, news["category"], cat_url)

    # Транслитерация для slug (ЧПУ)
    slug = transliterate(russian_title)

    footer = (
        f'{related_block}'
        f'<p><small>Источник: <a href="{news["link"]}" '
        f'target="_blank" rel="nofollow noopener">{news["link"]}</a></small></p>'
    )

    post_data = {
        "title":      russian_title,
        "content":    content + footer,
        "status":     "publish",
        "categories": [cat_id],
        "date":       datetime.now(timezone.utc).isoformat(),
        "slug":       slug,                    # ← транслитерация для ЧПУ
        "meta": {
            "rank_math_focus_keyword": focus_keyword,
            "rank_math_title": russian_title,
            "rank_math_description": (news["summary"] or russian_title)[:160],
            "_yoast_wpseo_focuskw": focus_keyword,
            "keywords": focus_keyword,
            "source_url": news["link"],
        },
    }

    if media_id:
        post_data["featured_media"] = media_id

    try:
        resp = requests.post(endpoint, json=post_data, auth=auth, timeout=30)
        resp.raise_for_status()
        post_id  = resp.json().get("id")
        post_url = resp.json().get("link")

        log.info(
            "ОПУБЛИКОВАН пост #%s (slug=%s): %s",
            post_id, slug, post_url
        )
        log.info("Заголовок (RU): '%s'", russian_title)
        log.info("Фокусный ключевик (Rank Math): '%s'", focus_keyword)
        log.info("Внутренних ссылок в блоке «Читайте также»: %d", min(len(related), RELATED_BLOCK_COUNT))
        return True
    except requests.HTTPError as exc:
        log.error(
            "HTTP %s при публикации '%s': %s",
            exc.response.status_code, russian_title, exc.response.text[:500]
        )
        return False
    except Exception as exc:
        log.error("Ошибка публикации '%s': %s", russian_title, exc)
        return False

# ══════════════════════════════════════════════════════════════════════════════
# 5. ГЛАВНЫЙ ЦИКЛ
# ══════════════════════════════════════════════════════════════════════════════

def run() -> None:
    log.info("=== Запуск автопостинга (%s) ===", datetime.now().strftime("%Y-%m-%d %H:%M"))
    log.info("WordPress URL: %s", WP_URL)
    log.info("Пользователь: %s", WP_USER)

    published_links = load_published_history()
    internal = fetch_internal_content()

    all_news  = fetch_news(max_per_category=5, published_links=published_links)
    published = 0

    if not all_news:
        log.error("Новые новости не найдены! Все RSS-ленты недоступны или все новости уже опубликованы.")
        return

    for news in all_news:
        if published >= POSTS_PER_RUN:
            break

        log.info("→ Обрабатываем: [%s] %s", news["category"], news["title"])

        related = select_related_links(news, internal, limit=5)

        content = generate_article(news, related=related)
        if not content:
            log.warning("Groq не вернул контент, пропускаем")
            continue

        if not content.strip() or len(content) < 50:
            log.warning("Контент слишком короткий или пустой (%d символов), пропускаем", len(content))
            continue

        success = publish_post(news, content, related)
        if success:
            published += 1
            published_links.add(news["link"])
            save_published_history(published_links)

        time.sleep(3)

    log.info("=== Готово: опубликовано %d/%d статей ===", published, POSTS_PER_RUN)


if __name__ == "__main__":
    run()
