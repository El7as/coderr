# Coderr Backend

Coderr is a Django REST Framework–based backend that enables structured collaboration between **business users** and **customers**.  
It provides endpoints for managing offers, orders, and reviews, including a permission system that enforces clear business rules.

---

## Features

- User system with two roles: **customer** and **business**
- Offer creation and listing
- Order management
- Review system with strict permission rules:
  - Only customers can create reviews
  - Only the review owner can update or delete their review
  - All authenticated users can read reviews
- Token‑based authentication
- Clean, modular API structure

---

## Tech Stack

- **Python 3.12+**
- **Django 5**
- **Django REST Framework**
- **Token Authentication**
- **SQLite / PostgreSQL** (depending on your setup)

---

## Installation

```bash
git clone <your-repository-url>
cd coderr-backend

python -m venv env
source env/bin/activate   # Windows: env\Scripts\activate

pip install -r requirements.txt
python manage.py makemigrations
python manage.py migrate
python manage.py runserver

