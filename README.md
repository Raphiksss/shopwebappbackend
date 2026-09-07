# RedStore Backend

Бэкенд интернет-магазина, работающего как Telegram Mini App (Web App) + Telegram-бот.
Backend for an online shop that runs as a Telegram Mini App (Web App) + Telegram bot.

**Язык / Language:** [Русский](#русский) · [English](#english)

---

<a name="русский"></a>
<details open>
<summary><h2>🇷🇺 Русский</h2></summary>

### О проекте

Монолитный сервис на FastAPI, который обслуживает три группы клиентов:

1. **Telegram Mini App** (витрина): каталог, категории, корзина, избранное, заказы, пополнение баланса.
2. **Админ-панель** (внешний SPA): CRUD товаров и категорий, список заказов и пользователей, настройки магазина.
3. **Telegram-бот** (aiogram): регистрация пользователя по `/start`, выдача цифровых товаров, оплата Telegram Stars и CryptoBot, уведомления о заказах.

Оплата: внутренний баланс пользователя, который пополняется через Telegram Stars, CryptoBot (USDT) и ЮMoney (с проверкой SHA-1 подписи вебхука).

### Стек

| Слой | Технологии |
| --- | --- |
| API | FastAPI, Pydantic v2, pydantic-settings, Uvicorn |
| БД | PostgreSQL (asyncpg), SQLAlchemy 2.0 (async ORM), Alembic |
| Кеш / состояние | Redis (RedisJSON) |
| Брокер | RabbitMQ, FastStream |
| Бот | aiogram 3 |
| Хранилище файлов | локальный volume + Cloudflare R2 / S3 (aiobotocore), Pillow |
| Платежи | Telegram Stars, CryptoBot API, ЮMoney |
| Инфра | Docker Compose, GitLab CI |
| Формат кода | Black |

### Архитектура

```
        Telegram Mini App            Админ-панель (SPA)
                │                            │
                └──────────► FastAPI ◄────────┘
                             (main.py)
                                │
      ┌─────────────────┬───────┴────────┬──────────────────┐
      ▼                 ▼                ▼                  ▼
  PostgreSQL          Redis          RabbitMQ           R2 / volume
 (товары, юзеры,   (корзина,      (очереди задач)      (картинки,
  заказы, отзывы)   настройки)          │              файлы товаров)
                                        ▼
                                 Consumers (FastStream)
                                        │
                                        ▼
                                 aiogram Bot ──► Telegram API
```

API, consumers и polling бота запускаются в **одном процессе** через `lifespan` в `main.py`.

Очереди RabbitMQ (все `durable`, с TTL сообщений и Dead Letter Queue). TTL это `x-message-ttl`: если сообщение не обработали за это время, RabbitMQ перекладывает его в `dlq_queue`.

| Очередь | Назначение | TTL |
| --- | --- | --- |
| `instant_delivery_queue` | мгновенная выдача цифрового товара | 24 ч |
| `order_notifications_queue` | уведомление админа/пользователя о заказе | 1 ч |
| `stars_replenishment_queue` | выставление счёта в Telegram Stars | 1 ч |
| `crypto_bot_replenishment_queue` | выставление счёта в CryptoBot | 1 ч |
| `dlq_queue` | сообщения, не обработанные после ретраев | — |

### Структура проекта

```
api_v1/
  views/          роутеры FastAPI (products, cart, users, favorites,
                  categories, orders, auth, settings)
  services/       бизнес-логика, платежи, работа с Redis, загрузка картинок
  repositories/   доступ к БД через SQLAlchemy
  schemas/        Pydantic-модели запросов/ответов и сообщений брокера
bot/
  bot.py          aiogram: хендлеры, Stars, CryptoBot, выдача товара
  consumers.py    FastStream-подписчики очередей
core/
  config.py       настройки через pydantic-settings
  db_helper.py    async engine + сессии
  models/         ORM-модели (Product, Category, User, Order, Review, Admin)
  rabbitmq.py     брокер, очереди, publisher-функции
  s3_core.py      клиент S3/R2 с пережатием изображений
alembic/          миграции
scripts/          entrypoint.sh, init_db.py, init_minio.sh
```

### Что уже сделано

- **Каталог**: товары и категории с загрузкой изображений (пережатие через Pillow, EXIF-ориентация, whitelist MIME-типов), два типа товара: `instantly` (цифровой, выдаётся сразу) и `notinstantly` (обрабатывается вручную).
- **Корзина в Redis** (RedisJSON) с инкрементом количества, удалением одной позиции, позиции целиком и всей корзины.
- **Избранное** через many-to-many таблицу `favorites`.
- **Заказы**: списание с баланса, создание заказа и позиций, очистка корзины, публикация событий в RabbitMQ; фильтр по статусу и пагинация в админском списке. Позиция хранит снимок названия, цены и количества на момент покупки, поэтому изменение или удаление товара не переписывает историю.
- **Асинхронная обработка через RabbitMQ**: API отвечает сразу, тяжёлые операции (обращения к Telegram API, выдача товара) уходят в очереди с ретраями и DLQ.
- **Платежи**: Telegram Stars (`send_invoice`, `pre_checkout_query`, `successful_payment`), CryptoBot (создание инвойса и проверка статуса), ЮMoney (Quickpay + вебхук с проверкой SHA-1 подписи и защитой от повторной обработки через `SET NX EX` в Redis).
- **Админ-авторизация**: bcrypt-хеши в таблице `admins`, вход по логину/паролю, серверная сессия в подписанной cookie (`SessionMiddleware`), защита изменяющих эндпоинтов зависимостью `check_if_auth`.
- **Рантайм-настройки магазина в Redis**: акцентный цвет, курс звёзд, токен бота (с горячим перезапуском polling), токен CryptoBot, реквизиты ЮMoney, список включённых способов оплаты.
- **Инфраструктура**: Docker Compose (backend, PostgreSQL, Redis, RabbitMQ с healthcheck'ами), `entrypoint.sh` с ожиданием БД и автоинициализацией, деплой из GitLab CI по пушу в `main`.
- **Миграции**: 17 ревизий Alembic с async-движком и датированными именами файлов. Схема собирается только миграциями — `entrypoint.sh` всегда выполняет `alembic upgrade head` и останавливает контейнер, если миграция не прошла.

### Запуск

Проект запускается только через Docker: хосты сервисов и путь к каталогу с картинками заданы в Compose, а запуск из хостовой системы не поддерживается.

```bash
docker compose up -d --build
docker compose logs -f backend
```

- API: http://localhost:8000
- Swagger: http://localhost:8000/docs
- RabbitMQ UI: http://localhost:15672, логин и пароль из `RABBITMQ_USER` / `RABBITMQ_PASSWORD`

Все порты, кроме UI RabbitMQ на сервере, привязаны к `127.0.0.1`, поэтому с удалённой машины панель открывается только через туннель: `ssh -L 15672:127.0.0.1:15672 user@server`.

#### Переменные окружения

Конфигурация разложена по трём местам, приоритет справа налево: дефолты в `core/config.py` → `.env` → `environment` в `docker-compose.yml`.

**Из `.env`**, который лежит рядом с `docker-compose.yml`. На сервере его генерирует CI из переменных GitLab, локально пишется руками. В образ он не попадает, `.env` указан в `.dockerignore`. Все переменные ниже обязательные, без дефолтов, поэтому при отсутствии любой из них приложение падает на старте:

| Переменная | Назначение |
| --- | --- |
| `BOT_TOKEN` | токен Telegram-бота |
| `ADMIN_TG_ID` | Telegram ID администратора для уведомлений |
| `CRYPTO_BOT_TOKEN` | токен Crypto Pay API |
| `ADMIN_USERNAME`, `ADMIN_PASSWORD` | первый админ, создаётся `scripts/init_db.py` |
| `SECRET_SESSION_KEY` | ключ подписи cookie-сессий |
| `YOOMONEY_TOKEN`, `YOOMONEY_WALLET`, `YOOMONEY_NOTIFICATION_SECRET` | реквизиты ЮMoney |
| `R2_ACCESS_KEY`, `R2_SECRET_KEY`, `R2_ENDPOINT`, `R2_PUBLIC_URL` | доступ к Cloudflare R2 |
| `DB_PASSWORD` | пароль пользователя PostgreSQL |
| `RABBITMQ_USER`, `RABBITMQ_PASSWORD` | доступ к RabbitMQ |

**Из `docker-compose.yml`**, это топология сети Compose, в `.env` их дублировать не нужно (секция `environment` всё равно перекроет файл):

| Переменная | Значение |
| --- | --- |
| `DB_HOST`, `DB_PORT` | `postgresql`, `5432` |
| `REDIS_HOST`, `REDIS_PORT` | `redis`, `6379` |
| `RABBITMQ_HOST`, `RABBITMQ_PORT` | `rabbitmq`, `5672` |

**С дефолтами в конфиге**, задавать только если нужно поменять:

| Переменная | По умолчанию |
| --- | --- |
| `DB_USER`, `DB_NAME` | `postgres`, `postgres` |
| `IMAGES_DIR` | `/var/www/media` |
| `SESSION_EXPIRE_TIME`, `SESSION_SECURE` | `86400`, `true` |
| `logging_level` | `INFO` |

Строка подключения к БД собирается из `DB_*` в `core/config.py`, отдельной переменной с готовым URL нет. `DB_USER`, `DB_NAME`, `POSTGRES_USER`, `POSTGRES_PASSWORD` и `POSTGRES_DB` должны совпадать между приложением и сервисом `postgresql`, иначе подключения не будет.

### API

Все роуты под префиксом `/api/v1`. Полное описание в `/docs`.

| Группа | Эндпоинты |
| --- | --- |
| `/products` | `POST /` · `GET /` · `GET /{id}/` · `PATCH /{id}/` · `DELETE /{id}/` |
| `/categories` | `POST /` · `GET /` · `PATCH /{id}/` · `DELETE /{id}/` |
| `/cart` | `POST /{tg_id}/` · `GET /{tg_id}/` · `DELETE /{tg_id}/` · `DELETE /all_cart/{tg_id}/` · `DELETE /full_product/{tg_id}/` |
| `/favorites` | `GET /{tg_id}/` · `POST /{tg_id}/` · `DELETE /{tg_id}/` |
| `/orders` | `POST /` · `GET /` (фильтр по статусу, пагинация) · `PATCH /{order_id}/` |
| `/users` | `GET /` · `POST /` · `GET /{tg_id}/` · `PATCH /{user_id}/` · `POST /replenisment/{stars,crypto,yoomoney}/` · `POST /webhook/yoomoney/` |
| `/auth` | `POST /login/` · `POST /admin/` · `GET /me/` · `DELETE /logout/` |
| `/settings` | `GET`/`POST` для `accent_color`, `stars_exchange_rate`, `bot_token`, `crypto_token`, `yoo_money`, `payment_methods` |

### Миграции

```bash
docker compose exec backend alembic revision --autogenerate -m "описание"
docker compose exec backend alembic upgrade head
docker compose exec backend alembic downgrade -1
```

### Формат кода

```bash
docker compose exec backend black .          # отформатировать
docker compose exec backend black --check .  # проверить без изменений
```

В PyCharm: `Settings → Tools → Black` (включить) и `Settings → Tools → Actions on Save → Reformat code`.

### Планы

1. **Перестройка авторизации.** Серверные сессии в БД вместо подписанной cookie, чтобы админа можно было отозвать мгновенно, и авторизация клиента вместо `tg_id` в пути.
2. **Улучшение архитектуры.** Разделение API, бота и consumers по процессам, атомарное создание заказа, нормализация схемы.
3. **Кеширование.** Кеш каталога в Redis и общий пул подключений вместо нового клиента на каждый запрос.

</details>

---

<a name="english"></a>
<details>
<summary><h2>🇬🇧 English</h2></summary>

### Overview

A FastAPI monolith serving three groups of clients:

1. **Telegram Mini App** (storefront): catalog, categories, cart, favorites, orders, balance top-up.
2. **Admin panel** (external SPA): product and category CRUD, order and user lists, shop settings.
3. **Telegram bot** (aiogram): user registration on `/start`, digital product delivery, Telegram Stars and CryptoBot payments, order notifications.

Payments go through an internal user balance, topped up via Telegram Stars, CryptoBot (USDT) and YooMoney (with SHA-1 webhook signature verification).

### Tech stack

| Layer | Technologies |
| --- | --- |
| API | FastAPI, Pydantic v2, pydantic-settings, Uvicorn |
| Database | PostgreSQL (asyncpg), SQLAlchemy 2.0 (async ORM), Alembic |
| Cache / state | Redis (RedisJSON) |
| Broker | RabbitMQ, FastStream |
| Bot | aiogram 3 |
| File storage | local volume + Cloudflare R2 / S3 (aiobotocore), Pillow |
| Payments | Telegram Stars, CryptoBot API, YooMoney |
| Infra | Docker Compose, GitLab CI |
| Formatter | Black |

### Architecture

```
        Telegram Mini App             Admin panel (SPA)
                │                            │
                └──────────► FastAPI ◄────────┘
                             (main.py)
                                │
      ┌─────────────────┬───────┴────────┬──────────────────┐
      ▼                 ▼                ▼                  ▼
  PostgreSQL          Redis          RabbitMQ           R2 / volume
 (products, users,  (cart,          (task queues)      (images,
  orders, reviews)   settings)           │              product files)
                                        ▼
                                 Consumers (FastStream)
                                        │
                                        ▼
                                 aiogram Bot ──► Telegram API
```

The API, the consumers and the bot polling loop all start in a **single process** from the `lifespan` hook in `main.py`.

RabbitMQ queues (all `durable`, with a message TTL and a Dead Letter Queue). TTL is `x-message-ttl`: if a message is not consumed within that window, RabbitMQ moves it to `dlq_queue`.

| Queue | Purpose | TTL |
| --- | --- | --- |
| `instant_delivery_queue` | instant digital product delivery | 24 h |
| `order_notifications_queue` | order notification to admin/user | 1 h |
| `stars_replenishment_queue` | Telegram Stars invoice | 1 h |
| `crypto_bot_replenishment_queue` | CryptoBot invoice | 1 h |
| `dlq_queue` | messages that failed all retries | — |

### Project layout

```
api_v1/
  views/          FastAPI routers (products, cart, users, favorites,
                  categories, orders, auth, settings)
  services/       business logic, payments, Redis access, image upload
  repositories/   SQLAlchemy data access
  schemas/        Pydantic request/response and broker message models
bot/
  bot.py          aiogram handlers, Stars, CryptoBot, product delivery
  consumers.py    FastStream queue subscribers
core/
  config.py       pydantic-settings configuration
  db_helper.py    async engine + sessions
  models/         ORM models (Product, Category, User, Order, Review, Admin)
  rabbitmq.py     broker, queues, publisher helpers
  s3_core.py      S3/R2 client with image re-encoding
alembic/          migrations
scripts/          entrypoint.sh, init_db.py, init_minio.sh
```

### What is already implemented

- **Catalog**: products and categories with image upload (Pillow re-encoding, EXIF transpose, MIME whitelist), two product types: `instantly` (digital, delivered immediately) and `notinstantly` (handled manually).
- **Redis cart** (RedisJSON) with quantity increment, removing one unit, removing a whole line item, and clearing the cart.
- **Favorites** via the `favorites` many-to-many table.
- **Orders**: balance debit, order and order item creation, cart cleanup, event publishing to RabbitMQ; status filter and pagination for the admin list. Each line item stores a snapshot of the title, price and quantity at purchase time, so editing or deleting a product does not rewrite history.
- **Async processing over RabbitMQ**: the API responds immediately while slow work (Telegram API calls, product delivery) moves to queues with retries and a DLQ.
- **Payments**: Telegram Stars (`send_invoice`, `pre_checkout_query`, `successful_payment`), CryptoBot (invoice creation and status polling), YooMoney (Quickpay + webhook with SHA-1 signature check and replay protection via `SET NX EX` in Redis).
- **Admin auth**: bcrypt hashes in the `admins` table, login by username/password, server-side session in a signed cookie (`SessionMiddleware`), mutating endpoints guarded by the `check_if_auth` dependency.
- **Runtime shop settings in Redis**: accent color, stars exchange rate, bot token (with hot polling restart), CryptoBot token, YooMoney credentials, enabled payment methods.
- **Infrastructure**: Docker Compose (backend, PostgreSQL, Redis, RabbitMQ with healthchecks), `entrypoint.sh` that waits for the DB and auto-initializes it, GitLab CI deploy on push to `main`.
- **Migrations**: 17 Alembic revisions with an async engine and date-prefixed filenames. The schema is built by migrations alone — `entrypoint.sh` always runs `alembic upgrade head` and stops the container if a migration fails.

### Getting started

The project runs only through Docker: service hosts and the media directory path are set in Compose, and running from the host system is not supported.

```bash
docker compose up -d --build
docker compose logs -f backend
```

- API: http://localhost:8000
- Swagger: http://localhost:8000/docs
- RabbitMQ UI: http://localhost:15672, credentials from `RABBITMQ_USER` / `RABBITMQ_PASSWORD`

Every port is bound to `127.0.0.1`, so on a remote server the management UI is only reachable through a tunnel: `ssh -L 15672:127.0.0.1:15672 user@server`.

#### Environment variables

Configuration is split across three places, priority right to left: defaults in `core/config.py` → `.env` → `environment` in `docker-compose.yml`.

**From `.env`**, which sits next to `docker-compose.yml`. On the server CI generates it from GitLab variables, locally it is written by hand. It never enters the image, `.env` is listed in `.dockerignore`. All variables below are required, with no defaults, so the app crashes on startup if any is missing:

| Variable | Purpose |
| --- | --- |
| `BOT_TOKEN` | Telegram bot token |
| `ADMIN_TG_ID` | admin Telegram ID for notifications |
| `CRYPTO_BOT_TOKEN` | Crypto Pay API token |
| `ADMIN_USERNAME`, `ADMIN_PASSWORD` | first admin, created by `scripts/init_db.py` |
| `SECRET_SESSION_KEY` | cookie session signing key |
| `YOOMONEY_TOKEN`, `YOOMONEY_WALLET`, `YOOMONEY_NOTIFICATION_SECRET` | YooMoney credentials |
| `R2_ACCESS_KEY`, `R2_SECRET_KEY`, `R2_ENDPOINT`, `R2_PUBLIC_URL` | Cloudflare R2 access |
| `DB_PASSWORD` | PostgreSQL user password |
| `RABBITMQ_USER`, `RABBITMQ_PASSWORD` | RabbitMQ credentials |

**From `docker-compose.yml`**, this is Compose network topology, no need to duplicate them in `.env` (the `environment` section overrides the file anyway):

| Variable | Value |
| --- | --- |
| `DB_HOST`, `DB_PORT` | `postgresql`, `5432` |
| `REDIS_HOST`, `REDIS_PORT` | `redis`, `6379` |
| `RABBITMQ_HOST`, `RABBITMQ_PORT` | `rabbitmq`, `5672` |

**With defaults in the config**, set only if you need to change them:

| Variable | Default |
| --- | --- |
| `DB_USER`, `DB_NAME` | `postgres`, `postgres` |
| `IMAGES_DIR` | `/var/www/media` |
| `SESSION_EXPIRE_TIME`, `SESSION_SECURE` | `86400`, `true` |
| `logging_level` | `INFO` |

The DB connection string is assembled from the `DB_*` variables in `core/config.py`; there is no single ready-made URL variable. `DB_USER`, `DB_NAME`, `POSTGRES_USER`, `POSTGRES_PASSWORD` and `POSTGRES_DB` must match between the app and the `postgresql` service, otherwise the connection will fail.

### API

Everything lives under `/api/v1`. Full reference at `/docs`.

| Group | Endpoints |
| --- | --- |
| `/products` | `POST /` · `GET /` · `GET /{id}/` · `PATCH /{id}/` · `DELETE /{id}/` |
| `/categories` | `POST /` · `GET /` · `PATCH /{id}/` · `DELETE /{id}/` |
| `/cart` | `POST /{tg_id}/` · `GET /{tg_id}/` · `DELETE /{tg_id}/` · `DELETE /all_cart/{tg_id}/` · `DELETE /full_product/{tg_id}/` |
| `/favorites` | `GET /{tg_id}/` · `POST /{tg_id}/` · `DELETE /{tg_id}/` |
| `/orders` | `POST /` · `GET /` (status filter, pagination) · `PATCH /{order_id}/` |
| `/users` | `GET /` · `POST /` · `GET /{tg_id}/` · `PATCH /{user_id}/` · `POST /replenisment/{stars,crypto,yoomoney}/` · `POST /webhook/yoomoney/` |
| `/auth` | `POST /login/` · `POST /admin/` · `GET /me/` · `DELETE /logout/` |
| `/settings` | `GET`/`POST` for `accent_color`, `stars_exchange_rate`, `bot_token`, `crypto_token`, `yoo_money`, `payment_methods` |

### Migrations

```bash
docker compose exec backend alembic revision --autogenerate -m "message"
docker compose exec backend alembic upgrade head
docker compose exec backend alembic downgrade -1
```

### Code style

```bash
docker compose exec backend black .          # format
docker compose exec backend black --check .  # check without writing
```

In PyCharm: `Settings → Tools → Black` (enable) and `Settings → Tools → Actions on Save → Reformat code`.

### Roadmap

1. **Auth rebuild.** Server-side sessions in the database instead of a signed cookie, so an admin can be revoked instantly, plus real client auth instead of `tg_id` in the path.
2. **Architecture improvements.** Split the API, bot and consumers into separate processes, make order creation atomic, normalize the schema.
3. **Caching.** Redis cache for the catalog and a shared connection pool instead of a new client per request.

</details>
