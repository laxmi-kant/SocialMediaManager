import { create } from "zustand"
import api from "@/api/client"

interface User {
  id: string
  email: string
  full_name: string | null
  is_active: boolean
  created_at: string
}

interface AuthState {
  user: User | null
  loading: boolean
  error: string | null
  login: (email: string, password: string) => Promise<void>
  register: (email: string, password: string, fullName?: string) => Promise<void>
  logout: () => Promise<void>
  fetchMe: () => Promise<void>
  clearError: () => void
}

export const useAuthStore = create<AuthState>((set) => ({
  user: null,
  loading: false,
  error: null,

  login: async (email, password) => {
    set({ loading: true, error: null })
    try {
      await api.post("/auth/login", { email, password })
      const { data } = await api.get("/auth/me")
      set({ user: data, loading: false })
    } catch (err: unknown) {
      const message =
        (err as { response?: { data?: { detail?: string } } }).response?.data?.detail || "Login failed"
      set({ error: message, loading: false })
      throw err
    }
  },

  register: async (email, password, fullName) => {
    set({ loading: true, error: null })
    try {
      await api.post("/auth/register", { email, password, full_name: fullName || null })
      // Auto-login after register
      await api.post("/auth/login", { email, password })
      const { data } = await api.get("/auth/me")
      set({ user: data, loading: false })
    } catch (err: unknown) {
      const message =
        (err as { response?: { data?: { detail?: string } } }).response?.data?.detail || "Registration failed"
      set({ error: message, loading: false })
      throw err
    }
  },

  logout: async () => {
    try {
      await api.post("/auth/logout")
    } finally {
      set({ user: null })
      window.location.href = "/login"
    }
  },

  fetchMe: async () => {
    try {
      const { data } = await api.get("/auth/me")
      set({ user: data })
    } catch {
      set({ user: null })
    }
  },

  clearError: () => set({ error: null }),
}))
