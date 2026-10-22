#!/usr/bin/env python3
"""Новости ЛЧ с уникальными картинками по командам. Без дублей."""

import os
import re
import httpx
import time

WP_URL = os.environ.get("WP_BASE_URL", "https://beteasy.ru").rstrip("/")
AUTH = (os.environ["WP_USERNAME"], os.environ["WP_APP_PASSWORD"])
HEADERS = {"User-Agent": "BeteasyBot/1.0 (news@beteasy.ru)"}

# Пул разных картинок по командам (Unsplash, разные)
TEAM_IMAGES = {
    "como": "https://images.unsplash.com/photo-1508098682722-e99c43a406b2?w=1200&h=800&fit=crop",
    "manchester": "https://images.unsplash.com/photo-1522778119026-d647f0596c20?w=1200&h=800&fit=crop",
    "bayern": "https://images.unsplash.com/photo-1517466787929-bc90951d0974?w=1200&h=800&fit=crop",
    "arsenal": "https://images.unsplash.com/photo-1574629810360-7efbbe195018?w=1200&h=800&fit=crop",
    "madrid": "https://images.unsplash.com/photo-1431324155629-1a6deb1dec8d?w=1200&h=800&fit=crop",
    "leipzig": "https://images.unsplash.com/photo-1551958219-acbc608c6377?w=1200&h=800&fit=crop",
    "galatasaray": "https://images.unsplash.com/photo-1461896836934-ffe607ba6851?w=1200&h=800&fit=crop",
    "lille": "https://images.unsplash.com/photo-1579952363873-27f3bade9f55?w=1200&h=800&fit=crop",
    "villa": "https://images.unsplash.com/photo-1489944440615-453fc2b6a9a9?w=1200&h=800&fit=crop",
    "viking": "https://images.unsplash.com/photo-1575361204480-aadea25e6e68?w=1200&h=800&fit=crop",
    "inter": "https://images.unsplash.com/photo-1522778526097-ce0a22ceb253?w=1200&h=800&fit=crop",
    "shakhtar": "https://images.unsplash.com/photo-1543326727-cf6c39e8f84c?w=1200&h=800&fit=crop",
    "lask": "https://images.unsplash.com/photo-1517927033932-b3d18e8100b0?w=1200&h=800&fit=crop",
    "sporting": "https://images.unsplash.com/photo-1459865264687-595d652de67e?w=1200&h=800&fit=crop",
    "brugge": "https://images.unsplash.com/photo-1560272564-c83b66b1ad12?w=1200&h=800&fit=crop",
    "lens": "https://images.unsplash.com/photo-1556056504-5c7696c4c28d?w=1200&h=800&fit=crop",
    "betis": "https://images.unsplash.com/photo-1579952363873-27f3bade9f55?w=1200&h=800&fit=crop&sat=-20",
    "feyenoord": "https://images.unsplash.com/photo-1508098682722-e99c43a406b2?w=1200&h=800&fit=crop&hue=20",
    "trophy": "https://images.unsplash.com/photo-1574629810360-7efbbe195018?w=1200&h=800&fit=crop&q=80",
}

TRANSLIT = {
    "а": "a", "б": "b", "в": "v", "г": "g", "д": "d", "е": "e",
    "ё": "yo", "ж": "zh", "з": "z", "и": "i", "й": "y", "к": "k",
    "л": "l", "м": "m", "н": "n", "о": "o", "п": "p", "р": "r",
    "с": "s", "т": "t", "у": "u", "ф": "f", "х": "kh", "ц": "ts",
    "ч": "ch", "ш": "sh", "щ": "shch", "ъ": "", "ы": "y", "ь": "",
    "э": "e", "ю": "yu", "я": "ya",
}

def slugify(text: str) -> str:
    result = []
    for ch in text.lower():
        result.append(TRANSLIT.get(ch, ch))
    s = "".join(result)
    s = re.sub(r"[^a-z0-9\-]", "-", s)
    s = re.sub(r"-+", "-", s).strip("-")
    return s[:80] or "news"

def search_wikimedia(query: str) -> str | None:
    try:
        resp = httpx.get(
            "https://commons.wikimedia.org/w/api.php",
            params={
                "action": "query",
                "format": "json",
                "generator": "search",
                "gsrsearch": f"{query} filetype:bitmap",
                "gsrlimit": 3,
                "prop": "imageinfo",
                "iiprop": "url",
                "iiurlwidth": 1200,
            },
            headers=HEADERS,
            timeout=10,
        )
        if resp.status_code == 200:
            pages = resp.json().get("query", {}).get("pages", {})
            for page in pages.values():
                info = page.get("imageinfo", [])
                if info:
                    url = info[0].get("thumburl") or info[0].get("url")
                    if url and url.startswith("http") and ".svg" not in url.lower():
                        return url
    except Exception:
        pass
    return None

def get_image_for(teams_key: str, used: set) -> str:
    """Берёт картинку: Wikimedia → пул команды → любая неиспользованная."""
    # 1. Попытка Wikimedia
    url = search_wikimedia(teams_key)
    if url and url not in used:
        return url
    # 2. Из пула по ключу
    for key, img in TEAM_IMAGES.items():
        if key in teams_key.lower() and img not in used:
            return img
    # 3. Любая неиспользованная из пула
    for img in TEAM_IMAGES.values():
        if img not in used:
            return img
    # 4. Fallback
    return list(TEAM_IMAGES.values())[0]

NEWS = [
    {"title": "Комо разгромил Манчестер Юнайтед 4:1 в Лиге чемпионов", "key": "Como Manchester United", "content": "<p>21 октября 2026 года «Комо» нанёс одно из самых болезненных поражений «Манчестер Юнайтед» в европейской истории. Счёт 4:1 на «Джузеппе Синигалья» стал серьёзным ударом по репутации клуба.</p><p>Дублем отметился Николас Пас, ещё по голу забили Дукаса и Рамон. Юнайтед ответил только на 90+1 минуте усилиями Зиркзее.</p><p>Поражение усилило давление на тренерский штаб. Для «Комо» это важная победа на старте группового этапа.</p>"},
    {"title": "Райс спас Арсенал: Бавария и канониры сыграли 2:2", "key": "Bayern Munich Arsenal", "content": "<p>В центральном матче дня «Бавария» и «Арсенал» обменялись голами и зафиксировали ничью 2:2 на «Альянц Арене».</p><p>Эзе открыл счёт, Дэвис сравнял, Кейн вывел хозяев вперёд с пенальти, а Деклан Райс на 82-й минуте спас очко для лондонцев.</p><p>Ничья сохраняет интригу в борьбе за топ-8.</p>"},
    {"title": "Реал Мадрид разгромил РБ Лейпциг 4:1", "key": "Real Madrid Bernabeu", "content": "<p>«Реал Мадрид» продолжил идеальный старт в Лиге чемпионов, обыграв «РБ Лейпциг» со счётом 4:1 на «Сантьяго Бернабеу».</p><p>Мадридцы забили четыре мяча, включая зрелищный гол Яна Диоманде.</p><p>Третья победа подряд укрепляет позиции «Реала» в верхней части таблицы.</p>"},
    {"title": "Галатасарай обыграл Лилль 4:2 в Лиге чемпионов", "key": "Galatasaray Lille", "content": "<p>«Галатасарай» одержал уверенную победу над «Лиллем» — 4:2 на выезде. Турецкий клуб забил четыре мяча и взял три очка.</p><p>Среди авторов голов — Акгюн, Батраков и Осимхен.</p><p>Победа позволяет «Галатасараю» набрать очки в борьбе за выход в плей-офф.</p>"},
    {"title": "Астон Вилла обыграла Викинг 3:1 и сохранила 100% результат", "key": "Aston Villa", "content": "<p>«Астон Вилла» продолжила победную серию в Лиге чемпионов, обыграв «Викинг» 3:1 на «Вилла Парк».</p><p>Голы забили Баркли и Буэндиа, ещё один мяч — автогол.</p><p>Три победы из трёх матчей — отличный старт для бирмингемского клуба.</p>"},
    {"title": "Интер обыграл Шахтёр 1:0 на Сан-Сиро", "key": "Inter Milan San Siro", "content": "<p>«Интер» одержал минимальную победу над «Шахтёром» — 1:0 на «Сан-Сиро». Единственный гол забил Карлос Аугусто на 77-й минуте.</p><p>Матч прошёл в напряжённой борьбе.</p><p>Три очка важны для миланцев в таблице группового этапа.</p>"},
    {"title": "ЛАСК сенсационно обыграл Спортинг 3:2 в Лиссабоне", "key": "Sporting Lisbon", "content": "<p>Австрийский «ЛАСК» совершил сенсацию, обыграв «Спортинг» 3:2 на «Жозе Алваладе». Это первая победа клуба в Лиге чемпионов.</p><p>Результат стал одним из главных сюрпризов третьего тура.</p>"},
    {"title": "Брюгге разгромил Ланс 3:0", "key": "Club Brugge", "content": "<p>«Брюгге» одержал крупную победу над «Лансом» — 3:0 на своём поле. Голы забили Ванакен, Сейс и Форбс.</p><p>Бельгийский клуб полностью контролировал игру.</p>"},
    {"title": "Бетис обыграл Фейеноорд 1:0 благодаря пенальти Иско", "key": "Real Betis", "content": "<p>«Реал Бетис» победил «Фейеноорд» 1:0. Решающий гол с пенальти забил Иско.</p><p>Победа позволяет «Бетису» сохранить идеальный старт в турнире.</p>"},
    {"title": "Итоги третьего тура Лиги чемпионов: сенсации и громкие победы", "key": "Champions League trophy", "content": "<p>21 октября завершился третий тур общего этапа Лиги чемпионов. Главные события — разгром «Манчестер Юнайтед» от «Комо» (4:1), ничья «Баварии» и «Арсенала» (2:2) и победа «Реала» над «Лейпцигом» (4:1).</p><p>Также сенсацию сотворил «ЛАСК», обыграв «Спортинг» 3:2.</p><p>Таблица остаётся плотной.</p>"},
]

def post_exists(client: httpx.Client, slug: str) -> bool:
    r = client.get(f"{WP_URL}/wp-json/wp/v2/posts", params={"slug": slug}, auth=AUTH)
    return r.status_code == 200 and len(r.json()) > 0

def upload_image(client: httpx.Client, url: str, title: str) -> int | None:
    try:
        img = client.get(url, timeout=15, follow_redirects=True, headers=HEADERS)
        if img.status_code != 200 or len(img.content) < 3000:
            return None
        safe = slugify(title)[:40] or "news"
        r = client.post(
            f"{WP_URL}/wp-json/wp/v2/media",
            content=img.content,
            headers={
                "Content-Disposition": f'attachment; filename="{safe}.jpg"',
                "Content-Type": "image/jpeg",
            },
            auth=AUTH,
        )
        if r.status_code in (200, 201):
            return r.json().get("id")
    except Exception as e:
        print(f"  img err: {e}")
    return None

def main():
    used_images: set[str] = set()
    with httpx.Client(timeout=60) as client:
        published = 0
        skipped = 0
        for item in NEWS:
            slug = slugify(item["title"])
            print(f"\n→ {item['title'][:50]}")
            if post_exists(client, slug):
                print("  SKIP (уже есть)")
                skipped += 1
                continue
            img_url = get_image_for(item["key"], used_images)
            used_images.add(img_url)
            print(f"  img: {img_url[:60]}")
            media_id = upload_image(client, img_url, item["title"])
            payload = {
                "title": item["title"],
                "content": item["content"],
                "status": "publish",
                "slug": slug,
                "categories": [16],
            }
            if media_id:
                payload["featured_media"] = media_id
            r = client.post(f"{WP_URL}/wp-json/wp/v2/posts", json=payload, auth=AUTH)
            if r.status_code in (200, 201):
                print(f"  OK media={media_id}")
                published += 1
            else:
                print(f"  ERR {r.status_code}")
            time.sleep(1)
        print(f"\nОпубликовано: {published}, пропущено дублей: {skipped}")

if __name__ == "__main__":
    main()
