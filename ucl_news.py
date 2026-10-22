#!/usr/bin/env python3
"""Публикует новости ЛЧ с поиском релевантных картинок (Wikimedia + Openverse)."""

import os
import re
import httpx

WP_URL = os.environ.get("WP_BASE_URL", "https://beteasy.ru").rstrip("/")
AUTH = (os.environ["WP_USERNAME"], os.environ["WP_APP_PASSWORD"])
HEADERS = {"User-Agent": "BeteasyNewsBot/1.0"}

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
    """Поиск картинки в Wikimedia Commons."""
    try:
        resp = httpx.get(
            "https://commons.wikimedia.org/w/api.php",
            params={
                "action": "query",
                "format": "json",
                "generator": "search",
                "gsrsearch": query[:80],
                "gsrlimit": 5,
                "prop": "imageinfo",
                "iiprop": "url",
                "iiurlwidth": 1200,
            },
            headers=HEADERS,
            timeout=15,
        )
        if resp.status_code == 200:
            pages = resp.json().get("query", {}).get("pages", {})
            for page in pages.values():
                info = page.get("imageinfo", [])
                if info:
                    url = info[0].get("thumburl") or info[0].get("url")
                    if url and url.startswith("http") and not url.endswith(".svg"):
                        return url
    except Exception:
        pass
    return None

def search_openverse(query: str) -> str | None:
    """Поиск в Openverse."""
    try:
        resp = httpx.get(
            "https://api.openverse.org/v1/images/",
            params={"q": query[:80], "page_size": 3, "license_type": "commercial"},
            headers=HEADERS,
            timeout=12,
        )
        if resp.status_code == 200:
            for result in resp.json().get("results", []):
                url = result.get("url")
                if url and url.startswith("http"):
                    return url
    except Exception:
        pass
    return None

def find_image(title: str, teams: str) -> str:
    """Ищет картинку по теме. Fallback на общий футбол."""
    queries = [
        teams,
        title.split(":")[0] if ":" in title else title,
        "football stadium champions league",
    ]
    for q in queries:
        url = search_wikimedia(q)
        if url:
            return url
        url = search_openverse(q)
        if url:
            return url
    # Fallback
    return "https://images.unsplash.com/photo-1574629810360-7efbbe195018?w=1200&h=800&fit=crop"

NEWS = [
    {"title": "Комо разгромил Манчестер Юнайтед 4:1 в Лиге чемпионов", "teams": "Como Manchester United", "content": "<p>21 октября 2026 года «Комо» нанёс одно из самых болезненных поражений «Манчестер Юнайтед» в европейской истории. Счёт 4:1 на «Джузеппе Синигалья» стал серьёзным ударом по репутации клуба.</p><p>Дублем отметился Николас Пас, ещё по голу забили Дукаса и Рамон. Юнайтед ответил только на 90+1 минуте усилиями Зиркзее.</p><p>Поражение усилило давление на тренерский штаб. Для «Комо» это важная победа на старте группового этапа.</p>"},
    {"title": "Райс спас Арсенал: Бавария и канониры сыграли 2:2", "teams": "Bayern Munich Arsenal Allianz Arena", "content": "<p>В центральном матче дня «Бавария» и «Арсенал» обменялись голами и зафиксировали ничью 2:2 на «Альянц Арене».</p><p>Эзе открыл счёт, Дэвис сравнял, Кейн вывел хозяев вперёд с пенальти, а Деклан Райс на 82-й минуте спас очко для лондонцев.</p><p>Ничья сохраняет интригу в борьбе за топ-8.</p>"},
    {"title": "Реал Мадрид разгромил РБ Лейпциг 4:1", "teams": "Real Madrid Bernabeu", "content": "<p>«Реал Мадрид» продолжил идеальный старт в Лиге чемпионов, обыграв «РБ Лейпциг» со счётом 4:1 на «Сантьяго Бернабеу».</p><p>Мадридцы забили четыре мяча, включая зрелищный гол Яна Диоманде.</p><p>Третья победа подряд укрепляет позиции «Реала» в верхней части таблицы.</p>"},
    {"title": "Галатасарай обыграл Лилль 4:2 в Лиге чемпионов", "teams": "Galatasaray Lille", "content": "<p>«Галатасарай» одержал уверенную победу над «Лиллем» — 4:2 на выезде. Турецкий клуб забил четыре мяча и взял три очка.</p><p>Среди авторов голов — Акгюн, Батраков и Осимхен.</p><p>Победа позволяет «Галатасараю» набрать очки в борьбе за выход в плей-офф.</p>"},
    {"title": "Астон Вилла обыграла Викинг 3:1 и сохранила 100% результат", "teams": "Aston Villa Park", "content": "<p>«Астон Вилла» продолжила победную серию в Лиге чемпионов, обыграв «Викинг» 3:1 на «Вилла Парк».</p><p>Голы забили Баркли и Буэндиа, ещё один мяч — автогол.</p><p>Три победы из трёх матчей — отличный старт для бирмингемского клуба.</p>"},
    {"title": "Интер обыграл Шахтёр 1:0 на Сан-Сиро", "teams": "Inter Milan San Siro", "content": "<p>«Интер» одержал минимальную победу над «Шахтёром» — 1:0 на «Сан-Сиро». Единственный гол забил Карлос Аугусто на 77-й минуте.</p><p>Матч прошёл в напряжённой борьбе.</p><p>Три очка важны для миланцев в таблице группового этапа.</p>"},
    {"title": "ЛАСК сенсационно обыграл Спортинг 3:2 в Лиссабоне", "teams": "Sporting Lisbon stadium", "content": "<p>Австрийский «ЛАСК» совершил сенсацию, обыграв «Спортинг» 3:2 на «Жозе Алваладе». Это первая победа клуба в Лиге чемпионов.</p><p>Результат стал одним из главных сюрпризов третьего тура.</p>"},
    {"title": "Брюгге разгромил Ланс 3:0", "teams": "Club Brugge stadium", "content": "<p>«Брюгге» одержал крупную победу над «Лансом» — 3:0 на своём поле. Голы забили Ванакен, Сейс и Форбс.</p><p>Бельгийский клуб полностью контролировал игру.</p>"},
    {"title": "Бетис обыграл Фейеноорд 1:0 благодаря пенальти Иско", "teams": "Real Betis Sevilla", "content": "<p>«Реал Бетис» победил «Фейеноорд» 1:0. Решающий гол с пенальти забил Иско.</p><p>Победа позволяет «Бетису» сохранить идеальный старт в турнире.</p>"},
    {"title": "Итоги третьего тура Лиги чемпионов: сенсации и громкие победы", "teams": "Champions League trophy", "content": "<p>21 октября завершился третий тур общего этапа Лиги чемпионов. Главные события — разгром «Манчестер Юнайтед» от «Комо» (4:1), ничья «Баварии» и «Арсенала» (2:2) и победа «Реала» над «Лейпцигом» (4:1).</p><p>Также сенсацию сотворил «ЛАСК», обыграв «Спортинг» 3:2.</p><p>Таблица остаётся плотной.</p>"},
]

def upload_image(client: httpx.Client, url: str, title: str) -> int | None:
    try:
        img = client.get(url, timeout=20, follow_redirects=True, headers=HEADERS)
        if img.status_code != 200 or len(img.content) < 5000:
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
        print(f"  upload err: {e}")
    return None

def main():
    with httpx.Client(timeout=60) as client:
        published = 0
        for item in NEWS:
            print(f"\n→ {item['title'][:55]}")
            img_url = find_image(item["title"], item["teams"])
            print(f"  image: {img_url[:70]}")
            media_id = upload_image(client, img_url, item["title"])
            payload = {
                "title": item["title"],
                "content": item["content"],
                "status": "publish",
                "slug": slugify(item["title"]),
                "categories": [16],
            }
            if media_id:
                payload["featured_media"] = media_id
                print(f"  media_id={media_id}")
            r = client.post(f"{WP_URL}/wp-json/wp/v2/posts", json=payload, auth=AUTH)
            if r.status_code in (200, 201):
                print(f"  OK → {r.json().get('link','')}")
                published += 1
            else:
                print(f"  ERR {r.status_code}")
        print(f"\nОпубликовано: {published}/10")

if __name__ == "__main__":
    main()
