import api from "./client"

export interface LeadEngagement {
  id: string
  engagement_type: string
  engagement_text: string | null
  engaged_at: string
}

export interface Lead {
  id: string
  linkedin_member_id: string
  name: string | null
  headline: string | null
  current_company: string | null
  profile_url: string | null
  email: string | null
  location: string | null
  industry: string | null
  ai_status: string | null
  tags: string[] | null
  notes: string | null
  created_at: string
  updated_at: string
  engagements: LeadEngagement[]
}

export interface LeadListResponse {
  items: Lead[]
  total: number
  page: number
  page_size: number
  pages: number
}

export interface LeadStats {
  total_leads: number
  open_to_work: number
  hiring: number
  has_email: number
}

export async function fetchLeads(params?: {
  search?: string
  ai_status?: string
  tag?: string
  sort_by?: string
  sort_order?: string
  page?: number
  page_size?: number
}): Promise<LeadListResponse> {
  const { data } = await api.get("/leads", { params })
  return data
}

export async function fetchLead(leadId: string): Promise<Lead> {
  const { data } = await api.get(`/leads/${leadId}`)
  return data
}

export async function updateLead(leadId: string, payload: { tags?: string[]; notes?: string }): Promise<Lead> {
  const { data } = await api.patch(`/leads/${leadId}`, payload)
  return data
}

export async function deleteLead(leadId: string): Promise<void> {
  await api.delete(`/leads/${leadId}`)
}

export async function fetchLeadStats(): Promise<LeadStats> {
  const { data } = await api.get("/leads/stats")
  return data
}

export function getExportUrl(aiStatus?: string): string {
  const base = "/api/v1/leads/export"
  return aiStatus ? `${base}?ai_status=${aiStatus}` : base
}
