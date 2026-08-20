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
- **Заказы**: списание с баланса, создание заказа и позиций, очистка корзины, публикация событий в RabbitMQ; фильтр по статусу и пагинация в админском списке.
- **Асинхронная обработка через RabbitMQ**: API отвечает сразу, тяжёлые операции (обращения к Telegram API, выдача товара) уходят в очереди с ретраями и DLQ.
- **Платежи**: Telegram Stars (`send_invoice`, `pre_checkout_query`, `successful_payment`), CryptoBot (создание инвойса и проверка статуса), ЮMoney (Quickpay + вебхук с проверкой SHA-1 подписи и защитой от повторной обработки через `SET NX EX` в Redis).
- **Админ-авторизация**: bcrypt-хеши в таблице `admins`, вход по логину/паролю, серверная сессия в подписанной cookie (`SessionMiddleware`), защита изменяющих эндпоинтов зависимостью `check_if_auth`.
- **Рантайм-настройки магазина в Redis**: акцентный цвет, курс звёзд, токен бота (с горячим перезапуском polling), токен CryptoBot, реквизиты ЮMoney, список включённых способов оплаты.
- **Инфраструктура**: Docker Compose (backend, PostgreSQL, Redis, RabbitMQ с healthcheck'ами), `entrypoint.sh` с ожиданием БД и автоинициализацией, деплой из GitLab CI по пушу в `main`.
- **Миграции**: 17 ревизий Alembic с async-движком и датированными именами файлов.

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

### Известные проблемы и техдолг

Список честный, он же основа для роадмапа ниже.

#### Безопасность

- **Публичные эндпоинты не проверяют, кто их вызывает.** `tg_id` приходит параметром пути, поэтому любой человек может прочитать и изменить чужую корзину и избранное, создать заказ за другого пользователя и списать его баланс, запросить `GET /users/` со списком всех пользователей. Подпись `initData` из Telegram Web App нигде не валидируется.
- **Пополнение баланса вызывается напрямую.** `POST /users/replenisment/*` принимает произвольные `tg_id` и `amount` без авторизации.
- **Сессию админа нельзя отозвать.** `SessionMiddleware` хранит состояние в подписанной cookie на клиенте, серверной записи о сессии нет. Удаление админа, смена пароля и утечка cookie не выкидывают его из системы: доступ живёт до истечения `SESSION_EXPIRE_TIME`, то есть сутки.
- **Нет CSRF-защиты и rate limit** для cookie-сессий и `POST /auth/login/`, `same_site` для `SessionMiddleware` не задан.
- **Токены хранятся в Redis в открытом виде**, а `GET /settings/bot_token/` возвращает токен бота.
- **Path traversal при загрузке файлов товара**: `os.path.join("files", data.filename)` использует имя файла от клиента без нормализации.
- **`db.sqlite3` закоммичен в репозиторий**, а образ собирается без `.dockerignore`, поэтому в него попадают `.git`, локальная БД и `files/`.

#### Консистентность данных

- **Удаление товара падает из-за жёстких внешних ключей.** Если товар лежит у кого-то в избранном, есть отзывы или он попал в заказ, `DELETE /products/{id}/` возвращает 500 с `IntegrityError`: FK созданы без `ON DELETE`, у relationship нет `cascade` и `passive_deletes`. Аналогично не удаляется категория с товарами и пользователь с избранным. Подробный разбор и план исправления в [планах](#планы).
- **Создание заказа не транзакционно**: баланс списывается и коммитится отдельно от создания заказа, до очистки корзины и публикации сообщений. Падение в середине оставляет пользователя без денег и без заказа.
- **Нет блокировки строки при списании баланса**: параллельные запросы дают двойную трату и отрицательный баланс. При недостатке средств возвращается `HTTPException(500)` вместо 400/402.
- **`OrdersItem` не хранит количество и цену на момент покупки**, поэтому состав и сумму заказа нельзя восстановить, а изменение цены товара переписывает историю.
- **Схема на естественных ключах**: `Product.category_title` ссылается на `categorys.title`, `Order.user` на `users.tg_id`. Переименование категории каскадит по всем товарам, а имя таблицы `categorys` появилось из автогенерации `__tablename__`.
- **Нет `created_at` / `updated_at`** ни в одной модели, заказы нельзя отсортировать по времени.
- **`Product.rating` живёт отдельно от `Review.rate`**: рейтинг не агрегируется из отзывов, а задаётся вручную из формы.
- **`scripts/init_db.py` на пустой БД делает `create_all` + `alembic stamp head`**, что расходится с историей миграций.
- **ЮMoney-вебхук идемпотентен по `label`, а не по `operation_id`**, а `int(float(amount))` отбрасывает копейки.

#### Архитектура

- **API, бот и consumers в одном процессе.** Горизонтально не масштабируется: при нескольких воркерах Uvicorn получим конфликт `getUpdates` и дублирующую обработку очередей.
- **Блокирующий код в async-хендлерах**: синхронный `redis` в корзине, `requests` в боте для CryptoBot API, bcrypt прямо в event loop.
- **Новое подключение к Redis на каждый запрос** в корзине, настройках и вебхуке, вместо общего пула.
- **Баг в `cart.add_product`**: `return r.json().get(...)` стоит после выхода из `with`, то есть обращение к уже закрытому клиенту.
- **Три точки подключения к RabbitMQ**: producer-брокер, consumer-брокер и лишний `RabbitRouter` в `api_v1/services/bot.py` с демо-эндпоинтом `POST /orders/new/`, публикующим сообщение в никуда.
- **Состояние бота в памяти процесса**: `cr_responses` и `cr_amounts` теряются при перезапуске и не работают в нескольких процессах.
- **Два конкурирующих хранилища файлов**: `core/s3_core.py` (R2) написан, но роутеры используют локальный `services/images.py` с захардкоженным доменом `https://media.redstoreapp.com/`.
- **Слои размыты**: часть роутеров дергает репозитории напрямую, минуя сервисы; `services/dependencies.py` совмещает парсинг формы с обращениями к БД; в `services/orders.py` локальная переменная называется `sum`.
- **Нет пагинации в каталоге**: `GET /products/` и `GET /categories/` всегда отдают всё целиком.
- **CORS-origins и хосты захардкожены** в `core/config.py`, включая локальный IP из домашней сети.

#### Качество и эксплуатация

- **Нет ни одного теста**, нет линтера и type-check в CI (пайплайн только деплоит).
- **Отладочный вывод в проде**: `print("d")` в `services/dependencies.py`, `print(items)` в `services/orders.py`, `print` в `repositories/products.py` и `bot/bot.py`.
- **Нет healthcheck-эндпоинта**: `GET /` возвращает строку `"Hello"`.
- **Мусор в зависимостях и репозитории**: `aiosqlite` вместе с `db.sqlite3` от раннего прототипа, одновременно `yoomoney` и `aioyoomoney-api`, пустой `files.py`, миграция с именем `описание_миграции`.
- **Контейнер запускается от root**, `poetry install` тянет и dev-зависимости.
- **Логирование через `logging.getLogger(__name__)` в `core/common.py`**, поэтому все логи ядра идут от одного имени; в `views/users.py` используется устаревший `logger.warn`.

### Планы

1. **Каскадное удаление товаров** (баг, чиним первым). Товар не удаляется, если он лежит у кого-то в избранном, имеет отзывы или попал в заказ.
2. **Перестройка авторизации.** Серверные сессии в БД вместо подписанной cookie, чтобы админа можно было отозвать мгновенно, и авторизация клиента вместо `tg_id` в пути.
3. **Улучшение архитектуры.** Разделение API, бота и consumers по процессам, атомарное создание заказа, нормализация схемы.
4. **Кеширование.** Кеш каталога в Redis и общий пул подключений вместо нового клиента на каждый запрос.

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
- **Orders**: balance debit, order and order item creation, cart cleanup, event publishing to RabbitMQ; status filter and pagination for the admin list.
- **Async processing over RabbitMQ**: the API responds immediately while slow work (Telegram API calls, product delivery) moves to queues with retries and a DLQ.
- **Payments**: Telegram Stars (`send_invoice`, `pre_checkout_query`, `successful_payment`), CryptoBot (invoice creation and status polling), YooMoney (Quickpay + webhook with SHA-1 signature check and replay protection via `SET NX EX` in Redis).
- **Admin auth**: bcrypt hashes in the `admins` table, login by username/password, server-side session in a signed cookie (`SessionMiddleware`), mutating endpoints guarded by the `check_if_auth` dependency.
- **Runtime shop settings in Redis**: accent color, stars exchange rate, bot token (with hot polling restart), CryptoBot token, YooMoney credentials, enabled payment methods.
- **Infrastructure**: Docker Compose (backend, PostgreSQL, Redis, RabbitMQ with healthchecks), `entrypoint.sh` that waits for the DB and auto-initializes it, GitLab CI deploy on push to `main`.
- **Migrations**: 17 Alembic revisions with an async engine and date-prefixed filenames.

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

### Known issues and tech debt

An honest list, and the basis for the roadmap below.

#### Security

- **Public endpoints do not verify the caller.** `tg_id` arrives as a path parameter, so anyone can read and modify another user's cart and favorites, place an order on their behalf and drain their balance, or call `GET /users/` for the full user list. Telegram Web App `initData` is never validated.
- **Balance top-up is directly callable.** `POST /users/replenisment/*` accepts arbitrary `tg_id` and `amount` with no authorization.
- **An admin session cannot be revoked.** `SessionMiddleware` keeps the state in a signed cookie on the client, with no server-side session record. Deleting an admin, changing a password or leaking the cookie does not log anyone out: access survives until `SESSION_EXPIRE_TIME` elapses, which is a full day.
- **No CSRF protection or rate limiting** for cookie sessions and `POST /auth/login/`; `same_site` is not configured for `SessionMiddleware`.
- **Tokens are stored in Redis in plaintext**, and `GET /settings/bot_token/` returns the bot token.
- **Path traversal on product file upload**: `os.path.join("files", data.filename)` uses the client-supplied filename without normalization.
- **`db.sqlite3` is committed to the repository**, and the image is built without a `.dockerignore`, so `.git`, the local DB and `files/` end up inside it.

#### Data consistency

- **Product deletion fails on hard foreign keys.** If a product is in someone's favorites, has reviews, or appears in an order, `DELETE /products/{id}/` returns a 500 with `IntegrityError`: the FKs were created without `ON DELETE`, and the relationships have no `cascade` or `passive_deletes`. A category with products and a user with favorites cannot be deleted either. Full breakdown and fix plan in the [roadmap](#roadmap).
- **Order creation is not transactional**: the balance is debited and committed separately from order creation, before the cart is cleared and messages are published. A mid-way failure leaves the user without money and without an order.
- **No row lock when debiting the balance**: concurrent requests allow double spending and a negative balance. Insufficient funds return `HTTPException(500)` instead of 400/402.
- **`OrdersItem` stores neither quantity nor the price at purchase time**, so the order contents and total cannot be reconstructed, and a price change rewrites history.
- **Schema built on natural keys**: `Product.category_title` references `categorys.title`, `Order.user` references `users.tg_id`. Renaming a category cascades across all products, and the `categorys` table name comes from the auto-generated `__tablename__`.
- **No `created_at` / `updated_at`** on any model, so orders cannot be sorted by time.
- **`Product.rating` is decoupled from `Review.rate`**: the rating is not aggregated from reviews, it is typed in through the form.
- **`scripts/init_db.py` runs `create_all` + `alembic stamp head` on an empty DB**, which drifts from the migration history.
- **The YooMoney webhook is idempotent on `label`, not `operation_id`**, and `int(float(amount))` drops the fractional part.

#### Architecture

- **API, bot and consumers share one process.** It does not scale horizontally: multiple Uvicorn workers would cause `getUpdates` conflicts and duplicated queue processing.
- **Blocking calls inside async handlers**: synchronous `redis` in the cart, `requests` in the bot for the CryptoBot API, bcrypt straight on the event loop.
- **A new Redis connection per request** in the cart, settings and webhook code instead of a shared pool.
- **Bug in `cart.add_product`**: `return r.json().get(...)` sits outside the `with` block, so it talks to an already closed client.
- **Three RabbitMQ connection points**: the producer broker, the consumer broker, and a leftover `RabbitRouter` in `api_v1/services/bot.py` with a demo `POST /orders/new/` endpoint publishing into nowhere.
- **Bot state kept in process memory**: `cr_responses` and `cr_amounts` are lost on restart and break with more than one process.
- **Two competing file storages**: `core/s3_core.py` (R2) exists, but the routers use the local `services/images.py` with a hardcoded `https://media.redstoreapp.com/` domain.
- **Blurred layers**: some routers hit repositories directly, bypassing services; `services/dependencies.py` mixes form parsing with DB access; `services/orders.py` shadows the builtin `sum`.
- **No pagination in the catalog**: `GET /products/` and `GET /categories/` always return everything.
- **CORS origins and hosts are hardcoded** in `core/config.py`, including a home LAN IP.

#### Quality and operations

- **Zero tests**, no linter or type check in CI (the pipeline only deploys).
- **Debug output in production**: `print("d")` in `services/dependencies.py`, `print(items)` in `services/orders.py`, `print` in `repositories/products.py` and `bot/bot.py`.
- **No healthcheck endpoint**: `GET /` returns the string `"Hello"`.
- **Leftovers in dependencies and the repo**: `aiosqlite` together with `db.sqlite3` from the early prototype, both `yoomoney` and `aioyoomoney-api`, an empty `files.py`, a migration literally named "описание_миграции".
- **The container runs as root**, and `poetry install` pulls dev dependencies too.
- **Logging goes through `logging.getLogger(__name__)` in `core/common.py`**, so all core logs share one logger name; `views/users.py` uses the deprecated `logger.warn`.

### Roadmap

1. **Cascading product deletes** (bug, fixed first). A product cannot be deleted while it sits in someone's favorites, has reviews, or appears in an order.
2. **Auth rebuild.** Server-side sessions in the database instead of a signed cookie, so an admin can be revoked instantly, plus real client auth instead of `tg_id` in the path.
3. **Architecture improvements.** Split the API, bot and consumers into separate processes, make order creation atomic, normalize the schema.
4. **Caching.** Redis cache for the catalog and a shared connection pool instead of a new client per request.

</details>
