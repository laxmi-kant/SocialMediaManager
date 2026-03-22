import { NavLink } from "react-router-dom"
import {
  LayoutDashboard,
  Newspaper,
  FileText,
  BarChart3,
  MessageSquare,
  Users,
  Settings,
} from "lucide-react"

const navItems = [
  { to: "/", icon: LayoutDashboard, label: "Dashboard" },
  { to: "/content", icon: Newspaper, label: "Content" },
  { to: "/posts", icon: FileText, label: "Posts" },
  { to: "/analytics", icon: BarChart3, label: "Analytics" },
  { to: "/comments", icon: MessageSquare, label: "Comments" },
  { to: "/leads", icon: Users, label: "Leads" },
  { to: "/settings", icon: Settings, label: "Settings" },
]

export function Sidebar() {
  return (
    <aside className="fixed left-0 top-0 h-screen w-60 border-r border-border bg-sidebar flex flex-col">
      <div className="p-4 border-b border-border">
        <h1 className="text-lg font-semibold text-sidebar-foreground">SMM</h1>
        <p className="text-xs text-muted-foreground">Social Media Manager</p>
      </div>
      <nav className="flex-1 p-2 space-y-1">
        {navItems.map((item) => (
          <NavLink
            key={item.to}
            to={item.to}
            end={item.to === "/"}
            className={({ isActive }) =>
              `flex items-center gap-3 px-3 py-2 rounded-md text-sm transition-colors ${
                isActive
                  ? "bg-sidebar-accent text-sidebar-primary font-medium"
                  : "text-sidebar-foreground hover:bg-sidebar-accent"
              }`
            }
          >
            <item.icon className="h-4 w-4" />
            {item.label}
          </NavLink>
        ))}
      </nav>
    </aside>
  )
}
