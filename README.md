# Achievements API

API для управления достижениями пользователей с поддержкой многоязычности и расширенной статистики.

## Особенности

- **Многоязычность**: Поддержка русского и английского языков
- **Асинхронность**: Полностью асинхронное FastAPI приложение с asyncpg
- **Статистика**: Сложная аналитика включая поиск 7-дневных серий достижений
- **Контейнеризация**: Docker Compose с PostgreSQL, FastAPI и Nginx
- **Тестирование**: Comprehensive test suite с 36 тестами
- **Документация**: Автоматическая OpenAPI документация

## Архитектура

```
app/
├── api/              # API endpoints
│   ├── users.py      # Пользователи
│   ├── achievements.py # Достижения
│   └── statistics.py # Статистика
├── core/
│   └── database.py   # Конфигурация БД
├── models/           # SQLAlchemy модели
│   ├── user.py
│   ├── achievement.py
│   └── user_achievement.py
├── schemas/          # Pydantic схемы
├── services/         # Бизнес-логика
└── tests/           # Тесты
```

## Быстрый старт

### Требования

- Docker и Docker Compose
- Python 3.11+ (для локальной разработки)

### Запуск

1. **Клонировать репозиторий**
   ```bash
   git clone <repository-url>
   cd elvis_test
   ```

2. **Запустить все сервисы**
   ```bash
   docker-compose up -d --build
   ```

3. **Применить миграции**
   ```bash
   docker-compose exec backend alembic upgrade head
   ```

4. **Проверить работу**
   - API: http://localhost/
   - Документация: http://localhost/docs
   - Альтернативная документация: http://localhost/redoc

## API Endpoints

### Пользователи

- `POST /users/` - Создать пользователя
- `GET /users/{user_id}` - Получить пользователя
- `GET /users/` - Список пользователей
- `GET /users/{user_id}/achievements` - Достижения пользователя (локализованные)

### Достижения

- `POST /achievements/` - Создать достижение
- `GET /achievements/{achievement_id}` - Получить достижение
- `GET /achievements/` - Список достижений
- `POST /achievements/award` - Выдать достижение пользователю

### Статистика

- `GET /stats/top-by-achievements` - Пользователь с наибольшим количеством достижений
- `GET /stats/top-by-points` - Пользователь с наибольшим количеством очков
- `GET /stats/min-max-points-difference` - Разница между пользователями с min/max очками
- `GET /stats/7-day-streak-users` - Пользователи с 7-дневными сериями достижений

## Примеры использования

### Создание пользователя

```bash
curl -X POST "http://localhost/users/" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "john_doe",
    "language": "en"
  }'
```

### Создание достижения

```bash
curl -X POST "http://localhost/achievements/" \
  -H "Content-Type: application/json" \
  -d '{
    "name_ru": "Первые шаги",
    "name_en": "First Steps",
    "description_ru": "Ваше первое достижение в системе",
    "description_en": "Your first achievement in the system",
    "points": 10
  }'
```

### Выдача достижения пользователю

```bash
curl -X POST "http://localhost/achievements/award" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": 1,
    "achievement_id": 1
  }'
```

## Разработка

### Локальная разработка

```bash
# Установить зависимости
pip install -r requirements.txt

# Запустить сервер разработки
uvicorn app.main:app --reload

# Запустить тесты
pytest app/tests/ -v
```

### Структура базы данных

#### Таблица users
- `id` - Primary Key
- `username` - Уникальное имя пользователя
- `language` - Язык пользователя (ru/en)

#### Таблица achievements
- `id` - Primary Key
- `name_ru` - Название на русском
- `name_en` - Название на английском
- `description_ru` - Описание на русском
- `description_en` - Описание на английском
- `points` - Количество очков (положительное число)

#### Таблица user_achievements
- `id` - Primary Key
- `user_id` - Foreign Key на users
- `achievement_id` - Foreign Key на achievements
- `awarded_at` - Timestamp выдачи достижения

## Тестирование

Проект включает comprehensive test suite:

```bash
# Запуск всех тестов
docker-compose exec backend pytest app/tests/ -v

# Запуск конкретной группы тестов
docker-compose exec backend pytest app/tests/test_users.py -v
docker-compose exec backend pytest app/tests/test_achievements.py -v
docker-compose exec backend pytest app/tests/test_statistics.py -v
```

### Покрытие тестов

- **36 тестов** покрывают все основные сценарии
- **CRUD операции** для пользователей и достижений
- **Локализация** достижений
- **Статистические расчеты** включая сложные SQL-запросы
- **Валидация** входных данных
- **Обработка ошибок** и пограничных случаев

## Технические особенности

### Асинхронность

- **asyncpg** для работы с PostgreSQL
- **AsyncSession** для всех операций с БД
- **Полностью асинхронные** API endpoints

### Многоязычность

- Достижения хранятся с переводами (ru/en)
- Автоматическая локализация на основе языка пользователя
- Поддержка добавления новых языков

### Статистика

- Эффективные SQL-запросы для аналитики
- Поддержка сложных временных серий
- Кроссплатформенность (PostgreSQL/SQLite)

## Развертывание

### Production

```bash
# Запуск в production режиме
docker-compose -f docker-compose.prod.yml up -d

# Мониторинг логов
docker-compose logs -f backend
```

### Nginx конфигурация

Включен reverse proxy через Nginx:
- Automatic SSL termination (при настройке)
- Load balancing support
- Static files serving

## Мониторинг

- **Logs**: Структурированное логирование
- **Health checks**: Встроенные проверки состояния
- **Metrics**: Готовность к интеграции с Prometheus

## Безопасность

- **Input validation** через Pydantic
- **SQL injection protection** через SQLAlchemy
- **CORS** настройки
- **Rate limiting** готовность

## Развитие

### Возможные улучшения

1. **Аутентификация**: JWT токены
2. **Кеширование**: Redis для статистики
3. **Уведомления**: WebSocket для real-time updates
4. **Изображения**: Поддержка иконок достижений
5. **Экспорт**: CSV/JSON экспорт статистики

### Масштабирование

- Готовность к horizontal scaling
- Database sharding поддержка
- Microservices decomposition
