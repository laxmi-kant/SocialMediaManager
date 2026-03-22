import type { PostAnalytics } from "@/api/analytics"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"

interface PlatformBreakdownProps {
  posts: PostAnalytics[]
}

export function PlatformBreakdown({ posts }: PlatformBreakdownProps) {
  const byPlatform = posts.reduce<Record<string, { count: number; likes: number; comments: number; shares: number; impressions: number }>>(
    (acc, p) => {
      if (!acc[p.platform]) {
        acc[p.platform] = { count: 0, likes: 0, comments: 0, shares: 0, impressions: 0 }
      }
      acc[p.platform].count++
      acc[p.platform].likes += p.likes
      acc[p.platform].comments += p.comments
      acc[p.platform].shares += p.shares
      acc[p.platform].impressions += p.impressions
      return acc
    },
    {},
  )

  const platformLabels: Record<string, string> = {
    twitter: "Twitter/X",
    linkedin: "LinkedIn",
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-base">Platform Breakdown</CardTitle>
      </CardHeader>
      <CardContent>
        {Object.keys(byPlatform).length === 0 ? (
          <p className="text-sm text-muted-foreground text-center py-4">No data yet.</p>
        ) : (
          <div className="space-y-4">
            {Object.entries(byPlatform).map(([platform, stats]) => (
              <div key={platform} className="space-y-1">
                <div className="flex items-center justify-between">
                  <span className="text-sm font-medium">{platformLabels[platform] || platform}</span>
                  <span className="text-xs text-muted-foreground">{stats.count} posts</span>
                </div>
                <div className="grid grid-cols-4 gap-2 text-center">
                  <div>
                    <p className="text-lg font-semibold">{stats.impressions.toLocaleString()}</p>
                    <p className="text-[10px] text-muted-foreground">Impressions</p>
                  </div>
                  <div>
                    <p className="text-lg font-semibold">{stats.likes.toLocaleString()}</p>
                    <p className="text-[10px] text-muted-foreground">Likes</p>
                  </div>
                  <div>
                    <p className="text-lg font-semibold">{stats.comments.toLocaleString()}</p>
                    <p className="text-[10px] text-muted-foreground">Comments</p>
                  </div>
                  <div>
                    <p className="text-lg font-semibold">{stats.shares.toLocaleString()}</p>
                    <p className="text-[10px] text-muted-foreground">Shares</p>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </CardContent>
    </Card>
  )
}
