import { useCallback, useEffect, useState } from "react"
import { type Comment, type CommentStats, fetchCommentStats, fetchComments } from "@/api/comments"
import { CommentCard } from "@/components/comments/CommentCard"
import { Button } from "@/components/ui/button"
import { Card, CardContent } from "@/components/ui/card"

const sentimentFilters = ["all", "positive", "negative", "neutral", "question"]
const typeFilters = ["all", "praise", "question", "complaint", "suggestion", "spam", "other"]

export default function Comments() {
  const [comments, setComments] = useState<Comment[]>([])
  const [stats, setStats] = useState<CommentStats | null>(null)
  const [loading, setLoading] = useState(true)
  const [sentiment, setSentiment] = useState("all")
  const [commentType, setCommentType] = useState("all")
  const [page, setPage] = useState(1)
  const [totalPages, setTotalPages] = useState(0)

  const load = useCallback(async () => {
    setLoading(true)
    try {
      const [resp, statsResp] = await Promise.all([
        fetchComments({
          sentiment: sentiment === "all" ? undefined : sentiment,
          comment_type: commentType === "all" ? undefined : commentType,
          page,
          page_size: 20,
        }),
        fetchCommentStats(),
      ])
      setComments(resp.items)
      setTotalPages(resp.pages)
      setStats(statsResp)
    } finally {
      setLoading(false)
    }
  }, [sentiment, commentType, page])

  useEffect(() => {
    load()
  }, [load])

  return (
    <div className="space-y-4">
      <h2 className="text-2xl font-semibold">Comments</h2>

      {stats && (
        <div className="grid grid-cols-3 gap-3">
          <Card>
            <CardContent className="pt-4 pb-3 text-center">
              <p className="text-2xl font-bold">{stats.total_comments}</p>
              <p className="text-xs text-muted-foreground">Total</p>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="pt-4 pb-3 text-center">
              <p className="text-2xl font-bold text-orange-600">{stats.unreplied_comments}</p>
              <p className="text-xs text-muted-foreground">Unreplied</p>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="pt-4 pb-3 text-center">
              <p className="text-2xl font-bold text-green-600">{stats.replied_comments}</p>
              <p className="text-xs text-muted-foreground">Replied</p>
            </CardContent>
          </Card>
        </div>
      )}

      <div className="space-y-2">
        <div className="flex gap-1 flex-wrap">
          <span className="text-xs text-muted-foreground self-center mr-1">Sentiment:</span>
          {sentimentFilters.map((s) => (
            <Button
              key={s}
              size="sm"
              variant={sentiment === s ? "default" : "outline"}
              onClick={() => { setSentiment(s); setPage(1) }}
              className="text-xs h-7"
            >
              {s.charAt(0).toUpperCase() + s.slice(1)}
            </Button>
          ))}
        </div>
        <div className="flex gap-1 flex-wrap">
          <span className="text-xs text-muted-foreground self-center mr-1">Type:</span>
          {typeFilters.map((t) => (
            <Button
              key={t}
              size="sm"
              variant={commentType === t ? "default" : "outline"}
              onClick={() => { setCommentType(t); setPage(1) }}
              className="text-xs h-7"
            >
              {t.charAt(0).toUpperCase() + t.slice(1)}
            </Button>
          ))}
        </div>
      </div>

      {loading ? (
        <div className="space-y-4">
          {[0, 1, 2].map((i) => (
            <div key={i} className="h-32 rounded-lg bg-muted animate-pulse" />
          ))}
        </div>
      ) : comments.length === 0 ? (
        <p className="text-center py-12 text-muted-foreground">
          No comments found. Comments will appear after you publish posts.
        </p>
      ) : (
        <div className="space-y-3">
          {comments.map((c) => (
            <CommentCard key={c.id} comment={c} onReplied={load} />
          ))}
        </div>
      )}

      {totalPages > 1 && (
        <div className="flex justify-center gap-2 pt-4">
          <Button variant="outline" size="sm" disabled={page <= 1} onClick={() => setPage(page - 1)}>
            Previous
          </Button>
          <span className="text-sm text-muted-foreground flex items-center">
            Page {page} of {totalPages}
          </span>
          <Button variant="outline" size="sm" disabled={page >= totalPages} onClick={() => setPage(page + 1)}>
            Next
          </Button>
        </div>
      )}
    </div>
  )
}
