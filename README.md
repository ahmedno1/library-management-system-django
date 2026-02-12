# E-Library (Django)

E-Library is a Django 6 web application for browsing a book catalog, discovering authors, borrowing books, and leaving reviews after returning a book. It includes user authentication with a Profile model (full name, phone number, profile photo) and a Bootstrap-based UI.

## Table of Contents

- [Features](#features)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Setup (Local Development)](#setup-local-development)
- [Key URLs](#key-urls)
- [Borrowing Rules](#borrowing-rules)
- [Reviews Rule](#reviews-rule)
- [Profiles (Full name / Phone / Photo)](#profiles-full-name--phone--photo)
- [Notes on File Uploads](#notes-on-file-uploads)
- [Troubleshooting](#troubleshooting)
- [Contributing](#contributing)

## Features

- **Books catalog**
  - Browse with search / filters / sorting / pagination
  - Book detail view with availability (total/available copies) and ratings summary
- **Authors**
  - Authors list with photo, short bio snippet, book count, and "View Author" button
  - Author detail page with full bio and a list of the author's books
- **Categories**
  - Category list + category detail page showing books in the category
- **Borrowing**
  - Borrow a book (decrements available copies)
  - View active borrows ("My Books")
  - Return a book (increments available copies)
  - Limits: max 5 active borrows; can't borrow the same book twice at once
- **Reviews**
  - Users can only review a book after borrowing and returning it
  - Ratings support half-star steps (0.5 increments)
- **Accounts & Profiles**
  - Registration: full name, username, email, phone number, password + confirm, profile photo
  - Profile page and profile edit page
  - Enforces **unique email** and **unique username**

## Tech Stack

- **Backend:** Django 6.0.1 (function-based views)
- **Database:** SQLite (development)
- **Images:** Pillow
- **UI:** Bootstrap 5 (CDN) + Bootstrap Icons (CDN)

## Project Structure

- `config/` - project settings + root URL configuration
- `library/` - books, authors, categories, homepage, contact page, template tags, middleware
- `borrowing/` - borrow/return flows and "My Books"
- `reviews/` - add review form/logic
- `accounts/` - registration/login/logout + Profile model and signals
- `templates/` - base layout + app templates
- `static/` - CSS/JS assets
- `db.sqlite3` - SQLite database (local development only; typically not committed)

## Setup (Local Development)

### 1) Create and activate a virtual environment

Windows (PowerShell):

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

macOS / Linux:

```bash
python3 -m venv venv
source venv/bin/activate
```

### 2) Install dependencies

```bash
pip install -r requirements.txt
```

### 3) Apply migrations

```bash
python manage.py migrate
```

### 4) Create an admin user (optional, recommended)

```bash
python manage.py createsuperuser
```

### 5) Run the server

```bash
python manage.py runserver
```

Open the app at `http://127.0.0.1:8000/`.

## Key URLs

- Home: `/`
- Books: `/books/`
- Book detail: `/book/<pk>/` (alias also exists at `/books/<pk>/`)
- Authors: `/authors/`
- Author detail: `/authors/<pk>/`
- Categories: `/categories/`
- Borrow a book: `/borrow/<pk>/`
- My borrowed books: `/my-books/`
- Add review: `/book/<book_id>/review/` (alias also exists at `/books/<book_id>/review/`)
- Register: `/register/` (also `/accounts/register/`)
- Login: `/login/` (also `/accounts/login/`)
- Profile: `/profile/` (also `/accounts/profile/`)
- Django admin: `/admin/`

## Borrowing Rules

- A book can only be borrowed if `available_copies > 0`.
- A user may have at most **5 active borrows**.
- A user can't have two active borrows for the same book.
- Due dates are computed using `BORROW_DURATION_DAYS` in `config/settings.py`.

## Reviews Rule

Users can only review a book after they have **borrowed and returned** it.

## Profiles (Full name / Phone / Photo)

Registration stores:
- Django `User`: `username`, `email`, `password`
- `accounts.Profile`: `full_name`, `phone_number`, `photo`

Profiles are auto-created via signals (`accounts/signals.py`).

## Notes on File Uploads

This project uses Django `ImageField` for:
- Author photos
- Book covers
- Profile photos

For production, configure `MEDIA_ROOT`/`MEDIA_URL` and serve media files via your web server (or cloud storage). For local development you can also add Django's static media serving in `config/urls.py` if needed.

## Troubleshooting

### `IntegrityError: UNIQUE constraint failed: auth_user.username`

This means the username you tried to register already exists.

- Pick a different username, or
- Delete the existing user (Django admin) and register again.

### Images upload but don't show in the browser

For local development, add media settings and routes:

- `MEDIA_URL` and `MEDIA_ROOT` in `config/settings.py`
- `urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)` in `config/urls.py` (development only)

## Contributing

This is a small learning/assignment project. If you extend it:
- keep views function-based for consistency,
- add tests where possible,
- run `python manage.py check` after changes.

