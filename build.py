"""Build the birthday site from data/config.json into dist/.

Photos can be placed in a private local source folder, then compressed into
web-friendly copies during build. The generated site references only the
compressed copies in dist/assets/photos.
"""

import html
import json
import shutil
from pathlib import Path

try:
    from PIL import Image, ImageOps
except ImportError:  # pragma: no cover - fallback for minimal environments
    Image = None
    ImageOps = None

ROOT = Path(__file__).resolve().parent
DATA = ROOT / "data" / "config.json"
TEMPLATE = ROOT / "templates" / "index.html"
DIST = ROOT / "dist"
PHOTO_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}
DEFAULT_PHOTO_SOURCE = "20th，zmj"
DEFAULT_PHOTO_COUNT = 40
PHOTO_MAX_SIZE = 1600
PHOTO_QUALITY = 82


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
    palette = ["%23ffd6e7", "%23ffc2d1", "%23ffd9a1", "%23f7d6ff", "%23c8f1ff"]
    bg = palette[index % len(palette)]
    label = html.escape(f"照片 {index + 1:02d}")
    return (
        "data:image/svg+xml,"
        "%3Csvg xmlns='http://www.w3.org/2000/svg' width='440' height='560' viewBox='0 0 440 560'%3E"
        f"%3Crect fill='{bg}' width='440' height='560'/%3E"
        "%3Ccircle cx='220' cy='188' r='72' fill='rgba(255,255,255,0.38)'/%3E"
        "%3Cpath d='M88 430 C142 330, 176 330, 220 382 C264 434, 314 344, 354 370 L354 560 L88 560 Z' fill='rgba(255,255,255,0.5)'/%3E"
        f"%3Ctext x='50%25' y='50%25' fill='white' font-size='36' font-weight='700' text-anchor='middle' dy='.35em'%3E{label}%3C/text%3E"
        "%3Ctext x='50%25' y='72%25' fill='white' font-size='20' text-anchor='middle' dy='.35em'%3E等待你的照片%3C/text%3E"
        "%3C/svg%3E"
    )


def discover_source_photos(source_dir: Path, limit: int) -> list[Path]:
    if not source_dir.exists():
        return []
    photos = [p for p in source_dir.iterdir() if p.is_file() and p.suffix.lower() in PHOTO_EXTENSIONS]
    return sorted(photos, key=lambda p: p.stem.zfill(10))[:limit]


def compress_photo(src: Path, dest: Path) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    if Image is None:
        shutil.copy(src, dest.with_suffix(src.suffix.lower()))
        return

    with Image.open(src) as image:
        image = ImageOps.exif_transpose(image)
        image.thumbnail((PHOTO_MAX_SIZE, PHOTO_MAX_SIZE), Image.Resampling.LANCZOS)
        if image.mode not in ("RGB", "L"):
            background = Image.new("RGB", image.size, (255, 255, 255))
            if "A" in image.getbands():
                background.paste(image, mask=image.getchannel("A"))
                image = background
            else:
                image = image.convert("RGB")
        else:
            image = image.convert("RGB")
        image.save(dest, "WEBP", quality=PHOTO_QUALITY, method=6)


def build_photo_items(config: dict) -> list[dict]:
    count = int(config.get("photo_count", DEFAULT_PHOTO_COUNT))
    source_dir = ROOT / config.get("photo_source_dir", DEFAULT_PHOTO_SOURCE)
    output_dir = DIST / "assets" / "photos"
    captions = config.get("photo_captions", [])
    source_photos = discover_source_photos(source_dir, count)
    items = []

    for index in range(count):
        caption = captions[index] if index < len(captions) else f"照片 {index + 1:02d} · 关于敏君的记忆"
        if index < len(source_photos):
            filename = f"zmj-memory-{index + 1:02d}.webp"
            dest = output_dir / filename
            compress_photo(source_photos[index], dest)
            items.append({"src": f"assets/photos/{filename}", "caption": caption})
        else:
            items.append({"src": "", "caption": caption})
    return items


def render_photos(photos: list) -> str:
    cards = []
    for index, photo in enumerate(photos):
        src = photo.get("src", "")
        caption = photo.get("caption", f"照片 {index + 1:02d}")
        image_src = html.escape(src) if src else _placeholder_photo(index)
        alt = html.escape(caption or f"照片 {index + 1:02d}")
        cards.append(
            f'<button class="photo-card" type="button" data-index="{index}" '
            f'data-src="{image_src}" data-caption="{html.escape(caption)}" '
            f'style="--order:{index}; --tilt:{-3 + (index % 7)}deg">'
            f'<span class="photo-number">{index + 1:02d}</span>'
            f'<img src="{image_src}" alt="{alt}" loading="lazy">'
            f'<span class="photo-caption">{html.escape(caption)}</span>'
            f"</button>"
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


def prepare_dist() -> None:
    DIST.mkdir(exist_ok=True)
    (DIST / "css").mkdir(exist_ok=True)
    (DIST / "js").mkdir(exist_ok=True)
    (DIST / "assets").mkdir(exist_ok=True)

    photos_dir = DIST / "assets" / "photos"
    if photos_dir.exists():
        shutil.rmtree(photos_dir)
    photos_dir.mkdir(parents=True, exist_ok=True)


def build() -> Path:
    config = load_config()
    template = TEMPLATE.read_text(encoding="utf-8")
    prepare_dist()

    shutil.copy(ROOT / "static" / "css" / "style.css", DIST / "css" / "style.css")
    shutil.copy(ROOT / "static" / "js" / "app.js", DIST / "js" / "app.js")

    assets_src = ROOT / "assets"
    if assets_src.exists():
        shutil.copytree(assets_src, DIST / "assets", dirs_exist_ok=True)

    photos = build_photo_items(config)

    js_config = {
        "together_since": config["together_since"],
        "letter": config["letter"],
        "secret_code": config["secret_code"],
        "bg_music": config.get("bg_music", ""),
        "birthday_song": config.get("birthday_song", ""),
        "timeline": config["timeline"],
        "photo_count": len(photos),
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
        "{{ photos_html }}": render_photos(photos),
        "{{ candles_html }}": render_candles(config.get("candle_count", 20)),
        "{{ gifts_html }}": render_gifts(config["gifts"]),
        "{{ bg_music_html }}": render_bg_music(config.get("bg_music", "")),
        "{{ config_json }}": json.dumps(js_config, ensure_ascii=False),
    }

    output = template
    for key, value in replacements.items():
        output = output.replace(key, value)

    (DIST / "index.html").write_text(output, encoding="utf-8")
    print(f"Built successfully -> {DIST / 'index.html'}")
    print(f"Compressed photos -> {DIST / 'assets' / 'photos'}")
    return DIST / "index.html"


if __name__ == "__main__":
    build()
