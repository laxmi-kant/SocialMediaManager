import { LogOut, User } from "lucide-react"
import { Button } from "@/components/ui/button"
import { useAuthStore } from "@/store/authStore"

export function Header() {
  const { user, logout } = useAuthStore()

  return (
    <header className="sticky top-0 z-10 h-14 border-b border-border bg-background/95 backdrop-blur flex items-center justify-between px-6">
      <div />
      <div className="flex items-center gap-3">
        {user && (
          <span className="flex items-center gap-2 text-sm text-muted-foreground">
            <User className="h-4 w-4" />
            {user.full_name || user.email}
          </span>
        )}
        <Button variant="ghost" size="sm" onClick={logout}>
          <LogOut className="h-4 w-4" />
        </Button>
      </div>
    </header>
  )
}
