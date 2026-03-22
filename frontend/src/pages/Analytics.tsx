import { useCallback, useEffect, useState } from "react"
import { type AnalyticsSummary, fetchAnalytics } from "@/api/analytics"
import { EngagementChart } from "@/components/analytics/EngagementChart"
import { PlatformBreakdown } from "@/components/analytics/PlatformBreakdown"
import { TopPostsTable } from "@/components/analytics/TopPostsTable"
import { Button } from "@/components/ui/button"
import { Card, CardContent } from "@/components/ui/card"

export default function Analytics() {
  const [data, setData] = useState<AnalyticsSummary | null>(null)
  const [loading, setLoading] = useState(true)
  const [days, setDays] = useState(30)
  const [platform, setPlatform] = useState("")

  const load = useCallback(async () => {
    setLoading(true)
    try {
      const resp = await fetchAnalytics({
        days,
        platform: platform || undefined,
      })
      setData(resp)
    } finally {
      setLoading(false)
    }
  }, [days, platform])

  useEffect(() => {
    load()
  }, [load])

  return (
    <div className="space-y-4">
      <h2 className="text-2xl font-semibold">Analytics</h2>

      <div className="flex gap-2 flex-wrap">
        {[7, 14, 30, 90].map((d) => (
          <Button key={d} size="sm" variant={days === d ? "default" : "outline"} onClick={() => setDays(d)}>
            {d}d
          </Button>
        ))}
        <div className="border-l border-border mx-1" />
        {["", "twitter", "linkedin"].map((p) => (
          <Button key={p} size="sm" variant={platform === p ? "default" : "outline"} onClick={() => setPlatform(p)}>
            {p === "" ? "All" : p === "twitter" ? "Twitter/X" : "LinkedIn"}
          </Button>
        ))}
      </div>

      {loading ? (
        <div className="space-y-4">
          {[0, 1, 2].map((i) => (
            <div key={i} className="h-40 rounded-lg bg-muted animate-pulse" />
          ))}
        </div>
      ) : data ? (
        <>
          <div className="grid grid-cols-2 md:grid-cols-5 gap-3">
            {[
              { label: "Posts", value: data.total_posts },
              { label: "Impressions", value: data.total_impressions.toLocaleString() },
              { label: "Likes", value: data.total_likes.toLocaleString() },
              { label: "Comments", value: data.total_comments.toLocaleString() },
              { label: "Eng. Rate", value: `${data.avg_engagement_rate}%` },
            ].map((stat) => (
              <Card key={stat.label}>
                <CardContent className="pt-4 pb-3 text-center">
                  <p className="text-2xl font-bold">{stat.value}</p>
                  <p className="text-xs text-muted-foreground">{stat.label}</p>
                </CardContent>
              </Card>
            ))}
          </div>

          <EngagementChart posts={data.posts} />

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
            <PlatformBreakdown posts={data.posts} />
            <TopPostsTable posts={data.posts} />
          </div>
        </>
      ) : null}
    </div>
  )
}
