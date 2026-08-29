import json
import os
import sys
import textwrap
from datetime import date, datetime, timezone
from pathlib import Path

import requests
from PIL import Image, ImageDraw, ImageFont

BASE_DIR = Path(__file__).parent
FONTS_DIR = BASE_DIR / "fonts"
QUOTES_FILE = BASE_DIR / "quotes.json"
OUTPUT_IMAGE = BASE_DIR / "quote_today.png"

# ---------- 1. Ma'lumotlarni o'qish ----------

def load_quotes():
    with open(QUOTES_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def pick_todays_quote(quotes):
    """Sana asosida navbat bilan iqtibos tanlaydi (har kuni boshqa, ro'yxat
    tugagach yana boshidan boshlaydi). Shu sababli alohida holat saqlash
    shart emas — GitHub Actions kabi holatsiz muhitda ham to'g'ri ishlaydi."""
    day_index = date.today().toordinal()
    return quotes[day_index % len(quotes)]


# ---------- 2. Rasm yaratish ----------

def wrap_text(draw, text, font, max_width):
    words = text.split()
    lines, current = [], ""
    for word in words:
        trial = f"{current} {word}".strip()
        bbox = draw.textbbox((0, 0), trial, font=font)
        if bbox[2] - bbox[0] <= max_width:
            current = trial
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


def fit_quote_font(draw, text, max_width, max_height, start_size=64, min_size=30):
    size = start_size
    while size >= min_size:
        font = ImageFont.truetype(str(FONTS_DIR / "DejaVuSans-Bold.ttf"), size)
        lines = wrap_text(draw, text, font, max_width)
        line_height = draw.textbbox((0, 0), "Ag", font=font)[3] + 14
        total_height = line_height * len(lines)
        if total_height <= max_height:
            return font, lines, line_height
        size -= 2
    return font, lines, line_height


def make_gradient(width, height, top_color, bottom_color):
    base = Image.new("RGB", (width, height), top_color)
    top = Image.new("RGB", (width, height), top_color)
    bottom = Image.new("RGB", (width, height), bottom_color)
    mask = Image.new("L", (width, height))
    mask_data = []
    for y in range(height):
        mask_data.extend([int(255 * (y / height))] * width)
    mask.putdata(mask_data)
    base.paste(bottom, (0, 0), mask)
    return base


def render_quote_image(quote_text, author, out_path):
    W, H = 1080, 1080
    img = make_gradient(W, H, (24, 28, 52), (55, 33, 92))
    draw = ImageDraw.Draw(img)

    margin_x = 110
    max_text_width = W - 2 * margin_x
    max_text_height = 560

    font, lines, line_height = fit_quote_font(
        draw, quote_text, max_text_width, max_text_height
    )

    total_height = line_height * len(lines)
    start_y = (H - total_height) // 2 - 30

    for i, line in enumerate(lines):
        bbox = draw.textbbox((0, 0), line, font=font)
        line_w = bbox[2] - bbox[0]
        x = (W - line_w) // 2
        y = start_y + i * line_height
        draw.text((x, y), line, font=font, fill=(255, 255, 255))

    # Ajratuvchi chiziqcha
    line_y = start_y + total_height + 40
    draw.line(
        [(W // 2 - 60, line_y), (W // 2 + 60, line_y)],
        fill=(200, 170, 255),
        width=4,
    )

    # Muallif
    author_font = ImageFont.truetype(str(FONTS_DIR / "DejaVuSans.ttf"), 36)
    author_text = f"— {author}"
    bbox = draw.textbbox((0, 0), author_text, font=author_font)
    author_w = bbox[2] - bbox[0]
    draw.text(
        ((W - author_w) // 2, line_y + 30),
        author_text,
        font=author_font,
        fill=(210, 200, 230),
    )

    # Pastki sana / brend belgisi (ixtiyoriy, o'chirib qo'yish mumkin)
    footer_font = ImageFont.truetype(str(FONTS_DIR / "DejaVuSans.ttf"), 24)
    footer_text = datetime.now().strftime("%d.%m.%Y")
    bbox = draw.textbbox((0, 0), footer_text, font=footer_font)
    footer_w = bbox[2] - bbox[0]
    draw.text(
        ((W - footer_w) // 2, H - 60),
        footer_text,
        font=footer_font,
        fill=(150, 140, 180),
    )

    img.save(out_path, "PNG")
    return out_path


# ---------- 3. Telegramga yuborish ----------

def send_photo_to_telegram(bot_token, chat_id, image_path, caption=""):
    url = f"https://api.telegram.org/bot{bot_token}/sendPhoto"
    with open(image_path, "rb") as photo:
        resp = requests.post(
            url,
            data={"chat_id": chat_id, "caption": caption},
            files={"photo": photo},
            timeout=30,
        )
    resp.raise_for_status()
    result = resp.json()
    if not result.get("ok"):
        raise RuntimeError(f"Telegram xatosi: {result}")
    return result


def main():
    bot_token = os.environ.get("BOT_TOKEN")
    chat_id = os.environ.get("CHANNEL_ID")

    if not bot_token or not chat_id:
        print("XATO: BOT_TOKEN va CHANNEL_ID muhit o'zgaruvchilari topilmadi.")
        sys.exit(1)

    quotes = load_quotes()
    if not quotes:
        print("XATO: quotes.json bo'sh.")
        sys.exit(1)

    today_quote = pick_todays_quote(quotes)
    print(f"Bugungi iqtibos: {today_quote['quote']} — {today_quote['author']}")

    render_quote_image(today_quote["quote"], today_quote["author"], OUTPUT_IMAGE)
    print(f"Rasm tayyor: {OUTPUT_IMAGE}")

    send_photo_to_telegram(bot_token, chat_id, OUTPUT_IMAGE)
    print("Telegram kanaliga muvaffaqiyatli yuborildi.")


if __name__ == "__main__":
    main()

