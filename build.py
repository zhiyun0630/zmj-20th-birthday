"""Build the birthday site from data/config.json into dist/."""

import html
import json
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DATA = ROOT / "data" / "config.json"
TEMPLATE = ROOT / "templates" / "index.html"
DIST = ROOT / "dist"


def load_config() -> dict:
    with open(DATA, encoding="utf-8") as f:
        return json.load(f)


def render_timeline(timeline: list) -> str:
    items = []
    for event in timeline:
        items.append(
            f'<div class="timeline-item">'
            f'<div class="timeline-dot"></div>'
            f'<div class="timeline-date">{html.escape(event["date"])}</div>'
            f'<div class="timeline-text">{html.escape(event["text"])}</div>'
            f"</div>"
        )
    return "\n            ".join(items)


def render_photos(photos: list) -> str:
    if not photos:
        return (
            '<div class="photo-card">'
            '<img src="data:image/svg+xml,'
            "%3Csvg xmlns='http://www.w3.org/2000/svg' width='220' height='280'%3E"
            "%3Crect fill='%23ffb6c1' width='220' height='280'/%3E"
            "%3Ctext x='50%25' y='50%25' fill='white' font-size='14' "
            "text-anchor='middle' dy='.3em'%3E放入照片到 assets/photos/%3C/text%3E"
            "%3C/svg%3E" '" alt="placeholder">'
            '<p>在 data/config.json 里配置照片</p></div>'
        )
    cards = []
    for photo in photos:
        cards.append(
            f'<div class="photo-card">'
            f'<img src="{html.escape(photo["src"])}" alt="{html.escape(photo.get("caption", ""))}" loading="lazy">'
            f'<p>{html.escape(photo.get("caption", ""))}</p>'
            f"</div>"
        )
    return "\n            ".join(cards)


def render_candles(count: int) -> str:
    return "\n                ".join(
        '<div class="candle"><div class="flame"></div></div>' for _ in range(count)
    )


def render_gifts(gifts: list) -> str:
    boxes = []
    for gift in gifts:
        emoji = html.escape(gift.get("emoji", "🎁"))
        text = html.escape(gift["text"])
        boxes.append(
            f'<div class="gift-box">'
            f'<div class="gift-inner">'
            f'<div class="gift-front">{emoji}</div>'
            f'<div class="gift-back">{text}</div>'
            f"</div></div>"
        )
    return "\n            ".join(boxes)


def render_bg_music(src: str) -> str:
    if not src:
        return '<audio id="bgMusic" loop preload="none"></audio>'
    return (
        f'<audio id="bgMusic" loop preload="none">'
        f'<source src="{html.escape(src)}" type="audio/mpeg">'
        f"</audio>"
    )


def build() -> Path:
    config = load_config()
    template = TEMPLATE.read_text(encoding="utf-8")

    js_config = {
        "together_since": config["together_since"],
        "letter": config["letter"],
        "secret_code": config["secret_code"],
        "bg_music": config.get("bg_music", ""),
        "birthday_song": config.get("birthday_song", ""),
        "timeline": config["timeline"],
    }

    replacements = {
        "{{ envelope_title }}": html.escape(config["envelope_title"]),
        "{{ her_name }}": html.escape(config["her_name"]),
        "{{ subtitle }}": html.escape(config["subtitle"]),
        "{{ candle_count }}": str(config.get("candle_count", 20)),
        "{{ secret_hint }}": html.escape(config.get("secret_hint", "")),
        "{{ secret_title }}": html.escape(config.get("secret_title", "")),
        "{{ secret_message }}": html.escape(config.get("secret_message", "")),
        "{{ secret_image }}": html.escape(config.get("secret_image", "")),
        "{{ timeline_html }}": render_timeline(config["timeline"]),
        "{{ photos_html }}": render_photos(config.get("photos", [])),
        "{{ candles_html }}": render_candles(config.get("candle_count", 20)),
        "{{ gifts_html }}": render_gifts(config["gifts"]),
        "{{ bg_music_html }}": render_bg_music(config.get("bg_music", "")),
        "{{ config_json }}": json.dumps(js_config, ensure_ascii=False),
    }

    output = template
    for key, value in replacements.items():
        output = output.replace(key, value)

    if DIST.exists():
        shutil.rmtree(DIST)
    DIST.mkdir()
    (DIST / "css").mkdir()
    (DIST / "js").mkdir()
    (DIST / "assets").mkdir(exist_ok=True)

    shutil.copy(ROOT / "static" / "css" / "style.css", DIST / "css" / "style.css")
    shutil.copy(ROOT / "static" / "js" / "app.js", DIST / "js" / "app.js")

    assets_src = ROOT / "assets"
    if assets_src.exists():
        shutil.copytree(assets_src, DIST / "assets", dirs_exist_ok=True)

    (DIST / "index.html").write_text(output, encoding="utf-8")
    print(f"Built successfully -> {DIST / 'index.html'}")
    return DIST / "index.html"


if __name__ == "__main__":
    build()
