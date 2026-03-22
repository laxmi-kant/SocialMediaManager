import { Bar, BarChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts"
import type { PostAnalytics } from "@/api/analytics"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"

interface EngagementChartProps {
  posts: PostAnalytics[]
}

export function EngagementChart({ posts }: EngagementChartProps) {
  const data = posts.slice(0, 10).map((p, i) => ({
    name: `Post ${i + 1}`,
    likes: p.likes,
    comments: p.comments,
    shares: p.shares,
    impressions: p.impressions,
  }))

  if (data.length === 0) {
    return (
      <Card>
        <CardHeader>
          <CardTitle className="text-base">Engagement Overview</CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-sm text-muted-foreground text-center py-8">
            No engagement data yet. Publish posts to see analytics.
          </p>
        </CardContent>
      </Card>
    )
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-base">Engagement Overview</CardTitle>
      </CardHeader>
      <CardContent>
        <ResponsiveContainer width="100%" height={300}>
          <BarChart data={data}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="name" tick={{ fontSize: 12 }} />
            <YAxis tick={{ fontSize: 12 }} />
            <Tooltip />
            <Bar dataKey="likes" fill="hsl(142, 76%, 36%)" name="Likes" />
            <Bar dataKey="comments" fill="hsl(221, 83%, 53%)" name="Comments" />
            <Bar dataKey="shares" fill="hsl(262, 83%, 58%)" name="Shares" />
          </BarChart>
        </ResponsiveContainer>
      </CardContent>
    </Card>
  )
}
