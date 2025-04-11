# 🧩 MetaAPI
[![uk](https://img.shields.io/badge/lang-uk-yellow.svg)](https://github.com/paseka-alex/metaprint/blob/api/README.uk.md)
**MetaAPI** is a Django-based backend project that provides an API and admin panel for managing products, orders, material accounting, and printers.
You can currently find it deployed at: https://metaapi.up.railway.app/

## ⚙️ Project App Structure

```
metaapi/
    ├── metaapi/ # Main app: env settings, root URLs
    ├── catalog/ # Product catalog, materials, technologies
    ├── orders/ # Order management
    ├── accounting/ # Printer info, material accounting, reporting
    ├── api/ # API logic, serializers, DRF, and documentation
    ├── templates/ # Django templates: welcome page, login, 404
```

## 📦 App Descriptions

- **metaapi**: Main app of the project. Contains general settings and URL routing.
- **catalog**: Manages the products shown in the store. Stores data about materials and technologies available for printing.
- **orders**: Handles all incoming orders — both standard and custom.
- **accounting**: Module for storing staff information about order complition as well as tracking incoming materials and generating reports.
- **api**: Provides API interaction with all main project models. Includes serializers and API docs generated using **drf_yasg**.


## 📚 API Documentation

API documentation is automatically generated with drf_yasg (Redoc) and is available at `/api/docs/` — https://metaapi.up.railway.app/api/docs/. Req. login to access.

There is also a document explaining the usage of certain features (db structure, api examples):  
https://docs.google.com/document/d/1TCyrdLdK9e8EM2zY55ZGU_JzdRJIqwxyoX3QbgQ8Was/edit?tab=t.jf4d5zpz61ly

## 🧰 Tech Stack

Below is the tech stack used in the project. Full list of dependencies can be found in `requirements.txt`.

### 🔧 Backend

- **Python 3.x**
- **Django 4.x**
- **Django REST Framework (DRF)** — for creating RESTful APIs
- **drf_yasg** — auto-generates Swagger/Redoc documentation
- **dj-database-url** — simplified database configuration via URL
- **django-unfold** — modern admin theme (with history, filters, import/export support)
- **djmoney** — for storing monetary values with currency support

### 🗃 Database

- **PostgreSQL** — primary database (configured via `DATABASE_URL`)
- **Redis** — used for caching.

### 🌐 Frontend / UI (within Django)
For better experience, was added a few pages, styled with tailwind CSS v4
- Django Templates:
  - Welcome page  
  - Login page  
  - 404 page  
- Admin styled with **Unfold**
