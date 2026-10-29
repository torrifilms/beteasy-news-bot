#!/usr/bin/env python3
"""Expand FAQ with detailed answers."""

import os
import httpx
import re

WP_URL = os.environ.get("WP_URL", "https://beteasy.ru").rstrip("/")
AUTH = (os.environ.get("WP_USER", ""), os.environ.get("WP_APP_PASS", ""))

NEW_FAQ = '''
<div class="tp-box" itemscope itemtype="https://schema.org/FAQPage">
<h3>FAQ</h3>
<div class="tp-faq" itemscope itemprop="mainEntity" itemtype="https://schema.org/Question">
<b itemprop="name">Кто тренер Реала в сезоне 2026/27?</b>
<div itemscope itemprop="acceptedAnswer" itemtype="https://schema.org/Answer">
<p itemprop="text">Главный тренер «Реал Мадрид» в сезоне 2026/27 — Жозе Моуринью. Португальский специалист вернулся в клуб после успешной работы в других европейских командах. Под его руководством «Реал» выиграл Лигу чемпионов в 2010 году и несколько титулов Ла Лиги. Моуринью известен своей тактической гибкостью и умением настраивать команду на важные матчи.</p>
</div>
</div>
<div class="tp-faq" itemscope itemprop="mainEntity" itemtype="https://schema.org/Question">
<b itemprop="name">Сколько титулов Лиги чемпионов у Реал Мадрид?</b>
<div itemscope itemprop="acceptedAnswer" itemtype="https://schema.org/Answer">
<p itemprop="text">«Реал Мадрид» — абсолютный рекордсмен по числу побед в Лиге чемпионов УЕФА. На счету клуба 15 трофеев главного европейского турнира. Первый титул был завоёван в 1956 году, а последний — в 2024 году. Ближайший преследователь — «Милан» с 7 победами. «Реал» также является рекордсменом по количеству финалов ЛЧ.</p>
</div>
</div>
<div class="tp-faq" itemscope itemprop="mainEntity" itemtype="https://schema.org/Question">
<b itemprop="name">Какой стадион у Реал Мадрид и сколько он вмещает?</b>
<div itemscope itemprop="acceptedAnswer" itemtype="https://schema.org/Answer">
<p itemprop="text">Домашний стадион «Реал Мадрид» — «Сантьяго Бернабеу», расположенный в центре Мадрида. После масштабной реконструкции 2023–2024 годов вместимость арены составляет около 81 000 зрителей. Стадион назван в честь легендарного президента клуба Сантьяго Бернабеу, который руководил командой с 1943 по 1978 год. Арена принимает матчи Ла Лиги, Лиги чемпионов и финалы международных турниров.</p>
</div>
</div>
<div class="tp-faq" itemscope itemprop="mainEntity" itemtype="https://schema.org/Question">
<b itemprop="name">Кто капитан Реал Мадрид в 2026 году?</b>
<div itemscope itemprop="acceptedAnswer" itemtype="https://schema.org/Answer">
<p itemprop="text">Капитан «Реал Мадрид» — Начо Фернандес, воспитанник академии клуба. Игрок провёл всю карьеру в «Реале» и является одним из самых преданных футболистов команды. Вице-капитаны — Лука Модрич и Дани Карвахаль. Начо отличается универсальностью: может сыграть как в центре обороны, так и на флангах.</p>
</div>
</div>
<div class="tp-faq" itemscope itemprop="mainEntity" itemtype="https://schema.org/Question">
<b itemprop="name">В каких турнирах выступает Реал Мадрид?</b>
<div itemscope itemprop="acceptedAnswer" itemtype="https://schema.org/Answer">
<p itemprop="text">«Реал Мадрид» выступает в двух основных турнирах: Ла Лига (чемпионат Испании) и Лига чемпионов УЕФА. Также клуб участвует в Кубке Испании (Копа дель Рей) и Суперкубке Испании. В сезоне 2026/27 команда занимает 3-е место в Ла Лиге с 24 очками после 10 туров и успешно выступает в групповом этапе Лиги чемпионов.</p>
</div>
</div>
<div class="tp-faq" itemscope itemprop="mainEntity" itemtype="https://schema.org/Question">
<b itemprop="name">Кто лучший бомбардир Реала в сезоне 2026/27?</b>
<div itemscope itemprop="acceptedAnswer" itemtype="https://schema.org/Answer">
<p itemprop="text">Лучший бомбардир «Реал Мадрид» в сезоне 2026/27 — Килиан Мбаппе. Французский нападающий забил 11 голов в 10 матчах Ла Лиги и продолжает забивать в Лиге чемпионов. Мбаппе перешёл в «Реал» летом 2024 года и сразу стал ключевым игроком атаки. Его скорость и техника делают его одним из лучших форвардов мира.</p>
</div>
</div>
<div class="tp-faq" itemscope itemprop="mainEntity" itemtype="https://schema.org/Question">
<b itemprop="name">Какая форма у Реала в последних матчах?</b>
<div itemscope itemprop="acceptedAnswer" itemtype="https://schema.org/Answer">
<p itemprop="text">«Реал Мадрид» находится в отличной форме: 5 побед подряд. Последние результаты: победа над «Барселоной» 2-1 (25 октября), разгром «Лейпцига» 4-1 (21 октября), победа над «Севильей» 4-1 (18 октября), выездная победа над «Ромой» 4-3 (14 октября) и победа над «Вильярреалом» 1-0 (10 октября). Команда набрала уверенность после сложного старта сезона.</p>
</div>
</div>
</div>
'''

def main():
    with httpx.Client(timeout=60) as client:
        r = client.get(WP_URL + "/wp-json/wp/v2/pages", params={"slug": "team-real-madrid", "context": "edit"}, auth=AUTH)
        if r.status_code != 200 or not r.json():
            print("ERR: page not found")
            return
        
        page = r.json()[0]
        content = page.get("content", {}).get("raw", "")
        
        # Replace old FAQ with new one
        if 'itemtype="https://schema.org/FAQPage"' in content:
            content = re.sub(
                r'<div class="tp-box" itemscope itemtype="https://schema.org/FAQPage">.*?</div>\s*(?=<script|$)',
                NEW_FAQ.strip() + '\n',
                content,
                flags=re.DOTALL
            )
            print("FAQ replaced")
        else:
            # Insert before script
            script_pos = content.find('<script>')
            if script_pos != -1:
                content = content[:script_pos] + NEW_FAQ + "\n" + content[script_pos:]
                print("FAQ inserted")
            else:
                content = content + NEW_FAQ
                print("FAQ appended")
        
        r2 = client.post(WP_URL + "/wp-json/wp/v2/pages/" + str(page["id"]), 
                        json={"content": content}, auth=AUTH)
        print("OK" if r2.status_code in (200, 201) else "ERR")

if __name__ == "__main__":
    main()
