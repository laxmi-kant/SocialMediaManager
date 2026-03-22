# High-Level Design (HLD)
## AI-Powered Social Media Manager Platform

**Document Version:** 1.0
**Date:** March 20, 2026
**Author:** Engineering Team

---

## Table of Contents
1. [System Architecture](#1-system-architecture)
2. [Tech Stack Selection](#2-tech-stack-selection)
3. [Data Flow Diagrams](#3-data-flow-diagrams)
4. [Integration Architecture](#4-integration-architecture)
5. [Deployment Architecture](#5-deployment-architecture)
6. [Security Architecture](#6-security-architecture)
7. [Scalability Considerations](#7-scalability-considerations)

---

## 1. System Architecture

### 1.1 Architecture Overview

The system follows a **layered architecture** with clear separation between presentation, API, business logic, and data layers, plus an asynchronous task processing layer.

```
┌──────────────────────────────────────────────────────────────────────┐
│                      PRESENTATION LAYER                              │
│  ┌──────────────────────────────────────────────────────────────┐    │
│  │          React + Vite + TypeScript Frontend                   │    │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐        │    │
│  │  │Dashboard │ │Content   │ │Post      │ │Settings  │        │    │
│  │  │Page      │ │Research  │ │Manager   │ │Page      │        │    │
│  │  └──────────┘ └──────────┘ └──────────┘ └──────────┘        │    │
│  │  ┌──────────────────────────────────────────────────┐        │    │
│  │  │  Zustand Store  │  React Query  │  Axios Client  │        │    │
│  │  └──────────────────────────────────────────────────┘        │    │
│  └──────────────────────────────────────────────────────────────┘    │
│                              │ HTTP/REST                             │
│                              ▼                                       │
│  ┌──────────────────────────────────────────────────────────────┐    │
│  │                   API LAYER (FastAPI)                          │    │
│  │  ┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐     │    │
│  │  │ Auth   │ │Content │ │ Posts  │ │Schedule│ │Analytic│     │    │
│  │  │ Router │ │ Router │ │ Router │ │ Router │ │ Router │     │    │
│  │  └────────┘ └────────┘ └────────┘ └────────┘ └────────┘     │    │
│  │  ┌──────────────────────────────────────────────────┐        │    │
│  │  │  JWT Middleware  │  CORS  │  Rate Limiting       │        │    │
│  │  └──────────────────────────────────────────────────┘        │    │
│  └──────────────────────────────────────────────────────────────┘    │
│                              │                                       │
│                              ▼                                       │
│  ┌──────────────────────────────────────────────────────────────┐    │
│  │                 BUSINESS LOGIC LAYER                           │    │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐       │    │
│  │  │  Content      │  │  AI Generator │  │  Publishers  │       │    │
│  │  │  Research     │  │  Service      │  │  Service     │       │    │
│  │  │  Service      │  │               │  │  + Profile   │       │    │
│  │  │              │  │               │  │  Intelligence │       │    │
│  │  │ ┌───────────┐ │  │ ┌───────────┐ │  │ ┌──────────┐│       │    │
│  │  │ │HackerNews │ │  │ │ Claude    │ │  │ │ Twitter  ││       │    │
│  │  │ │Reddit     │ │  │ │ Client    │ │  │ │ LinkedIn ││       │    │
│  │  │ │Dev.to     │ │  │ │ Prompts   │ │  │ │ Registry ││       │    │
│  │  │ │Jokes      │ │  │ │ Generator │ │  │ └──────────┘│       │    │
│  │  │ │GitHub     │ │  │ └───────────┘ │  └──────────────┘       │    │
│  │  │ │Aggregator │ │  └──────────────┘                         │    │
│  │  │ └───────────┘ │                                            │    │
│  │  └──────────────┘                                             │    │
│  └──────────────────────────────────────────────────────────────┘    │
│                              │                                       │
│                              ▼                                       │
│  ┌──────────────────────────────────────────────────────────────┐    │
│  │                    DATA LAYER                                 │    │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐       │    │
│  │  │ PostgreSQL   │  │    Redis      │  │  SQLAlchemy  │       │    │
│  │  │ (persistent) │  │  (cache +     │  │  ORM +       │       │    │
│  │  │              │  │   broker)     │  │  Alembic     │       │    │
│  │  └──────────────┘  └──────────────┘  └──────────────┘       │    │
│  └──────────────────────────────────────────────────────────────┘    │
│                                                                      │
│  ┌──────────────────────────────────────────────────────────────┐    │
│  │              ASYNC TASK LAYER (Celery + Redis)                │    │
│  │                                                               │    │
│  │  Worker 1 (General):                                          │    │
│  │  ┌────────────┐ ┌────────────┐ ┌────────────┐ ┌──────────┐  │    │
│  │  │ Research   │ │ Generation │ │ Publishing │ │Analytics │  │    │
│  │  │ Tasks      │ │ Tasks      │ │ Tasks      │ │ Tasks    │  │    │
│  │  │ (every 2h) │ │ (on-demand)│ │ (every 1m) │ │(every 6h)│  │    │
│  │  └────────────┘ └────────────┘ └────────────┘ └──────────┘  │    │
│  │                                                               │    │
│  │  Worker 2 (Comments + Profile Intelligence - Dedicated):      │    │
│  │  ┌────────────┐ ┌────────────┐ ┌────────────┐               │    │
│  │  │ Comment    │ │ Mention    │ │ Auto-Reply │               │    │
│  │  │ Fetch      │ │ Detection  │ │ Processing │               │    │
│  │  │ (configrbl)│ │ (configrbl)│ │            │               │    │
│  │  └────────────┘ └────────────┘ └────────────┘               │    │
│  │  ┌────────────┐ ┌────────────┐ ┌────────────┐               │    │
│  │  │ Profile    │ │ Status     │ │ Contact    │               │    │
│  │  │ Collector  │ │ Classifier │ │ Extractor  │               │    │
│  │  │ (on new    │ │ (AI-based) │ │ (public    │               │    │
│  │  │  engager)  │ │            │ │  data only)│               │    │
│  │  └────────────┘ └────────────┘ └────────────┘               │    │
│  │  Note: Comment reading & profile intelligence LinkedIn only.  │    │
│  │  Twitter requires Basic tier ($200/mo) for reading.           │    │
│  │                                                               │    │
│  │  ┌──────────────────────────────────────────────────┐        │    │
│  │  │           Celery Beat (Scheduler)                │        │    │
│  │  └──────────────────────────────────────────────────┘        │    │
│  └──────────────────────────────────────────────────────────────┘    │
└──────────────────────────────────────────────────────────────────────┘
```

### 1.2 Component Responsibilities

| Component | Responsibility |
|-----------|---------------|
| **React Frontend** | User interface, state management, API communication |
| **FastAPI Backend** | REST API, request validation, auth, routing to services |
| **Content Research Service** | Fetch trending content from external APIs, deduplicate, store |
| **AI Generator Service** | Generate social media posts using Claude API |
| **Publisher Service** | Publish posts to Twitter/LinkedIn, handle OAuth flows |
| **Profile Intelligence Service** | Collect LinkedIn profile data, AI status classification, contact extraction |
| **Celery Workers** | Execute async tasks (fetch, generate, publish, analytics, profile scanning) |
| **Celery Beat** | Schedule periodic tasks on defined intervals |
| **PostgreSQL** | Persistent storage for all application data |
| **Redis** | Message broker for Celery, API response cache, rate limit state |
| **SQLAlchemy + Alembic** | ORM for database access, schema migrations |

### 1.3 Communication Patterns

| From | To | Protocol | Pattern |
|------|----|----------|---------|
| Frontend → Backend | HTTP/REST | Request-Response (JSON) |
| Backend → PostgreSQL | TCP (asyncpg) | Async query |
| Backend → Redis | TCP (redis-py) | Cache get/set |
| Backend → Celery | Redis (broker) | Task dispatch (async) |
| Celery → External APIs | HTTPS | Request-Response (httpx) |
| Celery → PostgreSQL | TCP (psycopg2) | Sync query |
| Celery → Redis | TCP | Cache, rate limit checks |
| Celery Beat → Celery | Redis (broker) | Periodic task scheduling |

---

## 2. Tech Stack Selection

### 2.1 Backend: Python 3.10+ with FastAPI

**Decision:** FastAPI over Django, Flask, or Node.js/Express

| Factor | FastAPI | Django | Flask | Node.js/Express |
|--------|---------|--------|-------|-----------------|
| Async support | Native (ASGI) | Limited (channels) | Limited (Quart) | Native |
| API documentation | Auto OpenAPI/Swagger | Manual/DRF | Manual | Manual |
| Validation | Pydantic (built-in) | Serializers/forms | Manual | Manual/Joi |
| Performance | High (Starlette) | Moderate | Moderate | High |
| AI SDK support | Anthropic SDK (Python-first) | Same | Same | TypeScript SDK |
| Task queue | Celery (mature) | Celery | Celery | Bull/BullMQ |
| Learning curve | Low | Medium | Low | Low |

**Justification:** FastAPI's native async support is critical for our I/O-heavy workload (calling 6+ external APIs, Claude API, social media APIs). Auto-generated OpenAPI docs reduce documentation effort. Pydantic validation ensures data integrity across the pipeline. The Anthropic Python SDK is the most mature option.

### 2.2 Frontend: React 18 + Vite + TypeScript

**Decision:** React + Vite over Next.js, Vue, or Angular

| Factor | React + Vite | Next.js | Vue + Vite | Angular |
|--------|-------------|---------|-----------|---------|
| SSR needed? | No (SPA sufficient) | Yes (unnecessary overhead) | No | No |
| Build speed | Fast (Vite) | Moderate | Fast (Vite) | Moderate |
| Ecosystem | Largest | Large | Growing | Large |
| Dashboard components | Rich (Recharts, etc.) | Same | Fewer | Fewer |
| State management | Zustand/React Query | Same | Pinia | RxJS |
| TypeScript | Full support | Full support | Full support | Built-in |

**Justification:** Our frontend is a dashboard SPA - no SEO or SSR needed. Next.js's server-side features would be redundant since FastAPI handles our API. Vite provides the fastest dev experience. React has the richest ecosystem for dashboard UI (charts, tables, editors).

### 2.3 Database: PostgreSQL

**Decision:** PostgreSQL over MySQL, MongoDB, or SQLite

| Factor | PostgreSQL | MySQL | MongoDB | SQLite |
|--------|-----------|-------|---------|--------|
| JSONB support | Excellent | JSON (limited) | Native (BSON) | JSON1 extension |
| Array types | Native | No | Native | No |
| Full-text search | Built-in | Basic | Good | FTS5 |
| UUID support | Native gen_random_uuid() | Manual | ObjectId | Manual |
| Concurrent access | MVCC (excellent) | Good | Good | Limited |
| Docker ready | Excellent | Excellent | Excellent | File-based |

**Justification:** We need JSONB for flexible content metadata, array types for tags/scopes, UUID primary keys, and robust concurrent access for Celery workers + API server. PostgreSQL is the strongest relational option for all these needs.

### 2.4 Task Queue: Celery + Redis

**Decision:** Celery over APScheduler, Dramatiq, or Huey

| Factor | Celery | APScheduler | Dramatiq | Huey |
|--------|--------|-------------|----------|------|
| Periodic tasks | Celery Beat (mature) | Built-in | Needs add-on | Built-in |
| Broker options | Redis, RabbitMQ | In-process | Redis, RabbitMQ | Redis |
| Monitoring | Flower | Manual | Manual | Manual |
| Community | Largest | Medium | Growing | Small |
| Retry support | Built-in | Manual | Built-in | Built-in |
| Production proven | Extensive | Moderate | Growing | Small |

**Justification:** Celery is the most battle-tested task queue for Python. We need reliable periodic tasks (content fetching every 2h, scheduled publishing every minute, analytics every 6h). Celery Beat handles this natively. Redis serves as both broker and cache, avoiding additional infrastructure.

### 2.5 AI: Anthropic Claude API (Haiku 4.5)

**Decision:** Claude Haiku 4.5 as default, Sonnet 4.5 as option

| Factor | Claude Haiku 4.5 | Claude Sonnet 4.5 | GPT-4o-mini | GPT-4o |
|--------|-----------------|-------------------|-------------|--------|
| Cost (input/M tokens) | $1 | $3 | $0.15 | $2.50 |
| Cost (output/M tokens) | $5 | $15 | $0.60 | $10 |
| Quality for social media | Good | Excellent | Good | Excellent |
| Speed | Fast | Moderate | Fast | Moderate |
| Monthly cost (20 posts/day) | ~$0.60 | ~$1.80 | ~$0.10 | ~$1.50 |

**Justification:** Claude produces more natural, less "AI-sounding" social media content. Haiku 4.5 provides the best cost/quality balance for this use case at ~$0.60/month. Sonnet 4.5 available as upgrade for users wanting premium quality. Using Anthropic's own SDK ensures best integration support.

### 2.6 UI: Tailwind CSS + shadcn/ui + Recharts

| Component | Choice | Justification |
|-----------|--------|---------------|
| CSS Framework | Tailwind CSS | Utility-first, rapid development, consistent design system |
| Component Library | shadcn/ui | Accessible, unstyled primitives, copy-paste customizable |
| Charts | Recharts | Lightweight, React-native, good for dashboards |
| Icons | Lucide React | Clean, consistent, tree-shakeable |
| State | Zustand + React Query | Zustand for UI state, React Query for server state caching |
| Routing | React Router v6 | Standard, full-featured |
| HTTP Client | Axios | Interceptors for auth, request/response transforms |
| Date Handling | date-fns | Lightweight, tree-shakeable, immutable |

---

## 3. Data Flow Diagrams

### 3.1 Content Research Flow

```
                    Celery Beat (every 2 hours)
                              │
                              ▼
                    ┌─────────────────┐
                    │  Aggregator     │
                    │  Task           │
                    └────────┬────────┘
                             │
              ┌──────┬───────┼───────┬──────┬───────┐
              ▼      ▼       ▼       ▼      ▼       ▼
         ┌────────┐ ┌─────┐ ┌─────┐ ┌────┐ ┌─────┐ ┌──────┐
         │Hacker  │ │Redd │ │Dev  │ │Joke│ │Dad  │ │GitHub│
         │News    │ │it   │ │.to  │ │API │ │Joke │ │Trend │
         │Client  │ │Clnt │ │Clnt │ │Clnt│ │Clnt │ │Client│
         └───┬────┘ └──┬──┘ └──┬──┘ └─┬──┘ └──┬──┘ └──┬───┘
             │         │       │      │       │       │
             ▼         ▼       ▼      ▼       ▼       ▼
         ┌─────────────────────────────────────────────────┐
         │          Redis Cache Layer                       │
         │  (TTL: 15min for news, 1hr for jokes)           │
         └───────────────────────┬─────────────────────────┘
                                 │
                                 ▼
         ┌─────────────────────────────────────────────────┐
         │          Deduplication Layer                      │
         │  (UPSERT by source_type + external_id)          │
         └───────────────────────┬─────────────────────────┘
                                 │
                                 ▼
         ┌─────────────────────────────────────────────────┐
         │          PostgreSQL: content_sources              │
         └─────────────────────────────────────────────────┘
```

### 3.2 AI Content Generation Flow

```
         User clicks "Generate Post"
         or Schedule triggers generation
                      │
                      ▼
         ┌────────────────────────┐
         │  API: POST /posts/     │
         │  generate              │
         └───────────┬────────────┘
                     │
                     ▼
         ┌────────────────────────┐
         │  Generator Service     │
         │  1. Load content source│
         │  2. Select prompt      │
         │     template           │
         │  3. Build prompt       │
         └───────────┬────────────┘
                     │
                     ▼
         ┌────────────────────────┐
         │  Claude API            │
         │  (Haiku 4.5)           │
         │  POST /messages        │
         │  Input: prompt         │
         │  Output: post text     │
         └───────────┬────────────┘
                     │
                     ▼
         ┌────────────────────────┐
         │  Post-processing       │
         │  1. Validate char limit│
         │  2. Extract hashtags   │
         │  3. Log token usage    │
         └───────────┬────────────┘
                     │
                     ▼
         ┌────────────────────────┐
         │  PostgreSQL:            │
         │  generated_posts       │
         │  (status = 'draft')    │
         └────────────────────────┘
```

### 3.3 Publishing Flow

```
         User clicks "Publish Now"
         or Celery checks scheduled posts (every 1 min)
                      │
                      ▼
         ┌────────────────────────┐
         │  Is post approved or   │──No──► Reject / Stay in queue
         │  scheduled & due?      │
         └───────────┬────────────┘
                     │ Yes
                     ▼
         ┌────────────────────────┐
         │  Publisher Registry    │
         │  Get publisher for     │
         │  target_platform       │
         └───────────┬────────────┘
                     │
              ┌──────┴──────┐
              ▼             ▼
    ┌──────────────┐ ┌──────────────┐
    │ Twitter      │ │ LinkedIn     │
    │ Publisher    │ │ Publisher    │
    │              │ │              │
    │ 1.Load token │ │ 1.Load token │
    │ 2.Decrypt    │ │ 2.Decrypt    │
    │ 3.Check rate │ │ 3.Check rate │
    │   limit      │ │   limit      │
    │ 4.POST tweet │ │ 4.POST ugc   │
    │ 5.Get post ID│ │ 5.Get URN    │
    └──────┬───────┘ └──────┬───────┘
           │                │
           ▼                ▼
    ┌─────────────────────────────┐
    │  Result Handling             │
    │  Success: store post ID/URL  │
    │  Failure: log error, mark    │
    │           as failed          │
    └──────────────┬──────────────┘
                   │
                   ▼
    ┌─────────────────────────────┐
    │  PostgreSQL:                 │
    │  published_posts             │
    │  generated_posts.status =    │
    │    'published' or 'failed'   │
    └─────────────────────────────┘
```

### 3.4 OAuth Flow (Twitter/LinkedIn)

```
    User clicks "Connect Twitter"
              │
              ▼
    ┌─────────────────────┐
    │  Backend generates   │
    │  1. State token      │
    │  2. PKCE verifier    │
    │  3. Auth URL         │
    └──────────┬──────────┘
               │
               ▼
    ┌─────────────────────┐
    │  Redirect to         │
    │  Twitter/LinkedIn    │
    │  authorization page  │
    └──────────┬──────────┘
               │ User approves
               ▼
    ┌─────────────────────┐
    │  Callback URL with   │
    │  authorization code  │
    │  + state             │
    └──────────┬──────────┘
               │
               ▼
    ┌─────────────────────┐
    │  Backend:            │
    │  1. Verify state     │
    │  2. Exchange code    │
    │     for tokens       │
    │  3. Encrypt tokens   │
    │  4. Store in DB      │
    │  5. Fetch user info  │
    └──────────┬──────────┘
               │
               ▼
    ┌─────────────────────┐
    │  Redirect to         │
    │  Settings page       │
    │  (show connected)    │
    └─────────────────────┘
```

### 3.5 Complete Content Pipeline (End-to-End)

```
    ┌─────────────────────────────────────────────────────────────────┐
    │                     AUTOMATED PIPELINE                           │
    │                                                                  │
    │  Celery Beat ──► Research ──► Store ──► [Schedule Trigger]       │
    │  (every 2h)      Tasks       in DB      (if schedule active)    │
    │                                              │                   │
    │                                              ▼                   │
    │                                    ┌──────────────────┐          │
    │                                    │ Pick top content  │          │
    │                                    │ Generate AI post  │          │
    │                                    └────────┬─────────┘          │
    │                                             │                    │
    │                              ┌──────────────┴──────────────┐     │
    │                              ▼                             ▼     │
    │                    ┌──────────────┐              ┌──────────────┐│
    │                    │auto_approve  │              │Manual review ││
    │                    │= true        │              │= true        ││
    │                    │              │              │(default)     ││
    │                    │Schedule post │              │Queue as draft││
    │                    │for next slot │              │              ││
    │                    └──────┬───────┘              └──────┬───────┘│
    │                           │                            │         │
    │                           │                    User reviews,     │
    │                           │                    edits, approves   │
    │                           │                            │         │
    │                           ▼                            ▼         │
    │                    ┌─────────────────────────────────────┐       │
    │                    │  Celery: publish_scheduled_posts     │       │
    │                    │  (every 1 minute)                    │       │
    │                    │  Picks posts where:                  │       │
    │                    │    status='scheduled'                │       │
    │                    │    scheduled_for <= NOW()            │       │
    │                    └────────────────┬────────────────────┘       │
    │                                    │                             │
    │                                    ▼                             │
    │                         ┌─────────────────┐                      │
    │                         │ Publish to       │                      │
    │                         │ Twitter/LinkedIn │                      │
    │                         └────────┬────────┘                      │
    │                                  │                               │
    │                                  ▼                               │
    │                    ┌─────────────────────────┐                   │
    │                    │ Celery: fetch_analytics  │                   │
    │                    │ (every 6 hours)          │                   │
    │                    │ Fetch engagement metrics  │                   │
    │                    └─────────────────────────┘                   │
    └─────────────────────────────────────────────────────────────────┘
```

---

## 4. Integration Architecture

### 4.1 External API Integration Map

```
    ┌──────────────────────────────────────────────────────┐
    │                OUR PLATFORM                           │
    │                                                       │
    │  ┌──────────────────────────────────────────────┐    │
    │  │           HTTP Client (httpx)                 │    │
    │  │  ┌─────────┐ ┌──────────┐ ┌──────────────┐  │    │
    │  │  │ Retry   │ │ Rate     │ │ Response     │  │    │
    │  │  │ Logic   │ │ Limiter  │ │ Cache        │  │    │
    │  │  └─────────┘ └──────────┘ └──────────────┘  │    │
    │  └──────────────────────┬───────────────────────┘    │
    │                         │                             │
    └─────────────────────────┼─────────────────────────────┘
                              │
          ┌───────────────────┼───────────────────────────┐
          │                   │                           │
    ┌─────┴──────┐     ┌─────┴──────┐            ┌──────┴──────┐
    │ CONTENT     │     │ AI          │            │ SOCIAL       │
    │ SOURCES     │     │ GENERATION  │            │ PLATFORMS    │
    │             │     │             │            │              │
    │ HN API      │     │ Anthropic   │            │ Twitter API  │
    │ Reddit API  │     │ Claude API  │            │ v2           │
    │ Dev.to API  │     │             │            │              │
    │ JokeAPI     │     │ POST        │            │ LinkedIn API │
    │ DadJoke API │     │ /messages   │            │ (UGC Posts)  │
    │ GH Trending │     │             │            │              │
    │             │     │ Auth: API   │            │ Auth: OAuth  │
    │ Auth: Mixed │     │ key (header)│            │ 2.0 Bearer   │
    │ (None/OAuth)│     │             │            │ tokens       │
    └─────────────┘     └─────────────┘            └──────────────┘
```

### 4.2 API Authentication Summary

| API | Auth Method | Token Storage | Refresh Mechanism |
|-----|-------------|---------------|-------------------|
| Hacker News | None | N/A | N/A |
| Reddit | OAuth 2.0 (app) | .env (client_id/secret) | Auto refresh (script app type) |
| Dev.to | API Key | .env | None (static key) |
| JokeAPI | None | N/A | N/A |
| icanhazdadjoke | None (User-Agent) | N/A | N/A |
| GitHub Trending | None | N/A | N/A |
| Claude API | API Key | .env | None (static key) |
| Twitter/X | OAuth 2.0 (user) | PostgreSQL (encrypted) | Refresh token flow |
| LinkedIn | OAuth 2.0 (user) | PostgreSQL (encrypted) | Refresh token flow |

### 4.3 Error Handling Strategy for External APIs

```
    External API Call
          │
          ▼
    ┌──────────────┐
    │ Check Redis   │
    │ cache first   │──Hit──► Return cached response
    └──────┬───────┘
           │ Miss
           ▼
    ┌──────────────┐
    │ Check rate    │
    │ limiter       │──Blocked──► Wait or skip
    └──────┬───────┘
           │ Allowed
           ▼
    ┌──────────────┐
    │ Make HTTP     │
    │ request       │
    └──────┬───────┘
           │
    ┌──────┴──────────────────────────┐
    │                                  │
    ▼                                  ▼
  Success                          Error
    │                                  │
    ▼                              ┌───┴───┐
  Cache in                         ▼       ▼
  Redis                         429      5xx/timeout
    │                          Rate       Server
    ▼                          Limited    Error
  Return                          │       │
  data                            ▼       ▼
                              Wait for  Retry with
                              Retry-    exponential
                              After     backoff
                              header    (1s, 2s, 4s)
                                  │       │
                                  ▼       ▼
                              Retry   Max retries?
                                  │     │
                                  │  Yes ▼
                                  │  Log error,
                                  │  continue with
                                  │  other sources
                                  │     │
                                  └─────┘
```

---

## 5. Deployment Architecture

### 5.1 Docker Compose Architecture

```
    ┌──────────────────────────────────────────────────────────────┐
    │                    Docker Network (smm_network)               │
    │                                                               │
    │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐          │
    │  │  frontend    │  │  backend     │  │  celery      │          │
    │  │  (nginx +    │  │  (uvicorn)   │  │  worker      │          │
    │  │   React SPA) │  │              │  │              │          │
    │  │  Port: 3000  │  │  Port: 8000  │  │  (no port)   │          │
    │  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘          │
    │         │                 │                  │                 │
    │         │           ┌─────┴──────┐     ┌────┴─────┐          │
    │         │           │            │     │          │          │
    │         ▼           ▼            ▼     ▼          ▼          │
    │  ┌─────────────┐  ┌──────────┐  ┌──────────┐                │
    │  │  nginx       │  │PostgreSQL│  │  Redis    │  ┌──────────┐│
    │  │  (reverse    │  │          │  │           │  │  celery   ││
    │  │   proxy)     │  │Port: 5432│  │Port: 6379│  │  beat     ││
    │  │  Port: 80    │  │          │  │           │  │  (no port)││
    │  └─────────────┘  └──────────┘  └──────────┘  └──────────┘│
    │                                                               │
    │  Volumes:                                                     │
    │  - postgres_data:/var/lib/postgresql/data                     │
    │  - redis_data:/data                                           │
    └──────────────────────────────────────────────────────────────┘
```

### 5.2 Container Specifications

| Service | Image | Resources | Health Check |
|---------|-------|-----------|-------------|
| **postgres** | postgres:17-alpine | 256MB RAM, 1 CPU | pg_isready |
| **redis** | redis:7-alpine | 128MB RAM, 0.5 CPU | redis-cli ping |
| **backend** | python:3.11-slim + app | 512MB RAM, 1 CPU | GET /health |
| **celery-worker** | Same as backend | 512MB RAM, 1 CPU | celery inspect ping |
| **celery-worker-comments** | Same as backend | 256MB RAM, 0.5 CPU | celery inspect ping |
| **celery-beat** | Same as backend | 128MB RAM, 0.25 CPU | PID file check |
| **frontend** | node:20-alpine (build) + nginx:alpine (serve) | 128MB RAM, 0.5 CPU | GET / |

### 5.3 Environment Variables

```
# Database
DATABASE_URL=postgresql+asyncpg://user:pass@postgres:5432/smm
DATABASE_URL_SYNC=postgresql://user:pass@postgres:5432/smm  # For Celery

# Redis
REDIS_URL=redis://redis:6379/0

# Security
SECRET_KEY=<random-256-bit-key>
ENCRYPTION_KEY=<fernet-key-for-token-encryption>

# Claude API
ANTHROPIC_API_KEY=<your-key>
DEFAULT_AI_MODEL=claude-haiku-4-5-20251001

# Twitter OAuth
TWITTER_CLIENT_ID=<your-client-id>
TWITTER_CLIENT_SECRET=<your-client-secret>
TWITTER_CALLBACK_URL=http://localhost:8000/api/v1/platforms/twitter/callback

# LinkedIn OAuth
LINKEDIN_CLIENT_ID=<your-client-id>
LINKEDIN_CLIENT_SECRET=<your-client-secret>
LINKEDIN_CALLBACK_URL=http://localhost:8000/api/v1/platforms/linkedin/callback

# App
FRONTEND_URL=http://localhost:3000
BACKEND_URL=http://localhost:8000
CORS_ORIGINS=http://localhost:3000
```

---

## 6. Security Architecture

### 6.1 Security Layers

```
    Internet
       │
       ▼
    ┌──────────────────────────────────────┐
    │  Layer 1: NGINX (Reverse Proxy)      │
    │  - TLS termination (production)      │
    │  - Request size limits               │
    │  - Static file serving               │
    └──────────────────┬───────────────────┘
                       │
                       ▼
    ┌──────────────────────────────────────┐
    │  Layer 2: FastAPI Middleware          │
    │  - CORS (restrict to frontend origin)│
    │  - Rate limiting (slowapi)           │
    │  - Request validation (Pydantic)     │
    └──────────────────┬───────────────────┘
                       │
                       ▼
    ┌──────────────────────────────────────┐
    │  Layer 3: Authentication             │
    │  - JWT verification (every request)  │
    │  - Token expiry check                │
    │  - User lookup                       │
    └──────────────────┬───────────────────┘
                       │
                       ▼
    ┌──────────────────────────────────────┐
    │  Layer 4: Business Logic             │
    │  - Input sanitization                │
    │  - Authorization (user owns resource)│
    │  - Data validation                   │
    └──────────────────┬───────────────────┘
                       │
                       ▼
    ┌──────────────────────────────────────┐
    │  Layer 5: Data Layer                 │
    │  - ORM (parameterized queries)       │
    │  - Encrypted tokens (Fernet)         │
    │  - No plaintext secrets in DB        │
    └──────────────────────────────────────┘
```

### 6.2 Authentication Flow

```
    Registration:
    email + password ──► bcrypt hash ──► Store in users table

    Login:
    email + password ──► Verify bcrypt ──► Generate JWT (15min) + Refresh (7d)
                                           ──► Set httponly cookies

    API Request:
    Request + JWT cookie ──► Verify JWT ──► Extract user_id ──► Process request

    Token Refresh:
    Refresh cookie ──► Verify refresh token ──► Issue new JWT ──► Set cookie
```

### 6.3 Secret Management

| Secret | Storage | Access |
|--------|---------|--------|
| DB password | .env file | Docker Compose only |
| Redis password | .env file | Docker Compose only |
| JWT secret key | .env file | Backend only |
| Fernet encryption key | .env file | Backend only |
| Anthropic API key | .env file | Backend + Celery |
| Twitter OAuth secrets | .env file | Backend only |
| LinkedIn OAuth secrets | .env file | Backend only |
| User OAuth tokens | PostgreSQL (Fernet encrypted) | Decrypted at publish time only |

---

## 7. Scalability Considerations

### 7.1 Current Design Capacity

| Metric | Capacity | Bottleneck |
|--------|----------|-----------|
| Content sources | 6 (easily extensible) | Developer effort |
| Posts/day | ~50 (Twitter free tier limit) | API rate limits |
| Concurrent API requests | 20 (httpx connection pool) | Memory |
| Database records | Millions | PostgreSQL (robust) |
| Celery workers | 1 (sufficient for single user) | CPU |

### 7.2 Horizontal Scaling Path (Future)

If the platform evolves to multi-user SaaS:

1. **Database:** Add read replicas, connection pooling (PgBouncer)
2. **Celery:** Add more workers, use dedicated queues per task type
3. **Redis:** Redis Cluster for high availability
4. **Backend:** Multiple uvicorn workers behind load balancer
5. **Frontend:** CDN for static assets

### 7.3 Extensibility Points

| Extension | How to Add | Changes Required |
|-----------|-----------|-----------------|
| New content source | Create new client class implementing `ContentSourceBase` | 1 new file, register in aggregator |
| New social platform | Create new publisher implementing `PublisherBase` | 1 new file, register in registry, add OAuth endpoints |
| New AI model | Add model ID to config | Config change only |
| New content type | Add prompt template | 1 function in prompts.py |
| New posting format | Extend publisher interface | Publisher-specific changes |
| New profile data source | Create new profile collector implementing `ProfileCollectorBase` | 1 new file, register in profile service |

### 7.4 Caching Strategy

| Data | Cache Duration | Invalidation |
|------|---------------|-------------|
| HN top stories | 15 minutes | TTL-based |
| Reddit posts | 15 minutes | TTL-based |
| Dev.to articles | 15 minutes | TTL-based |
| Jokes | 1 hour | TTL-based |
| GitHub trending | 30 minutes | TTL-based |
| Analytics data | 1 hour | TTL-based |
| User sessions | 15 minutes (JWT) | Token expiry |
| Dashboard stats | 5 minutes | TTL-based |
