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

#### Docker (рекомендуется)

```bash
cp .env.example .env   # файла пока нет, переменные см. в таблице ниже
docker compose up -d --build
docker compose logs -f backend
```

- API: http://localhost:8000
- Swagger: http://localhost:8000/docs
- RabbitMQ UI: http://localhost:15672 (admin / admin123)

#### Локально

```bash
poetry install
docker compose up -d postgresql redis rabbitmq
alembic upgrade head
poetry run python main.py
```

#### Переменные окружения

Обязательные:

| Переменная | Назначение |
| --- | --- |
| `BOT_TOKEN` | токен Telegram-бота |
| `ADMIN_TG_ID` | Telegram ID администратора для уведомлений |
| `CRYPTO_BOT_TOKEN` | токен Crypto Pay API |
| `ADMIN_USERNAME`, `ADMIN_PASSWORD` | первый админ, создаётся `scripts/init_db.py` |
| `SECRET_SESSION_KEY` | ключ подписи cookie-сессий |
| `YOOMONEY_TOKEN`, `YOOMONEY_WALLET`, `YOOMONEY_NOTIFICATION_SECRET` | реквизиты ЮMoney |

Опциональные:

| Переменная | По умолчанию |
| --- | --- |
| `db_url` | строка подключения захардкожена в `core/config.py` |
| `REDIS_HOST`, `REDIS_PORT` | `localhost`, `6379` |
| `RABBITMQ_HOST`, `RABBITMQ_PORT`, `RABBITMQ_USER`, `RABBITMQ_PASSWORD` | `localhost`, `5672`, `admin`, `admin123` |
| `R2_ACCESS_KEY`, `R2_SECRET_KEY`, `R2_ENDPOINT`, `R2_PUBLIC_URL` | пустые |
| `IMAGES_DIR` | `/var/www/media` |
| `SESSION_EXPIRE_TIME`, `SESSION_SECURE` | `86400`, `true` |
| `logging_level`, `host`, `port` | `INFO`, `localhost`, `8000` |

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
alembic revision --autogenerate -m "описание"
alembic upgrade head
alembic downgrade -1
```

### Формат кода

```bash
poetry run black .          # отформатировать
poetry run black --check .  # проверить без изменений
```

В PyCharm: `Settings → Tools → Black` (включить) и `Settings → Tools → Actions on Save → Reformat code`.

### Известные проблемы и техдолг

Список честный, он же основа для роадмапа ниже.

#### Безопасность

- **Публичные эндпоинты не проверяют, кто их вызывает.** `tg_id` приходит параметром пути, поэтому любой человек может прочитать и изменить чужую корзину и избранное, создать заказ за другого пользователя и списать его баланс, запросить `GET /users/` со списком всех пользователей. Подпись `initData` из Telegram Web App нигде не валидируется.
- **Пополнение баланса вызывается напрямую.** `POST /users/replenisment/*` принимает произвольные `tg_id` и `amount` без авторизации.
- **Дефолтные секреты в репозитории**: `admin/admin123` для RabbitMQ (в `core/config.py` и `docker-compose.yml`), `password123` для PostgreSQL, готовая строка подключения к БД в `core/config.py`.
- **Порт RabbitMQ Management открыт наружу** (`"15672:15672"`), в отличие от остальных сервисов, привязанных к `127.0.0.1`, и с дефолтным паролем.
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

#### 1. Каскадное удаление и архивация товаров (баг, чиним первым)

Товар нельзя удалить, если он лежит у кого-то в избранном: приходит `IntegrityError` от жёсткой связи, а клиент получает необработанный 500. То же самое с товаром, на который есть отзывы или который попал в заказ, и с категорией, у которой есть товары.

Причина в том, что все внешние ключи созданы автогенерацией Alembic без `ON DELETE`, а у ORM-связей не задано ни `cascade`, ни `passive_deletes`:

| Ключ | Файл | Что происходит при удалении |
| --- | --- | --- |
| `favorites.product_id → products.id` | `core/models/Favorites.py` | строки избранного не удаляются, `DELETE` товара падает |
| `favorites.user_id → users.id` | `core/models/Favorites.py` | то же при удалении пользователя |
| `reviews.product_id → products.id` | `core/models/Review.py` | колонка `NOT NULL`, а связь по умолчанию пытается занулить FK |
| `ordersitems.product_id → products.id` | `core/models/Order.py` | то же, плюс удаление разрушило бы историю заказов |
| `products.category_title → categorys.title` | `core/models/Product.py` | указан только `onupdate="CASCADE"`, удаление категории с товарами падает |

Что делать:

- `ondelete="CASCADE"` на связях-справочниках, которые не жалко терять вместе с товаром: `favorites`, `reviews`. Миграция + `passive_deletes=True` в relationship.
- Товар, который встречается в заказах, **не удалять физически**: мягкое удаление (`is_active` / `archived_at`), он исчезает с витрины, но история заказов остаётся целой.
- `ondelete="RESTRICT"` для `ordersitems.product_id` и осмысленный ответ 409 вместо 500.
- Для категорий: `ondelete="SET NULL"` (товар остаётся без категории) вместо падения.
- Обработка `IntegrityError` в `repositories/products.py` и `repositories/categories.py`, чтобы наружу уходил понятный код ошибки, а не трассировка.

#### 2. Перестройка авторизации

Схема одна для всех клиентов: **серверные (stateful) сессии с хранением в БД**. Никаких stateless-токенов (JWT), потому что они живут до истечения срока и отозвать их нельзя. В cookie уезжает только непредсказуемый идентификатор сессии, всё состояние лежит в базе, поэтому доступ отзывается мгновенно удалением записи.

Сейчас работает противоположное: `SessionMiddleware` кладёт состояние в подписанную cookie, то есть сессия живёт на клиенте и сервер не может её погасить до истечения `SESSION_EXPIRE_TIME`.

**Хранилище сессий.** Таблица `sessions`:

| Поле | Зачем |
| --- | --- |
| `id` | первичный ключ |
| `token_hash` | SHA-256 от токена из cookie, сам токен в БД не хранится |
| `subject_type`, `subject_id` | `admin` / `user` и ссылка на владельца |
| `created_at`, `expires_at`, `last_seen_at` | срок жизни и sliding expiration |
| `revoked_at` | мгновенный отзыв без удаления истории |
| `ip`, `user_agent` | чтобы админ видел свои устройства и чужие входы |

**Поток запроса.** Зависимость вместо `check_if_auth`: берём токен из httpOnly cookie, считаем хеш, ищем сессию, проверяем `expires_at` и `revoked_at`, подтягиваем роль, обновляем `last_seen_at`. Кеш здесь не нужен: админов 2-3, выборка по уникальному индексу `token_hash` дешевле, чем инвалидация кеша при отзыве, а любой кеш с TTL как раз и сломал бы мгновенность отзыва.

**Что это даёт по контролю:**

- `DELETE /auth/sessions/{id}/` для одной сессии и «выйти на всех устройствах» для всех.
- Автоматический отзыв всех сессий админа при смене пароля и при его удалении или деактивации.
- Список активных сессий в админке: устройство, IP, время последней активности.
- Ротация токена при входе, чтобы закрыть session fixation.

**Клиент (Mini App)** получает такую же серверную сессию вместо `tg_id` в пути:

- `POST /auth/telegram/` принимает `initData` из `window.Telegram.WebApp`, проверяет подпись HMAC-SHA256 от `BOT_TOKEN` и свежесть `auth_date`.
- После проверки пользователь создаётся или находится по `tg_id`, создаётся сессия, клиент дальше работает по cookie и `initData` не пересылает.
- `tg_id` и `user_id` берутся из сессии: `/cart/{tg_id}/`, `/favorites/{tg_id}/`, `POST /orders/` теряют параметр и работают только со своими данными. Это закрывает доступ к чужим корзинам, избранному, заказам и балансу.
- Вебхуки платёжек остаются вне сессий и проверяются подписью провайдера.
- Пополнение баланса только по подтверждённому платежу, публичные `replenisment`-эндпоинты убираются.

Плюс общая обвязка: httpOnly + `Secure` + `SameSite`, CSRF-токен на изменяющие запросы, rate limit и блокировка после серии неудачных входов, аудит-лог действий администратора.

Что учесть при реализации: витрина и API живут на разных хостах, поэтому cookie для Mini App кросс-сайтовая и требует `Secure` + `SameSite=None` (`allow_credentials=True` в CORS уже стоит). В WebView Telegram это работает, но ограничения на сторонние cookie в некоторых клиентах стоит проверить на реальных устройствах до перевода витрины на сессии.

#### 3. Улучшение архитектуры

- Разнести API, polling бота и consumers по отдельным процессам/контейнерам, чтобы масштабировать API воркерами.
- Убрать блокирующий I/O: `redis.asyncio` с общим пулом, `aiohttp`/`httpx` вместо `requests`, bcrypt в thread pool.
- Единая транзакционная граница на запрос (session-per-request + commit в одном месте), заказ создаётся атомарно, баланс списывается с `SELECT ... FOR UPDATE`.
- Outbox-паттерн для публикации в RabbitMQ, чтобы сообщение уходило только после коммита транзакции.
- Нормализация схемы: `category_id` вместо `category_title`, `user_id` вместо `tg_id` в заказах, `quantity` и `price_at_purchase` в `OrdersItem`, `created_at`/`updated_at` во всех моделях, рейтинг как агрегат отзывов.
- Одно хранилище файлов (R2) за интерфейсом, локальный путь только для dev, домены из конфига.
- Чистые слои view → service → repository, вынос платежных провайдеров за общий интерфейс.
- Пагинация, фильтры и сортировка в каталоге.
- Тесты (pytest + httpx + testcontainers), линтеры и type-check в CI, `.dockerignore`, non-root контейнер.

#### 4. Кеширование

- Кеш каталога и категорий в Redis с инвалидацией при изменении товара, вместо чтения из PostgreSQL на каждый запрос витрины.
- Кеш детальной карточки товара и рантайм-настроек магазина, чтобы `GET /settings/*` не ходил в Redis по одному ключу за раз.
- ETag / `Cache-Control` для витринных GET-эндпоинтов и CDN-кеш для изображений.
- Общий connection pool и единый слой доступа к кешу, вместо ручного `redis.Redis(...)` в каждой функции.
- Защита от cache stampede на популярных товарах, метрики hit/miss.

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

#### Docker (recommended)

```bash
cp .env.example .env   # no such file yet, see the variables table below
docker compose up -d --build
docker compose logs -f backend
```

- API: http://localhost:8000
- Swagger: http://localhost:8000/docs
- RabbitMQ UI: http://localhost:15672 (admin / admin123)

#### Local

```bash
poetry install
docker compose up -d postgresql redis rabbitmq
alembic upgrade head
poetry run python main.py
```

#### Environment variables

Required:

| Variable | Purpose |
| --- | --- |
| `BOT_TOKEN` | Telegram bot token |
| `ADMIN_TG_ID` | admin Telegram ID for notifications |
| `CRYPTO_BOT_TOKEN` | Crypto Pay API token |
| `ADMIN_USERNAME`, `ADMIN_PASSWORD` | first admin, created by `scripts/init_db.py` |
| `SECRET_SESSION_KEY` | cookie session signing key |
| `YOOMONEY_TOKEN`, `YOOMONEY_WALLET`, `YOOMONEY_NOTIFICATION_SECRET` | YooMoney credentials |

Optional:

| Variable | Default |
| --- | --- |
| `db_url` | connection string hardcoded in `core/config.py` |
| `REDIS_HOST`, `REDIS_PORT` | `localhost`, `6379` |
| `RABBITMQ_HOST`, `RABBITMQ_PORT`, `RABBITMQ_USER`, `RABBITMQ_PASSWORD` | `localhost`, `5672`, `admin`, `admin123` |
| `R2_ACCESS_KEY`, `R2_SECRET_KEY`, `R2_ENDPOINT`, `R2_PUBLIC_URL` | empty |
| `IMAGES_DIR` | `/var/www/media` |
| `SESSION_EXPIRE_TIME`, `SESSION_SECURE` | `86400`, `true` |
| `logging_level`, `host`, `port` | `INFO`, `localhost`, `8000` |

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
alembic revision --autogenerate -m "message"
alembic upgrade head
alembic downgrade -1
```

### Code style

```bash
poetry run black .          # format
poetry run black --check .  # check without writing
```

In PyCharm: `Settings → Tools → Black` (enable) and `Settings → Tools → Actions on Save → Reformat code`.

### Known issues and tech debt

An honest list, and the basis for the roadmap below.

#### Security

- **Public endpoints do not verify the caller.** `tg_id` arrives as a path parameter, so anyone can read and modify another user's cart and favorites, place an order on their behalf and drain their balance, or call `GET /users/` for the full user list. Telegram Web App `initData` is never validated.
- **Balance top-up is directly callable.** `POST /users/replenisment/*` accepts arbitrary `tg_id` and `amount` with no authorization.
- **Default secrets committed to the repo**: `admin/admin123` for RabbitMQ (in `core/config.py` and `docker-compose.yml`), `password123` for PostgreSQL, a ready-to-use DB connection string in `core/config.py`.
- **RabbitMQ management port is exposed publicly** (`"15672:15672"`), unlike the other services bound to `127.0.0.1`, and with the default password.
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

#### 1. Cascading deletes and product archiving (bug, fixed first)

A product cannot be deleted while it sits in someone's favorites: the hard FK raises `IntegrityError` and the client gets an unhandled 500. The same happens for a product that has reviews or appears in an order, and for a category that still has products.

The cause is that every foreign key came from Alembic autogeneration without `ON DELETE`, and the ORM relationships declare neither `cascade` nor `passive_deletes`:

| Key | File | What happens on delete |
| --- | --- | --- |
| `favorites.product_id → products.id` | `core/models/Favorites.py` | favorite rows stay, the product `DELETE` fails |
| `favorites.user_id → users.id` | `core/models/Favorites.py` | same when deleting a user |
| `reviews.product_id → products.id` | `core/models/Review.py` | the column is `NOT NULL` while the default relationship tries to nullify the FK |
| `ordersitems.product_id → products.id` | `core/models/Order.py` | same, and deleting would destroy order history |
| `products.category_title → categorys.title` | `core/models/Product.py` | only `onupdate="CASCADE"` is set, so deleting a category with products fails |

The plan:

- `ondelete="CASCADE"` for dependent rows that should disappear with the product: `favorites`, `reviews`. Migration plus `passive_deletes=True` on the relationship.
- A product referenced by orders must **never be hard-deleted**: soft delete (`is_active` / `archived_at`) removes it from the storefront while order history stays intact.
- `ondelete="RESTRICT"` for `ordersitems.product_id` and a meaningful 409 instead of a 500.
- For categories: `ondelete="SET NULL"` (the product survives without a category) instead of failing.
- Handle `IntegrityError` in `repositories/products.py` and `repositories/categories.py` so callers get a proper status code rather than a traceback.

#### 2. Auth rebuild

One scheme for every client: **server-side (stateful) sessions stored in the database**. No stateless tokens (JWT), because they stay valid until they expire and cannot be revoked. The cookie carries nothing but an unpredictable session id, all state lives in the DB, so access is revoked instantly by deleting the record.

Today it works the other way around: `SessionMiddleware` puts the state into a signed cookie, so the session lives on the client and the server cannot kill it before `SESSION_EXPIRE_TIME` runs out.

**Session store.** A `sessions` table:

| Column | Purpose |
| --- | --- |
| `id` | primary key |
| `token_hash` | SHA-256 of the cookie token; the token itself is never stored |
| `subject_type`, `subject_id` | `admin` / `user` plus a reference to the owner |
| `created_at`, `expires_at`, `last_seen_at` | lifetime and sliding expiration |
| `revoked_at` | instant revocation without losing history |
| `ip`, `user_agent` | so an admin can see their devices and spot foreign logins |

**Request flow.** A dependency replacing `check_if_auth`: read the token from the httpOnly cookie, hash it, look the session up, check `expires_at` and `revoked_at`, load the role, refresh `last_seen_at`. No cache here: there are 2-3 admins, a lookup on the unique `token_hash` index is cheaper than invalidating a cache on revocation, and any TTL-based cache would break the instant revocation we are building this for.

**What this buys in terms of control:**

- `DELETE /auth/sessions/{id}/` for a single session and "log out everywhere" for all of them.
- Automatic revocation of every admin session on password change and on admin deletion or deactivation.
- A list of active sessions in the admin panel: device, IP, last activity.
- Token rotation on login to close session fixation.

**The client (Mini App)** gets the same server-side session instead of `tg_id` in the path:

- `POST /auth/telegram/` takes `initData` from `window.Telegram.WebApp`, verifies the HMAC-SHA256 signature derived from `BOT_TOKEN` and checks `auth_date` freshness.
- On success the user is created or looked up by `tg_id`, a session is created, and from then on the client works purely on the cookie and stops resending `initData`.
- `tg_id` and `user_id` come from the session: `/cart/{tg_id}/`, `/favorites/{tg_id}/` and `POST /orders/` lose the parameter and can only touch the caller's own data. That closes access to other users' carts, favorites, orders and balances.
- Payment webhooks stay outside the session layer and are verified by provider signature.
- Top up the balance only from a confirmed payment; drop the public `replenisment` endpoints.

Plus the shared hardening: httpOnly + `Secure` + `SameSite`, a CSRF token on mutating requests, rate limiting and lockout after repeated failed logins, and an audit log of admin actions.

Implementation note: the storefront and the API live on different hosts, so the Mini App cookie is cross-site and needs `Secure` + `SameSite=None` (CORS already sets `allow_credentials=True`). This works inside the Telegram WebView, but third-party cookie restrictions in some clients should be verified on real devices before moving the storefront onto sessions.

#### 3. Architecture improvements

- Split the API, bot polling and consumers into separate processes/containers so the API can scale with workers.
- Remove blocking I/O: `redis.asyncio` with a shared pool, `aiohttp`/`httpx` instead of `requests`, bcrypt in a thread pool.
- One transaction boundary per request (session-per-request with a single commit point), atomic order creation, balance debited with `SELECT ... FOR UPDATE`.
- Outbox pattern for RabbitMQ publishing so messages leave only after the transaction commits.
- Schema normalization: `category_id` instead of `category_title`, `user_id` instead of `tg_id` on orders, `quantity` and `price_at_purchase` on `OrdersItem`, `created_at`/`updated_at` everywhere, rating aggregated from reviews.
- A single file storage (R2) behind an interface, local paths for dev only, domains from config.
- Clean view → service → repository layering, payment providers behind a shared interface.
- Pagination, filtering and sorting in the catalog.
- Tests (pytest + httpx + testcontainers), linters and type checks in CI, a `.dockerignore`, a non-root container.

#### 4. Caching

- Cache the catalog and categories in Redis with invalidation on product changes, instead of hitting PostgreSQL on every storefront request.
- Cache product detail pages and runtime shop settings so `GET /settings/*` stops fetching one Redis key at a time.
- ETag / `Cache-Control` for storefront GET endpoints and CDN caching for images.
- A shared connection pool and a single cache access layer instead of a manual `redis.Redis(...)` in every function.
- Cache stampede protection for hot products, plus hit/miss metrics.

</details>
