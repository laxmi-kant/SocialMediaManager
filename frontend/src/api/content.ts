import api from "./client"

export interface ContentSource {
  id: string
  source_type: string
  external_id: string | null
  title: string
  url: string | null
  content: string | null
  author: string | null
  score: number
  tags: string[] | null
  metadata: Record<string, unknown> | null
  fetched_at: string
  created_at: string
}

export interface ContentListResponse {
  items: ContentSource[]
  total: number
  page: number
  page_size: number
  pages: number
}

export async function fetchContent(params: {
  source_type?: string
  sort_by?: string
  sort_order?: string
  page?: number
  page_size?: number
}): Promise<ContentListResponse> {
  const { data } = await api.get("/content", { params })
  return data
}

export async function fetchContentById(id: string): Promise<ContentSource> {
  const { data } = await api.get(`/content/${id}`)
  return data
}

export async function refreshContent(): Promise<{ message: string; task_id: string }> {
  const { data } = await api.post("/content/refresh")
  return data
}
