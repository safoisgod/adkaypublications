# Publishing House — Django Backend

A production-grade REST API for the Publishing House platform.
Built with Django 4.2, Django REST Framework, PostgreSQL, Redis, and Celery.

---

## Quick Start

```bash
# 1. Clone and enter the backend directory
cd publishing_platform/backend

# 2. Run the automated setup script
bash setup.sh

# 3. Start the development server
source venv/bin/activate
python manage.py runserver
```

**API Base URL:** `http://localhost:8000/api/v1/`  
**Admin Panel:** `http://localhost:8000/admin/`  
**API Docs (Swagger):** `http://localhost:8000/api/docs/`

---

## Manual Setup

```bash
# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate          # Linux/Mac
venv\Scripts\activate             # Windows

# Install dependencies
pip install -r requirements/development.txt

# Configure environment
cp .env.example .env
# Edit .env with your settings

# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Load sample data
python manage.py seed_data

# Start server
python manage.py runserver
```

---

## Tech Stack

| Layer       | Technology                        |
|-------------|-----------------------------------|
| Framework   | Django 4.2 + Django REST Framework|
| Auth        | JWT via djangorestframework-simplejwt |
| Database    | PostgreSQL 15                     |
| Cache       | Redis 7 (django-redis)            |
| Task Queue  | Celery 5 + Redis broker           |
| Filtering   | django-filter                     |
| API Docs    | drf-spectacular (Swagger/ReDoc)   |
| Images      | Pillow                            |
| Security    | bleach, CORS headers              |

---

## Project Structure

```
backend/
├── config/                   # Project settings & routing
│   ├── settings/
│   │   ├── base.py           # Shared settings
│   │   ├── development.py    # Dev overrides
│   │   └── production.py     # Production overrides
│   ├── urls.py               # Root URL config
│   └── celery.py             # Celery config
│
├── apps/
│   ├── core/                 # Shared models, utils, pagination
│   ├── accounts/             # CustomUser + JWT auth
│   ├── books/                # Books + Genres
│   ├── blog/                 # Posts + Categories + Tags
│   ├── authors/              # Author profiles
│   ├── services/             # Publishing services
│   ├── contact/              # Contact form submissions
│   ├── newsletter/           # Email subscriptions
│   └── search/               # Cross-model search
│
├── fixtures/                 # Sample data JSON
├── requirements/             # Pip requirements split by env
├── media/                    # Uploaded files (dev)
├── staticfiles/              # Collected static (prod)
├── nginx.conf                # Production Nginx config
├── gunicorn.conf.py          # Production Gunicorn config
├── Dockerfile                # Container image
├── docker-compose.yml        # Local dev orchestration
└── setup.sh                  # First-time setup script
```

---

## API Reference

### Authentication

| Method | Endpoint                          | Description                  | Auth Required |
|--------|-----------------------------------|------------------------------|---------------|
| POST   | `/api/v1/auth/register/`          | Register new user            | No            |
| POST   | `/api/v1/auth/login/`             | Login, returns JWT tokens    | No            |
| POST   | `/api/v1/auth/logout/`            | Blacklist refresh token      | Yes           |
| POST   | `/api/v1/auth/token/refresh/`     | Refresh access token         | No            |
| GET    | `/api/v1/auth/me/`                | Get own profile              | Yes           |
| PATCH  | `/api/v1/auth/me/`                | Update own profile           | Yes           |
| POST   | `/api/v1/auth/change-password/`   | Change password              | Yes           |

### Books

| Method | Endpoint                          | Description                  |
|--------|-----------------------------------|------------------------------|
| GET    | `/api/v1/books/`                  | Paginated book catalogue     |
| GET    | `/api/v1/books/featured/`         | Featured books               |
| GET    | `/api/v1/books/bestsellers/`      | Bestselling books            |
| GET    | `/api/v1/books/new-releases/`     | New releases                 |
| GET    | `/api/v1/books/genres/`           | All genres + book counts     |
| GET    | `/api/v1/books/<slug>/`           | Book detail + related books  |

**Book Filters:** `?genre=`, `?author=`, `?is_featured=`, `?is_bestseller=`, `?min_price=`, `?max_price=`, `?year=`, `?search=`, `?ordering=`

### Blog

| Method | Endpoint                              | Description               |
|--------|---------------------------------------|---------------------------|
| GET    | `/api/v1/blog/posts/`                 | Paginated post list       |
| GET    | `/api/v1/blog/posts/featured/`        | Featured posts            |
| GET    | `/api/v1/blog/posts/<slug>/`          | Post detail + related     |
| POST   | `/api/v1/blog/posts/<slug>/view/`     | Increment view counter    |
| GET    | `/api/v1/blog/categories/`            | Categories + post counts  |
| GET    | `/api/v1/blog/tags/`                  | Tags + post counts        |

**Post Filters:** `?category=`, `?tag=`, `?author=`, `?is_featured=`, `?year=`, `?month=`, `?search=`

### Authors

| Method | Endpoint                          | Description                  |
|--------|-----------------------------------|------------------------------|
| GET    | `/api/v1/authors/`                | Paginated author list        |
| GET    | `/api/v1/authors/featured/`       | Featured authors             |
| GET    | `/api/v1/authors/<slug>/`         | Author detail + their books  |

### Services

| Method | Endpoint                          | Description                  |
|--------|-----------------------------------|------------------------------|
| GET    | `/api/v1/services/`               | All active services          |
| GET    | `/api/v1/services/<slug>/`        | Service detail               |

### Contact & Newsletter

| Method | Endpoint                              | Description               |
|--------|---------------------------------------|---------------------------|
| POST   | `/api/v1/contact/`                    | Submit contact form       |
| POST   | `/api/v1/newsletter/subscribe/`       | Subscribe to newsletter   |
| POST   | `/api/v1/newsletter/unsubscribe/`     | Unsubscribe               |

### Search

| Method | Endpoint                          | Description                         |
|--------|-----------------------------------|-------------------------------------|
| GET    | `/api/v1/search/?q=<query>`       | Search books, posts, authors        |

**Search Params:** `?q=` (required), `?type=all|books|posts|authors`, `?limit=1-12`

### Homepage

| Method | Endpoint                          | Description                        |
|--------|-----------------------------------|------------------------------------|
| GET    | `/api/v1/homepage/`               | Aggregated homepage data (cached)  |

---

## API Response Format

All responses follow this envelope structure:

```json
// Success
{
  "status": "success",
  "data": { ... }
}

// Success (paginated)
{
  "status": "success",
  "data": [ ... ],
  "meta": {
    "count": 48,
    "total_pages": 4,
    "current_page": 1,
    "next": "http://...",
    "previous": null
  }
}

// Error
{
  "status": "error",
  "message": "Human-readable summary",
  "errors": { "field": ["error detail"] }
}
```

---

## Authentication Flow

```
1. POST /api/v1/auth/login/
   → Returns: { access: "...", refresh: "...", user: {...} }

2. Include access token in subsequent requests:
   Authorization: Bearer <access_token>

3. Access token expires after 15 minutes.
   POST /api/v1/auth/token/refresh/  { refresh: "..." }
   → Returns: { access: "new_access_token" }

4. POST /api/v1/auth/logout/  { refresh: "..." }
   → Blacklists the refresh token
```

---

## Running with Docker

```bash
# Start all services (Postgres, Redis, Django, Celery)
docker-compose up -d

# Run migrations
docker-compose exec api python manage.py migrate

# Seed data
docker-compose exec api python manage.py seed_data

# View logs
docker-compose logs -f api

# Stop everything
docker-compose down
```

---

## Running Celery (without Docker)

```bash
# Start worker
celery -A config worker -l info

# Start beat (scheduled tasks)
celery -A config beat -l info

# Monitor tasks (optional)
celery -A config flower
```

---

## Admin Panel

Access at `/admin/` with your superuser credentials.

**Key Admin Features:**
- Custom branded dashboard with platform statistics
- Image previews for books, authors, and blog posts
- Publish/unpublish bulk actions
- Contact message read/unread tracking
- Subscriber CSV export
- Rich list filters on all models
- Inline author editing on books

---

## Environment Variables

| Variable                              | Required | Default            | Description                     |
|---------------------------------------|----------|--------------------|---------------------------------|
| `SECRET_KEY`                          | ✓        | —                  | Django secret key               |
| `DEBUG`                               |          | `True`             | Debug mode                      |
| `ALLOWED_HOSTS`                       | ✓ (prod) | `localhost`        | Comma-separated hostnames       |
| `DB_NAME`                             | ✓        | `publishing_db`    | PostgreSQL database name        |
| `DB_USER`                             | ✓        | `postgres`         | PostgreSQL user                 |
| `DB_PASSWORD`                         | ✓        | —                  | PostgreSQL password             |
| `DB_HOST`                             |          | `localhost`        | PostgreSQL host                 |
| `DB_PORT`                             |          | `5432`             | PostgreSQL port                 |
| `REDIS_URL`                           |          | `redis://...6379/0`| Redis connection URL            |
| `JWT_ACCESS_TOKEN_LIFETIME_MINUTES`   |          | `15`               | JWT access token lifespan       |
| `JWT_REFRESH_TOKEN_LIFETIME_DAYS`     |          | `7`                | JWT refresh token lifespan      |
| `CORS_ALLOWED_ORIGINS`                | ✓        | —                  | Comma-separated frontend URLs   |
| `EMAIL_HOST_USER`                     |          | —                  | SMTP email address              |
| `EMAIL_HOST_PASSWORD`                 |          | —                  | SMTP password                   |
| `ADMIN_EMAIL`                         |          | —                  | Admin notification recipient    |
| `USE_S3`                              |          | `False`            | Enable S3 media storage         |
| `AWS_ACCESS_KEY_ID`                   | If S3    | —                  | AWS credentials                 |
| `AWS_SECRET_ACCESS_KEY`               | If S3    | —                  | AWS credentials                 |
| `AWS_STORAGE_BUCKET_NAME`             | If S3    | —                  | S3 bucket name                  |

---

## Security Checklist (Production)

- [ ] `DEBUG=False`
- [ ] Strong `SECRET_KEY` (50+ random chars)
- [ ] `ALLOWED_HOSTS` set to actual domain
- [ ] PostgreSQL with strong password
- [ ] HTTPS enforced via Nginx
- [ ] `CORS_ALLOWED_ORIGINS` set to frontend domain only
- [ ] Media files served by Nginx (not Django)
- [ ] Superuser uses strong password + 2FA (if configured)
- [ ] Sentry DSN configured for error tracking
- [ ] Regular DB backups scheduled

---

## Management Commands

```bash
# Seed database with sample data
python manage.py seed_data

# Flush and re-seed
python manage.py seed_data --flush

# Load fixture files
python manage.py loaddata fixtures/genres.json
python manage.py loaddata fixtures/blog_categories.json
python manage.py loaddata fixtures/services.json

# Collect static files
python manage.py collectstatic

# Check for common issues
python manage.py check --deploy
```
