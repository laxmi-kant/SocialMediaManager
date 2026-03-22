import api from "./client"

export interface Post {
  id: string
  user_id: string
  content_source_id: string | null
  target_platform: string
  content_text: string
  content_type: string
  tone: string
  hashtags: string[] | null
  ai_model: string | null
  token_usage: { input_tokens: number; output_tokens: number } | null
  status: string
  scheduled_for: string | null
  created_at: string
  updated_at: string
}

export interface PostListResponse {
  items: Post[]
  total: number
  page: number
  page_size: number
  pages: number
}

export async function fetchPosts(params: {
  status?: string
  target_platform?: string
  page?: number
  page_size?: number
}): Promise<PostListResponse> {
  const { data } = await api.get("/posts", { params })
  return data
}

export async function generatePost(contentId: string, body: {
  target_platform: string
  content_type: string
  tone?: string
}): Promise<Post> {
  const { data } = await api.post(`/content/${contentId}/generate`, body)
  return data
}

export async function updatePost(postId: string, body: {
  content_text?: string
  hashtags?: string[]
  tone?: string
}): Promise<Post> {
  const { data } = await api.put(`/posts/${postId}`, body)
  return data
}

export async function approvePost(postId: string): Promise<Post> {
  const { data } = await api.post(`/posts/${postId}/approve`)
  return data
}

export async function rejectPost(postId: string): Promise<Post> {
  const { data } = await api.post(`/posts/${postId}/reject`)
  return data
}

export async function deletePost(postId: string): Promise<void> {
  await api.delete(`/posts/${postId}`)
}

export async function schedulePost(postId: string, scheduledFor: string): Promise<Post> {
  const { data } = await api.post(`/posts/${postId}/schedule`, { scheduled_for: scheduledFor })
  return data
}

export async function publishPost(postId: string): Promise<Post> {
  const { data } = await api.post(`/posts/${postId}/publish`)
  return data
}
