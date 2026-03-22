# Feature Specification Document
## AI-Powered Social Media Manager Platform

**Document Version:** 1.0
**Date:** March 20, 2026
**Author:** Product Team

---

## Table of Contents
1. [Feature Overview](#1-feature-overview)
2. [Module 1: Content Research](#2-module-1-content-research)
3. [Module 2: AI Content Generation](#3-module-2-ai-content-generation)
4. [Module 3: Post Management](#4-module-3-post-management)
5. [Module 4: Publishing](#5-module-4-publishing)
6. [Module 5: Scheduling](#6-module-5-scheduling)
7. [Module 6: Analytics](#7-module-6-analytics)
8. [Module 7: Dashboard](#8-module-7-dashboard)
9. [Module 8: Settings & Platform Management](#9-module-8-settings--platform-management)
10. [Module 9: Authentication](#10-module-9-authentication)
11. [Module 10: Comment Management](#10b-module-10-comment-management)
12. [Module 11: LinkedIn Profile Intelligence](#10c-module-11-linkedin-profile-intelligence)
13. [Platform-Specific Features](#11-platform-specific-features)
14. [MoSCoW Prioritization](#12-moscow-prioritization)
15. [User Stories](#13-user-stories)

---

## 1. Feature Overview

The platform consists of 11 core modules forming an end-to-end content pipeline:

```
[Auth] → [Dashboard] → [Content Research] → [AI Generation] → [Post Management] → [Publishing]
                              ↑                                        ↓               ↓
                        [Scheduling] ←──────────────────────── [Analytics]    [Comment Management]
                              ↑
                        [Settings/Platforms]
```

---

## 2. Module 1: Content Research

### 2.1 Features

#### F1.1: Automated Trending Content Aggregation
- System fetches trending content from multiple sources every 2 hours automatically
- **Tech Sources:** Hacker News, Reddit (r/technology, r/programming, r/webdev), Dev.to, GitHub Trending
- **Business/Marketing Sources:** Reddit (r/marketing, r/entrepreneur, r/smallbusiness, r/startups, r/digital_marketing)
- **Humor Sources:** JokeAPI, icanhazdadjoke
- Content is deduplicated by source + external ID
- Each item stores: title, URL, content/summary, author, score, tags, source type, category (tech/business/marketing/humor)

#### F1.2: Content Feed Browser
- Paginated feed of fetched content, newest first
- Each content card shows: source icon, title, score/popularity, time fetched, preview text, tags
- Click to expand for full content details and source link

#### F1.3: Source Filtering
- Filter by source type: All, Hacker News, Reddit, Dev.to, Jokes, GitHub
- Filter by time range: Today, This Week, This Month
- Sort by: Score (popularity), Recency, Source

#### F1.4: Manual Content Refresh
- Button to trigger immediate content fetch from all sources
- Shows loading state and count of new items fetched

#### F1.5: One-Click Post Generation
- Each content card has a "Generate Post" button
- Opens platform/tone selector, then generates AI post
- Links generated post back to source content

#### F1.6: Content Scoring
- Display popularity score (upvotes, stars, reactions) from each source
- Higher-scored content appears first by default

---

## 3. Module 2: AI Content Generation

### 3.1 Features

#### F2.1: Platform-Specific Post Generation
- Generate posts optimized for Twitter (max 280 characters) or LinkedIn (300-700 words)
- Each platform has distinct prompt templates and formatting rules
- Twitter: Concise, engaging, with hashtags, optional emoji
- LinkedIn: Professional tone, thought leadership angle, longer format, relevant hashtags

#### F2.2: Content Type Support (Preset Types)
- **Tech Insight** - Commentary on a tech article/trend
- **News Commentary** - React to trending news with professional insight
- **Joke/Humor** - Adapt jokes for social media engagement
- **GitHub Spotlight** - Highlight a trending repository
- **Tip/How-To** - Quick actionable tip derived from content
- **Thread Starter** - Opening post designed to spark discussion
- **Industry Insight** - Business/marketing trend analysis
- **Motivational/Inspirational** - Inspiring takeaway from a success story
- **Business Tip** - Actionable business or marketing advice

#### F2.2b: Custom Content Types
- Users can create additional content types with custom names
- Each custom type has a configurable prompt template
- Prompt templates support variables: `{{title}}`, `{{content}}`, `{{url}}`, `{{platform}}`, `{{tone}}`
- Custom types appear alongside preset types in the generation UI
- Users can edit and delete custom types

#### F2.3: Tone Selection
- Professional (default for LinkedIn)
- Casual (default for Twitter)
- Humorous (for joke content)
- Thought Leadership (for industry insights)
- Educational (for tips and tutorials)

#### F2.4: AI Model Selection
- Default: Claude Haiku 4.5 (fast, affordable)
- Option: Claude Sonnet 4.5 (higher quality for important posts)
- Display estimated token cost per generation

#### F2.5: Batch Generation
- Select multiple content items and generate posts for all at once
- Choose target platform and tone for the batch
- All generated posts enter the review queue as drafts

#### F2.6: Regeneration
- "Regenerate" button on any draft post to get a new version
- Option to regenerate with different tone or platform
- Previous versions are not kept (replaced)

#### F2.7: Hashtag Generation
- AI automatically suggests relevant hashtags
- User can edit/remove/add hashtags before publishing
- Platform-aware (Twitter: 2-3 hashtags, LinkedIn: 3-5 hashtags)

---

## 4. Module 3: Post Management

### 4.1 Features

#### F3.1: Post Queue with Status Tabs
- View all generated posts filtered by status:
  - **Draft** - AI-generated, awaiting review
  - **Approved** - Reviewed and ready to publish/schedule
  - **Scheduled** - Approved with a future publish time
  - **Published** - Successfully sent to platform
  - **Rejected** - Declined by reviewer
- Count badge on each tab showing number of posts

#### F3.2: Post Editor
- Editable text area for the post content
- Live character counter (red when exceeding platform limit)
- Platform indicator icon (Twitter bird / LinkedIn logo)
- **Platform switcher:** User can change target platform on a draft post. Switching triggers re-validation of character limits and re-generation if content exceeds new platform's limits
- Source content reference (link to the original content that inspired the post)
- Edit hashtags inline
- Save changes button

#### F3.3: Post Preview
- Real-time preview showing how the post will appear on the target platform
- Twitter preview: Mock tweet card with avatar, name, text, hashtags
- LinkedIn preview: Mock LinkedIn post with profile, text, engagement buttons

#### F3.4: Approve / Reject Workflow
- "Approve" button moves post to approved status
- "Reject" button moves post to rejected status with optional reason
- Approved posts can then be published immediately or scheduled

#### F3.5: Publish Now
- One-click publish button on approved posts
- Confirmation dialog before publishing
- Shows success/failure toast notification
- Links to the published post on the platform

#### F3.6: Schedule for Later
- Date/time picker to set future publish time
- Timezone-aware scheduling
- Post moves to "Scheduled" status
- Can be rescheduled or cancelled before publish time

#### F3.7: Post History
- Timeline view of all published posts
- Shows: platform, publish date, post text (truncated), engagement metrics
- Click to expand full details
- Link to view post on the platform

#### F3.8: Bulk Actions
- Select multiple draft posts
- Bulk approve, bulk reject, or bulk schedule
- Bulk delete

---

## 5. Module 4: Publishing

### 5.1 Features

#### F4.1: Twitter/X Publishing
- Post text tweets (max 280 characters)
- Include hashtags
- Handle API errors gracefully (rate limits, auth failures)
- Store platform post ID and URL after successful publish
- Free tier: 1,500 tweets/month

#### F4.2: LinkedIn Publishing
- Post text posts (max 3,000 characters)
- Professional formatting
- Include hashtags
- Handle API errors gracefully
- Store platform post URN and URL after successful publish

#### F4.3: Publish Error Handling
- Failed publishes show error message in post details
- Retry button for failed publications
- Clear error categorization: auth expired, rate limited, content policy, network error
- Automatic token refresh on auth expiry

#### F4.4: Post Deletion
- Delete a published post from the platform via API
- Updates local status to "deleted"
- Confirmation dialog before deletion

---

## 6. Module 5: Scheduling

### 6.1 Features

#### F5.1: Recurring Schedules
- Create named schedules with:
  - Target platform (Twitter or LinkedIn)
  - Content types to include (e.g., tech insights + jokes)
  - Cron expression for timing (e.g., 9 AM and 5 PM on weekdays)
  - Timezone selection
  - Auto-approve toggle (skip human review or not)
- Multiple schedules can be active simultaneously

#### F5.2: Schedule Management
- List all schedules with status (active/paused)
- Edit schedule parameters
- Pause/resume schedules
- Delete schedules

#### F5.3: Automated Content Pipeline
- When a schedule triggers:
  1. System selects top-scoring content from sources matching the schedule's content types
  2. Generates a post via Claude AI for the target platform
  3. If auto_approve: schedules immediately for the next time slot
  4. If not auto_approve: creates as draft for human review

#### F5.4: Schedule Calendar View
- Visual calendar showing upcoming scheduled posts
- Drag-and-drop to reschedule (future enhancement)
- Color-coded by platform

#### F5.5: One-Time Scheduling
- Schedule a specific post for a specific date/time
- Not recurring, just a delayed publish

---

## 7. Module 6: Analytics

### 7.1 Features

#### F6.1: Engagement Metrics Collection
- Periodically fetch metrics from Twitter and LinkedIn for published posts
- Metrics collected: impressions, likes, comments, shares/retweets, clicks
- Snapshots taken every 6 hours for first 7 days after publishing

#### F6.2: Analytics Dashboard
- Date range picker (7 days, 30 days, 90 days, custom)
- Summary metric cards: Total impressions, Total engagement, Avg engagement rate, Posts published
- Engagement over time chart (line chart)
- Platform comparison chart (bar chart: Twitter vs LinkedIn)

#### F6.3: Per-Post Analytics
- View detailed metrics for any published post
- Engagement timeline chart (how metrics grew over time)
- Compare against average performance

#### F6.4: Top Performing Posts
- Table of best-performing posts sorted by engagement rate
- Shows: post text preview, platform, publish date, impressions, engagement rate
- Identify which content types and tones perform best

#### F6.5: Content Type Performance
- Breakdown of engagement by content type (tech insight, joke, news, etc.)
- Helps user understand what content resonates with their audience
- Influences future content generation priorities

---

## 8. Module 7: Dashboard

### 8.1 Features

#### F7.1: Stats Overview
- 5 metric cards at the top:
  - Posts this week (published count)
  - Avg engagement rate (across all recent posts)
  - Pending reviews (draft posts awaiting approval)
  - Upcoming scheduled (posts scheduled for future)
  - Unreplied comments (comments + mentions awaiting reply)

#### F7.2: Recent Activity Feed
- Timeline of recent events:
  - Post published to Twitter/LinkedIn
  - Post approved/rejected
  - New content fetched
  - Schedule triggered
  - Errors (failed publishes, API issues)

#### F7.3: Upcoming Schedule
- Next 5 scheduled posts with:
  - Platform icon
  - Post text preview (truncated)
  - Scheduled time with countdown
  - Quick action: publish now / cancel

#### F7.4: Quick Actions
- "Fetch Trending Content" button
- "Generate Posts" button (opens batch generation)
- "Review Drafts" link (goes to post manager with draft filter)
- "Connect Platform" link (goes to settings if no platforms connected)

#### F7.5: Content Source Health
- Status indicators for each content source
- Shows: last fetch time, items fetched, any errors
- Helps user know if a source API is down

---

## 9. Module 8: Settings & Platform Management

### 9.1 Features

#### F8.1: Platform Connection - Twitter
- "Connect Twitter" button initiates OAuth 2.0 flow
- Redirects to Twitter authorization page
- On callback, stores encrypted access/refresh tokens
- Shows connected account name and avatar
- "Disconnect" button to revoke and remove tokens

#### F8.2: Platform Connection - LinkedIn
- "Connect LinkedIn" button initiates OAuth 2.0 flow
- Redirects to LinkedIn authorization page
- On callback, stores encrypted access/refresh tokens
- Shows connected account name
- "Disconnect" button

#### F8.3: Connection Status
- Visual indicator (green/red) for each platform
- Shows: connected account name, token expiry status
- Auto-refresh tokens before expiry

#### F8.4: Content Preferences
- Default tone selection (professional, casual, humorous)
- Preferred content types (checkboxes)
- Default AI model selection
- Timezone setting

#### F8.5: API Usage Monitor
- Show Claude API token usage (input/output tokens this month)
- Estimated cost this month
- Twitter API usage (tweets posted this month vs 1,500 limit)

#### F8.6: Content Source Configuration (Full Customization)
- Enable/disable individual content sources (toggle per source)
- **Reddit:** User can add/remove subreddits to follow (text input with add/remove buttons)
- **Dev.to:** User can set tag filters (e.g., only fetch articles tagged "javascript", "ai")
- **GitHub Trending:** User can filter by programming language
- Set fetch frequency override per source (every 1h, 2h, 4h, 6h, 12h)
- Default subreddits pre-configured but fully editable

---

## 10. Module 9: Authentication

### 10.1 Features

#### F9.1: User Registration
- Email + password registration
- Password strength requirements (min 8 chars, mixed case, number)
- Email validation

#### F9.2: User Login
- Email + password login
- JWT token issued (15 min expiry)
- Refresh token in httponly cookie (7 days)

#### F9.3: Session Management
- Auto-refresh JWT before expiry
- Logout clears all tokens
- Session persists across page refreshes

#### F9.4: Profile Management
- Update display name
- Change password
- View account creation date

---

## 10b. Module 10: Comment Management (AI-Powered Replies)

### 10b.1 Features

#### F10.1: Comment Fetching
- System periodically fetches new comments on published posts from Twitter and LinkedIn
- Comments stored locally with: commenter name, comment text, timestamp, platform, post reference
- Dashboard notification when new comments arrive

#### F10.2: AI-Generated Reply Suggestions
- For each new comment, AI analyzes the comment context and the original post
- Generates a contextually appropriate reply suggestion
- Reply considers: comment sentiment, question detection, topic relevance
- Reply matches the tone of the original post (professional, casual, etc.)

#### F10.3: Review & Send Reply Workflow (Default Mode)
- New comments appear in a "Comments" section on the dashboard or Post Manager
- Each comment shows: commenter info, comment text, AI-suggested reply
- User can: edit the reply, approve and send, or dismiss
- Sent replies are tracked and linked to the original comment

#### F10.4: Auto-Reply Mode (Configurable)
- Users can enable auto-reply per platform or globally
- System automatically sends AI-generated replies without human review
- Configurable filters: auto-reply only to questions, only to positive comments, etc.
- Rate limit on auto-replies (max 10/hour) to avoid spam detection
- Auto-reply can be disabled at any time

#### F10.5: Mention Detection & Auto-Reply
- System detects when the user is @mentioned in posts or comments on Twitter/LinkedIn
- Mentions trigger a notification in the dashboard (highlighted with priority badge)
- AI generates a contextual reply to the mention, considering the mention context
- Mention replies are prioritized over regular comment replies in the review queue
- Auto-reply mode can auto-respond to mentions (if enabled)
- Rate limit on mention auto-replies (separate from comment auto-replies)

#### F10.6: Comment Analytics
- Track reply rate (% of comments that received a reply)
- Track average response time (time between comment and reply)
- Track sentiment of incoming comments (positive/neutral/negative)
- Show most engaging posts (by comment count)
- Show mention frequency and response rate

---

## 10c. Module 11: LinkedIn Profile Intelligence (Lead Generation)

### 10c.1 Features

#### F11.1: Profile Data Collection from Engagers
- When someone comments on, likes, or engages with a published LinkedIn post, the system collects their publicly available profile data
- Data collected: full name, headline, profile URL, current company, industry, location, connection/follower count
- Profiles are deduplicated by LinkedIn profile URL
- System fetches profile data in the background (via Celery worker) to avoid slowing down comment fetch

#### F11.2: Status Detection (AI-Powered)
- AI analyzes the collected profile headline and about text to classify the person's status:
  - **OPEN TO WORK** - Detected from headline keywords ("Open to work", "Looking for opportunities", "Seeking new role", "#OpenToWork")
  - **HIRING** - Detected from headline keywords ("Hiring", "We're hiring", "Looking for talent", "#Hiring")
  - **Looking for Business** - Detected from keywords ("Looking for partners", "Open to collaborations", "Seeking clients", "Business inquiries welcome")
  - **General** - No specific status detected
- AI classification considers the full context of headline + about section, not just keyword matching
- Status is stored and can be updated on subsequent profile scans

#### F11.3: Contact Information Extraction
- System collects publicly accessible contact information from LinkedIn profiles:
  - **Email** - If made public on the profile (via LinkedIn API `r_emailaddress` scope for connections, or visible in contact info)
  - **Phone/Mobile** - If made public on the profile
  - **Website/Portfolio** - Personal or business website URL
  - **Twitter/X handle** - If listed on the profile
- Contact info is only collected when publicly available; the system never scrapes or circumvents privacy settings
- Contact info availability is clearly marked (available / not public)

#### F11.4: Lead Management Dashboard
- Dedicated "Leads" page showing all collected profiles as a searchable, filterable table
- Columns: Name, Headline, Company, Status (OPEN TO WORK/HIRING/etc.), Industry, Location, Email, Phone, Engagement Count, Last Engaged, Profile Link
- Filter by: Status type, Industry, Has Email, Has Phone, Engagement date range
- Sort by: Engagement count (most engaged first), Recency, Name
- Click on a profile row to expand full details

#### F11.5: Lead Categorization & Tagging
- Users can manually add tags to leads (e.g., "Potential Client", "Recruiter", "Partner", "Follow Up")
- Auto-tags based on AI status detection (OPEN TO WORK, HIRING, etc.)
- Users can add private notes to any lead
- Star/favorite leads for quick access

#### F11.6: Lead Export
- Export leads as CSV with selected columns
- Filter before export (e.g., export only HIRING leads with email)
- Export includes: Name, Headline, Company, Status, Email, Phone, Website, Profile URL, Tags, Notes, Last Engaged date

#### F11.7: Engagement Tracking per Lead
- Track how many times a lead has engaged with your posts
- Track types of engagement: comments, likes, shares
- Show engagement history timeline per lead
- Identify "hot leads" - people who engage frequently

#### F11.8: Privacy & Compliance
- Only collect publicly accessible data (respect LinkedIn privacy settings)
- Users can delete any lead's data (right to be forgotten)
- System clearly marks data source (LinkedIn public profile)
- No automated outreach or messaging (data collection only)
- Comply with LinkedIn API Terms of Service

---

## 11. Platform-Specific Features

### 11.1 Twitter/X Specific
| Feature | Details |
|---------|---------|
| Character limit | 280 characters (enforced in editor with counter) |
| Hashtags | 2-3 recommended, generated by AI |
| Posting format | Single tweet (no threads in V1) |
| Tone | Tends toward casual, engaging, concise |
| Metrics | Impressions, likes, retweets, replies, clicks |
| Rate limit | 1,500 tweets/month (free tier) |

### 11.2 LinkedIn Specific
| Feature | Details |
|---------|---------|
| Character limit | 3,000 characters |
| Hashtags | 3-5 recommended, professional |
| Posting format | Long-form text post |
| Tone | Professional, thought leadership |
| Metrics | Impressions, likes, comments, shares, clicks |
| Formatting | Line breaks, emojis (professional use), bullet points |
| Post structure | Hook line → Body → Call to action → Hashtags |

---

## 12. MoSCoW Prioritization

### Must Have (MVP - V1.0)
| ID | Feature | Module |
|----|---------|--------|
| M1 | Automated content aggregation from tech + business + marketing sources | Content Research |
| M2 | Content feed browser with source/category filtering | Content Research |
| M3 | AI post generation for Twitter (280 char) | AI Generation |
| M4 | AI post generation for LinkedIn (long-form) | AI Generation |
| M5 | Post editor with character counter | Post Management |
| M6 | Draft → Approve → Publish workflow | Post Management |
| M7 | Twitter OAuth + publishing | Publishing |
| M8 | LinkedIn OAuth + publishing | Publishing |
| M9 | User registration and login (JWT) | Authentication |
| M10 | Basic dashboard with stats and activity | Dashboard |
| M11 | Settings page with platform connections | Settings |
| M12 | Recurring schedules with cron expressions | Scheduling |
| M13 | Automated content pipeline (schedule → generate → publish) | Scheduling |
| M14 | Basic analytics (impressions, likes, comments) | Analytics |
| M15 | AI-powered comment reply suggestions (review & send) | Comment Management |
| M16 | Tone selection (professional, casual, humorous) | AI Generation |
| M17 | Publish error handling with retry | Publishing |
| M18 | LinkedIn profile data collection from post engagers | Profile Intelligence |
| M19 | AI-powered status detection (OPEN TO WORK, HIRING, Looking for Business) | Profile Intelligence |
| M20 | Lead management dashboard with search/filter | Profile Intelligence |

### Should Have (V1.1)
| ID | Feature | Module |
|----|---------|--------|
| S1 | Auto-reply mode for comments (configurable) | Comment Management |
| S2 | Custom content types with user-defined prompt templates | AI Generation |
| S3 | Post preview (Twitter/LinkedIn mock) | Post Management |
| S4 | Batch generation from multiple content items | AI Generation |
| S5 | API usage monitor | Settings |
| S6 | Comment sentiment analysis | Comment Management |
| S7 | Content source health monitoring | Dashboard |
| S8 | Contact information extraction (email, phone, website) | Profile Intelligence |
| S9 | Lead tagging and notes | Profile Intelligence |
| S10 | Lead export as CSV | Profile Intelligence |

### Could Have (V1.2)
| ID | Feature | Module |
|----|---------|--------|
| C1 | Auto-approve mode on schedules | Scheduling |
| C2 | Content type performance breakdown | Analytics |
| C3 | Schedule calendar view | Scheduling |
| C4 | Regenerate post with different tone | AI Generation |
| C5 | Bulk approve/reject/schedule | Post Management |
| C6 | Top performing posts analysis | Analytics |
| C7 | Engagement over time charts | Analytics |
| C8 | Post deletion from platform | Publishing |
| C9 | Comment analytics (reply rate, sentiment) | Comment Management |
| C10 | Engagement tracking per lead (frequency, history) | Profile Intelligence |
| C11 | Hot leads identification (frequent engagers) | Profile Intelligence |

### Won't Have (V1, consider for V2+)
| ID | Feature | Reason |
|----|---------|--------|
| W1 | Image/media generation (DALL-E) | Different product scope |
| W2 | Twitter thread creation | Complex, V2 feature |
| W3 | LinkedIn carousel posts | Requires image generation |
| W4 | Team collaboration / multi-user | Complexity for MVP |
| W5 | Social listening / brand monitoring | Requires expensive APIs |
| W6 | Instagram / TikTok posting | Different content format |
| W7 | Mobile app | Web-responsive is sufficient |
| W8 | A/B testing of posts | Needs larger data set |
| W9 | Drag-and-drop schedule calendar | UI complexity |
| W10 | Content repurposing (blog → posts) | V2 feature |

---

## 13. User Stories

### Content Research
| ID | User Story | Acceptance Criteria |
|----|-----------|-------------------|
| US-1 | As a user, I want the system to automatically fetch trending tech content so I don't have to manually browse multiple sites | Content from 6 sources fetched every 2 hours; visible in content feed |
| US-2 | As a user, I want to filter content by source type so I can focus on specific categories | Tabs for each source type; count badge; instant filtering |
| US-3 | As a user, I want to see popularity scores so I can prioritize high-engagement topics | Score displayed on each card; sortable by score |
| US-4 | As a user, I want to manually trigger a content refresh when I need fresh content | "Refresh" button; loading indicator; new items count shown |

### AI Generation
| ID | User Story | Acceptance Criteria |
|----|-----------|-------------------|
| US-5 | As a user, I want to generate a Twitter post from a trending article with one click | "Generate Post" button on content card; post created within 5 seconds; respects 280 char limit |
| US-6 | As a user, I want to generate a LinkedIn post with professional tone from the same content | Platform selector before generation; LinkedIn post is 300-700 words with thought leadership angle |
| US-7 | As a user, I want AI to suggest relevant hashtags | 2-3 hashtags for Twitter, 3-5 for LinkedIn; editable by user |
| US-8 | As a user, I want to choose the tone of my post | Tone dropdown (professional, casual, humorous, educational); affects generated content |
| US-9 | As a user, I want to generate posts from multiple items at once to save time | Checkbox selection + "Generate Batch" button; all posts created as drafts |

### Post Management
| ID | User Story | Acceptance Criteria |
|----|-----------|-------------------|
| US-10 | As a user, I want to review AI-generated posts before they go live | All generated posts start as "draft"; visible in review queue |
| US-11 | As a user, I want to edit a generated post to add my personal touch | Editable text area; character counter; save button |
| US-12 | As a user, I want to approve or reject posts | Approve/Reject buttons; post status updates; toast notification |
| US-13 | As a user, I want to see how my post will look on the platform before publishing | Preview panel showing platform-specific mock rendering |
| US-14 | As a user, I want to publish an approved post immediately | "Publish Now" button with confirmation; success/failure feedback |
| US-15 | As a user, I want to schedule a post for a specific date and time | Date/time picker; timezone-aware; post moves to "Scheduled" |

### Publishing
| ID | User Story | Acceptance Criteria |
|----|-----------|-------------------|
| US-16 | As a user, I want my post published to Twitter when I click publish | Post appears on my Twitter timeline; platform post ID stored |
| US-17 | As a user, I want my post published to LinkedIn | Post appears on my LinkedIn feed; post URN stored |
| US-18 | As a user, I want to see a link to my published post on the platform | Clickable URL to the live post |
| US-19 | As a user, I want to know if a publish failed and be able to retry | Error message shown; retry button; clear error categorization |

### Scheduling
| ID | User Story | Acceptance Criteria |
|----|-----------|-------------------|
| US-20 | As a user, I want to set up a recurring schedule to post automatically | Schedule form with platform, content types, cron timing, timezone |
| US-21 | As a user, I want the system to auto-generate content for my schedule | System picks top content, generates post, queues for review/auto-publish |
| US-22 | As a user, I want to pause and resume schedules | Toggle switch on schedule; paused schedules don't trigger |
| US-23 | As a user, I want to choose whether scheduled posts need my review | Auto-approve toggle per schedule; default: review required |

### Analytics
| ID | User Story | Acceptance Criteria |
|----|-----------|-------------------|
| US-24 | As a user, I want to see how my posts are performing | Analytics page with engagement metrics per post |
| US-25 | As a user, I want to compare Twitter vs LinkedIn performance | Side-by-side platform comparison chart |
| US-26 | As a user, I want to identify my best-performing posts | Top posts table sorted by engagement rate |
| US-27 | As a user, I want to understand which content types work best | Content type breakdown with engagement metrics |

### Settings
| ID | User Story | Acceptance Criteria |
|----|-----------|-------------------|
| US-28 | As a user, I want to connect my Twitter account | OAuth flow; connected account shown with name/avatar |
| US-29 | As a user, I want to connect my LinkedIn account | OAuth flow; connected account shown with name |
| US-30 | As a user, I want to disconnect a platform | "Disconnect" button; confirmation; tokens removed |
| US-31 | As a user, I want to see my API usage and costs | Token usage display; estimated monthly cost; Twitter post count vs limit |
| US-32 | As a user, I want to set my default preferences | Default tone, content types, AI model, timezone saved |

### Comment Management
| ID | User Story | Acceptance Criteria |
|----|-----------|-------------------|
| US-33 | As a user, I want to see new comments on my published posts | Comments fetched periodically; shown in dashboard with commenter info |
| US-34 | As a user, I want AI to suggest a reply to each comment | AI analyzes comment context + original post; generates contextual reply |
| US-35 | As a user, I want to review, edit, and send AI-suggested replies | Edit reply text; approve and send; or dismiss. Reply posted to platform |
| US-36 | As a user, I want to enable auto-reply for certain comment types | Toggle auto-reply per platform; filter by question/positive; rate limited |
| US-37 | As a user, I want to see comment engagement stats | Reply rate, comment sentiment breakdown, most engaging posts |

### Custom Content Types
| ID | User Story | Acceptance Criteria |
|----|-----------|-------------------|
| US-38 | As a user, I want to create custom content types with my own prompt templates | Form with name + prompt template; supports variables; saved to DB |
| US-39 | As a user, I want my custom types to appear in the generation UI | Custom types listed alongside preset types when generating a post |
| US-40 | As a user, I want to edit or delete my custom content types | Edit/delete buttons on each custom type; changes apply to future generations |

### LinkedIn Profile Intelligence
| ID | User Story | Acceptance Criteria |
|----|-----------|-------------------|
| US-44 | As a user, I want to automatically collect profile data of people who engage with my LinkedIn posts | Profile data (name, headline, company, profile URL) collected for commenters and likers; visible in Leads page |
| US-45 | As a user, I want AI to detect if someone is OPEN TO WORK, HIRING, or Looking for Business | AI classifies status from headline/about text; status badge shown on each lead |
| US-46 | As a user, I want to see email and phone numbers of leads if publicly available | Contact info extracted from public profiles; marked as "available" or "not public" |
| US-47 | As a user, I want to search and filter my leads by status, industry, or contact availability | Leads table with search bar, filters for status/industry/has-email/has-phone |
| US-48 | As a user, I want to tag leads and add notes for follow-up | Tag input on lead detail; notes text area; tags visible in list view |
| US-49 | As a user, I want to export my leads as a CSV file | Export button with column selection; filters applied before export |
| US-50 | As a user, I want to see how often a lead engages with my posts | Engagement count and history timeline on lead detail view |
| US-51 | As a user, I want to delete a lead's data for privacy compliance | Delete button on lead; confirmation dialog; all data removed |

### Dashboard
| ID | User Story | Acceptance Criteria |
|----|-----------|-------------------|
| US-41 | As a user, I want a quick overview when I open the app | Stats cards, recent activity, upcoming posts, new comments visible |
| US-42 | As a user, I want quick actions to common tasks | Buttons for fetch content, generate posts, review drafts, reply to comments |
| US-43 | As a user, I want to know if content sources are healthy | Status indicators showing last fetch time and any errors |
