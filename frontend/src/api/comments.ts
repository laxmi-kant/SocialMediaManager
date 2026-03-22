import api from "./client"

export interface CommentReply {
  id: string
  comment_id: string
  reply_text: string
  ai_suggested_text: string | null
  reply_mode: string
  status: string
  sent_at: string | null
  created_at: string
}

export interface Comment {
  id: string
  published_post_id: string
  platform: string
  platform_comment_id: string
  commenter_name: string | null
  commenter_username: string | null
  commenter_profile_url: string | null
  commenter_follower_count: number | null
  comment_text: string
  is_mention: boolean
  sentiment: string | null
  comment_type: string | null
  commented_at: string | null
  created_at: string
  replies: CommentReply[]
}

export interface CommentListResponse {
  items: Comment[]
  total: number
  page: number
  page_size: number
  pages: number
}

export interface CommentStats {
  total_comments: number
  unreplied_comments: number
  replied_comments: number
}

export async function fetchComments(params?: {
  sentiment?: string
  comment_type?: string
  page?: number
  page_size?: number
}): Promise<CommentListResponse> {
  const { data } = await api.get("/comments", { params })
  return data
}

export async function generateReply(commentId: string, tone?: string): Promise<CommentReply> {
  const { data } = await api.post(`/comments/${commentId}/generate-reply`, { tone: tone || "professional" })
  return data
}

export async function sendReply(commentId: string, replyText: string): Promise<CommentReply> {
  const { data } = await api.post(`/comments/${commentId}/reply`, { reply_text: replyText })
  return data
}

export async function fetchCommentStats(): Promise<CommentStats> {
  const { data } = await api.get("/comments/stats")
  return data
}
