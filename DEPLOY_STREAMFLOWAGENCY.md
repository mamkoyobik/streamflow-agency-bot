# Streamflow Production Deploy (`streamflowagency.com`)

## 1) Перед деплоем
- Сайт и бот должны работать из одной БД (`DATABASE_URL` одинаковый в обоих сервисах).
- `SITE_URL` в обоих сервисах: `https://streamflowagency.com`.
- Таймзона (время заявок): `APP_TIMEZONE=UTC+6` (или ваш IANA timezone, например `Asia/Almaty`).

## 2) Railway: переменные окружения

### Web service (`web_server.py`)
- `BOT_TOKEN`
- `ADMIN_GROUP_ID`
- `ADMIN_USERNAME`
- `BOT_USERNAME`
- `CHANNEL_LINK`
- `SITE_URL=https://streamflowagency.com`
- `DATABASE_URL=...`
- `DB_CONNECT_TIMEOUT=15`
- `HOST=0.0.0.0`
- `WEB_SEND_FULL_TO_ADMIN=false`

### Bot service (`bot.py`)
- `BOT_TOKEN`
- `ADMIN_GROUP_ID`
- `CHANNEL_ID`
- `CHANNEL_EN_ID`
- `CHANNEL_PT_ID`
- `CHANNEL_ES_ID`
- `OPENAI_API_KEY=...`
- `OPENAI_TRANSLATE_MODEL=gpt-4o-mini`
- `ADMIN_USERNAME`
- `SITE_URL=https://streamflowagency.com`
- `DATABASE_URL=...`
- `DB_CONNECT_TIMEOUT=15`
- `APP_TIMEZONE=UTC+6`

## 3) Домен в Railway
1. Открой web service.
2. `Settings` -> `Domains` -> `Custom Domain`.
3. Добавь:
- `streamflowagency.com`
- `www.streamflowagency.com`
4. Railway покажет DNS записи. Добавь их у регистратора домена.
5. Дождись статуса `Verified` + `Issued` (TLS сертификат).

## 4) Проверка после деплоя
```bash
curl -I https://streamflowagency.com/
curl -I https://www.streamflowagency.com/
curl https://streamflowagency.com/robots.txt
curl https://streamflowagency.com/sitemap.xml
curl https://streamflowagency.com/api/config
```

Ожидаемо:
- сайт открывается по `https://streamflowagency.com`;
- `robots.txt` и `sitemap.xml` ссылаются на `streamflowagency.com`;
- `/api/config` возвращает JSON без ошибок.

## 5) Что уже подготовлено в коде
- SEO URL/каноникал/OG/Twitter ссылки переведены на `https://streamflowagency.com`.
- `robots.txt` и `sitemap.xml` переведены на `streamflowagency.com`.
- Дефолтный `SITE_URL` в боте переведен на `https://streamflowagency.com`.
- В `web_server.py` добавлен canonical redirect и secure headers.
