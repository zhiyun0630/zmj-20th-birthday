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


def _placeholder_photo(index: int) -> str:
    palette = ['%23ffd6e7', '%23ffc2d1', '%23ffd9a1', '%23f7d6ff', '%23c8f1ff']
    bg = palette[index % len(palette)]
    label = html.escape(f'照片 {index + 1}')
    svg = (
        "data:image/svg+xml,"
        "%3Csvg xmlns='http://www.w3.org/2000/svg' width='220' height='280' viewBox='0 0 220 280'%3E"
        f"%3Crect fill='{bg}' width='220' height='280'/%3E"
        "%3Ccircle cx='110' cy='96' r='34' fill='rgba(255,255,255,0.38)'/%3E"
        "%3Cpath d='M48 210 C72 168, 90 166, 110 190 C130 214, 154 172, 172 184 L172 280 L48 280 Z' fill='rgba(255,255,255,0.5)'/%3E"
        f"%3Ctext x='50%25' y='50%25' fill='white' font-size='20' font-weight='700' text-anchor='middle' dy='.35em'%3E{label}%3C/text%3E"
        "%3Ctext x='50%25' y='72%25' fill='white' font-size='12' text-anchor='middle' dy='.35em'%3E替换为你的照片%3C/text%3E"
        "%3C/svg%3E"
    )
    return svg


def render_photos(photos: list) -> str:
    items = photos or []
    while len(items) < 10:
        items.append({"src": "", "caption": f"照片 {len(items) + 1}"})

    cards = []
    for index, photo in enumerate(items[:10]):
        src = photo.get("src", "")
        caption = photo.get("caption", f"照片 {index + 1}")
        if src and (ROOT / src).exists():
            image_src = html.escape(src)
            alt = html.escape(caption)
        else:
            image_src = _placeholder_photo(index)
            alt = html.escape(caption or f"照片 {index + 1}")
        cards.append(
            f'<div class="photo-card">'
            f'<img src="{image_src}" alt="{alt}" loading="lazy">'
            f'<p>{html.escape(caption)}</p>'
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

    DIST.mkdir(exist_ok=True)
    (DIST / "css").mkdir(exist_ok=True)
    (DIST / "js").mkdir(exist_ok=True)
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
