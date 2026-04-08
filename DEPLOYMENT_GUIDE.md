# Инструкция по развёртыванию проекта с PostgreSQL

## 1. Подготовка окружения

### 1.1 Убедитесь, что Docker установлен
```bash
docker --version
docker-compose --version
```

### 1.2 Перейдите в директорию проекта
```bash
cd /home/timoshik/Documents/kursach_\ rabochii/kursach_timoshik_ready/kursach_timoshik/healthy_world
```

---

## 2. Запуск PostgreSQL в Docker

### 2.1 Проверьте конфиг docker-compose.yml
```bash
cat docker-compose.yml
```

Файл должен содержать конфигурацию PostgreSQL с переменными окружения.

### 2.2 Запустите контейнеры
```bash
docker-compose up -d
```

Эта команда:
- Запустит контейнер PostgreSQL в фоне (`-d` флаг)
- Создаст необходимые volumes и networks
- Инициализирует БД с переданными переменными окружения

### 2.3 Проверьте, что контейнер запустился
```bash
docker-compose ps
```

Вы должны увидеть запущенный сервис `db` со статусом `Up`.

### 2.4 (Опционально) Проверьте логи
```bash
docker-compose logs db
```

---

## 3. Установка зависимостей Python

### 3.1 Установите зависимости из requirements.txt
```bash
pip3 install --break-system-packages -r requirements.txt
```

Или создайте виртуальное окружение (рекомендуется):
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 3.2 Проверьте установку
```bash
python3 -m django --version
```

---

## 4. Применение миграций БД

### 4.1 Создайте миграции для нового модуля games (если их нет)
```bash
python3 manage.py makemigrations games
```

Результат: `Migrations for 'games': games/migrations/0001_initial.py`

### 4.2 Примените все миграции к БД
```bash
python3 manage.py migrate
```

Вывод должен быть похож на:
```
Operations to perform:
  Apply all migrations: admin, auth, contenttypes, fooddiary, games, sessions, users

Running migrations:
  Applying contenttypes.0001_initial... OK
  Applying auth.0001_initial... OK
  ...
  Applying games.0001_initial... OK
  ...
```

---

## 5. Загрузка тестовых данных

### 5.1 Запустите Django shell
```bash
python3 manage.py shell
```

### 5.2 Выполните в shell следующий код:
```python
from games.models import Product, GameLevel, CalorieCounterQuestion
import json

# Создаем продукты
products_data = [
    {"name": "Яблоко", "calories": 52},
    {"name": "Банан", "calories": 89},
    {"name": "Хлеб пшеничный", "calories": 265},
    {"name": "Молоко", "calories": 64},
    {"name": "Курица без кожи", "calories": 165},
    {"name": "Рис белый вареный", "calories": 130},
    {"name": "Картофель вареный", "calories": 82},
    {"name": "Помидоры", "calories": 18},
    {"name": "Огурцы", "calories": 16},
]

products = {}
for prod in products_data:
    p = Product.objects.get_or_create(
        name=prod["name"],
        defaults={"calories": prod["calories"]}
    )[0]
    products[prod["name"]] = p

# Создаем уровни
levels_data = [
    {
        "title": "Легкий завтрак",
        "description": "Соберите завтрак на 300 ккал",
        "target_calories": 300,
        "min_calories": 250,
        "max_calories": 350,
        "difficulty": "easy",
        "products": ["Хлеб пшеничный", "Молоко", "Яблоко"]
    },
]

for level_data in levels_data:
    prod_list = level_data.pop("products")
    level, created = GameLevel.objects.get_or_create(
        title=level_data["title"],
        defaults=level_data
    )
    if created:
        for prod_name in prod_list:
            level.products.add(products[prod_name])

print("✅ Тестовые данные загружены!")
exit()
```

### 5.3 Выйдите из shell
```bash
exit()
```

---

## 6. Создание суперпользователя (админа)

```bash
python3 manage.py createsuperuser
```

Следуйте подсказкам:
```
Username: admin
Email address: admin@example.com
Password: ********
Password (again): ********
Superuser created successfully.
```

---

## 7. Запуск разработческого сервера

### 7.1 Запустите Django сервер
```bash
python3 manage.py runserver
```

Вывод:
```
Starting development server at http://127.0.0.1:8000/
```

### 7.2 Откройте в браузере
```
http://localhost:8000
```

### 7.3 Админка доступна по адресу
```
http://localhost:8000/admin
```

Используйте учетные данные суперпользователя, которые создали на шаге 6.

---

## 8. Проверка работы игр

### 8.1 Главная страница игр
```
http://localhost:8000/games/
```

### 8.2 Игра "Собери здоровое меню"
```
http://localhost:8000/games/menu-builder/levels/
```

### 8.3 Игра "Подсчитай калории"
```
http://localhost:8000/games/calorie-counter/levels/
```

---

## 9. Остановка сервера и контейнеров

### 9.1 Остановить Django сервер
```bash
Ctrl + C
```

### 9.2 Остановить Docker контейнеры
```bash
docker-compose down
```

Эта команда остановит и удалит контейнеры, но сохранит данные в volumes.

### 9.3 Остановить контейнеры (без удаления)
```bash
docker-compose stop
```

### 9.4 Запустить остановленные контейнеры
```bash
docker-compose start
```

---

## 10. Полный цикл команд (сокращенно)

```bash
# 1. Перейти в проект
cd /home/timoshik/Documents/kursach_\ rabochii/kursach_timoshik_ready/kursach_timoshik/healthy_world

# 2. Запустить PostgreSQL
docker-compose up -d

# 3. Установить зависимости
pip3 install --break-system-packages -r requirements.txt

# 4. Применить миграции
python3 manage.py migrate

# 5. Создать суперпользователя
python3 manage.py createsuperuser

# 6. Запустить сервер
python3 manage.py runserver
```

---

## 11. Проверка статуса

### 11.1 Проверить контейнеры
```bash
docker-compose ps
```

### 11.2 Проверить логи PostgreSQL
```bash
docker-compose logs db
```

### 11.3 Проверить логи Django
```bash
# Сервер выводит логи в консоль где запущен
```

### 11.4 Подключиться к БД напрямую (если нужно)
```bash
docker-compose exec db psql -U postgres -d healthy_world
```

Внутри psql:
```sql
\dt              -- список таблиц
\d games_product -- описание таблицы
SELECT * FROM games_product;  -- просмотр данных
\q              -- выход
```

---

## 12. Решение проблем

### Проблема: "could not translate host name db"
**Причина:** PostgreSQL контейнер не запущен
**Решение:**
```bash
docker-compose up -d
docker-compose logs db
```

### Проблема: "port already in use"
**Причина:** Порт 8000 занят другим процессом
**Решение:**
```bash
python3 manage.py runserver 8001
# или
lsof -i :8000  # найти процесс
kill -9 <PID>  # убить процесс
```

### Проблема: "ModuleNotFoundError: No module named 'django'"
**Причина:** Зависимости не установлены
**Решение:**
```bash
pip3 install --break-system-packages -r requirements.txt
```

### Проблема: "OperationalError: FATAL: role 'user' does not exist"
**Причина:** Неверные переменные окружения в docker-compose.yml
**Решение:** Проверьте значения POSTGRES_USER, POSTGRES_PASSWORD, POSTGRES_DB в docker-compose.yml

---

## Итоговая структура

После выполнения всех действий:

```
healthy_world/                    # Корневая папка проекта
├── games/                        # Новый модуль с играми
│   ├── migrations/              # Миграции БД
│   ├── templates/games/         # HTML шаблоны
│   ├── models.py                # Модели
│   ├── views.py                 # Представления
│   ├── urls.py                  # Маршруты
│   └── ...
├── fooddiary/                   # Модуль дневника питания
├── users/                       # Модуль пользователей
├── mainpage/                    # Главная страница
├── healthy_world/               # Основной конфиг
│   ├── settings.py              # Настройки (PostgreSQL)
│   ├── urls.py                  # Главные маршруты
│   └── ...
├── db.sqlite3                   # БД (для разработки без Docker)
├── docker-compose.yml           # Конфиг Docker
├── manage.py                    # Django управление
├── requirements.txt             # Зависимости Python
└── ...
```

---

## Готово! ✅

После выполнения всех шагов ваш проект с двумя мини-играми будет полностью готов к использованию с PostgreSQL в Docker.
