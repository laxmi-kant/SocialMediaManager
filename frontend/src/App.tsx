import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom"
import { useEffect } from "react"
import { Toaster } from "@/components/ui/sonner"
import { ErrorBoundary } from "@/components/common/ErrorBoundary"
import { MainLayout } from "@/components/layout/MainLayout"
import { useAuthStore } from "@/store/authStore"
import Login from "@/pages/Login"
import Register from "@/pages/Register"
import Dashboard from "@/pages/Dashboard"
import Content from "@/pages/Content"
import Posts from "@/pages/Posts"
import Analytics from "@/pages/Analytics"
import Comments from "@/pages/Comments"
import Leads from "@/pages/Leads"
import SettingsPage from "@/pages/SettingsPage"

function ProtectedRoute({ children }: { children: React.ReactNode }) {
  const { user } = useAuthStore()
  if (!user) return <Navigate to="/login" replace />
  return <>{children}</>
}

export default function App() {
  const { fetchMe } = useAuthStore()

  useEffect(() => {
    fetchMe()
  }, [fetchMe])

  return (
    <BrowserRouter>
      <Toaster position="top-right" richColors />
      <Routes>
        <Route path="/login" element={<Login />} />
        <Route path="/register" element={<Register />} />
        <Route
          element={
            <ProtectedRoute>
              <MainLayout />
            </ProtectedRoute>
          }
        >
          <Route path="/" element={<ErrorBoundary><Dashboard /></ErrorBoundary>} />
          <Route path="/content" element={<ErrorBoundary><Content /></ErrorBoundary>} />
          <Route path="/posts" element={<ErrorBoundary><Posts /></ErrorBoundary>} />
          <Route path="/analytics" element={<ErrorBoundary><Analytics /></ErrorBoundary>} />
          <Route path="/comments" element={<ErrorBoundary><Comments /></ErrorBoundary>} />
          <Route path="/leads" element={<ErrorBoundary><Leads /></ErrorBoundary>} />
          <Route path="/settings" element={<ErrorBoundary><SettingsPage /></ErrorBoundary>} />
        </Route>
      </Routes>
    </BrowserRouter>
  )
}
