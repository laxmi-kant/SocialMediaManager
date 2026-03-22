# Product Requirements Document (PRD)
## AI-Powered Social Media Manager Platform

**Document Version:** 1.0
**Date:** March 20, 2026
**Author:** Product Team
**Status:** Draft

---

## Table of Contents
1. [Product Vision & Objectives](#1-product-vision--objectives)
2. [User Personas](#2-user-personas)
3. [Functional Requirements](#3-functional-requirements)
4. [Non-Functional Requirements](#4-non-functional-requirements)
5. [Success Metrics & KPIs](#5-success-metrics--kpis)
6. [Constraints & Assumptions](#6-constraints--assumptions)
7. [MVP Scope & Release Plan](#7-mvp-scope--release-plan)
8. [Acceptance Criteria](#8-acceptance-criteria)

---

## 1. Product Vision & Objectives

### 1.1 Vision Statement
Build an intelligent, self-hosted social media management platform that transforms trending content into engaging social media posts using AI, enabling tech professionals to maintain a consistent online presence with minimal effort.

### 1.2 Problem Statement
Tech professionals and content creators want to maintain an active social media presence on LinkedIn and Twitter/X, but:
- They lack time to manually browse trending sources, craft posts, and publish daily
- Existing tools cost $25-199/month and still require manual content ideation
- AI tools generate generic, low-quality content that gets shadowbanned
- No existing solution offers an integrated pipeline from content discovery to publishing

### 1.3 Product Objectives
| Objective | Measurement |
|-----------|-------------|
| **O1:** Reduce time spent on social media content creation by 80% | User creates and publishes a post in under 2 minutes (vs 15+ minutes manually) |
| **O2:** Enable consistent posting cadence | User publishes at least 3 posts/week with scheduling |
| **O3:** Generate high-quality, platform-optimized content | Posts achieve engagement rates comparable to manually written posts |
| **O4:** Minimize operating costs | Total API costs under $5/month for typical usage |
| **O5:** Provide actionable content insights | User can identify best-performing content types within 30 days |

### 1.4 Product Principles
1. **Content pipeline first** - The core value is the end-to-end flow: discover → generate → review → publish
2. **Quality over quantity** - Better to post 3 excellent posts/week than 3 mediocre posts/day
3. **Human in the loop** - AI assists, human approves. Default to review, not auto-publish
4. **Simplicity** - A solo tech professional should be productive within 10 minutes of setup
5. **Extensibility** - New content sources and platforms should be pluggable without architecture changes

---

## 2. User Personas

### 2.1 Primary Persona: Arjun - The Solo Tech Professional

| Attribute | Detail |
|-----------|--------|
| **Age** | 32 |
| **Role** | Senior Software Engineer at a mid-size company |
| **Location** | Bangalore, India (IST timezone) |
| **Platforms** | LinkedIn (primary), Twitter/X (secondary) |
| **Posting frequency** | Wants to post 3-5 times/week but currently posts 1-2 times/month |
| **Content style** | Tech insights, programming tips, industry commentary |
| **Technical skill** | High - comfortable with Docker, CLI, API keys |
| **Budget** | Minimal - prefers free/self-hosted tools |

**Goals:**
- Build personal brand as a thought leader in his tech domain
- Share interesting tech content consistently without spending hours on it
- Grow LinkedIn connections and Twitter followers organically

**Pain Points:**
- Spends 30+ minutes when he does post (browsing HN/Reddit for ideas, writing, formatting)
- Tried Buffer/Hootsuite but found them expensive for personal use and they don't help with content ideation
- Used ChatGPT for drafts but the output feels generic; worried about AI detection
- Inconsistent posting leads to low visibility and slow follower growth

**Scenario:**
Arjun opens the dashboard in the morning, sees trending tech content already aggregated. He clicks "Generate Post" on an interesting HN article, reviews the AI-generated LinkedIn post, makes a small tweak, and publishes. Total time: 2 minutes. He also has a schedule set up to auto-generate a Twitter post from trending repos every weekday at 5 PM.

### 2.2 Secondary Persona: Sarah - The Digital Marketer (US)

| Attribute | Detail |
|-----------|--------|
| **Age** | 34 |
| **Role** | Digital Marketing Manager at a B2B SaaS startup |
| **Location** | Austin, Texas (CST timezone) |
| **Platforms** | LinkedIn (primary), Twitter/X (secondary) |
| **Posting frequency** | Wants to post daily |
| **Content style** | Marketing trends, industry insights, business tips |
| **Technical skill** | Moderate - can follow setup docs, comfortable with web apps |
| **Budget** | $0-30/month |

**Goals:**
- Position her company as a thought leader in their niche
- Drive traffic to company blog through social sharing
- Stay on top of marketing trends and share insights
- Engage with comments and mentions to build community

**Pain Points:**
- Spending 2+ hours daily on social media content curation
- Existing tools too expensive for a startup's marketing budget
- Getting mentions and comments but can't reply fast enough

### 2.3 Tertiary Persona: Markus - The European Small Business Owner

| Attribute | Detail |
|-----------|--------|
| **Age** | 42 |
| **Role** | Founder of a consulting firm |
| **Location** | Berlin, Germany (CET timezone) |
| **Platforms** | LinkedIn (primary) |
| **Posting frequency** | 3-4 times/week |
| **Content style** | Business insights, industry news, motivational content |
| **Technical skill** | Low-moderate - needs clear documentation |
| **Budget** | $20-50/month |

**Goals:**
- Build personal brand as an industry expert
- Generate leads through LinkedIn thought leadership
- Auto-respond to comments and mentions to maintain engagement

**Pain Points:**
- No time to manually write posts while running a business
- Misses important mentions and comments from potential clients
- Current tools don't help with content ideation

---

## 3. Functional Requirements

### 3.1 Content Research (FR-100 Series)

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-101 | System SHALL fetch trending content from Hacker News API (top stories, configurable limit) every 2 hours | Must |
| FR-102 | System SHALL fetch trending content from Reddit API (configurable subreddits) every 2 hours | Must |
| FR-103 | System SHALL fetch trending articles from Dev.to API every 2 hours | Must |
| FR-104 | System SHALL fetch random jokes from JokeAPI and icanhazdadjoke every 2 hours | Must |
| FR-105 | System SHALL fetch trending repositories from GitHub Trending API every 2 hours | Must |
| FR-106 | System SHALL deduplicate content by (source_type, external_id) to avoid duplicates | Must |
| FR-107 | System SHALL store fetched content with title, URL, content summary, author, score, tags, and source type | Must |
| FR-108 | User SHALL be able to browse fetched content in a paginated feed | Must |
| FR-109 | User SHALL be able to filter content by source type | Must |
| FR-110 | User SHALL be able to sort content by score or recency | Should |
| FR-111 | User SHALL be able to manually trigger a content refresh | Should |
| FR-112 | System SHALL cache API responses in Redis to respect rate limits | Must |

### 3.2 AI Content Generation (FR-200 Series)

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-201 | User SHALL be able to generate a Twitter post (max 280 chars) from any content item | Must |
| FR-202 | User SHALL be able to generate a LinkedIn post (300-700 words) from any content item | Must |
| FR-203 | System SHALL use Claude Haiku 4.5 as the default AI model for generation | Must |
| FR-204 | System SHALL use platform-specific prompt templates for content generation | Must |
| FR-205 | Generated posts SHALL include relevant hashtags (2-3 for Twitter, 3-5 for LinkedIn) | Must |
| FR-206 | User SHALL be able to select tone (professional, casual, humorous, educational) | Should |
| FR-207 | User SHALL be able to generate posts from multiple content items in batch | Should |
| FR-208 | User SHALL be able to regenerate a post to get a different version | Should |
| FR-209 | System SHALL track AI model used and token usage for each generation | Should |
| FR-210 | User SHALL be able to select Claude Sonnet 4.5 for higher-quality generation | Could |

### 3.3 Post Management (FR-300 Series)

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-301 | All generated posts SHALL start with "draft" status | Must |
| FR-302 | User SHALL be able to view posts filtered by status (draft, approved, scheduled, published, rejected) | Must |
| FR-303 | User SHALL be able to edit post text content | Must |
| FR-304 | User SHALL see a live character counter that shows remaining characters | Must |
| FR-305 | User SHALL be able to approve a draft post (changes status to "approved") | Must |
| FR-306 | User SHALL be able to reject a draft post (changes status to "rejected") | Must |
| FR-307 | User SHALL be able to publish an approved post immediately | Must |
| FR-308 | User SHALL be able to schedule a post for a specific date/time | Should |
| FR-309 | User SHALL see a preview of how the post will look on the target platform | Should |
| FR-310 | User SHALL be able to edit hashtags on a post | Should |
| FR-311 | User SHALL be able to perform bulk approve/reject on multiple posts | Could |
| FR-312 | User SHALL be able to view published post history with engagement data | Should |

### 3.4 Publishing (FR-400 Series)

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-401 | System SHALL publish posts to Twitter/X using API v2 | Must |
| FR-402 | System SHALL publish posts to LinkedIn using UGC Post API | Must |
| FR-403 | System SHALL store the platform post ID and URL after successful publish | Must |
| FR-404 | System SHALL handle publish failures gracefully with clear error messages | Must |
| FR-405 | System SHALL provide a retry mechanism for failed publications | Should |
| FR-406 | System SHALL automatically refresh expired OAuth tokens | Must |
| FR-407 | System SHALL enforce rate limits (max posts/day within API free tier limits) | Must |
| FR-408 | User SHALL be able to delete a published post from the platform | Could |

### 3.5 Scheduling (FR-500 Series)

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-501 | User SHALL be able to create recurring schedules with cron expressions | Should |
| FR-502 | System SHALL check for scheduled posts every minute and publish those that are due | Should |
| FR-503 | User SHALL be able to set timezone for schedules | Should |
| FR-504 | User SHALL be able to toggle auto-approve on schedules | Could |
| FR-505 | User SHALL be able to pause and resume schedules | Should |
| FR-506 | System SHALL auto-generate content for active schedules based on configured content types | Should |

### 3.6 Analytics (FR-600 Series)

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-601 | System SHALL fetch engagement metrics (impressions, likes, comments, shares) for published posts | Should |
| FR-602 | User SHALL see analytics summary with total impressions and engagement rate | Should |
| FR-603 | User SHALL be able to view per-post engagement metrics | Should |
| FR-604 | User SHALL see a platform comparison chart (Twitter vs LinkedIn) | Could |
| FR-605 | User SHALL see top-performing posts ranked by engagement | Could |
| FR-606 | User SHALL see content type performance breakdown | Could |

### 3.7 Comment & Mention Management (FR-700 Series)

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-701c | System SHALL periodically fetch new comments on published posts from Twitter and LinkedIn | Must |
| FR-702c | Comment polling frequency SHALL be configurable by the user (default: every 15 minutes) | Must |
| FR-703c | System SHALL use AI to generate contextually appropriate reply suggestions for each comment | Must |
| FR-704c | AI reply SHALL consider: original post context, comment sentiment, commenter intent (question, praise, criticism) | Must |
| FR-705c | User SHALL be able to review, edit, and send AI-suggested replies (default mode) | Must |
| FR-706c | User SHALL be able to enable auto-reply mode per platform | Must |
| FR-707c | Auto-reply SHALL have configurable filters (reply to questions only, positive comments only, all) | Should |
| FR-708c | Auto-reply SHALL be rate-limited (max 10 replies/hour by default, configurable) | Must |
| FR-709c | System SHALL detect when the user is mentioned (@mentioned) in posts or comments | Must |
| FR-710c | Mentions SHALL trigger a notification in the dashboard | Must |
| FR-711c | System SHALL auto-generate a reply to mentions using AI (same review/auto-reply workflow) | Must |
| FR-712c | Mention replies SHALL be prioritized over regular comment replies | Should |
| FR-713c | System SHALL track all replies sent (manual and auto) with timestamps | Must |
| FR-714c | User SHALL see comment/mention analytics (reply rate, sentiment, response time) | Should |

### 3.8 Authentication (FR-800 Series)

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-701 | User SHALL be able to register with email and password | Must |
| FR-702 | User SHALL be able to log in and receive a JWT token | Must |
| FR-703 | System SHALL use httponly cookies for JWT storage | Must |
| FR-704 | System SHALL auto-refresh JWT tokens before expiry | Must |
| FR-705 | User SHALL be able to log out (clears all tokens) | Must |
| FR-706 | User SHALL be able to update display name and password | Should |

### 3.8 LinkedIn Profile Intelligence (FR-1000 Series)

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-1001 | System SHALL collect publicly available profile data (name, headline, company, industry, location, profile URL, follower count) from LinkedIn users who engage with published posts | Must |
| FR-1002 | System SHALL deduplicate profiles by LinkedIn profile URL to avoid duplicate leads | Must |
| FR-1003 | System SHALL use AI to classify each lead's status as OPEN TO WORK, HIRING, Looking for Business, or General based on headline and about text | Must |
| FR-1004 | AI classification SHALL consider full context of headline + about section, not just keyword matching | Must |
| FR-1005 | System SHALL extract publicly accessible contact information (email, phone, website, Twitter handle) from LinkedIn profiles when available | Should |
| FR-1006 | System SHALL clearly mark contact info availability (available / not public) per field | Should |
| FR-1007 | User SHALL be able to view all leads in a searchable, filterable table (Leads page) | Must |
| FR-1008 | User SHALL be able to filter leads by status type (OPEN TO WORK, HIRING, etc.), industry, contact availability, and engagement date | Must |
| FR-1009 | User SHALL be able to sort leads by engagement count, recency, or name | Must |
| FR-1010 | User SHALL be able to add manual tags and private notes to leads | Should |
| FR-1011 | User SHALL be able to star/favorite leads for quick access | Should |
| FR-1012 | User SHALL be able to export leads as CSV with selected columns and applied filters | Should |
| FR-1013 | System SHALL track engagement count and history per lead (how many times they engaged, types of engagement) | Could |
| FR-1014 | User SHALL be able to delete any lead's data (right to be forgotten / privacy compliance) | Must |
| FR-1015 | System SHALL only collect publicly accessible data and comply with LinkedIn API Terms of Service | Must |
| FR-1016 | Profile data collection SHALL run in background (Celery worker) without blocking comment fetch | Must |

### 3.9 Dashboard (FR-800 Series)

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-801 | Dashboard SHALL show summary stats (posts this week, engagement rate, pending reviews, upcoming scheduled) | Must |
| FR-802 | Dashboard SHALL show recent activity feed | Must |
| FR-803 | Dashboard SHALL show upcoming scheduled posts | Should |
| FR-804 | Dashboard SHALL provide quick action buttons (fetch content, generate posts, review drafts) | Should |
| FR-805 | Dashboard SHALL show content source health indicators | Could |

### 3.9 Settings (FR-900 Series)

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-901 | User SHALL be able to connect Twitter account via OAuth | Must |
| FR-902 | User SHALL be able to connect LinkedIn account via OAuth | Must |
| FR-903 | User SHALL see connection status for each platform | Must |
| FR-904 | User SHALL be able to disconnect a platform account | Must |
| FR-905 | User SHALL be able to set default content preferences (tone, content types, timezone) | Should |
| FR-906 | User SHALL see API usage and estimated costs | Could |

---

## 4. Non-Functional Requirements

### 4.1 Performance

| ID | Requirement | Target |
|----|-------------|--------|
| NFR-P01 | API response time for standard endpoints | < 500ms (p95) |
| NFR-P02 | AI content generation response time | < 10 seconds |
| NFR-P03 | Dashboard page load time | < 2 seconds |
| NFR-P04 | Content feed pagination response | < 300ms |
| NFR-P05 | Concurrent users supported | At least 5 (self-hosted) |

### 4.2 Security

| ID | Requirement |
|----|-------------|
| NFR-S01 | All passwords SHALL be hashed with bcrypt (cost factor >= 12) |
| NFR-S02 | JWT tokens SHALL expire within 15 minutes |
| NFR-S03 | Refresh tokens SHALL expire within 7 days |
| NFR-S04 | OAuth tokens SHALL be encrypted at rest using Fernet symmetric encryption |
| NFR-S05 | API SHALL enforce CORS to only allow the configured frontend origin |
| NFR-S06 | All API endpoints (except auth) SHALL require valid JWT authentication |
| NFR-S07 | OAuth flows SHALL use state parameter for CSRF protection |
| NFR-S08 | All secrets SHALL be stored in environment variables, never in code |
| NFR-S09 | SQL injection SHALL be prevented via ORM parameterized queries |
| NFR-S10 | Input validation SHALL be enforced on all API endpoints via Pydantic schemas |

### 4.3 Reliability

| ID | Requirement |
|----|-------------|
| NFR-R01 | Failed content fetches SHALL NOT block other source fetches |
| NFR-R02 | Failed publishes SHALL be logged and retryable |
| NFR-R03 | External API calls SHALL retry with exponential backoff (3 retries max) |
| NFR-R04 | System SHALL handle API rate limiting gracefully (wait and retry on 429) |
| NFR-R05 | Database operations SHALL use transactions for data consistency |
| NFR-R06 | Celery tasks SHALL be idempotent (safe to retry) |

### 4.4 Scalability

| ID | Requirement |
|----|-------------|
| NFR-SC01 | Architecture SHALL support adding new content sources without code changes to existing sources |
| NFR-SC02 | Architecture SHALL support adding new social media platforms without code changes to existing publishers |
| NFR-SC03 | Database schema SHALL use UUIDs for primary keys (no sequential ID conflicts) |
| NFR-SC04 | Content sources table SHALL use JSONB metadata for flexible source-specific fields |

### 4.5 Maintainability

| ID | Requirement |
|----|-------------|
| NFR-M01 | Code SHALL follow Python PEP 8 style guidelines |
| NFR-M02 | Frontend code SHALL use TypeScript strict mode |
| NFR-M03 | All API endpoints SHALL be documented via OpenAPI/Swagger (auto-generated by FastAPI) |
| NFR-M04 | Database migrations SHALL be managed via Alembic |
| NFR-M05 | Environment configuration SHALL use Pydantic Settings with .env files |
| NFR-M06 | Structured logging SHALL be used (JSON format via structlog) |

### 4.6 Usability

| ID | Requirement |
|----|-------------|
| NFR-U01 | User SHALL be able to set up and publish first post within 15 minutes of installation |
| NFR-U02 | Dashboard SHALL be responsive (usable on 1024px+ screens) |
| NFR-U03 | All user actions SHALL provide visual feedback (loading states, success/error toasts) |
| NFR-U04 | Error messages SHALL be human-readable and actionable |

### 4.7 Deployment

| ID | Requirement |
|----|-------------|
| NFR-D01 | Application SHALL be deployable via Docker Compose with a single command |
| NFR-D02 | All services (backend, frontend, database, Redis, Celery) SHALL be containerized |
| NFR-D03 | Environment SHALL be configurable via .env file |
| NFR-D04 | .env.example SHALL document all required environment variables |

---

## 5. Success Metrics & KPIs

### 5.1 Product Success Metrics

| Metric | Target | Measurement Method |
|--------|--------|-------------------|
| **Daily active usage** | User opens dashboard at least 5 days/week | Login frequency tracking |
| **Posts per week** | 5+ posts published weekly across platforms | Published posts count |
| **Content generation ratio** | 70%+ of generated posts approved (not rejected) | Approved / (Approved + Rejected) |
| **Engagement rate** | Equal to or better than manually written posts | Platform analytics comparison |
| **Comment reply rate** | 80%+ of comments receive a reply (auto or manual) | Replied / Total comments |
| **Mention response time** | < 1 hour average response to mentions (with auto-reply enabled) | Mention timestamp vs reply timestamp |
| **Monthly cost** | < $5/month for typical usage | Claude API billing |

### 5.2 Technical KPIs

| KPI | Target | Alert Threshold |
|-----|--------|----------------|
| API uptime | 99%+ during active hours | < 95% |
| Content fetch success rate | 95%+ across all sources | < 80% for any single source |
| Publish success rate | 98%+ | < 90% |
| AI generation latency | < 10 seconds | > 15 seconds |
| Database query time | < 100ms (p95) | > 500ms |

---

## 6. Constraints & Assumptions

### 6.1 Constraints

| Constraint | Impact |
|-----------|--------|
| **Twitter Free Tier:** 1,500 tweets/month, write-only (no reading) | Max ~50 tweets/day; no engagement metric reading on free tier |
| **LinkedIn API:** Requires developer app approval | Delay before LinkedIn publishing works |
| **Claude API:** Requires Anthropic API key and billing | Must have valid API key; costs ~$0.60/month |
| **Self-hosted:** Requires Docker and a machine to run on | User needs technical knowledge to install |
| **Single-user:** V1 designed for one user | No multi-tenant or team features |
| **Text-only:** No image or video generation | Posts are text + hashtags only |
| **Two platforms:** Only Twitter and LinkedIn | No Instagram, TikTok, etc. in V1 |

### 6.2 Assumptions

| Assumption | Risk if Wrong |
|-----------|---------------|
| User has Docker and Docker Compose installed | Provide alternative setup instructions |
| User can obtain Twitter Developer Account and create an app | Document the process; may take a few days for approval |
| User can obtain LinkedIn Developer App approval | Document the process; may take 1-2 weeks |
| User has an Anthropic API key | Document signup process; requires billing setup |
| PostgreSQL and Redis work within Docker without special config | May need platform-specific adjustments |
| Free-tier API rate limits are sufficient for personal use | Monitor usage; provide upgrade path documentation |
| Claude Haiku 4.5 quality is sufficient for social media posts | Allow model selection; Sonnet as fallback |
| Users are comfortable with English-language content | I18n is out of scope for V1 |

### 6.3 Dependencies

| Dependency | Type | Risk |
|-----------|------|------|
| Anthropic Claude API | External service | Medium - API changes/outages |
| Twitter/X API v2 | External service | High - Frequent pricing/policy changes |
| LinkedIn API | External service | Medium - Approval process delays |
| Hacker News API | External service | Low - Stable, maintained by YC |
| Reddit API | External service | Medium - ToS changes, auth requirements |
| Dev.to API | External service | Low - Stable, open platform |
| JokeAPI | External service | Low - Free, community-maintained |
| GitHub Trending (community) | Community API | Medium - Unofficial, may break |
| PostgreSQL | Infrastructure | Low - Self-hosted, stable |
| Redis | Infrastructure | Low - Self-hosted, stable |

---

## 7. MVP Scope & Release Plan

### 7.1 MVP (V1.0) - "First Post in 15 Minutes"

**Goal:** User can set up the platform, connect accounts, and publish their first AI-generated post within 15 minutes.

**Scope:**
- Content Research: Automated fetching from all 6 sources, content browser with filters
- AI Generation: Twitter and LinkedIn post generation with Claude Haiku 4.5
- Post Management: Draft → Approve → Publish workflow with editor and character counter
- Publishing: Twitter and LinkedIn OAuth + post publishing
- Dashboard: Stats overview, recent activity, quick actions
- Auth: Registration, login, JWT sessions
- Settings: Platform connections, connection status

**Excluded from MVP:**
- Scheduling (recurring and one-time)
- Analytics
- Batch generation
- Tone selection
- Post preview (platform mock)
- Bulk actions
- Auto-approve
- API usage monitoring
- LinkedIn Profile Intelligence (V1.1)

### 7.2 V1.1 - "Set It and Forget It + Lead Intelligence"

**Goal:** User can set up recurring schedules, let the system generate and queue posts automatically, and collect lead intelligence from LinkedIn post engagers.

**Scope (additions):**
- Recurring schedules with cron expressions
- Automated content pipeline (schedule → generate → queue for review)
- One-time scheduling (schedule a post for later)
- Basic analytics (engagement metrics from platforms)
- Tone selection
- Post preview
- Batch generation
- Publish retry mechanism
- LinkedIn Profile Intelligence (profile collection, AI status detection, lead dashboard)
- Lead search/filter by status, industry, contact availability
- Contact info extraction (email, phone, website) from public profiles

### 7.3 V1.2 - "Optimize and Grow"

**Goal:** User can analyze what works and optimize their content strategy.

**Scope (additions):**
- Auto-approve mode on schedules
- Content type performance breakdown
- Top performing posts analysis
- Engagement over time charts
- Schedule calendar view
- Bulk approve/reject
- Content source health monitoring
- Source configuration (subreddits, etc.)
- Post deletion from platform

### 7.4 V2.0 - "Scale Up" (Future)

**Scope (vision):**
- Additional platforms (Mastodon, Bluesky, Threads, Medium)
- Image generation (DALL-E integration)
- Twitter threads and LinkedIn carousels
- Multi-user / team support
- SaaS hosted offering
- Content repurposing (blog → posts)
- A/B testing

---

## 8. Acceptance Criteria

### 8.1 System-Level Acceptance Criteria

| ID | Criteria | Verification |
|----|----------|-------------|
| AC-01 | System starts with `docker-compose up` and all services are healthy within 60 seconds | Run docker-compose up, verify all containers running |
| AC-02 | User can register, log in, and see dashboard | Manual test: register → login → dashboard loads |
| AC-03 | Trending content appears within 5 minutes of first startup (after initial fetch) | Check content feed after initial Celery Beat trigger |
| AC-04 | User can generate a Twitter post from content item in < 10 seconds | Time from "Generate" click to post appearing |
| AC-05 | Generated Twitter post respects 280 character limit | Verify character count on 50+ generated posts |
| AC-06 | Generated LinkedIn post is 300-700 words with professional tone | Verify word count and tone on 20+ generated posts |
| AC-07 | User can edit, approve, and publish a post to Twitter | End-to-end test: edit → approve → publish → verify on Twitter |
| AC-08 | User can edit, approve, and publish a post to LinkedIn | End-to-end test: edit → approve → publish → verify on LinkedIn |
| AC-09 | Published post URL links to the actual post on the platform | Click published post link, verify it opens correct post |
| AC-10 | Failed publish shows clear error message and retry option | Disconnect network, attempt publish, verify error + retry |
| AC-11 | OAuth tokens are encrypted in database (not plaintext) | Inspect database, verify tokens are encrypted strings |
| AC-12 | System handles API rate limits without crashing | Simulate rate limit (429 response), verify graceful handling |
| AC-13 | Content feed updates every 2 hours without user intervention | Wait for Celery Beat cycle, verify new content appears |
| AC-14 | All API endpoints return appropriate error codes (400, 401, 404, 500) | API test suite with invalid inputs |
| AC-15 | Dashboard loads within 2 seconds with 1000+ content items in database | Load test with seeded data |

### 8.2 Content Quality Acceptance Criteria

| ID | Criteria | Verification |
|----|----------|-------------|
| AQ-01 | Twitter posts are grammatically correct and coherent | Human review of 50 generated posts |
| AQ-02 | LinkedIn posts have a clear structure (hook, body, CTA, hashtags) | Human review of 20 generated posts |
| AQ-03 | Hashtags are relevant to the content topic | Human review |
| AQ-04 | Posts don't contain hallucinated information beyond the source content | Compare generated post to source |
| AQ-05 | Tone matches the selected tone option | Generate same content with different tones, verify difference |
| AQ-06 | No offensive or inappropriate content in generated posts | Review 100+ generated posts across content types |

### 8.3 Comment Reply Quality Acceptance Criteria

| ID | Criteria | Verification |
|----|----------|-------------|
| CR-01 | AI-generated replies are contextually relevant to the comment | Human review of 50 comment-reply pairs |
| CR-02 | Replies match the tone of the original post | Compare reply tone to post tone across samples |
| CR-03 | Replies correctly identify questions and provide answers | Test with 20 question-type comments, verify answers are relevant |
| CR-04 | Replies to mentions acknowledge the mentioner appropriately | Test with 20 mention scenarios |
| CR-05 | Replies don't contain hallucinated information | Compare reply claims to original post and comment content |
| CR-06 | Auto-reply rate limiting works correctly (max N replies/hour) | Enable auto-reply, simulate 20 comments in 5 minutes, verify only 10 are replied |
| CR-07 | Negative/hostile comments receive professional, non-confrontational replies | Test with 10 negative comments, verify replies are diplomatic |

### 8.4 Lead Intelligence Acceptance Criteria

| ID | Criteria | Verification |
|----|----------|-------------|
| LI-01 | AI correctly identifies OPEN TO WORK status from headline variations | Test with 30 profiles with various "open to work" phrasing, verify 85%+ accuracy |
| LI-02 | AI correctly identifies HIRING status from headline variations | Test with 30 profiles with various "hiring" phrasing, verify 85%+ accuracy |
| LI-03 | AI correctly identifies Looking for Business status | Test with 20 profiles with business-seeking phrasing, verify 80%+ accuracy |
| LI-04 | Profile deduplication works correctly (no duplicate leads) | Simulate same person commenting twice, verify single lead entry |
| LI-05 | Contact info extraction only captures publicly available data | Verify no private data accessed; test with profiles that have hidden contact info |
| LI-06 | Lead export CSV contains correct data matching applied filters | Export with filters, verify row count and column accuracy |
| LI-07 | Lead deletion removes all associated data (profile, contact, engagement history) | Delete a lead, verify all related records are cascade-deleted |
