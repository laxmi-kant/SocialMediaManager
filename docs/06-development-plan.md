# Development Plan
## AI-Powered Social Media Manager Platform

**Document Version:** 1.0
**Date:** March 20, 2026
**Author:** Engineering Team

---

## Table of Contents
1. [Sprint Overview](#1-sprint-overview)
2. [Sprint 1: Foundation](#2-sprint-1-foundation)
3. [Sprint 2: Content Research Pipeline](#3-sprint-2-content-research-pipeline)
4. [Sprint 3: AI Content Generation](#4-sprint-3-ai-content-generation)
5. [Sprint 4: Social Media Publishing](#5-sprint-4-social-media-publishing)
6. [Sprint 5: Scheduling & Analytics](#6-sprint-5-scheduling--analytics)
7. [Sprint 6: Comment Management](#7-sprint-6-comment-management)
8. [Sprint 7: LinkedIn Profile Intelligence](#7b-sprint-7-linkedin-profile-intelligence)
9. [Sprint 8: Production Hardening](#8-sprint-8-production-hardening)
10. [Task Dependency Graph](#8-task-dependency-graph)
11. [Testing Strategy](#9-testing-strategy)
12. [Definition of Done](#10-definition-of-done)

---

## 1. Sprint Overview

| Sprint | Focus | Key Deliverable |
|--------|-------|----------------|
| Sprint 1 | Foundation | Running app with auth, empty dashboard |
| Sprint 2 | Content Research | Trending content from 6 sources, browsable in UI |
| Sprint 3 | AI Generation | Generate and review posts from content |
| Sprint 4 | Publishing | Connect & publish to Twitter/LinkedIn |
| Sprint 5 | Scheduling & Analytics | Automated pipeline, engagement tracking |
| Sprint 6 | Comment Management | AI-powered comment replies, mention detection |
| Sprint 7 | LinkedIn Profile Intelligence | Lead generation from post engagers |
| Sprint 8 | Production Hardening | Docker deployment, testing, polish |

---

## 2. Sprint 1: Foundation

**Goal:** Project scaffolding, database, authentication, basic UI shell.

### Tasks

| ID | Task | Files | Dependencies |
|----|------|-------|-------------|
| S1.1 | Initialize git repo, .gitignore, README | `.gitignore`, `README.md` | None |
| S1.2 | Create docker-compose.yml (PostgreSQL + Redis) | `docker-compose.yml` | None |
| S1.3 | Create .env.example with all variables | `.env.example` | None |
| S1.4 | Set up backend Python project (pyproject.toml, requirements.txt) | `backend/requirements.txt`, `backend/pyproject.toml` | S1.1 |
| S1.5 | Create FastAPI app entry point with config | `backend/app/main.py`, `backend/app/config.py` | S1.4 |
| S1.6 | Set up SQLAlchemy database connection | `backend/app/database.py` | S1.5, S1.2 |
| S1.7 | Create ORM models for core + comment tables (9 tables: users, platform_accounts, content_sources, schedules, generated_posts, published_posts, analytics_snapshots, comments, comment_replies) | `backend/app/models/*.py` | S1.6 |
| S1.8 | Set up Alembic and create initial migration (9 core + comment tables) | `backend/alembic.ini`, `backend/alembic/` | S1.7 |
| S1.9 | Implement security utils (JWT, bcrypt, Fernet) | `backend/app/utils/security.py` | S1.5 |
| S1.10 | Create Pydantic schemas for auth | `backend/app/schemas/user.py` | S1.7 |
| S1.11 | Implement auth API routes (register, login, refresh, me) | `backend/app/api/v1/auth.py` | S1.9, S1.10 |
| S1.12 | Create API dependencies (get_db, get_current_user) | `backend/app/api/deps.py` | S1.11 |
| S1.13 | Set up React frontend with Vite + TypeScript | `frontend/package.json`, `frontend/vite.config.ts` | S1.1 |
| S1.14 | Install and configure Tailwind CSS + shadcn/ui | `frontend/tailwind.config.ts`, `frontend/src/styles/` | S1.13 |
| S1.15 | Create MainLayout with Sidebar and Header | `frontend/src/components/layout/*.tsx` | S1.14 |
| S1.16 | Set up React Router with page routes | `frontend/src/App.tsx` | S1.15 |
| S1.17 | Create auth store (Zustand) and API client (Axios) | `frontend/src/store/authStore.ts`, `frontend/src/api/client.ts` | S1.13 |
| S1.18 | Create Login and Register pages | `frontend/src/pages/Login.tsx`, `frontend/src/pages/Register.tsx` | S1.17 |
| S1.19 | Create empty Dashboard page with placeholder cards | `frontend/src/pages/Dashboard.tsx` | S1.15 |
| S1.20 | Set up GitHub Actions CI (ruff lint for Python, ESLint for TypeScript) | `.github/workflows/ci.yml` | S1.4, S1.13 |
| S1.21 | Set up pytest configuration and test fixtures (conftest.py) | `backend/tests/conftest.py`, `backend/pytest.ini` | S1.5 |
| S1.22 | Write unit tests for security utils (JWT, bcrypt, Fernet) | `backend/tests/test_utils/test_security.py` | S1.9, S1.21 |
| S1.23 | Write API integration tests for auth endpoints | `backend/tests/test_api/test_auth.py` | S1.11, S1.21 |
| S1.24 | Verify end-to-end: docker-compose up → register → login → dashboard | - | All S1.* |

### Sprint 1 Deliverable
- `docker-compose up` starts PostgreSQL and Redis
- Backend runs on port 8000 with `/docs` showing Swagger UI
- User can register, login, and see an empty dashboard
- JWT authentication working with httponly cookies
- GitHub Actions CI runs linting on push/PR
- Auth unit tests and API integration tests passing

---

## 3. Sprint 2: Content Research Pipeline

**Goal:** Fetch trending content from all sources, display in UI with filters.

### Tasks

| ID | Task | Files | Dependencies |
|----|------|-------|-------------|
| S2.1 | Create ResilientHTTPClient with retry/backoff | `backend/app/utils/http_client.py` | S1.5 |
| S2.2 | Create RedisCache helper | `backend/app/utils/cache.py` | S1.5 |
| S2.3 | Create RedisRateLimiter | `backend/app/utils/rate_limiter.py` | S1.5 |
| S2.4 | Define ContentSourceBase abstract class | `backend/app/services/content_research/base.py` | S2.1 |
| S2.5 | Implement HackerNewsClient | `backend/app/services/content_research/hackernews.py` | S2.4 |
| S2.6 | Implement DevToClient | `backend/app/services/content_research/devto.py` | S2.4 |
| S2.7 | Implement JokeClient (JokeAPI + icanhazdadjoke) | `backend/app/services/content_research/jokes.py` | S2.4 |
| S2.8 | Implement GitHubTrendingClient | `backend/app/services/content_research/github_trending.py` | S2.4 |
| S2.9 | Implement RedditClient (with OAuth) | `backend/app/services/content_research/reddit.py` | S2.4 |
| S2.10 | Implement ContentAggregator | `backend/app/services/content_research/aggregator.py` | S2.5-S2.9 |
| S2.11 | Set up Celery app and configuration | `backend/app/tasks/celery_app.py` | S1.5 |
| S2.12 | Create research Celery task (fetch_trending_content) | `backend/app/tasks/research_tasks.py` | S2.10, S2.11 |
| S2.13 | Create content Pydantic schemas | `backend/app/schemas/content.py` | S1.7 |
| S2.14 | Create content API routes (list, get, refresh) | `backend/app/api/v1/content.py` | S2.13 |
| S2.15 | Add Celery worker and beat to docker-compose | `docker-compose.yml` | S2.11 |
| S2.16 | Create frontend API client for content | `frontend/src/api/content.ts` | S1.17 |
| S2.17 | Create ContentCard component | `frontend/src/components/content/ContentCard.tsx` | S1.14 |
| S2.18 | Create TrendingFeed component | `frontend/src/components/content/TrendingFeed.tsx` | S2.17 |
| S2.19 | Create ContentFilter component (source tabs, sort) | `frontend/src/components/content/ContentFilter.tsx` | S1.14 |
| S2.20 | Create ContentResearch page | `frontend/src/pages/ContentResearch.tsx` | S2.16-S2.19 |
| S2.21 | Write unit tests for each content source client (mock HTTP) | `backend/tests/test_services/test_content_research/*.py` | S2.5-S2.10, S1.21 |
| S2.22 | Write unit tests for cache and rate limiter utils | `backend/tests/test_utils/test_cache.py`, `test_rate_limiter.py` | S2.2, S2.3, S1.21 |
| S2.23 | Write API integration tests for content endpoints | `backend/tests/test_api/test_content.py` | S2.14, S1.21 |
| S2.24 | Verify: content auto-fetches and appears in feed | - | All S2.* |

### Sprint 2 Deliverable
- Celery Beat triggers content fetch every 2 hours
- Content from 6 sources stored in database
- Frontend shows trending content with source filtering and sort
- Manual refresh button works
- Redis caching prevents excessive API calls

---

## 4. Sprint 3: AI Content Generation

**Goal:** Generate platform-specific social media posts from trending content.

### Tasks

| ID | Task | Files | Dependencies |
|----|------|-------|-------------|
| S3.1 | Create Anthropic SDK client wrapper | `backend/app/services/ai_generator/client.py` | S1.5 |
| S3.2 | Create prompt templates for all platform/type combos | `backend/app/services/ai_generator/prompts.py` | S3.1 |
| S3.3 | Implement PostGenerator service | `backend/app/services/ai_generator/generator.py` | S3.1, S3.2 |
| S3.4 | Create generation Celery tasks | `backend/app/tasks/generation_tasks.py` | S3.3, S2.11 |
| S3.5 | Create post Pydantic schemas | `backend/app/schemas/post.py` | S1.7 |
| S3.6 | Create posts API routes (CRUD, approve, reject, generate) | `backend/app/api/v1/posts.py` | S3.5 |
| S3.7 | Add generate endpoint to content API | `backend/app/api/v1/content.py` (update) | S3.3, S2.14 |
| S3.8 | Create frontend API client for posts | `frontend/src/api/posts.ts` | S1.17 |
| S3.9 | Create PostCard component | `frontend/src/components/posts/PostCard.tsx` | S1.14 |
| S3.10 | Create PostQueue component (with status tabs) | `frontend/src/components/posts/PostQueue.tsx` | S3.9 |
| S3.11 | Create PostEditor component (text area, char counter, hashtags) | `frontend/src/components/posts/PostEditor.tsx` | S1.14 |
| S3.12 | Create PostPreview component (Twitter/LinkedIn mock) | `frontend/src/components/posts/PostPreview.tsx` | S1.14 |
| S3.13 | Create PostManager page | `frontend/src/pages/PostManager.tsx` | S3.8-S3.12 |
| S3.14 | Add "Generate Post" button to ContentCard | `frontend/src/components/content/ContentCard.tsx` (update) | S3.7 |
| S3.15 | Create common Modal, Toast, ConfirmDialog components | `frontend/src/components/common/*.tsx` | S1.14 |
| S3.16 | Write unit tests for AI generator (prompts, generator, client) | `backend/tests/test_services/test_ai_generator/*.py` | S3.1-S3.3, S1.21 |
| S3.17 | Write API integration tests for posts endpoints | `backend/tests/test_api/test_posts.py` | S3.6, S1.21 |
| S3.18 | Verify: generate → edit → approve workflow end-to-end | - | All S3.* |

### Sprint 3 Deliverable
- User can click "Generate Post" on any content item
- Choose platform (Twitter/LinkedIn) and tone
- AI generates post in < 10 seconds
- Post appears in review queue as "draft"
- User can edit text, change hashtags, approve or reject
- Character counter enforces platform limits

---

## 5. Sprint 4: Social Media Publishing

**Goal:** Connect Twitter/LinkedIn accounts and publish posts.

### Tasks

| ID | Task | Files | Dependencies |
|----|------|-------|-------------|
| S4.1 | Create PublisherBase abstract class | `backend/app/services/publishers/base.py` | S1.5 |
| S4.2 | Implement TwitterPublisher | `backend/app/services/publishers/twitter.py` | S4.1, S2.1 |
| S4.3 | Implement LinkedInPublisher | `backend/app/services/publishers/linkedin.py` | S4.1, S2.1 |
| S4.4 | Create PublisherRegistry | `backend/app/services/publishers/registry.py` | S4.2, S4.3 |
| S4.5 | Create platform Pydantic schemas | `backend/app/schemas/platform.py` | S1.7 |
| S4.6 | Implement Twitter OAuth flow (authorize + callback) | `backend/app/api/v1/platforms.py` | S4.5, S1.9 |
| S4.7 | Implement LinkedIn OAuth flow (authorize + callback) | `backend/app/api/v1/platforms.py` (update) | S4.5, S1.9 |
| S4.8 | Implement platform list and disconnect endpoints | `backend/app/api/v1/platforms.py` (update) | S4.5 |
| S4.9 | Implement publish_post_now endpoint | `backend/app/api/v1/posts.py` (update) | S4.4 |
| S4.10 | Create publishing Celery tasks | `backend/app/tasks/publishing_tasks.py` | S4.4, S2.11 |
| S4.11 | Implement schedule post endpoint | `backend/app/api/v1/posts.py` (update) | S3.6 |
| S4.12 | Create frontend API client for platforms | `frontend/src/api/platforms.ts` | S1.17 |
| S4.13 | Create PlatformCard component (connect/disconnect) | `frontend/src/components/settings/PlatformCard.tsx` | S1.14 |
| S4.14 | Create Settings page with platform connections | `frontend/src/pages/Settings.tsx` | S4.12, S4.13 |
| S4.15 | Add Publish Now and Schedule buttons to PostEditor | `frontend/src/components/posts/PostEditor.tsx` (update) | S4.9, S4.11 |
| S4.16 | Create SchedulePicker component (date/time picker) | `frontend/src/components/posts/SchedulePicker.tsx` | S1.14 |
| S4.17 | Write unit tests for publishers (Twitter, LinkedIn, registry) | `backend/tests/test_services/test_publishers/*.py` | S4.2-S4.4, S1.21 |
| S4.18 | Write API integration tests for platform endpoints | `backend/tests/test_api/test_platforms.py` | S4.6-S4.8, S1.21 |
| S4.19 | Verify: connect Twitter → generate post → publish → verify on Twitter | - | All S4.* |
| S4.20 | Verify: connect LinkedIn → generate post → publish → verify on LinkedIn | - | All S4.* |

### Sprint 4 Deliverable
- User can connect Twitter and LinkedIn accounts via OAuth
- Settings page shows connection status
- User can publish approved posts immediately
- User can schedule posts for a future time
- Posts appear on the actual platform
- Published post URL is clickable
- Failed publishes show clear error messages

---

## 6. Sprint 5: Scheduling & Analytics

**Goal:** Automated content pipeline and engagement tracking.

### Tasks

| ID | Task | Files | Dependencies |
|----|------|-------|-------------|
| S5.1 | Create schedule Pydantic schemas | `backend/app/schemas/schedule.py` | S1.7 |
| S5.2 | Create schedule API routes (CRUD) | `backend/app/api/v1/schedules.py` | S5.1 |
| S5.3 | Implement process_active_schedules Celery task | `backend/app/tasks/generation_tasks.py` (update) | S5.2, S3.3 |
| S5.4 | Create analytics Pydantic schemas | `backend/app/schemas/analytics.py` | S1.7 |
| S5.5 | Add get_metrics to TwitterPublisher | `backend/app/services/publishers/twitter.py` (update) | S4.2 |
| S5.6 | Add get_metrics to LinkedInPublisher | `backend/app/services/publishers/linkedin.py` (update) | S4.3 |
| S5.7 | Create analytics Celery task (fetch_analytics) | `backend/app/tasks/analytics_tasks.py` | S5.5, S5.6, S2.11 |
| S5.8 | Create analytics API routes | `backend/app/api/v1/analytics.py` | S5.4 |
| S5.9 | Create dashboard API route | `backend/app/api/v1/dashboard.py` | S5.8 |
| S5.10 | Create frontend API clients for schedules and analytics | `frontend/src/api/schedules.ts`, `frontend/src/api/analytics.ts` | S1.17 |
| S5.11 | Create ScheduleManager component (list + create form) | `frontend/src/components/settings/ScheduleManager.tsx` | S5.10 |
| S5.12 | Add ScheduleManager to Settings page | `frontend/src/pages/Settings.tsx` (update) | S5.11 |
| S5.13 | Create EngagementChart component (Recharts) | `frontend/src/components/analytics/EngagementChart.tsx` | S1.14 |
| S5.14 | Create PlatformComparison component | `frontend/src/components/analytics/PlatformBreakdown.tsx` | S1.14 |
| S5.15 | Create TopPostsTable component | `frontend/src/components/analytics/TopPostsTable.tsx` | S1.14 |
| S5.16 | Create Analytics page | `frontend/src/pages/Analytics.tsx` | S5.10, S5.13-S5.15 |
| S5.17 | Update Dashboard with real data (stats, activity, upcoming) | `frontend/src/pages/Dashboard.tsx` (update) | S5.9 |
| S5.18 | Add API usage panel to Settings | `frontend/src/pages/Settings.tsx` (update) | S5.10 |
| S5.19 | Write unit tests for schedule processing and analytics tasks | `backend/tests/test_tasks/test_generation_tasks.py`, `test_analytics_tasks.py` | S5.3, S5.7, S1.21 |
| S5.20 | Write API integration tests for schedule and analytics endpoints | `backend/tests/test_api/test_schedules.py`, `test_analytics.py` | S5.2, S5.8, S1.21 |
| S5.21 | Verify: schedule → auto-generate → review → publish → analytics | - | All S5.* |

### Sprint 5 Deliverable
- User can create recurring schedules (e.g., "Post tech insight to LinkedIn every weekday at 9 AM")
- System auto-generates posts based on schedules
- Posts queue for review or auto-publish based on schedule settings
- Analytics page shows engagement metrics with charts
- Dashboard shows real stats, recent activity, and upcoming posts

---

## 7. Sprint 6: Comment Management

**Goal:** AI-powered comment replies, mention detection, and auto-reply system.

### Tasks

| ID | Task | Files | Dependencies |
|----|------|-------|-------------|
| S6.1 | Create comment and comment_replies ORM models | `backend/app/models/comment.py` | S1.7 |
| S6.2 | Create comment Pydantic schemas | `backend/app/schemas/comment.py` | S6.1 |
| S6.3 | Implement CommentFetcher (LinkedIn API) | `backend/app/services/comments/fetcher.py` | S4.3, S2.1 |
| S6.4 | Implement CommentClassifier (AI sentiment + type) | `backend/app/services/comments/classifier.py` | S3.1 |
| S6.5 | Implement CommentReplyGenerator (AI replies) | `backend/app/services/comments/reply_generator.py` | S3.1, S6.4 |
| S6.6 | Implement AutoReplyProcessor | `backend/app/services/comments/auto_reply.py` | S6.5, S4.3 |
| S6.7 | Create comment Celery tasks (fetch, auto-reply) | `backend/app/tasks/comment_tasks.py` | S6.3, S6.6, S2.11 |
| S6.8 | Create comment API routes (list, reply, generate-reply, dismiss, settings) | `backend/app/api/v1/comments.py` | S6.2 |
| S6.9 | Add comment worker to docker-compose | `docker-compose.yml` (update) | S6.7 |
| S6.10 | Create frontend API client for comments | `frontend/src/api/comments.ts` | S1.17 |
| S6.11 | Create CommentCard component | `frontend/src/components/comments/CommentCard.tsx` | S1.14 |
| S6.12 | Create CommentsPage with filters and auto-reply settings | `frontend/src/pages/Comments.tsx` | S6.10, S6.11 |
| S6.13 | Update Dashboard with unreplied comments stat card | `frontend/src/pages/Dashboard.tsx` (update) | S6.8 |
| S6.14 | Write unit tests for comment services (fetcher, classifier, reply generator, auto-reply) | `backend/tests/test_services/test_comments/*.py` | S6.3-S6.6, S1.21 |
| S6.15 | Write API integration tests for comment endpoints | `backend/tests/test_api/test_comments.py` | S6.8, S1.21 |
| S6.16 | Verify: comment fetch → AI reply → review → send → track | - | All S6.* |

### Sprint 6 Deliverable
- Comments fetched periodically from LinkedIn
- AI classifies comment sentiment and type
- AI generates contextual reply suggestions
- User can review, edit, and send replies
- Auto-reply mode with configurable filters and rate limiting
- Dashboard shows unreplied comments count
- Unit + API tests for all comment services and endpoints

---

## 7b. Sprint 7: LinkedIn Profile Intelligence

**Goal:** Collect lead data from LinkedIn post engagers, AI-classify statuses, build lead management dashboard.

**Note on LinkedIn API limitations:** The standard LinkedIn API provides limited profile data for non-connections. For MVP, the lead schema will store only reliably available fields: name, headline, current_company, profile_url, email (if public), location, industry. Fields like about_text, follower_count, phone, and twitter_handle are defined in the LLD as aspirational but will initially be stored as NULL. A "View on LinkedIn" link will be provided for users to manually check additional details.

### Tasks

| ID | Task | Files | Dependencies |
|----|------|-------|-------------|
| S7.1 | Create linkedin_leads and lead_engagements ORM models (slim schema: guaranteed fields only) | `backend/app/models/lead.py` | S1.6 |
| S7.2 | Create Alembic migration for leads tables (separate from initial migration) | `backend/alembic/versions/xxx_add_leads.py` | S7.1 |
| S7.3 | Create lead Pydantic schemas | `backend/app/schemas/lead.py` | S7.1 |
| S7.4 | Implement LinkedInProfileCollector | `backend/app/services/profile_intelligence/collector.py` | S4.3, S2.1 |
| S7.5 | Implement LeadStatusClassifier (AI) | `backend/app/services/profile_intelligence/classifier.py` | S3.1 |
| S7.6 | Implement LeadManager (orchestrator) | `backend/app/services/profile_intelligence/manager.py` | S7.4, S7.5 |
| S7.7 | Create profile Celery tasks (collect_engager_profiles, scan_single_profile) | `backend/app/tasks/profile_tasks.py` | S7.6, S2.11 |
| S7.8 | Create leads API routes (list, get, update, delete, export, stats) | `backend/app/api/v1/leads.py` | S7.3 |
| S7.9 | Implement CSV export endpoint | `backend/app/api/v1/leads.py` (update) | S7.6 |
| S7.10 | Create frontend API client for leads | `frontend/src/api/leads.ts` | S1.17 |
| S7.11 | Create LeadTable component | `frontend/src/components/leads/LeadTable.tsx` | S1.14 |
| S7.12 | Create LeadFilters component | `frontend/src/components/leads/LeadFilters.tsx` | S1.14 |
| S7.13 | Create LeadDetailModal component (with "View on LinkedIn" link) | `frontend/src/components/leads/LeadDetailModal.tsx` | S1.14 |
| S7.14 | Create LeadStats component | `frontend/src/components/leads/LeadStats.tsx` | S1.14 |
| S7.15 | Create LeadsPage | `frontend/src/pages/Leads.tsx` | S7.10-S7.14 |
| S7.16 | Add Leads nav item to sidebar | `frontend/src/components/layout/Sidebar.tsx` (update) | S7.15 |
| S7.17 | Create ExportModal component | `frontend/src/components/leads/ExportModal.tsx` | S7.9, S1.14 |
| S7.18 | Write unit tests for profile intelligence (collector, classifier, manager) | `backend/tests/test_services/test_profile_intelligence/*.py` | S7.4-S7.6, S1.21 |
| S7.19 | Write API integration tests for leads endpoints | `backend/tests/test_api/test_leads.py` | S7.8, S1.21 |
| S7.20 | Verify: comment/like → profile collected → status classified → appears in Leads page | - | All S7.* |

### Sprint 7 Deliverable
- Profiles collected from LinkedIn post engagers (commenters, likers)
- AI classifies status: OPEN TO WORK, HIRING, Looking for Business, General
- Public email extracted when available; "View on LinkedIn" link for additional details
- Leads page with search, filter by status/industry/contact availability
- Lead detail view with engagement history, tags, notes
- CSV export with column selection and filters
- Lead deletion for privacy compliance
- Unit + API tests for all profile intelligence services and endpoints

---

## 8. Sprint 8: Production Hardening

**Goal:** Docker deployment, logging, API hardening, UI polish, and E2E testing.

**Note:** Unit and API integration tests are written within each feature sprint (Sprints 1-7). This sprint focuses on infrastructure, production readiness, and a basic E2E test.

### Tasks

| ID | Task | Files | Dependencies |
|----|------|-------|-------------|
| S8.1 | Add structured logging (structlog) across all services | `backend/app/utils/logging.py`, all services | S1.5 |
| S8.2 | Add API rate limiting (slowapi) | `backend/app/main.py` (update) | S1.5 |
| S8.3 | Add health check endpoint | `backend/app/api/v1/health.py` | S1.5 |
| S8.4 | Create backend Dockerfile | `backend/Dockerfile` | S1.4 |
| S8.5 | Create frontend Dockerfile (multi-stage: build + nginx) | `frontend/Dockerfile` | S1.13 |
| S8.6 | Create nginx configuration (reverse proxy) | `frontend/nginx.conf` | S8.5 |
| S8.7 | Update docker-compose for full-stack deployment (7 services) | `docker-compose.yml` (update) | S8.4, S8.5 |
| S8.8 | Add error handling UI (error boundaries, retry) | `frontend/src/components/common/ErrorBoundary.tsx` | S1.14 |
| S8.9 | Add loading states to all pages | All frontend pages | S1.14 |
| S8.10 | Responsive design review and fixes | All frontend components | S1.14 |
| S8.11 | Test coverage gap analysis and fill missing tests | All test files | S1.21 |
| S8.12 | Set up Playwright and write basic E2E test (register → login → fetch content → generate → publish) | `frontend/e2e/`, `playwright.config.ts` | S8.7 |
| S8.13 | Add E2E test job to GitHub Actions CI | `.github/workflows/ci.yml` (update) | S8.12, S1.20 |
| S8.14 | Final docker-compose up test (full stack, all 7 services) | - | All S8.* |
| S8.15 | Write setup documentation in README | `README.md` (update) | All |

### Sprint 8 Deliverable
- `docker-compose up` starts all 7 services (postgres, redis, backend, celery-worker, celery-worker-comments, celery-beat, frontend)
- Health check endpoint at `/health`
- API rate limiting prevents abuse
- Structured JSON logging for all services
- All prior sprint tests passing (70%+ coverage on critical paths)
- Basic Playwright E2E test for happy path
- Error boundaries and loading states throughout UI
- Responsive on 1024px+ screens
- README with complete setup instructions

---

## 8. Task Dependency Graph

```
Sprint 1 (Foundation)
S1.1 ──► S1.4 ──► S1.5 ──► S1.6 ──► S1.7 ──► S1.8
                    │                   │
                    ▼                   ▼
                  S1.9 ──► S1.11     S1.10
                    │         │
                    ▼         ▼
                  S1.12 ◄─── S1.11
S1.1 ──► S1.13 ──► S1.14 ──► S1.15 ──► S1.16
                                         │
           S1.17 ◄── S1.13              │
             │                           │
             ▼                           ▼
           S1.18 ──────────────────► S1.19
S1.4 ──► S1.20 (CI/CD)
S1.13 ──► S1.20
S1.5 ──► S1.21 (test config)
S1.9 ──► S1.22 (security tests)
S1.11 ──► S1.23 (auth API tests)
All S1.* ──► S1.24 (verify)

Sprint 2 (Content Research)
S1.5 ──► S2.1 ──► S2.4 ──► S2.5 ──┐
S1.5 ──► S2.2                      ├──► S2.10 ──► S2.12 ──► S2.21
S1.5 ──► S2.3     S2.4 ──► S2.6 ──┤
                   S2.4 ──► S2.7 ──┤
                   S2.4 ──► S2.8 ──┤
                   S2.4 ──► S2.9 ──┘
S1.5 ──► S2.11 ──► S2.12
S1.5 ──► S2.13 ──► S2.14
S1.17 ──► S2.16 ──► S2.20
S1.14 ──► S2.17 ──► S2.18 ──► S2.20
S1.14 ──► S2.19 ──► S2.20

Sprint 3 (AI Generation)
S1.5 ──► S3.1 ──► S3.2 ──► S3.3 ──► S3.4
                             │
                             ▼
S1.7 ──► S3.5 ──► S3.6 ◄── S3.3
                    │
S1.17 ──► S3.8 ──► S3.13
S1.14 ──► S3.9 ──► S3.10 ──► S3.13
S1.14 ──► S3.11 ──► S3.13
S1.14 ──► S3.12 ──► S3.13
S1.14 ──► S3.15

Sprint 4 (Publishing)
S1.5 ──► S4.1 ──► S4.2 ──► S4.4
                   S4.3 ──► S4.4 ──► S4.9
S1.7 ──► S4.5 ──► S4.6
                   S4.7
                   S4.8
S4.4 ──► S4.10
S1.17 ──► S4.12 ──► S4.14
S1.14 ──► S4.13 ──► S4.14

Sprint 5 (Scheduling & Analytics)
S1.7 ──► S5.1 ──► S5.2
S5.2 ──► S5.3
S1.7 ──► S5.4 ──► S5.8
S4.2 ──► S5.5 ──► S5.7
S4.3 ──► S5.6 ──► S5.7
S5.8 ──► S5.9

Sprint 6 (Comment Management)
S1.7 ──► S6.1 ──► S6.2
S4.3 ──► S6.3
S3.1 ──► S6.4 ──► S6.5 ──► S6.6
S6.3 ──► S6.7
S6.6 ──► S6.7
S6.2 ──► S6.8
S1.17 ──► S6.10 ──► S6.12
S1.14 ──► S6.11 ──► S6.12

Sprint 7 (Profile Intelligence)
S1.6 ──► S7.1 ──► S7.2 (separate Alembic migration) ──► S7.3
S4.3 ──► S7.4 ──► S7.6
S3.1 ──► S7.5 ──► S7.6
S7.6 ──► S7.7
S7.3 ──► S7.8 ──► S7.9
S1.17 ──► S7.10 ──► S7.15
S1.14 ──► S7.11 ──► S7.15
S1.14 ──► S7.12 ──► S7.15
S1.14 ──► S7.13 ──► S7.15
S1.14 ──► S7.14 ──► S7.15
S7.4-S7.6 ──► S7.18 (unit tests)
S7.8 ──► S7.19 (API tests)
All S7.* ──► S7.20 (verify)

Sprint 8 (Hardening)
All sprints ──► S8.*
```

---

## 9. Testing Strategy

### 9.1 Testing Layers

| Layer | Tool | Coverage Target |
|-------|------|----------------|
| Unit Tests (Backend) | pytest + pytest-asyncio | 80% on services |
| API Integration Tests | pytest + httpx TestClient | All endpoints |
| Celery Task Tests | pytest + celery test utils | All tasks |
| Frontend Component Tests | Vitest + React Testing Library | Key components |
| E2E Tests (Future) | Playwright | Critical user flows |

### 9.2 Test Categories

#### Unit Tests (Backend)
```
tests/
├── test_services/
│   ├── test_content_research/
│   │   ├── test_hackernews.py      # Mock HTTP responses, verify parsing
│   │   ├── test_reddit.py          # Mock OAuth + API responses
│   │   ├── test_devto.py
│   │   ├── test_jokes.py
│   │   ├── test_github_trending.py
│   │   └── test_aggregator.py      # Test orchestration, error handling
│   ├── test_ai_generator/
│   │   ├── test_prompts.py         # Verify prompt templates produce valid prompts
│   │   ├── test_generator.py       # Mock Claude API, verify post creation
│   │   └── test_client.py          # Mock Anthropic SDK
│   ├── test_publishers/
│   │   ├── test_twitter.py         # Mock Twitter API, verify publish flow
│   │   ├── test_linkedin.py        # Mock LinkedIn API
│   │   └── test_registry.py        # Test publisher lookup
│   └── test_profile_intelligence/
│       ├── test_collector.py       # Mock LinkedIn profile API, verify data extraction
│       ├── test_classifier.py      # Mock Claude API, verify status classification
│       └── test_manager.py         # Test orchestration, dedup, upsert
├── test_utils/
│   ├── test_security.py            # JWT creation/verification, encryption
│   ├── test_rate_limiter.py        # Token bucket logic
│   └── test_cache.py               # Redis cache operations
└── test_tasks/
    ├── test_research_tasks.py      # Test Celery task execution
    ├── test_generation_tasks.py
    └── test_publishing_tasks.py
```

#### API Integration Tests
```
tests/test_api/
├── test_auth.py
│   ├── test_register_success
│   ├── test_register_duplicate_email
│   ├── test_register_weak_password
│   ├── test_login_success
│   ├── test_login_invalid_credentials
│   ├── test_refresh_token
│   ├── test_me_authenticated
│   └── test_me_unauthenticated
├── test_content.py
│   ├── test_list_content_empty
│   ├── test_list_content_filtered
│   ├── test_list_content_sorted
│   ├── test_list_content_paginated
│   ├── test_get_content_by_id
│   ├── test_get_content_not_found
│   └── test_refresh_content_triggers_task
├── test_posts.py
│   ├── test_generate_post_from_content
│   ├── test_list_posts_by_status
│   ├── test_update_post_text
│   ├── test_approve_draft_post
│   ├── test_reject_draft_post
│   ├── test_approve_non_draft_fails
│   ├── test_publish_approved_post
│   └── test_schedule_post
├── test_platforms.py
│   ├── test_list_platforms_empty
│   ├── test_twitter_authorize_redirect
│   ├── test_disconnect_platform
│   └── test_disconnect_nonexistent
├── test_leads.py
│   ├── test_list_leads_empty
│   ├── test_list_leads_filtered_by_status
│   ├── test_list_leads_search
│   ├── test_get_lead_detail
│   ├── test_update_lead_tags_notes
│   ├── test_delete_lead_cascade
│   ├── test_export_leads_csv
│   └── test_lead_stats
└── test_dashboard.py
    ├── test_dashboard_data
    └── test_dashboard_unauthenticated
```

### 9.3 Test Fixtures

```python
# conftest.py
@pytest.fixture
async def test_db():
    """Create test database and apply migrations."""
    # Use test-specific PostgreSQL database
    # Rollback after each test

@pytest.fixture
async def test_client(test_db):
    """FastAPI TestClient with test database."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client

@pytest.fixture
async def authenticated_client(test_client):
    """TestClient with authenticated user."""
    # Register + login, set auth cookie
    yield client

@pytest.fixture
def mock_claude_api():
    """Mock Anthropic API responses."""
    with patch("anthropic.Anthropic") as mock:
        mock.return_value.messages.create.return_value = MockResponse(
            content=[MockContent(text="Generated tweet about AI #Tech")]
        )
        yield mock

@pytest.fixture
def sample_content_sources(test_db):
    """Pre-populated content sources for testing."""
    # Insert 10 sample items from various sources
```

### 9.4 Mocking Strategy

| External Service | Mock Strategy |
|-----------------|---------------|
| Hacker News API | httpx mock with sample JSON responses |
| Reddit API | httpx mock with OAuth + feed responses |
| Dev.to API | httpx mock |
| JokeAPI | httpx mock |
| Claude API | Patch `anthropic.Anthropic` client |
| Twitter API | httpx mock for OAuth + publish |
| LinkedIn API | httpx mock for OAuth + publish + profile data |
| LinkedIn Profile API | httpx mock with sample profile JSON (name, headline, company) |
| Redis | Use real Redis (from Docker) or fakeredis |
| PostgreSQL | Use real test database (from Docker) |

---

## 10. Definition of Done

### 10.1 Per-Task DoD

A task is "done" when:
- [ ] Code is written and follows project conventions (PEP 8, TypeScript strict)
- [ ] Linting passes (ruff for Python, ESLint for TypeScript)
- [ ] Unit tests written for new business logic (services, utils)
- [ ] API tests written for new endpoints
- [ ] No TypeScript `any` types (unless unavoidable)
- [ ] No hardcoded secrets or credentials
- [ ] Error handling covers expected failure cases
- [ ] Code reviewed (self-review for solo development)

### 10.2 Per-Sprint DoD

A sprint is "done" when:
- [ ] All sprint tasks are done (per-task DoD)
- [ ] Sprint deliverable works end-to-end as described
- [ ] No regression in previously working features
- [ ] Docker services start and stop cleanly
- [ ] All tests pass (`pytest` for backend)
- [ ] No unhandled console errors in browser (frontend)

### 10.3 Overall Project DoD

The project is "done" when:
- [ ] All 8 sprints completed
- [ ] `docker-compose up` starts full stack in under 60 seconds
- [ ] User can complete the full pipeline: register → connect platforms → fetch content → generate post → review → publish → view analytics
- [ ] Published posts appear on actual Twitter/LinkedIn accounts
- [ ] Analytics show real engagement data
- [ ] Schedules generate and publish posts automatically
- [ ] Comments fetched and AI replies working (LinkedIn)
- [ ] LinkedIn profile intelligence collecting leads from post engagers
- [ ] Lead status classification (OPEN TO WORK, HIRING, etc.) working
- [ ] Leads page with search, filter, export functional
- [ ] README provides clear setup instructions
- [ ] .env.example documents all required variables
- [ ] Test suite passes with 70%+ coverage on critical paths

---

## Appendix: Key File Summary

| File | Purpose | Sprint |
|------|---------|--------|
| `docker-compose.yml` | All services definition | S1, S2, S6 |
| `backend/app/main.py` | FastAPI app entry point | S1 |
| `backend/app/config.py` | Environment configuration | S1 |
| `backend/app/database.py` | Database connection | S1 |
| `backend/app/models/*.py` | ORM models (9 core+comment tables in S1, 2 lead tables in S7) | S1, S7 |
| `backend/app/utils/security.py` | JWT, bcrypt, Fernet | S1 |
| `backend/app/utils/http_client.py` | Resilient HTTP client | S2 |
| `backend/app/utils/cache.py` | Redis cache helpers | S2 |
| `backend/app/services/content_research/aggregator.py` | Content pipeline orchestrator | S2 |
| `backend/app/services/ai_generator/generator.py` | AI post generation | S3 |
| `backend/app/services/ai_generator/prompts.py` | Prompt templates | S3 |
| `backend/app/services/publishers/registry.py` | Publisher lookup | S4 |
| `backend/app/tasks/celery_app.py` | Celery configuration | S2 |
| `frontend/src/pages/Dashboard.tsx` | Main dashboard | S1, S5 |
| `frontend/src/pages/ContentResearch.tsx` | Content browser | S2 |
| `frontend/src/pages/PostManager.tsx` | Post review/edit | S3 |
| `frontend/src/pages/Settings.tsx` | Platform connections | S4, S5 |
| `backend/app/services/profile_intelligence/collector.py` | LinkedIn profile collector | S7 |
| `backend/app/services/profile_intelligence/classifier.py` | AI status classifier | S7 |
| `backend/app/services/profile_intelligence/manager.py` | Lead management orchestrator | S7 |
| `backend/app/tasks/profile_tasks.py` | Profile collection tasks | S7 |
| `frontend/src/pages/Analytics.tsx` | Engagement charts | S5 |
| `frontend/src/pages/Comments.tsx` | Comment management | S6 |
| `frontend/src/pages/Leads.tsx` | Lead management dashboard | S7 |
