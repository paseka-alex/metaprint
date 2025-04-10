# 🧩 MetaAPI
**MetaAPI** — це бекенд-проєкт на базі Django, що забезпечує API та адмін-панель для роботи з продукцією, замовленнями, обліком матеріалів та друкарями.
На даній стадії його можна знайти за посиланням: https://metaapi.up.railway.app/
## ⚙️ Структура проєкту
```
metaapi/
    ├── metaapi/ # Головний додаток: налаштування, кореневі URL-и
    ├── catalog/ # Каталог продукції, матеріалів, технологій
    ├── orders/ # Управління замовленнями 
    ├── accounting/ # Інформація про друкарів, облік матеріалів (звітність)
    ├── api/ # API логіка, серіалізатори, DRF та документація
    ├── templates/ # Django-шаблони: welcome-сторінка, login, 404
```

## 📦 Опис додатків

- **metaapi**: Головний додаток проєкту. Містить загальні налаштування та маршрутизацію URL.
- **catalog**: Робота з продукцією, що відображається у магазині. Тут зберігаються дані про матеріали та технології, доступні для друкарів.
- **orders**: Управління усіма вхідними замовленнями — як стандартними, так і кастомними.
- **accounting**: Модуль для зберігання інформації про друкарів, а також облік вхідних матеріалів та звітність.
- **api**: Забезпечує API для взаємодії з усіма основними моделями проєкту. Включає серіалізатори та документацію API, згенеровану за допомогою **drf_yasg**.

## 📚 Документація API

Документація автоматично генерується за допомогою drf_yasg (Redoc). Знайти можна за посиланням /api/docs/ - https://metaapi.up.railway.app/api/docs/
Також є документ з поясненнями відносно використання деяких функцій - https://docs.google.com/document/d/1TCyrdLdK9e8EM2zY55ZGU_JzdRJIqwxyoX3QbgQ8Was/edit?tab=t.jf4d5zpz61ly.

## 🧰 Стек технологій

Нижче перечислено стак технологій для проекту. Повний список використовуємих пакетів знаходиться в requirements.txt.

### 🔧 Backend

- **Python 3.x**
- **Django 4.x**
- **Django REST Framework (DRF)** — створення RESTful API
- **drf_yasg** — автоматична генерація документації Swagger/Redoc
- **dj-database-url** — спрощене налаштування бази даних через URL
- **django-unfold** — сучасна тема для адміністративної панелі (з підтримкою історії, фільтрів, імпорту/експорту)
- **djmoney** — для зберігання грошових значень та підтримки валют

### 🗃 База даних

- **PostgreSQL** — основна СУБД (налаштування через `DATABASE_URL`)
- **Redus** - для зберігання кешу.

### 🌐 Frontend / UI (в межах Django)

- Django Templates:
  - Welcome page
  - Login page
  - 404 page
- Стилізована адмінка через **Unfold**

### 🌍 Інші налаштування

- Підтримка локалізації: `uk`, `en`
- Таймзона: `UTC`
- Автентифікація: `TokenAuthentication`, `SessionAuthentication`
- Логування у `secure_logs/` з використанням `RotatingFileHandler`
