import api from "./client"

export interface PostAnalytics {
  post_id: string
  platform: string
  content_text: string
  published_at: string | null
  platform_url: string | null
  impressions: number
  likes: number
  comments: number
  shares: number
  clicks: number
  engagement_rate: number | null
}

export interface AnalyticsSummary {
  total_posts: number
  total_impressions: number
  total_likes: number
  total_comments: number
  total_shares: number
  avg_engagement_rate: number
  posts: PostAnalytics[]
}

export interface DashboardStats {
  total_posts: number
  published_posts: number
  scheduled_posts: number
  draft_posts: number
  total_impressions: number
  total_likes: number
  avg_engagement_rate: number
  recent_posts: Array<{
    id: string
    platform: string
    text: string
    status: string
    updated_at: string
  }>
  upcoming_posts: Array<{
    id: string
    platform: string
    text: string
    scheduled_for: string | null
  }>
}

export async function fetchAnalytics(params?: {
  days?: number
  platform?: string
}): Promise<AnalyticsSummary> {
  const { data } = await api.get("/analytics", { params })
  return data
}

export async function fetchDashboard(): Promise<DashboardStats> {
  const { data } = await api.get("/dashboard")
  return data
}
