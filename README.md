# AI-Powered Social Media Manager

An intelligent, self-hosted platform that researches trending content (news, tech, business, humor), generates social media posts using Claude AI, and publishes to LinkedIn and Twitter/X.

## Features

- **Content Research** - Automated trending content aggregation from Hacker News, Reddit, Dev.to, GitHub Trending, JokeAPI
- **AI Content Generation** - Claude AI generates platform-optimized posts with tone selection
- **Post Management** - Draft > Review > Approve > Publish workflow
- **Publishing** - Direct publishing to LinkedIn and Twitter/X
- **Scheduling** - Recurring schedules with cron expressions and automated content pipeline
- **Analytics** - Engagement metrics tracking and performance insights
- **Comment Management** - AI-powered comment reply suggestions with auto-reply mode (LinkedIn)
- **LinkedIn Profile Intelligence** - Lead generation from post engagers with AI status classification
- **CSV Export** - Export leads data for use in external CRM tools

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | Python 3.11, FastAPI, SQLAlchemy 2.0 (async), Alembic |
| Frontend | React 19, Vite, TypeScript, Tailwind CSS v4, shadcn/ui |
| Database | PostgreSQL 17, Redis 7 |
| Task Queue | Celery 5 with Redis broker |
| AI | Anthropic Claude API (Haiku 4.5 default) |
| Deployment | Docker Compose (7 services) |
| CI/CD | GitHub Actions |

## Quick Start (Docker)

```bash
# 1. Clone the repository
git clone <repo-url>
cd SocialMediaManager

# 2. Copy and configure environment variables
cp .env.example .env
# Edit .env with your API keys (at minimum: ANTHROPIC_API_KEY, SECRET_KEY, ENCRYPTION_KEY)

# 3. Start all services
docker compose up -d

# 4. Run database migrations
docker compose exec backend alembic upgrade head

# 5. Access the app
# Frontend:    http://localhost:3000
# Backend API: http://localhost:8000
# Swagger docs: http://localhost:8000/docs
# Health check: http://localhost:8000/health
```

## Local Development Setup

### Prerequisites

- Python 3.11+
- Node.js 20+
- PostgreSQL 17
- Redis 7

### Backend

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Set environment variables
cp ../.env.example ../.env
# Edit ../.env

# Run database migrations
alembic upgrade head

# Start the backend
uvicorn app.main:app --reload --port 8000
```

### Frontend

```bash
cd frontend

# Install dependencies
npm install

# Start dev server (proxies API to localhost:8000)
npm run dev
```

### Celery Workers

```bash
cd backend

# General worker (research, generation, publishing, analytics, profile)
celery -A app.tasks.celery_app worker -l info -Q research,generation,publishing,analytics,profile

# Comments worker (separate for isolation)
celery -A app.tasks.celery_app worker -l info -Q comments

# Beat scheduler (periodic tasks)
celery -A app.tasks.celery_app beat -l info
```

## Docker Services

| Service | Description | Port |
|---------|-------------|------|
| `postgres` | PostgreSQL database | 5432 |
| `redis` | Redis cache and Celery broker | 6379 |
| `backend` | FastAPI application | 8000 |
| `celery-worker` | General Celery worker | - |
| `celery-worker-comments` | Comments/profile Celery worker | - |
| `celery-beat` | Celery Beat scheduler | - |
| `frontend` | React app served via nginx | 3000 |

## API Endpoints

| Route | Description |
|-------|-------------|
| `GET /health` | Health check |
| `POST /api/v1/auth/register` | User registration |
| `POST /api/v1/auth/login` | User login (returns JWT cookie) |
| `GET /api/v1/content/trending` | Fetch trending content |
| `GET /api/v1/posts` | List generated posts |
| `POST /api/v1/posts/generate` | Generate a post with AI |
| `POST /api/v1/posts/{id}/publish` | Publish a post |
| `GET /api/v1/comments` | List comments |
| `GET /api/v1/leads` | List leads |
| `GET /api/v1/leads/export` | Export leads as CSV |
| `GET /api/v1/analytics` | Analytics summary |
| `GET /api/v1/dashboard` | Dashboard stats |
| `GET /api/v1/schedules` | List schedules |
| `GET /api/v1/platforms` | List connected platforms |

Full API documentation available at `/docs` (Swagger) or `/redoc`.

## Environment Variables

See [.env.example](.env.example) for all configuration options. Key variables:

| Variable | Required | Description |
|----------|----------|-------------|
| `ANTHROPIC_API_KEY` | Yes | Claude AI API key |
| `SECRET_KEY` | Yes | JWT signing key (generate random 256-bit) |
| `ENCRYPTION_KEY` | Yes | Fernet key for token encryption |
| `DATABASE_URL` | Yes | PostgreSQL async connection string |
| `REDIS_URL` | Yes | Redis connection string |
| `TWITTER_CLIENT_ID` | No | Twitter OAuth app client ID |
| `LINKEDIN_CLIENT_ID` | No | LinkedIn OAuth app client ID |

## Testing

```bash
# Backend unit & integration tests
cd backend
pytest --cov=app -v

# Frontend type check
cd frontend
npx tsc --noEmit

# E2E tests (requires running services)
cd frontend
npx playwright install chromium
npx playwright test
```

## Project Structure

```
SocialMediaManager/
├── backend/                 # FastAPI backend
│   ├── app/
│   │   ├── api/v1/         # API route handlers
│   │   ├── models/         # SQLAlchemy ORM models
│   │   ├── schemas/        # Pydantic validation schemas
│   │   ├── services/       # Business logic
│   │   │   ├── ai_generator/      # Claude AI integration
│   │   │   ├── comments/          # Comment management
│   │   │   ├── content_research/  # Content source fetchers
│   │   │   ├── profile_intelligence/  # Lead management
│   │   │   └── publishers/        # Platform publishers
│   │   ├── tasks/          # Celery async tasks
│   │   └── utils/          # Shared utilities
│   ├── alembic/            # Database migrations
│   ├── tests/              # Backend tests
│   └── Dockerfile
├── frontend/               # React frontend
│   ├── src/
│   │   ├── api/            # API client functions
│   │   ├── components/     # React components
│   │   ├── pages/          # Page components
│   │   └── store/          # Zustand state stores
│   ├── e2e/                # Playwright E2E tests
│   ├── nginx.conf          # Production nginx config
│   └── Dockerfile
├── docs/                   # Project documentation
├── docker-compose.yml
├── .env.example
└── .github/workflows/ci.yml
```

## Documentation

- [Market Research](docs/01-market-research.md)
- [Feature Specification](docs/02-feature-specification.md)
- [Product Requirements (PRD)](docs/03-prd.md)
- [High-Level Design (HLD)](docs/04-hld.md)
- [Low-Level Design (LLD)](docs/05-lld.md)
- [Development Plan](docs/06-development-plan.md)

## License

MIT
