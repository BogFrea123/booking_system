# Система бронювання кімнат

Django-проект для бронювання кімнат та місць для заходів.

---

## Структура проекту

```
booking_system/
├── manage.py
├── requirements.txt
├── booking_project/
│   ├── __init__.py
│   ├── settings.py
│   └── urls.py
└── bookings/
    ├── __init__.py
    ├── models.py       ← Моделі: Room, Booking
    ├── views.py        ← Всі views (список, деталі, бронювання, адмін)
    ├── forms.py        ← BookingForm, RoomForm
    ├── urls.py         ← URL-маршрути
    ├── admin.py        ← Налаштування Django admin
    ├── fixtures/
    │   └── initial_rooms.json   ← Тестові дані
    └── templates/
        └── bookings/
            ├── base.html
            ├── room_list.html
            ├── room_detail.html
            ├── booking_form.html
            ├── booking_detail.html
            ├── my_bookings.html
            ├── admin_bookings.html
            ├── room_form.html
            └── login.html
```

---

## Встановлення та запуск

### 1. Клонуй або розпакуй проект

```bash
cd booking_system
```

### 2. Створи та активуй віртуальне середовище

```bash
python -m venv venv

# Windows:
venv\Scripts\activate

# macOS / Linux:
source venv/bin/activate
```

### 3. Встанови залежності

```bash
pip install -r requirements.txt
```

### 4. Застосуй міграції

```bash
python manage.py makemigrations
python manage.py migrate
```

### 5. Завантаж тестові дані (кімнати)

```bash
python manage.py loaddata bookings/fixtures/initial_rooms.json
```

### 6. Створи суперкористувача (адміністратора)

```bash
python manage.py createsuperuser
```

### 7. Запусти сервер

```bash
python manage.py runserver
```

Відкрий браузер: **http://127.0.0.1:8000**

---

## Функціональність

| URL | Опис |
|-----|------|
| `/` | Список кімнат з фільтрами |
| `/rooms/<id>/` | Деталі кімнати + календар доступності |
| `/rooms/<id>/book/` | Форма бронювання |
| `/my-bookings/` | Мої бронювання |
| `/bookings/<id>/` | Деталі бронювання |
| `/bookings/<id>/cancel/` | Скасування бронювання |
| `/admin-panel/bookings/` | Адмін: список бронювань |
| `/admin-panel/rooms/add/` | Адмін: додати кімнату |
| `/admin-panel/rooms/<id>/edit/` | Адмін: редагувати кімнату |
| `/django-admin/` | Стандартна панель Django Admin |
| `/login/` | Вхід |
| `/logout/` | Вихід |
| `/api/rooms/<id>/availability/` | JSON API: зайняті дати |

---

## Моделі

### Room (Кімната)
- `name` — назва
- `room_type` — тип (conference / office / event / coworking)
- `capacity` — вмістимість (осіб)
- `price_per_day` — ціна за день (грн)
- `description` — опис
- `is_active` — чи активна

### Booking (Бронювання)
- `user` → FK до User
- `room` → FK до Room
- `start_date` / `end_date` — дати бронювання
- `status` — pending / confirmed / cancelled
- `notes` — примітки
- `created_at`, `updated_at` — часові мітки

### User
Стандартна модель `django.contrib.auth.models.User`.

---

## База даних

За замовчуванням використовується **SQLite** (`db.sqlite3`).

Для **PostgreSQL** — відредагуй `DATABASES` у `settings.py`:

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'booking_db',
        'USER': 'postgres',
        'PASSWORD': 'your_password',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```

---

## Ролі користувачів

- **Звичайний користувач** — переглядає кімнати, бронює, скасовує свої бронювання.
- **Адміністратор** (`is_staff=True`) — додатково керує кімнатами та змінює статуси бронювань.
