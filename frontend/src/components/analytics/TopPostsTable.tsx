import { ExternalLink } from "lucide-react"
import type { PostAnalytics } from "@/api/analytics"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"

interface TopPostsTableProps {
  posts: PostAnalytics[]
}

export function TopPostsTable({ posts }: TopPostsTableProps) {
  const top = posts.slice(0, 10)

  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-base">Top Posts</CardTitle>
      </CardHeader>
      <CardContent>
        {top.length === 0 ? (
          <p className="text-sm text-muted-foreground text-center py-4">No published posts yet.</p>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b text-left text-xs text-muted-foreground">
                  <th className="pb-2 pr-4">Post</th>
                  <th className="pb-2 pr-4">Platform</th>
                  <th className="pb-2 pr-4 text-right">Likes</th>
                  <th className="pb-2 pr-4 text-right">Comments</th>
                  <th className="pb-2 pr-4 text-right">Shares</th>
                  <th className="pb-2 text-right">Eng. Rate</th>
                </tr>
              </thead>
              <tbody>
                {top.map((p) => (
                  <tr key={p.post_id} className="border-b last:border-0">
                    <td className="py-2 pr-4 max-w-[200px]">
                      <div className="flex items-center gap-1">
                        <span className="truncate text-xs">{p.content_text}</span>
                        {p.platform_url && (
                          <a href={p.platform_url} target="_blank" rel="noopener noreferrer">
                            <ExternalLink className="h-3 w-3 text-muted-foreground shrink-0" />
                          </a>
                        )}
                      </div>
                    </td>
                    <td className="py-2 pr-4 text-xs text-muted-foreground">
                      {p.platform === "twitter" ? "Twitter/X" : "LinkedIn"}
                    </td>
                    <td className="py-2 pr-4 text-right">{p.likes}</td>
                    <td className="py-2 pr-4 text-right">{p.comments}</td>
                    <td className="py-2 pr-4 text-right">{p.shares}</td>
                    <td className="py-2 text-right">
                      {p.engagement_rate !== null ? `${p.engagement_rate}%` : "-"}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </CardContent>
    </Card>
  )
}
