# Low-Level Design (LLD)
## AI-Powered Social Media Manager Platform

**Document Version:** 1.0
**Date:** March 20, 2026
**Author:** Engineering Team

---

## Table of Contents
1. [Database Schema](#1-database-schema)
2. [API Endpoint Specifications](#2-api-endpoint-specifications)
3. [Module Structure & Class Diagrams](#3-module-structure--class-diagrams)
4. [Sequence Diagrams](#4-sequence-diagrams)
5. [Error Handling Strategy](#5-error-handling-strategy)
6. [Caching Strategy](#6-caching-strategy)
7. [Task Queue Design](#7-task-queue-design)
8. [Frontend Component Hierarchy](#8-frontend-component-hierarchy)

---

## 1. Database Schema

### 1.1 Entity-Relationship Diagram

```
    ┌──────────────┐     1    *    ┌──────────────────┐
    │    users      │──────────────│ platform_accounts │
    │              │              │                    │
    │ id (PK)      │              │ id (PK)            │
    │ email        │              │ user_id (FK)       │
    │ password_hash│              │ platform           │
    │ full_name    │              │ access_token (enc) │
    │ is_active    │              │ refresh_token (enc)│
    │ created_at   │              │ token_expires_at   │
    │ updated_at   │              └──────────┬─────────┘
    └──────┬───────┘                         │
           │                                 │
           │ 1    *                           │
           ▼                                 │
    ┌──────────────────┐                     │
    │ generated_posts   │                     │
    │                   │                     │
    │ id (PK)           │                     │
    │ user_id (FK)      │                     │
    │ content_source_id │──┐                  │
    │   (FK, nullable)  │  │                  │
    │ target_platform   │  │                  │
    │ content_text      │  │                  │
    │ content_type      │  │                  │
    │ tone              │  │                  │
    │ hashtags[]        │  │                  │
    │ ai_model          │  │                  │
    │ prompt_used       │  │                  │
    │ token_usage (json)│  │                  │
    │ status            │  │                  │
    │ scheduled_for     │  │                  │
    │ schedule_id (FK)  │──┼──┐               │
    │ created_at        │  │  │               │
    │ updated_at        │  │  │               │
    └──────┬────────────┘  │  │               │
           │               │  │               │
           │ 1    *        │  │               │
           ▼               │  │               │
    ┌──────────────────┐   │  │               │
    │ published_posts   │   │  │               │
    │                   │   │  │               │
    │ id (PK)           │   │  │               │
    │ generated_post_id │   │  │               │
    │   (FK)            │   │  │               │
    │ platform_account  │───┼──┼───────────────┘
    │   _id (FK)        │   │  │
    │ platform_post_id  │   │  │
    │ platform_url      │   │  │
    │ published_at      │   │  │
    │ status            │   │  │
    │ error_message     │   │  │
    │ created_at        │   │  │
    └──────┬────────────┘   │  │
           │                │  │
           │ 1    *         │  │
           ▼                │  │
    ┌──────────────────┐    │  │
    │analytics_snapshots│    │  │
    │                   │    │  │
    │ id (PK)           │    │  │
    │ published_post_id │    │  │
    │   (FK)            │    │  │
    │ impressions       │    │  │
    │ likes             │    │  │
    │ comments          │    │  │
    │ shares            │    │  │
    │ clicks            │    │  │
    │ engagement_rate   │    │  │
    │ snapshot_at       │    │  │
    └──────────────────┘    │  │
                            │  │
    ┌──────────────────┐    │  │
    │ content_sources   │◄───┘  │
    │                   │       │
    │ id (PK)           │       │
    │ source_type       │       │
    │ external_id       │       │
    │ title             │       │
    │ url               │       │
    │ content           │       │
    │ author            │       │
    │ score             │       │
    │ tags[]            │       │
    │ metadata (jsonb)  │       │
    │ fetched_at        │       │
    │ created_at        │       │
    └──────────────────┘       │
                               │
    ┌──────────────────┐       │
    │ schedules         │◄──────┘
    │                   │
    │ id (PK)           │
    │ user_id (FK)      │
    │ name              │
    │ platform          │
    │ content_types[]   │
    │ cron_expression   │
    │ timezone          │
    │ auto_approve      │
    │ is_active         │
    │ created_at        │
    │ updated_at        │
    └──────────────────┘
```

### 1.2 Complete SQL Schema

```sql
-- Enable UUID generation
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- ============================================
-- TABLE: users
-- ============================================
CREATE TABLE users (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email           VARCHAR(255) UNIQUE NOT NULL,
    password_hash   VARCHAR(255) NOT NULL,
    full_name       VARCHAR(255),
    is_active       BOOLEAN DEFAULT TRUE,
    created_at      TIMESTAMPTZ DEFAULT NOW(),
    updated_at      TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_users_email ON users(email);

-- ============================================
-- TABLE: platform_accounts
-- ============================================
CREATE TABLE platform_accounts (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id             UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    platform            VARCHAR(50) NOT NULL,           -- 'twitter', 'linkedin'
    platform_user_id    VARCHAR(255),                   -- User's ID on the platform
    display_name        VARCHAR(255),                   -- User's display name on platform
    access_token        TEXT NOT NULL,                   -- Fernet-encrypted
    refresh_token       TEXT,                            -- Fernet-encrypted
    token_expires_at    TIMESTAMPTZ,
    scopes              TEXT[],                          -- OAuth scopes granted
    is_active           BOOLEAN DEFAULT TRUE,
    created_at          TIMESTAMPTZ DEFAULT NOW(),
    updated_at          TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(user_id, platform)
);

CREATE INDEX idx_platform_accounts_user ON platform_accounts(user_id);

-- ============================================
-- TABLE: content_sources
-- ============================================
CREATE TABLE content_sources (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    source_type     VARCHAR(50) NOT NULL,               -- 'hackernews', 'reddit', 'devto', 'joke', 'github'
    external_id     VARCHAR(255),                       -- ID on source platform
    title           TEXT NOT NULL,
    url             TEXT,
    content         TEXT,                                -- Summary, joke text, description
    author          VARCHAR(255),
    score           INTEGER DEFAULT 0,                  -- Upvotes, stars, reactions
    tags            TEXT[],                              -- Categories, topics
    metadata        JSONB DEFAULT '{}',                 -- Flexible source-specific fields
    fetched_at      TIMESTAMPTZ DEFAULT NOW(),
    created_at      TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(source_type, external_id)
);

CREATE INDEX idx_content_sources_type_score ON content_sources(source_type, score DESC);
CREATE INDEX idx_content_sources_fetched ON content_sources(fetched_at DESC);
CREATE INDEX idx_content_sources_type_fetched ON content_sources(source_type, fetched_at DESC);

-- ============================================
-- TABLE: schedules
-- ============================================
CREATE TABLE schedules (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id             UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    name                VARCHAR(255) NOT NULL,
    platform            VARCHAR(50) NOT NULL,           -- 'twitter', 'linkedin'
    content_types       TEXT[] NOT NULL,                 -- ['tech_insight', 'joke', 'news']
    cron_expression     VARCHAR(100) NOT NULL,           -- '0 9,17 * * 1-5'
    timezone            VARCHAR(100) DEFAULT 'UTC',
    auto_approve        BOOLEAN DEFAULT FALSE,
    is_active           BOOLEAN DEFAULT TRUE,
    created_at          TIMESTAMPTZ DEFAULT NOW(),
    updated_at          TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_schedules_user ON schedules(user_id);
CREATE INDEX idx_schedules_active ON schedules(is_active) WHERE is_active = TRUE;

-- ============================================
-- TABLE: generated_posts
-- ============================================
CREATE TABLE generated_posts (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id             UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    content_source_id   UUID REFERENCES content_sources(id) ON DELETE SET NULL,
    target_platform     VARCHAR(50) NOT NULL,           -- 'twitter', 'linkedin'
    content_text        TEXT NOT NULL,
    content_type        VARCHAR(50) NOT NULL,            -- 'tech_insight', 'joke', 'news_commentary', 'github_spotlight', 'tip'
    tone                VARCHAR(50) DEFAULT 'professional',
    hashtags            TEXT[],
    ai_model            VARCHAR(100),                   -- 'claude-haiku-4-5-20251001'
    prompt_used         TEXT,
    token_usage         JSONB,                          -- {"input_tokens": 500, "output_tokens": 200}
    status              VARCHAR(30) DEFAULT 'draft',    -- 'draft','approved','scheduled','published','rejected','failed'
    scheduled_for       TIMESTAMPTZ,
    schedule_id         UUID REFERENCES schedules(id) ON DELETE SET NULL,
    created_at          TIMESTAMPTZ DEFAULT NOW(),
    updated_at          TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_generated_posts_user_status ON generated_posts(user_id, status);
CREATE INDEX idx_generated_posts_status ON generated_posts(status);
CREATE INDEX idx_generated_posts_scheduled ON generated_posts(scheduled_for)
    WHERE status = 'scheduled';

-- ============================================
-- TABLE: published_posts
-- ============================================
CREATE TABLE published_posts (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    generated_post_id   UUID NOT NULL REFERENCES generated_posts(id) ON DELETE CASCADE,
    platform_account_id UUID NOT NULL REFERENCES platform_accounts(id) ON DELETE CASCADE,
    platform_post_id    VARCHAR(255),                   -- Tweet ID, LinkedIn post URN
    platform_url        TEXT,                           -- Direct URL to the live post
    published_at        TIMESTAMPTZ DEFAULT NOW(),
    status              VARCHAR(30) DEFAULT 'success',  -- 'success', 'failed', 'deleted'
    error_message       TEXT,
    created_at          TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_published_posts_generated ON published_posts(generated_post_id);
CREATE INDEX idx_published_posts_account ON published_posts(platform_account_id);
CREATE INDEX idx_published_posts_time ON published_posts(published_at DESC);

-- ============================================
-- TABLE: analytics_snapshots
-- ============================================
CREATE TABLE analytics_snapshots (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    published_post_id   UUID NOT NULL REFERENCES published_posts(id) ON DELETE CASCADE,
    impressions         INTEGER DEFAULT 0,
    likes               INTEGER DEFAULT 0,
    comments            INTEGER DEFAULT 0,
    shares              INTEGER DEFAULT 0,
    clicks              INTEGER DEFAULT 0,
    engagement_rate     DECIMAL(7,4),                   -- e.g., 0.0345 = 3.45%
    snapshot_at         TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_analytics_post_time ON analytics_snapshots(published_post_id, snapshot_at DESC);

-- ============================================
-- TABLE: comments (fetched from platforms)
-- ============================================
CREATE TABLE comments (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    published_post_id   UUID NOT NULL REFERENCES published_posts(id) ON DELETE CASCADE,
    platform            VARCHAR(50) NOT NULL,           -- 'twitter', 'linkedin'
    platform_comment_id VARCHAR(255) NOT NULL,          -- Comment ID on platform
    commenter_name      VARCHAR(255),                   -- Display name
    commenter_username  VARCHAR(255),                   -- @handle or profile slug
    commenter_profile_url TEXT,                         -- Link to commenter's profile
    commenter_follower_count INTEGER,                   -- Follower/connection count
    comment_text        TEXT NOT NULL,                   -- The comment content
    is_mention          BOOLEAN DEFAULT FALSE,          -- Was user @mentioned?
    is_reply_to_reply   BOOLEAN DEFAULT FALSE,          -- Thread context
    parent_comment_id   UUID REFERENCES comments(id),   -- For threaded replies
    sentiment           VARCHAR(20),                    -- 'positive', 'neutral', 'negative' (AI-classified)
    comment_type        VARCHAR(30),                    -- 'question', 'praise', 'criticism', 'general', 'mention'
    commented_at        TIMESTAMPTZ,                    -- When the comment was posted on platform
    fetched_at          TIMESTAMPTZ DEFAULT NOW(),
    created_at          TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(platform, platform_comment_id)
);

CREATE INDEX idx_comments_post ON comments(published_post_id);
CREATE INDEX idx_comments_unreplied ON comments(id) WHERE NOT EXISTS (
    SELECT 1 FROM comment_replies cr WHERE cr.comment_id = comments.id
);
CREATE INDEX idx_comments_mentions ON comments(is_mention) WHERE is_mention = TRUE;
CREATE INDEX idx_comments_platform_time ON comments(platform, commented_at DESC);

-- ============================================
-- TABLE: comment_replies (our replies to comments)
-- ============================================
CREATE TABLE comment_replies (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    comment_id          UUID NOT NULL REFERENCES comments(id) ON DELETE CASCADE,
    reply_text          TEXT NOT NULL,                   -- The reply content
    ai_suggested_text   TEXT,                           -- Original AI suggestion (before edits)
    ai_model            VARCHAR(100),                   -- Model used for generation
    token_usage         JSONB,                          -- {input_tokens, output_tokens}
    reply_mode          VARCHAR(20) NOT NULL,            -- 'manual', 'auto'
    status              VARCHAR(30) DEFAULT 'draft',    -- 'draft', 'sent', 'failed'
    platform_reply_id   VARCHAR(255),                   -- Reply ID on platform after posting
    sent_at             TIMESTAMPTZ,
    error_message       TEXT,
    created_at          TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_comment_replies_comment ON comment_replies(comment_id);
CREATE INDEX idx_comment_replies_status ON comment_replies(status);

-- ============================================
-- TABLE: linkedin_leads (profile intelligence)
-- ============================================
CREATE TABLE linkedin_leads (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id             UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    linkedin_profile_url TEXT NOT NULL,                    -- Unique identifier for dedup
    linkedin_user_id    VARCHAR(255),                      -- LinkedIn member ID if available
    full_name           VARCHAR(255),
    headline            TEXT,                               -- LinkedIn headline
    about_text          TEXT,                               -- LinkedIn about/summary section
    current_company     VARCHAR(255),
    industry            VARCHAR(255),
    location            VARCHAR(255),
    follower_count      INTEGER,
    profile_image_url   TEXT,

    -- AI-classified status
    status_type         VARCHAR(50) DEFAULT 'general',     -- 'open_to_work', 'hiring', 'looking_for_business', 'general'
    status_confidence   DECIMAL(3,2),                      -- AI confidence score (0.00-1.00)
    status_keywords     TEXT[],                             -- Keywords that triggered the classification

    -- Contact info (publicly available only)
    email               VARCHAR(255),                       -- Public email if available
    phone               VARCHAR(50),                        -- Public phone if available
    website             TEXT,                                -- Personal/business website
    twitter_handle      VARCHAR(255),                       -- Twitter/X handle if listed

    -- User-managed fields
    tags                TEXT[],                              -- User-defined tags
    notes               TEXT,                                -- Private notes
    is_starred          BOOLEAN DEFAULT FALSE,              -- Favorited by user

    -- Engagement tracking
    engagement_count    INTEGER DEFAULT 1,                  -- Total engagements with user's posts
    first_engaged_at    TIMESTAMPTZ,                        -- First engagement timestamp
    last_engaged_at     TIMESTAMPTZ,                        -- Most recent engagement

    -- Metadata
    profile_fetched_at  TIMESTAMPTZ,                        -- Last time profile data was refreshed
    created_at          TIMESTAMPTZ DEFAULT NOW(),
    updated_at          TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(user_id, linkedin_profile_url)
);

CREATE INDEX idx_leads_user ON linkedin_leads(user_id);
CREATE INDEX idx_leads_status ON linkedin_leads(user_id, status_type);
CREATE INDEX idx_leads_starred ON linkedin_leads(user_id, is_starred) WHERE is_starred = TRUE;
CREATE INDEX idx_leads_engagement ON linkedin_leads(user_id, engagement_count DESC);
CREATE INDEX idx_leads_last_engaged ON linkedin_leads(user_id, last_engaged_at DESC);

-- ============================================
-- TABLE: lead_engagements (engagement history)
-- ============================================
CREATE TABLE lead_engagements (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    lead_id             UUID NOT NULL REFERENCES linkedin_leads(id) ON DELETE CASCADE,
    published_post_id   UUID NOT NULL REFERENCES published_posts(id) ON DELETE CASCADE,
    engagement_type     VARCHAR(30) NOT NULL,               -- 'comment', 'like', 'share'
    platform_ref_id     VARCHAR(255),                       -- Comment ID or reaction ID on platform
    engaged_at          TIMESTAMPTZ,
    created_at          TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_lead_engagements_lead ON lead_engagements(lead_id, engaged_at DESC);
CREATE INDEX idx_lead_engagements_post ON lead_engagements(published_post_id);
```

### 1.3 Metadata JSONB Examples

```json
// Hacker News metadata
{
    "hn_id": 12345,
    "num_comments": 150,
    "story_type": "story",
    "domain": "techcrunch.com"
}

// Reddit metadata
{
    "subreddit": "technology",
    "permalink": "/r/technology/comments/...",
    "num_comments": 230,
    "upvote_ratio": 0.95,
    "is_self": false
}

// GitHub Trending metadata
{
    "language": "Python",
    "stars": 1500,
    "forks": 120,
    "description": "A new ML framework",
    "built_by": ["user1", "user2"]
}

// Joke metadata
{
    "category": "Programming",
    "type": "twopart",
    "setup": "Why do programmers...",
    "delivery": "Because they...",
    "safe": true
}
```

---

## 2. API Endpoint Specifications

### 2.1 Authentication Endpoints

#### POST /api/v1/auth/register
```
Request:
{
    "email": "user@example.com",
    "password": "SecureP@ss123",
    "full_name": "John Doe"
}

Response (201):
{
    "id": "uuid",
    "email": "user@example.com",
    "full_name": "John Doe",
    "created_at": "2026-03-20T10:00:00Z"
}

Errors:
- 400: Invalid email format / password too weak
- 409: Email already registered
```

#### POST /api/v1/auth/login
```
Request:
{
    "email": "user@example.com",
    "password": "SecureP@ss123"
}

Response (200):
{
    "access_token": "eyJhbG...",
    "token_type": "bearer",
    "expires_in": 900
}
Headers Set:
- Set-Cookie: access_token=eyJhbG...; HttpOnly; Secure; SameSite=Strict; Max-Age=900
- Set-Cookie: refresh_token=eyJhbG...; HttpOnly; Secure; SameSite=Strict; Path=/api/v1/auth/refresh; Max-Age=604800

Errors:
- 401: Invalid credentials
```

#### POST /api/v1/auth/refresh
```
Request: (refresh_token from cookie)

Response (200):
{
    "access_token": "eyJhbG...(new)",
    "token_type": "bearer",
    "expires_in": 900
}

Errors:
- 401: Invalid or expired refresh token
```

#### GET /api/v1/auth/me
```
Auth: Required (JWT)

Response (200):
{
    "id": "uuid",
    "email": "user@example.com",
    "full_name": "John Doe",
    "is_active": true,
    "created_at": "2026-03-20T10:00:00Z"
}
```

### 2.2 Content Endpoints

#### GET /api/v1/content
```
Auth: Required
Query Params:
- source_type: string (optional) - 'hackernews', 'reddit', 'devto', 'joke', 'github'
- sort_by: string (optional) - 'score' | 'fetched_at' (default: 'fetched_at')
- sort_order: string (optional) - 'asc' | 'desc' (default: 'desc')
- page: int (optional, default: 1)
- page_size: int (optional, default: 20, max: 100)

Response (200):
{
    "items": [
        {
            "id": "uuid",
            "source_type": "hackernews",
            "external_id": "12345",
            "title": "Show HN: A New AI Framework",
            "url": "https://example.com/article",
            "content": "Article summary...",
            "author": "pg",
            "score": 350,
            "tags": ["ai", "python"],
            "metadata": {"hn_id": 12345, "num_comments": 150},
            "fetched_at": "2026-03-20T08:00:00Z"
        }
    ],
    "total": 150,
    "page": 1,
    "page_size": 20,
    "pages": 8
}
```

#### GET /api/v1/content/{id}
```
Auth: Required

Response (200):
{
    "id": "uuid",
    "source_type": "hackernews",
    ... (full content object)
}

Errors:
- 404: Content not found
```

#### POST /api/v1/content/refresh
```
Auth: Required

Response (202):
{
    "message": "Content refresh triggered",
    "task_id": "celery-task-uuid"
}
```

#### POST /api/v1/content/{id}/generate
```
Auth: Required
Request:
{
    "target_platform": "twitter",        -- 'twitter' | 'linkedin'
    "content_type": "tech_insight",      -- 'tech_insight' | 'joke' | 'news_commentary' | 'github_spotlight' | 'tip'
    "tone": "professional"               -- 'professional' | 'casual' | 'humorous' | 'educational' (optional)
}

Response (201):
{
    "id": "uuid",
    "content_source_id": "uuid",
    "target_platform": "twitter",
    "content_text": "Generated tweet text #AI #Python",
    "content_type": "tech_insight",
    "tone": "professional",
    "hashtags": ["#AI", "#Python"],
    "ai_model": "claude-haiku-4-5-20251001",
    "token_usage": {"input_tokens": 450, "output_tokens": 85},
    "status": "draft",
    "created_at": "2026-03-20T10:05:00Z"
}

Errors:
- 404: Content not found
- 500: AI generation failed
```

### 2.3 Post Endpoints

#### GET /api/v1/posts
```
Auth: Required
Query Params:
- status: string (optional) - 'draft' | 'approved' | 'scheduled' | 'published' | 'rejected'
- target_platform: string (optional) - 'twitter' | 'linkedin'
- page: int (default: 1)
- page_size: int (default: 20)

Response (200):
{
    "items": [
        {
            "id": "uuid",
            "content_text": "Post text...",
            "target_platform": "twitter",
            "content_type": "tech_insight",
            "status": "draft",
            "hashtags": ["#AI"],
            "scheduled_for": null,
            "content_source": {
                "id": "uuid",
                "title": "Source article title",
                "url": "https://...",
                "source_type": "hackernews"
            },
            "published_post": null,
            "created_at": "2026-03-20T10:05:00Z"
        }
    ],
    "total": 25,
    "page": 1,
    "page_size": 20,
    "pages": 2
}
```

#### PUT /api/v1/posts/{id}
```
Auth: Required
Request:
{
    "content_text": "Updated post text",  -- optional
    "hashtags": ["#AI", "#ML"],           -- optional
    "tone": "casual"                      -- optional
}

Response (200): Updated post object

Errors:
- 404: Post not found
- 403: Post not owned by user
- 400: Post is already published (cannot edit)
```

#### POST /api/v1/posts/{id}/approve
```
Auth: Required

Response (200):
{
    "id": "uuid",
    "status": "approved",
    ...
}

Errors:
- 400: Post is not in 'draft' status
```

#### POST /api/v1/posts/{id}/reject
```
Auth: Required
Request (optional):
{
    "reason": "Content doesn't match brand voice"
}

Response (200):
{
    "id": "uuid",
    "status": "rejected",
    ...
}
```

#### POST /api/v1/posts/{id}/publish
```
Auth: Required

Response (200):
{
    "id": "uuid",
    "status": "published",
    "published_post": {
        "id": "uuid",
        "platform_post_id": "1234567890",
        "platform_url": "https://twitter.com/user/status/1234567890",
        "published_at": "2026-03-20T10:10:00Z",
        "status": "success"
    }
}

Errors:
- 400: Post not in 'approved' status
- 400: No platform account connected for target platform
- 502: Platform API error (with error details)
```

#### POST /api/v1/posts/{id}/schedule
```
Auth: Required
Request:
{
    "scheduled_for": "2026-03-21T09:00:00+05:30"
}

Response (200):
{
    "id": "uuid",
    "status": "scheduled",
    "scheduled_for": "2026-03-21T03:30:00Z"
}

Errors:
- 400: scheduled_for is in the past
- 400: Post not in 'approved' status
```

#### POST /api/v1/posts/generate-batch
```
Auth: Required
Request:
{
    "content_source_ids": ["uuid1", "uuid2", "uuid3"],
    "target_platform": "twitter",
    "content_type": "tech_insight",
    "tone": "professional"
}

Response (202):
{
    "message": "Batch generation started",
    "task_id": "celery-task-uuid",
    "count": 3
}
```

### 2.4 Platform Endpoints

#### GET /api/v1/platforms
```
Auth: Required

Response (200):
{
    "platforms": [
        {
            "id": "uuid",
            "platform": "twitter",
            "display_name": "@johndoe",
            "is_active": true,
            "token_expires_at": "2026-04-20T10:00:00Z",
            "created_at": "2026-03-15T10:00:00Z"
        }
    ]
}
```

#### GET /api/v1/platforms/twitter/authorize
```
Auth: Required

Response (302): Redirect to Twitter OAuth authorization URL
Sets session cookie with state + PKCE verifier
```

#### GET /api/v1/platforms/twitter/callback
```
Query Params: code, state

Response (302): Redirect to frontend /settings?connected=twitter

Side effects:
- Exchange code for tokens
- Encrypt tokens
- Store in platform_accounts
- Fetch user profile info
```

#### GET /api/v1/platforms/linkedin/authorize
```
Auth: Required
Response (302): Redirect to LinkedIn OAuth authorization URL
```

#### GET /api/v1/platforms/linkedin/callback
```
Query Params: code, state
Response (302): Redirect to frontend /settings?connected=linkedin
```

#### DELETE /api/v1/platforms/{id}
```
Auth: Required
Response (204): No content

Side effects:
- Delete platform account and encrypted tokens
```

### 2.5 Schedule Endpoints

#### GET /api/v1/schedules
```
Auth: Required

Response (200):
{
    "items": [
        {
            "id": "uuid",
            "name": "Weekday Morning Tech Posts",
            "platform": "linkedin",
            "content_types": ["tech_insight", "news_commentary"],
            "cron_expression": "0 9 * * 1-5",
            "timezone": "Asia/Kolkata",
            "auto_approve": false,
            "is_active": true,
            "created_at": "2026-03-18T10:00:00Z"
        }
    ]
}
```

#### POST /api/v1/schedules
```
Auth: Required
Request:
{
    "name": "Weekday Morning Tech Posts",
    "platform": "linkedin",
    "content_types": ["tech_insight", "news_commentary"],
    "cron_expression": "0 9 * * 1-5",
    "timezone": "Asia/Kolkata",
    "auto_approve": false
}

Response (201): Schedule object

Errors:
- 400: Invalid cron expression
- 400: Invalid timezone
```

#### PUT /api/v1/schedules/{id}
```
Auth: Required
Request: Any schedule fields to update

Response (200): Updated schedule object
```

#### DELETE /api/v1/schedules/{id}
```
Auth: Required
Response (204): No content
```

### 2.6 Analytics Endpoints

#### GET /api/v1/analytics/overview
```
Auth: Required
Query Params:
- days: int (default: 7) - 7, 30, 90

Response (200):
{
    "period_days": 7,
    "total_posts": 15,
    "total_impressions": 12500,
    "total_likes": 340,
    "total_comments": 45,
    "total_shares": 28,
    "avg_engagement_rate": 0.0328,
    "platform_breakdown": {
        "twitter": {"posts": 8, "impressions": 5200, "engagement_rate": 0.0285},
        "linkedin": {"posts": 7, "impressions": 7300, "engagement_rate": 0.0371}
    },
    "top_posts": [
        {
            "id": "uuid",
            "content_text": "Post text preview...",
            "platform": "linkedin",
            "impressions": 2100,
            "engagement_rate": 0.0512,
            "published_at": "2026-03-18T09:00:00Z"
        }
    ]
}
```

#### GET /api/v1/analytics/posts/{published_post_id}
```
Auth: Required

Response (200):
{
    "post": { ... published post details ... },
    "snapshots": [
        {
            "impressions": 500,
            "likes": 15,
            "comments": 3,
            "shares": 2,
            "engagement_rate": 0.04,
            "snapshot_at": "2026-03-20T06:00:00Z"
        },
        {
            "impressions": 1200,
            "likes": 35,
            "comments": 8,
            "shares": 5,
            "engagement_rate": 0.04,
            "snapshot_at": "2026-03-20T12:00:00Z"
        }
    ]
}
```

### 2.7 Comment Endpoints

#### GET /api/v1/comments
```
Auth: Required
Query Params:
- status: string (optional) - 'unreplied' | 'replied' | 'all' (default: 'unreplied')
- is_mention: boolean (optional) - filter mentions only
- platform: string (optional) - 'linkedin'
- page: int (default: 1)
- page_size: int (default: 20)

Response (200):
{
    "items": [
        {
            "id": "uuid",
            "published_post_id": "uuid",
            "platform": "linkedin",
            "commenter_name": "Jane Smith",
            "commenter_username": "janesmith",
            "commenter_profile_url": "https://linkedin.com/in/janesmith",
            "commenter_follower_count": 5200,
            "comment_text": "Great insights! How do you see AI affecting...",
            "is_mention": false,
            "sentiment": "positive",
            "comment_type": "question",
            "commented_at": "2026-03-20T11:30:00Z",
            "ai_suggested_reply": "Thank you, Jane! AI is transforming...",
            "reply": null,
            "original_post_preview": "My latest post about AI trends..."
        }
    ],
    "total": 12,
    "page": 1
}
```

#### GET /api/v1/posts/{post_id}/comments
```
Auth: Required
Response (200): Same structure as above, filtered to specific post
```

#### POST /api/v1/comments/{id}/reply
```
Auth: Required
Request:
{
    "reply_text": "Thank you, Jane! AI is indeed transforming..."
}

Response (200):
{
    "id": "uuid",
    "comment_id": "uuid",
    "reply_text": "Thank you, Jane!...",
    "reply_mode": "manual",
    "status": "sent",
    "platform_reply_id": "linkedin-reply-123",
    "sent_at": "2026-03-20T12:00:00Z"
}

Errors:
- 404: Comment not found
- 400: Already replied
- 502: Platform API error
```

#### POST /api/v1/comments/{id}/generate-reply
```
Auth: Required
Request (optional):
{
    "tone": "professional"    -- override tone
}

Response (200):
{
    "suggested_reply": "Thank you for your thoughtful question, Jane!...",
    "comment_type": "question",
    "sentiment": "positive",
    "token_usage": {"input_tokens": 350, "output_tokens": 120}
}
```

#### POST /api/v1/comments/{id}/dismiss
```
Auth: Required
Response (200): { "status": "dismissed" }
```

#### PUT /api/v1/comments/settings
```
Auth: Required
Request:
{
    "auto_reply_enabled": true,
    "auto_reply_platforms": ["linkedin"],
    "auto_reply_filters": ["questions", "positive"],
    "auto_reply_rate_limit": 10,
    "comment_poll_interval_minutes": 15
}

Response (200): Updated settings
```

### 2.8 Lead Intelligence Endpoints

#### GET /api/v1/leads
```
Auth: Required
Query Params:
- status_type: string (optional) - 'open_to_work' | 'hiring' | 'looking_for_business' | 'general'
- industry: string (optional) - filter by industry
- has_email: boolean (optional) - filter leads with email
- has_phone: boolean (optional) - filter leads with phone
- is_starred: boolean (optional) - filter starred leads
- tags: string (optional) - comma-separated tag filter
- search: string (optional) - search name, headline, company
- sort_by: string (optional) - 'engagement_count' | 'last_engaged_at' | 'full_name' (default: 'last_engaged_at')
- sort_order: string (optional) - 'asc' | 'desc' (default: 'desc')
- page: int (default: 1)
- page_size: int (default: 20, max: 100)

Response (200):
{
    "items": [
        {
            "id": "uuid",
            "full_name": "Jane Smith",
            "headline": "Senior Product Manager | Open to new opportunities",
            "current_company": "TechCorp Inc.",
            "industry": "Technology",
            "location": "San Francisco, CA",
            "linkedin_profile_url": "https://linkedin.com/in/janesmith",
            "follower_count": 5200,
            "status_type": "open_to_work",
            "status_confidence": 0.92,
            "email": "jane@example.com",
            "phone": null,
            "website": "https://janesmith.com",
            "twitter_handle": "@janesmith",
            "tags": ["Potential Client", "Tech"],
            "notes": null,
            "is_starred": true,
            "engagement_count": 5,
            "first_engaged_at": "2026-03-10T09:00:00Z",
            "last_engaged_at": "2026-03-20T14:30:00Z"
        }
    ],
    "total": 85,
    "page": 1,
    "page_size": 20,
    "pages": 5
}
```

#### GET /api/v1/leads/{id}
```
Auth: Required

Response (200):
{
    "id": "uuid",
    "full_name": "Jane Smith",
    "headline": "Senior Product Manager | Open to new opportunities",
    "about_text": "Passionate about building products that...",
    "current_company": "TechCorp Inc.",
    "industry": "Technology",
    "location": "San Francisco, CA",
    "linkedin_profile_url": "https://linkedin.com/in/janesmith",
    "follower_count": 5200,
    "profile_image_url": "https://...",
    "status_type": "open_to_work",
    "status_confidence": 0.92,
    "status_keywords": ["Open to new opportunities"],
    "email": "jane@example.com",
    "phone": null,
    "website": "https://janesmith.com",
    "twitter_handle": "@janesmith",
    "tags": ["Potential Client", "Tech"],
    "notes": "Met at conference, interested in our services",
    "is_starred": true,
    "engagement_count": 5,
    "first_engaged_at": "2026-03-10T09:00:00Z",
    "last_engaged_at": "2026-03-20T14:30:00Z",
    "engagements": [
        {
            "id": "uuid",
            "engagement_type": "comment",
            "published_post_preview": "My thoughts on AI trends...",
            "engaged_at": "2026-03-20T14:30:00Z"
        },
        {
            "id": "uuid",
            "engagement_type": "like",
            "published_post_preview": "5 tips for product managers...",
            "engaged_at": "2026-03-18T10:15:00Z"
        }
    ]
}

Errors:
- 404: Lead not found
```

#### PUT /api/v1/leads/{id}
```
Auth: Required
Request:
{
    "tags": ["Potential Client", "Follow Up"],   -- optional
    "notes": "Discussed partnership options",     -- optional
    "is_starred": true                            -- optional
}

Response (200): Updated lead object

Errors:
- 404: Lead not found
- 403: Lead not owned by user
```

#### DELETE /api/v1/leads/{id}
```
Auth: Required
Response (204): No content

Side effects:
- Deletes lead, all engagement history, contact info
- Cascade delete ensures complete data removal
```

#### POST /api/v1/leads/export
```
Auth: Required
Request:
{
    "columns": ["full_name", "headline", "company", "status_type", "email", "phone", "website", "tags", "notes", "last_engaged_at"],
    "filters": {
        "status_type": "hiring",
        "has_email": true
    }
}

Response (200): CSV file download
Content-Type: text/csv
Content-Disposition: attachment; filename="leads_export_2026-03-20.csv"
```

#### GET /api/v1/leads/stats
```
Auth: Required

Response (200):
{
    "total_leads": 85,
    "by_status": {
        "open_to_work": 23,
        "hiring": 15,
        "looking_for_business": 8,
        "general": 39
    },
    "with_email": 34,
    "with_phone": 12,
    "new_this_week": 11,
    "hot_leads": 5
}
```

### 2.9 Dashboard Endpoint

#### GET /api/v1/dashboard
```
Auth: Required

Response (200):
{
    "stats": {
        "posts_this_week": 12,
        "avg_engagement_rate": 0.0328,
        "pending_reviews": 5,
        "upcoming_scheduled": 3
    },
    "recent_activity": [
        {
            "type": "published",
            "message": "Posted to Twitter: 'Check out this...'",
            "timestamp": "2026-03-20T09:00:00Z",
            "post_id": "uuid"
        },
        {
            "type": "content_fetched",
            "message": "Fetched 45 new items from 6 sources",
            "timestamp": "2026-03-20T08:00:00Z"
        }
    ],
    "upcoming_posts": [
        {
            "id": "uuid",
            "content_text": "Preview text...",
            "target_platform": "linkedin",
            "scheduled_for": "2026-03-20T17:00:00Z"
        }
    ],
    "source_health": {
        "hackernews": {"status": "healthy", "last_fetch": "2026-03-20T08:00:00Z", "items_count": 30},
        "reddit": {"status": "healthy", "last_fetch": "2026-03-20T08:00:00Z", "items_count": 20},
        "devto": {"status": "healthy", "last_fetch": "2026-03-20T08:00:00Z", "items_count": 15},
        "joke": {"status": "healthy", "last_fetch": "2026-03-20T08:00:00Z", "items_count": 10},
        "github": {"status": "error", "last_fetch": "2026-03-20T06:00:00Z", "error": "API timeout"}
    }
}
```

---

## 3. Module Structure & Class Diagrams

### 3.1 Content Research Module

```
ContentSourceBase (ABC)
├── source_type: str (abstract property)
├── fetch_trending(limit: int) -> List[ContentItem] (abstract)
└── _http_client: ResilientHTTPClient

HackerNewsClient(ContentSourceBase)
├── source_type = "hackernews"
├── BASE_URL = "https://hacker-news.firebaseio.com/v0"
├── fetch_trending(limit=30) -> List[ContentItem]
│   ├── GET /topstories.json
│   ├── GET /item/{id}.json (for each story)
│   └── Map to ContentItem
└── _get_story_details(story_id: int) -> dict

RedditClient(ContentSourceBase)
├── source_type = "reddit"
├── subreddits: List[str] = ["technology", "programming", "webdev"]
├── fetch_trending(limit=20) -> List[ContentItem]
│   ├── OAuth token management
│   ├── GET /r/{subreddit}/hot.json
│   └── Map to ContentItem
└── _authenticate() -> str (access_token)

DevToClient(ContentSourceBase)
├── source_type = "devto"
├── fetch_trending(limit=20) -> List[ContentItem]
│   ├── GET /articles?top=1 (past day)
│   └── Map to ContentItem

JokeClient(ContentSourceBase)
├── source_type = "joke"
├── fetch_trending(limit=10) -> List[ContentItem]
│   ├── GET JokeAPI /joke/Any?amount=5
│   ├── GET icanhazdadjoke /
│   └── Map jokes to ContentItem

GitHubTrendingClient(ContentSourceBase)
├── source_type = "github"
├── fetch_trending(limit=20) -> List[ContentItem]
│   ├── GET /repositories?since=daily
│   └── Map repos to ContentItem

ContentAggregator
├── sources: List[ContentSourceBase]
├── cache: RedisCache
├── db: AsyncSession
├── fetch_all(limit_per_source: int) -> AggregationResult
│   ├── Run all sources concurrently (asyncio.gather)
│   ├── Handle individual source failures
│   └── Bulk upsert results
└── _bulk_upsert(items: List[ContentItem]) -> int
```

### 3.2 AI Generator Module

```
AnthropicClientWrapper
├── client: anthropic.Anthropic
├── default_model: str
├── generate(prompt: str, max_tokens: int, model: str = None) -> GenerationResult
│   ├── Call messages.create()
│   ├── Track token usage
│   └── Return text + metadata

PromptTemplates
├── twitter_tech_insight(source: ContentSource) -> str
├── twitter_joke(source: ContentSource) -> str
├── twitter_github_spotlight(source: ContentSource) -> str
├── twitter_news_commentary(source: ContentSource) -> str
├── twitter_tip(source: ContentSource) -> str
├── linkedin_tech_insight(source: ContentSource) -> str
├── linkedin_joke(source: ContentSource) -> str
├── linkedin_news_commentary(source: ContentSource) -> str
├── linkedin_github_spotlight(source: ContentSource) -> str
├── linkedin_tip(source: ContentSource) -> str
└── get_prompt(platform: str, content_type: str, source: ContentSource, tone: str) -> str

PostGenerator
├── ai_client: AnthropicClientWrapper
├── prompts: PromptTemplates
├── db: AsyncSession
├── generate_post(content_source_id: UUID, platform: str, content_type: str, tone: str, user_id: UUID) -> GeneratedPost
│   ├── Load content source from DB
│   ├── Build prompt from templates
│   ├── Call AI client
│   ├── Post-process (validate length, extract hashtags)
│   └── Save generated_post (status='draft')
├── regenerate_post(post_id: UUID) -> GeneratedPost
└── _validate_platform_limits(text: str, platform: str) -> str
```

### 3.3 Publisher Module

```
PublishResult
├── success: bool
├── platform_post_id: str | None
├── platform_url: str | None
├── error_message: str | None

PostMetrics
├── impressions: int
├── likes: int
├── comments: int
├── shares: int
├── clicks: int

PublisherBase (ABC)
├── publish(text: str, hashtags: List[str], account: PlatformAccount) -> PublishResult (abstract)
├── delete(platform_post_id: str, account: PlatformAccount) -> bool (abstract)
├── get_metrics(platform_post_id: str, account: PlatformAccount) -> PostMetrics (abstract)
└── _decrypt_token(encrypted_token: str) -> str

TwitterPublisher(PublisherBase)
├── API_URL = "https://api.twitter.com/2"
├── publish(text, hashtags, account) -> PublishResult
│   ├── Format tweet (text + hashtags within 280 chars)
│   ├── POST /tweets
│   └── Parse response for tweet ID
├── delete(platform_post_id, account) -> bool
│   └── DELETE /tweets/{id}
├── get_metrics(platform_post_id, account) -> PostMetrics
│   └── GET /tweets/{id}?tweet.fields=public_metrics (Basic+ only)
└── _build_oauth_header(method, url, params) -> dict

LinkedInPublisher(PublisherBase)
├── API_URL = "https://api.linkedin.com/rest"
├── publish(text, hashtags, account) -> PublishResult
│   ├── Format post (text + hashtags)
│   ├── POST /posts
│   └── Parse response for post URN
├── delete(platform_post_id, account) -> bool
│   └── DELETE /posts/{urn}
└── get_metrics(platform_post_id, account) -> PostMetrics
    └── GET post analytics endpoint

PublisherRegistry
├── _publishers: Dict[str, Type[PublisherBase]]
├── register(platform: str, publisher_class: Type[PublisherBase]) -> None
├── get(platform: str) -> PublisherBase
└── list_platforms() -> List[str]
```

### 3.4 Comment Management Module

```
CommentFetcher
├── fetch_comments(published_post: PublishedPost) -> List[Comment]
│   ├── LinkedIn: GET /socialActions/{post_urn}/comments
│   ├── Twitter: GET /2/tweets/{id}/... (Basic tier required, deferred)
│   └── Deduplicate by (platform, platform_comment_id)
└── fetch_mentions(account: PlatformAccount) -> List[Comment]
    └── LinkedIn: GET /socialActions mentioning user

CommentClassifier
├── ai_client: AnthropicClientWrapper
├── classify(comment: Comment, original_post: str) -> ClassificationResult
│   ├── Step 1: Call Claude to classify comment
│   │   ├── sentiment: 'positive' | 'neutral' | 'negative'
│   │   └── comment_type: 'question' | 'praise' | 'criticism' | 'general' | 'mention'
│   └── Return classification result
└── CLASSIFICATION_PROMPT: str

CommentReplyGenerator
├── ai_client: AnthropicClientWrapper
├── prompts: Dict[str, str]  # Per comment_type
├── generate_reply(comment: Comment, classification: ClassificationResult, original_post: str, tone: str) -> str
│   ├── Select prompt template based on comment_type
│   ├── Build prompt with comment text, original post context, tone
│   ├── Call Claude to generate reply
│   └── Validate reply (length, tone, no hallucination)
├── REPLY_PROMPTS: Dict[str, str]
│   ├── "question" -> "You are replying to a question on {{platform}}..."
│   ├── "praise" -> "You are replying to a positive comment..."
│   ├── "criticism" -> "You are replying to constructive criticism..."
│   ├── "general" -> "You are replying to a general comment..."
│   └── "mention" -> "Someone mentioned you in a comment..."
└── _validate_reply(reply: str, platform: str) -> str

AutoReplyProcessor
├── settings: CommentSettings (from user preferences)
├── classifier: CommentClassifier
├── generator: CommentReplyGenerator
├── publisher: PublisherBase
├── process_auto_replies(comments: List[Comment]) -> AutoReplyResult
│   ├── Filter comments by auto_reply_filters
│   ├── Check rate limit (max N replies/hour)
│   ├── For each eligible comment:
│   │   ├── Classify comment
│   │   ├── Generate reply
│   │   ├── Post reply to platform
│   │   └── Save reply record
│   └── Return summary (replied, skipped, failed)
└── _check_rate_limit() -> bool
```

### 3.5 Profile Intelligence Module

```
LinkedInProfileCollector
├── http_client: ResilientHTTPClient
├── collect_engager_profiles(published_post: PublishedPost, account: PlatformAccount) -> List[RawProfile]
│   ├── Fetch commenters via LinkedIn API
│   ├── Fetch likers via LinkedIn API (if available)
│   ├── For each engager: GET /people/{id} or basic profile data
│   └── Return list of raw profile data
├── fetch_profile_details(profile_url: str, account: PlatformAccount) -> ProfileDetails
│   ├── GET LinkedIn profile by URL/ID
│   ├── Extract: name, headline, about, company, industry, location, followers
│   └── Extract: public contact info (email, phone, website, twitter)
└── _deduplicate(profiles: List[RawProfile], existing: Set[str]) -> List[RawProfile]

LeadStatusClassifier
├── ai_client: AnthropicClientWrapper
├── classify(headline: str, about_text: str) -> StatusClassification
│   ├── Build prompt with headline + about text
│   ├── Call Claude to classify:
│   │   ├── status_type: 'open_to_work' | 'hiring' | 'looking_for_business' | 'general'
│   │   ├── confidence: float (0.0-1.0)
│   │   └── keywords: List[str] (phrases that triggered classification)
│   └── Return classification result
├── CLASSIFICATION_PROMPT: str
│   └── "Analyze this LinkedIn profile and classify the person's professional status..."
└── batch_classify(profiles: List[RawProfile]) -> List[StatusClassification]
    └── Classify multiple profiles efficiently (batch AI calls)

LeadManager
├── db: AsyncSession
├── collector: LinkedInProfileCollector
├── classifier: LeadStatusClassifier
├── process_new_engagers(published_post_id: UUID, user_id: UUID) -> ProcessResult
│   ├── Collect engager profiles from LinkedIn
│   ├── Deduplicate against existing leads
│   ├── For new profiles:
│   │   ├── Fetch detailed profile data
│   │   ├── Classify status via AI
│   │   ├── Extract contact info
│   │   └── Create lead record
│   ├── For existing profiles:
│   │   ├── Increment engagement_count
│   │   ├── Update last_engaged_at
│   │   └── Re-classify if profile data changed
│   └── Return summary (new_leads, updated, errors)
├── export_leads(user_id: UUID, columns: List[str], filters: dict) -> bytes (CSV)
│   ├── Query leads with filters
│   ├── Format as CSV with selected columns
│   └── Return CSV bytes
└── delete_lead(lead_id: UUID, user_id: UUID) -> bool
    └── Cascade delete lead + engagements
```

### 3.6 Utility Classes

```
ResilientHTTPClient
├── client: httpx.AsyncClient
├── retry_config: RetryConfig
├── get(url, **kwargs) -> httpx.Response
├── post(url, **kwargs) -> httpx.Response
└── _retry_with_backoff(method, *args, **kwargs) -> httpx.Response

RedisRateLimiter
├── redis: Redis
├── key: str
├── max_tokens: int
├── refill_rate: float
├── acquire() -> bool
└── reset() -> None

RedisCache
├── redis: Redis
├── get(key: str) -> Optional[str]
├── set(key: str, value: str, ttl: int) -> None
├── delete(key: str) -> None
└── get_or_set(key: str, factory: Callable, ttl: int) -> str

SecurityUtils
├── hash_password(password: str) -> str
├── verify_password(password: str, hash: str) -> bool
├── create_access_token(data: dict, expires_delta: timedelta) -> str
├── create_refresh_token(data: dict) -> str
├── decode_token(token: str) -> dict
├── encrypt_token(plaintext: str) -> str
└── decrypt_token(ciphertext: str) -> str
```

---

## 4. Sequence Diagrams

### 4.1 Content Fetch Sequence

```
    Celery Beat        Aggregator       HN Client       Redis        PostgreSQL
        │                  │               │              │              │
        │  trigger task    │               │              │              │
        │─────────────────►│               │              │              │
        │                  │  check cache  │              │              │
        │                  │──────────────────────────────►│              │
        │                  │  cache miss   │              │              │
        │                  │◄──────────────────────────────│              │
        │                  │  fetch top    │              │              │
        │                  │──────────────►│              │              │
        │                  │               │  GET /top    │              │
        │                  │               │──────────►   │              │
        │                  │               │  [ids]   ◄── │              │
        │                  │               │  GET /item   │              │
        │                  │               │──────────►   │              │
        │                  │  [stories]    │              │              │
        │                  │◄──────────────│              │              │
        │                  │  set cache    │              │              │
        │                  │──────────────────────────────►│              │
        │                  │               │              │              │
        │                  │  (repeat for Reddit, Dev.to, Jokes, GitHub) │
        │                  │               │              │              │
        │                  │  bulk upsert  │              │              │
        │                  │──────────────────────────────────────────────►│
        │                  │  result count │              │              │
        │                  │◄──────────────────────────────────────────────│
        │  task complete   │               │              │              │
        │◄─────────────────│               │              │              │
```

### 4.2 Post Generation Sequence

```
    User          Frontend       Backend API     Generator     Claude API    PostgreSQL
      │               │              │              │              │             │
      │ click         │              │              │              │             │
      │ "Generate"    │              │              │              │             │
      │──────────────►│              │              │              │             │
      │               │ POST         │              │              │             │
      │               │ /content/    │              │              │             │
      │               │ {id}/generate│              │              │             │
      │               │─────────────►│              │              │             │
      │               │              │ load source  │              │             │
      │               │              │──────────────────────────────────────────►│
      │               │              │ source data  │              │             │
      │               │              │◄──────────────────────────────────────────│
      │               │              │ generate     │              │             │
      │               │              │─────────────►│              │             │
      │               │              │              │ build prompt │             │
      │               │              │              │──────┐       │             │
      │               │              │              │◄─────┘       │             │
      │               │              │              │ POST         │             │
      │               │              │              │ /messages    │             │
      │               │              │              │─────────────►│             │
      │               │              │              │ generated    │             │
      │               │              │              │ text         │             │
      │               │              │              │◄─────────────│             │
      │               │              │              │ validate     │             │
      │               │              │              │──────┐       │             │
      │               │              │              │◄─────┘       │             │
      │               │              │ post object  │              │             │
      │               │              │◄─────────────│              │             │
      │               │              │ save draft   │              │             │
      │               │              │──────────────────────────────────────────►│
      │               │ 201 + post   │              │              │             │
      │               │◄─────────────│              │              │             │
      │ show draft    │              │              │              │             │
      │◄──────────────│              │              │              │             │
```

### 4.3 OAuth Connection Sequence

```
    User        Frontend       Backend        Twitter/LinkedIn    PostgreSQL
      │             │              │                  │                │
      │ click       │              │                  │                │
      │ "Connect"   │              │                  │                │
      │────────────►│              │                  │                │
      │             │ GET          │                  │                │
      │             │ /platforms/  │                  │                │
      │             │ twitter/     │                  │                │
      │             │ authorize    │                  │                │
      │             │─────────────►│                  │                │
      │             │              │ generate state   │                │
      │             │              │ + PKCE verifier  │                │
      │             │              │ store in Redis   │                │
      │             │              │──────┐           │                │
      │             │              │◄─────┘           │                │
      │             │ 302 redirect │                  │                │
      │             │◄─────────────│                  │                │
      │ redirect    │              │                  │                │
      │◄────────────│              │                  │                │
      │             │              │                  │                │
      │ authorize   │              │                  │                │
      │ on platform │              │                  │                │
      │────────────────────────────────────────────►  │                │
      │             │              │                  │                │
      │ callback    │              │                  │                │
      │ with code   │              │                  │                │
      │──────────────────────────►│                   │                │
      │             │              │ verify state     │                │
      │             │              │ exchange code    │                │
      │             │              │─────────────────►│                │
      │             │              │ access_token     │                │
      │             │              │ refresh_token    │                │
      │             │              │◄─────────────────│                │
      │             │              │ encrypt tokens   │                │
      │             │              │ get user info    │                │
      │             │              │─────────────────►│                │
      │             │              │ user profile     │                │
      │             │              │◄─────────────────│                │
      │             │              │ store account    │                │
      │             │              │────────────────────────────────►  │
      │             │ 302 redirect │                  │                │
      │             │ /settings    │                  │                │
      │◄──────────────────────────│                   │                │
      │ show        │              │                  │                │
      │ connected   │              │                  │                │
      │────────────►│              │                  │                │
```

### 4.4 Scheduled Publishing Sequence

```
    Celery Beat     Publishing Task    PostgreSQL    Publisher Registry    Twitter/LinkedIn
        │                 │                │                │                    │
        │ every 1 min     │                │                │                    │
        │────────────────►│                │                │                    │
        │                 │ query due      │                │                    │
        │                 │ posts          │                │                    │
        │                 │───────────────►│                │                    │
        │                 │ scheduled      │                │                    │
        │                 │ posts where    │                │                    │
        │                 │ scheduled_for  │                │                    │
        │                 │ <= NOW()       │                │                    │
        │                 │◄───────────────│                │                    │
        │                 │                │                │                    │
        │                 │ for each post: │                │                    │
        │                 │                │                │                    │
        │                 │ get publisher  │                │                    │
        │                 │───────────────────────────────►│                    │
        │                 │ publisher      │                │                    │
        │                 │◄───────────────────────────────│                    │
        │                 │                │                │                    │
        │                 │ load account   │                │                    │
        │                 │───────────────►│                │                    │
        │                 │ account (enc)  │                │                    │
        │                 │◄───────────────│                │                    │
        │                 │                │                │                    │
        │                 │ decrypt token  │                │                    │
        │                 │──────┐         │                │                    │
        │                 │◄─────┘         │                │                    │
        │                 │                │                │                    │
        │                 │ publish        │                │                    │
        │                 │──────────────────────────────────────────────────►  │
        │                 │ result         │                │                    │
        │                 │◄──────────────────────────────────────────────────  │
        │                 │                │                │                    │
        │                 │ save result    │                │                    │
        │                 │ update status  │                │                    │
        │                 │───────────────►│                │                    │
        │                 │                │                │                    │
        │ task complete   │                │                │                    │
        │◄────────────────│                │                │                    │
```

---

## 5. Error Handling Strategy

### 5.1 Error Categories

| Category | HTTP Status | Handling |
|----------|-------------|----------|
| Validation Error | 400 | Return field-level error messages |
| Authentication Error | 401 | Return "Invalid credentials" or "Token expired" |
| Authorization Error | 403 | Return "Not authorized to access this resource" |
| Not Found | 404 | Return "Resource not found" |
| Conflict | 409 | Return "Resource already exists" (e.g., duplicate email) |
| Rate Limited | 429 | Return "Too many requests, try again in X seconds" |
| External API Error | 502 | Return "Platform API error" with details |
| Internal Error | 500 | Log full traceback, return generic error |

### 5.2 Error Response Format

```json
{
    "error": {
        "code": "VALIDATION_ERROR",
        "message": "Invalid input data",
        "details": [
            {
                "field": "content_text",
                "message": "Content exceeds 280 character limit for Twitter"
            }
        ]
    }
}
```

### 5.3 Error Codes

```python
class ErrorCode(str, Enum):
    VALIDATION_ERROR = "VALIDATION_ERROR"
    AUTH_INVALID_CREDENTIALS = "AUTH_INVALID_CREDENTIALS"
    AUTH_TOKEN_EXPIRED = "AUTH_TOKEN_EXPIRED"
    AUTH_TOKEN_INVALID = "AUTH_TOKEN_INVALID"
    RESOURCE_NOT_FOUND = "RESOURCE_NOT_FOUND"
    RESOURCE_CONFLICT = "RESOURCE_CONFLICT"
    PLATFORM_NOT_CONNECTED = "PLATFORM_NOT_CONNECTED"
    PLATFORM_TOKEN_EXPIRED = "PLATFORM_TOKEN_EXPIRED"
    PLATFORM_API_ERROR = "PLATFORM_API_ERROR"
    PLATFORM_RATE_LIMITED = "PLATFORM_RATE_LIMITED"
    AI_GENERATION_FAILED = "AI_GENERATION_FAILED"
    INVALID_POST_STATUS = "INVALID_POST_STATUS"
    RATE_LIMITED = "RATE_LIMITED"
    PROFILE_FETCH_FAILED = "PROFILE_FETCH_FAILED"
    LEAD_NOT_FOUND = "LEAD_NOT_FOUND"
    INTERNAL_ERROR = "INTERNAL_ERROR"
```

### 5.4 External API Error Handling

```python
# Retry policy per service
RETRY_POLICIES = {
    "hackernews": RetryPolicy(max_retries=3, backoff=1.0, retry_on=[429, 500, 502, 503]),
    "reddit":     RetryPolicy(max_retries=3, backoff=2.0, retry_on=[429, 500, 502, 503]),
    "devto":      RetryPolicy(max_retries=2, backoff=1.0, retry_on=[429, 500, 502, 503]),
    "jokeapi":    RetryPolicy(max_retries=2, backoff=0.5, retry_on=[429, 500]),
    "github":     RetryPolicy(max_retries=2, backoff=1.0, retry_on=[429, 500, 502]),
    "claude":     RetryPolicy(max_retries=3, backoff=2.0, retry_on=[429, 500, 529]),
    "twitter":    RetryPolicy(max_retries=2, backoff=5.0, retry_on=[429, 500, 503]),
    "linkedin":   RetryPolicy(max_retries=2, backoff=5.0, retry_on=[429, 500, 503]),
}
```

---

## 6. Caching Strategy

### 6.1 Redis Cache Keys

```python
CACHE_CONFIG = {
    # Content source caches
    "cache:hn:topstories":         {"ttl": 900},    # 15 minutes
    "cache:reddit:{subreddit}":    {"ttl": 900},    # 15 minutes
    "cache:devto:trending":        {"ttl": 900},    # 15 minutes
    "cache:jokes:batch":           {"ttl": 3600},   # 1 hour
    "cache:github:trending":       {"ttl": 1800},   # 30 minutes

    # Dashboard/analytics caches
    "cache:dashboard:{user_id}":   {"ttl": 300},    # 5 minutes
    "cache:analytics:{post_id}":   {"ttl": 3600},   # 1 hour

    # Rate limiter keys
    "ratelimit:reddit":            {"max": 30, "window": 60},    # 30/min
    "ratelimit:newsapi":           {"max": 90, "window": 86400}, # 90/day
    "ratelimit:jokeapi":           {"max": 60, "window": 60},    # 60/min
    "ratelimit:twitter:publish":   {"max": 50, "window": 86400}, # 50/day
    "ratelimit:linkedin:publish":  {"max": 25, "window": 86400}, # 25/day

    # Profile intelligence caches
    "cache:profile:{linkedin_url}": {"ttl": 86400},  # 24 hours (profile data)
    "cache:lead_stats:{user_id}":   {"ttl": 300},    # 5 minutes

    # OAuth state (CSRF protection)
    "oauth:state:{state_token}":   {"ttl": 600},    # 10 minutes
}
```

### 6.2 Cache Invalidation Rules

| Event | Invalidated Keys |
|-------|-----------------|
| Content fetched | `cache:dashboard:{user_id}` |
| Post generated | `cache:dashboard:{user_id}` |
| Post published | `cache:dashboard:{user_id}`, `cache:analytics:*` |
| Platform connected/disconnected | `cache:dashboard:{user_id}` |
| Analytics fetched | `cache:analytics:{post_id}` (refreshed) |

---

## 7. Task Queue Design

### 7.1 Celery Configuration

```python
# celery_app.py
celery_app = Celery("smm")
celery_app.config_from_object({
    "broker_url": REDIS_URL,
    "result_backend": REDIS_URL,
    "task_serializer": "json",
    "result_serializer": "json",
    "accept_content": ["json"],
    "timezone": "UTC",
    "enable_utc": True,
    "task_track_started": True,
    "task_time_limit": 300,           # 5 min hard timeout
    "task_soft_time_limit": 240,      # 4 min soft timeout
    "worker_prefetch_multiplier": 1,  # Fair task distribution
    "worker_max_tasks_per_child": 100, # Restart worker after 100 tasks (memory leak prevention)
})
```

### 7.2 Celery Beat Schedule

```python
celery_app.conf.beat_schedule = {
    "fetch-trending-content": {
        "task": "app.tasks.research_tasks.fetch_trending_content",
        "schedule": crontab(minute=0, hour="*/2"),      # Every 2 hours
        "options": {"queue": "research"},
    },
    "process-active-schedules": {
        "task": "app.tasks.generation_tasks.process_active_schedules",
        "schedule": crontab(minute="*/30"),              # Every 30 minutes
        "options": {"queue": "generation"},
    },
    "publish-scheduled-posts": {
        "task": "app.tasks.publishing_tasks.publish_scheduled_posts",
        "schedule": crontab(minute="*"),                 # Every minute
        "options": {"queue": "publishing"},
    },
    "fetch-analytics": {
        "task": "app.tasks.analytics_tasks.fetch_analytics",
        "schedule": crontab(minute=0, hour="*/6"),       # Every 6 hours
        "options": {"queue": "analytics"},
    },
    "collect-engager-profiles": {
        "task": "app.tasks.profile_tasks.collect_engager_profiles",
        "schedule": crontab(minute=30, hour="*/3"),       # Every 3 hours (offset from comment fetch)
        "options": {"queue": "comments"},                  # Runs on comment worker
    },
}
```

### 7.3 Task Definitions

```python
# research_tasks.py
@celery_app.task(bind=True, max_retries=2, default_retry_delay=60)
def fetch_trending_content(self):
    """Fetch trending content from all sources."""
    aggregator = ContentAggregator(sources=[...])
    result = aggregator.fetch_all(limit_per_source=20)
    return {"fetched": result.total_items, "errors": result.errors}

# generation_tasks.py
@celery_app.task(bind=True, max_retries=1, default_retry_delay=30)
def generate_post(self, content_source_id, target_platform, content_type, tone, user_id):
    """Generate a single post from content source."""
    generator = PostGenerator(...)
    post = generator.generate_post(content_source_id, target_platform, content_type, tone, user_id)
    return {"post_id": str(post.id)}

@celery_app.task(bind=True)
def process_active_schedules(self):
    """Check active schedules and generate content if due."""
    # For each active schedule where cron matches current time:
    # 1. Pick top content matching schedule's content_types
    # 2. Generate post
    # 3. Set status based on auto_approve flag

# publishing_tasks.py
@celery_app.task(bind=True, max_retries=2, default_retry_delay=120)
def publish_scheduled_posts(self):
    """Publish all posts that are due."""
    # Query: status='scheduled' AND scheduled_for <= NOW()
    # For each: publish via publisher registry

@celery_app.task(bind=True, max_retries=2, default_retry_delay=60)
def publish_post_now(self, generated_post_id, user_id):
    """Publish a single post immediately."""

# analytics_tasks.py
@celery_app.task(bind=True, max_retries=1)
def fetch_analytics(self):
    """Fetch engagement metrics for recent posts."""
    # Query published_posts from last 7 days
    # For each: call publisher.get_metrics()
    # Save analytics_snapshot

# profile_tasks.py
@celery_app.task(bind=True, max_retries=2, default_retry_delay=120)
def collect_engager_profiles(self):
    """Collect profile data from people who engage with published posts."""
    # Query recent published posts (last 24h) on LinkedIn
    # For each: collect engager profiles via LeadManager
    # Classify statuses via AI, extract contact info
    # Upsert leads

@celery_app.task(bind=True, max_retries=1, default_retry_delay=60)
def scan_single_profile(self, profile_url, user_id, published_post_id):
    """Fetch and classify a single LinkedIn profile (triggered on new comment/engagement)."""
    # Fetch profile details
    # Classify status
    # Extract contact info
    # Create or update lead record
```

---

## 8. Frontend Component Hierarchy

### 8.1 Page Component Tree

```
App
├── AuthProvider (context)
│   ├── PublicRoutes
│   │   ├── LoginPage
│   │   └── RegisterPage
│   │
│   └── ProtectedRoutes
│       └── MainLayout
│           ├── Sidebar
│           │   ├── NavItem (Dashboard)
│           │   ├── NavItem (Content Research)
│           │   ├── NavItem (Post Manager)
│           │   ├── NavItem (Analytics)
│           │   ├── NavItem (Leads)
│           │   └── NavItem (Settings)
│           │
│           ├── Header
│           │   ├── PageTitle
│           │   └── UserMenu
│           │
│           └── PageContent (React Router Outlet)
│               ├── DashboardPage
│               │   ├── StatsRow
│               │   │   ├── MetricCard (Posts This Week)
│               │   │   ├── MetricCard (Engagement Rate)
│               │   │   ├── MetricCard (Pending Reviews)
│               │   │   └── MetricCard (Upcoming Scheduled)
│               │   ├── RecentActivity
│               │   │   └── ActivityItem (repeating)
│               │   ├── UpcomingPosts
│               │   │   └── ScheduledPostCard (repeating)
│               │   └── QuickActions
│               │       ├── Button (Fetch Content)
│               │       ├── Button (Generate Posts)
│               │       └── Button (Review Drafts)
│               │
│               ├── ContentResearchPage
│               │   ├── ContentFilter
│               │   │   ├── SourceTabs (All, HN, Reddit, Dev.to, Jokes, GitHub)
│               │   │   └── SortSelect (Score, Recency)
│               │   ├── RefreshButton
│               │   └── TrendingFeed
│               │       └── ContentCard (repeating)
│               │           ├── SourceIcon
│               │           ├── Title + Link
│               │           ├── ScoreBadge
│               │           ├── ContentPreview
│               │           ├── TagList
│               │           └── GenerateButton
│               │
│               ├── PostManagerPage
│               │   ├── StatusTabs (Draft, Approved, Scheduled, Published, Rejected)
│               │   │   └── CountBadge
│               │   ├── PostQueue
│               │   │   └── PostCard (repeating)
│               │   │       ├── PlatformIcon
│               │   │       ├── ContentPreview
│               │   │       ├── StatusBadge
│               │   │       ├── ScheduleInfo
│               │   │       └── ActionButtons
│               │   └── PostEditorModal (on post select)
│               │       ├── TextArea (with char counter)
│               │       ├── CharacterCounter
│               │       ├── HashtagEditor
│               │       ├── PlatformPreview
│               │       ├── SourceReference
│               │       ├── SchedulePicker
│               │       └── ActionBar
│               │           ├── ApproveButton
│               │           ├── RejectButton
│               │           ├── PublishNowButton
│               │           ├── ScheduleButton
│               │           └── RegenerateButton
│               │
│               ├── AnalyticsPage
│               │   ├── DateRangePicker
│               │   ├── OverviewStats
│               │   │   ├── MetricCard (Total Impressions)
│               │   │   ├── MetricCard (Total Engagement)
│               │   │   ├── MetricCard (Avg Rate)
│               │   │   └── MetricCard (Posts Published)
│               │   ├── EngagementChart (Recharts LineChart)
│               │   ├── PlatformComparison (Recharts BarChart)
│               │   └── TopPostsTable
│               │       └── TopPostRow (repeating)
│               │
│               ├── CommentsPage
│               │   ├── CommentFilter
│               │   │   ├── StatusTabs (Unreplied, Replied, Mentions, All)
│               │   │   └── PlatformFilter
│               │   ├── CommentList
│               │   │   └── CommentCard (repeating)
│               │   │       ├── CommenterInfo (name, avatar, follower count, profile link)
│               │   │       ├── CommentText
│               │   │       ├── SentimentBadge (positive/neutral/negative)
│               │   │       ├── CommentTypeBadge (question/praise/criticism)
│               │   │       ├── OriginalPostPreview (truncated)
│               │   │       ├── AIReplyPreview (editable)
│               │   │       └── ActionBar
│               │   │           ├── EditReplyButton
│               │   │           ├── SendReplyButton
│               │   │           ├── RegenerateButton
│               │   │           └── DismissButton
│               │   └── AutoReplySettings
│               │       ├── EnableToggle (per platform)
│               │       ├── FilterCheckboxes (questions, positive, all)
│               │       └── RateLimitInput
│               │
│               ├── LeadsPage
│               │   ├── LeadStats
│               │   │   ├── MetricCard (Total Leads)
│               │   │   ├── MetricCard (Open to Work)
│               │   │   ├── MetricCard (Hiring)
│               │   │   └── MetricCard (With Email)
│               │   ├── LeadFilters
│               │   │   ├── SearchInput
│               │   │   ├── StatusFilter (Open to Work, Hiring, Looking for Business, General)
│               │   │   ├── IndustryFilter
│               │   │   ├── ContactFilter (Has Email, Has Phone)
│               │   │   └── StarredToggle
│               │   ├── LeadTable
│               │   │   └── LeadRow (repeating)
│               │   │       ├── ProfileAvatar
│               │   │       ├── NameAndHeadline
│               │   │       ├── CompanyAndIndustry
│               │   │       ├── StatusBadge (OPEN TO WORK / HIRING / etc.)
│               │   │       ├── ContactIcons (email, phone, website)
│               │   │       ├── EngagementCount
│               │   │       ├── StarButton
│               │   │       └── ActionMenu (View, Tag, Note, Delete)
│               │   ├── LeadDetailModal (on row click)
│               │   │   ├── ProfileHeader (avatar, name, headline, profile link)
│               │   │   ├── StatusSection (AI classification with confidence)
│               │   │   ├── ContactSection (email, phone, website, twitter)
│               │   │   ├── CompanyInfo
│               │   │   ├── TagEditor (add/remove tags)
│               │   │   ├── NotesTextArea
│               │   │   └── EngagementTimeline
│               │   │       └── EngagementItem (repeating - type, post preview, date)
│               │   └── ExportButton
│               │       └── ExportModal (column selection, filter preview)
│               │
│               └── SettingsPage
│                   ├── PlatformConnections
│                   │   ├── PlatformCard (Twitter)
│                   │   │   ├── ConnectionStatus
│                   │   │   ├── AccountInfo
│                   │   │   └── Connect/Disconnect Button
│                   │   └── PlatformCard (LinkedIn)
│                   │       └── (same structure)
│                   ├── ContentPreferences
│                   │   ├── DefaultToneSelect
│                   │   ├── ContentTypeCheckboxes
│                   │   └── TimezoneSelect
│                   ├── ScheduleManager
│                   │   ├── ScheduleList
│                   │   │   └── ScheduleCard (repeating)
│                   │   └── CreateScheduleForm
│                   └── APIUsagePanel
│                       ├── TokenUsageBar
│                       ├── CostEstimate
│                       └── TwitterPostCounter
```

### 8.2 Shared Components

```
components/common/
├── Button          - Primary, secondary, danger, ghost variants
├── Modal           - Overlay dialog with close button
├── Toast           - Success, error, info notification
├── LoadingSpinner  - Centered spinner with optional text
├── Badge           - Status badges (draft, approved, etc.)
├── Pagination      - Page navigation with page size selector
├── EmptyState      - Illustration + message for empty lists
├── ErrorBoundary   - Catch rendering errors, show fallback
├── ConfirmDialog   - Confirmation before destructive actions
└── Tooltip         - Hover tooltip for icons/labels
```

### 8.3 State Management

```
Zustand Stores:
├── authStore
│   ├── user: User | null
│   ├── isAuthenticated: boolean
│   ├── login(email, password): Promise<void>
│   ├── logout(): void
│   └── refreshToken(): Promise<void>
│
└── uiStore
    ├── sidebarOpen: boolean
    ├── toggleSidebar(): void
    ├── activeToast: Toast | null
    └── showToast(message, type): void

React Query Keys:
├── ["content", filters]           - Content feed
├── ["content", id]                - Single content item
├── ["posts", status, platform]    - Post queue
├── ["posts", id]                  - Single post
├── ["platforms"]                  - Connected platforms
├── ["schedules"]                  - Schedule list
├── ["analytics", "overview"]      - Analytics overview
├── ["analytics", "post", id]      - Post analytics
└── ["dashboard"]                  - Dashboard data
```
