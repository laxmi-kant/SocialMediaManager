import api from "./client"

export interface PlatformAccount {
  id: string
  platform: string
  platform_user_id: string | null
  display_name: string | null
  is_active: boolean
  token_expires_at: string | null
  scopes: string[] | null
  created_at: string
}

export interface PlatformListResponse {
  platforms: PlatformAccount[]
}

export async function fetchPlatforms(): Promise<PlatformListResponse> {
  const { data } = await api.get("/platforms")
  return data
}

export async function disconnectPlatform(platformId: string): Promise<void> {
  await api.delete(`/platforms/${platformId}`)
}

export function getTwitterAuthUrl(): string {
  return "/api/v1/platforms/twitter/authorize"
}

export function getLinkedInAuthUrl(): string {
  return "/api/v1/platforms/linkedin/authorize"
}
