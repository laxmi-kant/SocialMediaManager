import { useEffect, useState } from "react"
import { Clock, FileText, Heart, Send, TrendingUp } from "lucide-react"
import { type DashboardStats, fetchDashboard } from "@/api/analytics"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"

export default function Dashboard() {
  const [stats, setStats] = useState<DashboardStats | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchDashboard()
      .then(setStats)
      .finally(() => setLoading(false))
  }, [])

  if (loading) {
    return (
      <div>
        <h2 className="text-2xl font-semibold mb-6">Dashboard</h2>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          {[0, 1, 2, 3].map((i) => (
            <div key={i} className="h-24 rounded-lg bg-muted animate-pulse" />
          ))}
        </div>
      </div>
    )
  }

  const statCards = [
    { label: "Total Posts", value: stats?.total_posts ?? 0, icon: FileText },
    { label: "Published", value: stats?.published_posts ?? 0, icon: Send },
    { label: "Scheduled", value: stats?.scheduled_posts ?? 0, icon: Clock },
    { label: "Engagement", value: `${stats?.avg_engagement_rate ?? 0}%`, icon: TrendingUp },
  ]

  return (
    <div className="space-y-6">
      <h2 className="text-2xl font-semibold">Dashboard</h2>

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {statCards.map((stat) => (
          <Card key={stat.label}>
            <CardHeader className="flex flex-row items-center justify-between pb-2">
              <CardTitle className="text-sm font-medium text-muted-foreground">
                {stat.label}
              </CardTitle>
              <stat.icon className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <p className="text-2xl font-bold">{stat.value}</p>
            </CardContent>
          </Card>
        ))}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card>
          <CardHeader>
            <CardTitle className="text-base">Recent Activity</CardTitle>
          </CardHeader>
          <CardContent>
            {stats?.recent_posts && stats.recent_posts.length > 0 ? (
              <div className="space-y-3">
                {stats.recent_posts.map((post) => (
                  <div key={post.id} className="flex items-start gap-3 text-sm">
                    <Send className="h-4 w-4 text-emerald-500 mt-0.5 shrink-0" />
                    <div className="min-w-0">
                      <p className="truncate">{post.text}</p>
                      <p className="text-xs text-muted-foreground">
                        {post.platform === "twitter" ? "Twitter/X" : "LinkedIn"} &middot;{" "}
                        {new Date(post.updated_at).toLocaleDateString()}
                      </p>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-sm text-muted-foreground text-center py-4">
                No recent activity. Start publishing posts!
              </p>
            )}
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="text-base">Upcoming Posts</CardTitle>
          </CardHeader>
          <CardContent>
            {stats?.upcoming_posts && stats.upcoming_posts.length > 0 ? (
              <div className="space-y-3">
                {stats.upcoming_posts.map((post) => (
                  <div key={post.id} className="flex items-start gap-3 text-sm">
                    <Clock className="h-4 w-4 text-blue-500 mt-0.5 shrink-0" />
                    <div className="min-w-0">
                      <p className="truncate">{post.text}</p>
                      <p className="text-xs text-muted-foreground">
                        {post.platform === "twitter" ? "Twitter/X" : "LinkedIn"} &middot;{" "}
                        {post.scheduled_for ? new Date(post.scheduled_for).toLocaleString() : "Pending"}
                      </p>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-sm text-muted-foreground text-center py-4">
                No upcoming posts. Schedule some posts!
              </p>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
