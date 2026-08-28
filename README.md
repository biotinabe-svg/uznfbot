# Har kunlik iqtibos boti (Telegram)

Bu loyiha har kuni `quotes.json` fayldan bitta iqtibosni tanlab, chiroyli rasm
(1080x1080) shaklida yaratadi va Telegram kanalingizga avtomatik yuboradi.
Ishga tushirish uchun GitHub Actions ishlatiladi — **bepul va serversiz**.

## 1. Telegram bot yaratish

1. Telegramda **@BotFather** ga yozing.
2. `/newbot` buyrug'ini yuboring, botga nom va username bering.
3. BotFather sizga **token** beradi (masalan: `123456789:AAExxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx`).
   Buni saqlab qo'ying — bu `BOT_TOKEN`.

## 2. Botni kanalga admin qilib qo'shish

1. Telegram kanalingizni oching → **Administrators** → **Add Admin**.
2. Yaratgan botingizni qidirib toping va qo'shing.
3. Kamida **"Post Messages"** huquqini bering.

## 3. Kanal ID sini olish

- Agar kanal public bo'lsa (username bor, masalan `@mening_kanalim`),
  `CHANNEL_ID` sifatida shu username'ni ishlating: `@mening_kanalim`.
- Agar kanal private bo'lsa, ID raqamli bo'ladi (masalan `-1001234567890`).
  Buni olish uchun kanalga istalgan xabar yuboring, so'ng brauzerda:
  `https://api.telegram.org/bot<BOT_TOKEN>/getUpdates`
  manziliga kiring va natijadagi `"chat":{"id": ...}` qiymatini oling.

## 4. Loyihani GitHub'ga yuklash

1. GitHub'da yangi **repository** yarating (public yoki private — farqi yo'q).
2. Ushbu papkadagi barcha fayllarni o'sha repoga yuklang (yoki `git push` qiling).

## 5. Maxfiy kalitlarni (Secrets) sozlash

Repo ichida: **Settings → Secrets and variables → Actions → New repository secret**

| Nomi | Qiymati |
|---|---|
| `BOT_TOKEN` | BotFather bergan token |
| `CHANNEL_ID` | Kanal username (`@...`) yoki raqamli ID |

## 6. Iqtiboslarni to'ldirish

`quotes.json` faylini oching va o'zingizning (masalan ChatGPT yordamida
tayyorlagan) mashhurlar iqtiboslarini shu formatda kiriting:

```json
[
  { "quote": "Iqtibos matni shu yerda.", "author": "Muallif ismi" },
  { "quote": "Yana bir iqtibos.", "author": "Boshqa muallif" }
]
```

Bot har kuni ro'yxatdagi navbatdagi iqtibosni tanlaydi (sana bo'yicha),
ro'yxat tugagach yana boshidan boshlaydi — shuning uchun ro'yxat qancha uzun
bo'lsa, iqtiboslar shuncha kam takrorlanadi.

## 7. Ishga tushirish vaqti

`.github/workflows/daily-quote.yml` faylida:

```yaml
- cron: "0 2 * * *"   # 02:00 UTC = 07:00 Toshkent vaqti
```

Boshqa vaqt kerak bo'lsa, shu qatorni o'zgartiring
([crontab.guru](https://crontab.guru) yordam beradi — vaqtni UTC da yozish kerak).

## 8. Qo'lda test qilish

GitHub'da: **Actions** bo'limi → **Daily Quote to Telegram** → **Run workflow**
tugmasini bosing. Bir necha soniyadan so'ng kanalingizga rasm kelishi kerak.

## Lokal (kompyuteringizda) test qilish

```bash
pip install -r requirements.txt
export BOT_TOKEN="sizning_tokeningiz"
export CHANNEL_ID="@mening_kanalim"
python generate_and_send.py
```

## Dizaynni o'zgartirish

Rasmning rangi, shrift o'lchami, matn joylashuvi kabi narsalarni
`generate_and_send.py` faylidagi `render_quote_image()` funksiyasida
o'zgartirishingiz mumkin (masalan `make_gradient(W, H, (24,28,52), (55,33,92))`
qatoridagi ranglarni almashtiring).
