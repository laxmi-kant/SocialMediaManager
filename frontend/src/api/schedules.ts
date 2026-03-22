import api from "./client"

export interface Schedule {
  id: string
  user_id: string
  name: string
  platform: string
  content_types: string[]
  cron_expression: string
  timezone: string
  auto_approve: boolean
  is_active: boolean
  created_at: string
  updated_at: string
}

export interface ScheduleListResponse {
  items: Schedule[]
  total: number
}

export async function fetchSchedules(): Promise<ScheduleListResponse> {
  const { data } = await api.get("/schedules")
  return data
}

export async function createSchedule(body: {
  name: string
  platform: string
  content_types: string[]
  cron_expression: string
  timezone?: string
  auto_approve?: boolean
}): Promise<Schedule> {
  const { data } = await api.post("/schedules", body)
  return data
}

export async function updateSchedule(id: string, body: {
  name?: string
  content_types?: string[]
  cron_expression?: string
  timezone?: string
  auto_approve?: boolean
  is_active?: boolean
}): Promise<Schedule> {
  const { data } = await api.put(`/schedules/${id}`, body)
  return data
}

export async function deleteSchedule(id: string): Promise<void> {
  await api.delete(`/schedules/${id}`)
}
