import { useCallback, useEffect, useState } from "react"
import { RefreshCw } from "lucide-react"
import { type ContentSource, fetchContent, refreshContent } from "@/api/content"
import { ContentFilter } from "@/components/content/ContentFilter"
import { TrendingFeed } from "@/components/content/TrendingFeed"
import { Button } from "@/components/ui/button"

export default function Content() {
  const [items, setItems] = useState<ContentSource[]>([])
  const [loading, setLoading] = useState(true)
  const [refreshing, setRefreshing] = useState(false)
  const [sourceFilter, setSourceFilter] = useState("")
  const [sortBy, setSortBy] = useState("fetched_at")
  const [page, setPage] = useState(1)
  const [totalPages, setTotalPages] = useState(0)

  const load = useCallback(async () => {
    setLoading(true)
    try {
      const resp = await fetchContent({
        source_type: sourceFilter || undefined,
        sort_by: sortBy,
        sort_order: "desc",
        page,
        page_size: 30,
      })
      setItems(resp.items)
      setTotalPages(resp.pages)
    } catch {
      // handled by interceptor
    } finally {
      setLoading(false)
    }
  }, [sourceFilter, sortBy, page])

  useEffect(() => {
    load()
  }, [load])

  const handleRefresh = async () => {
    setRefreshing(true)
    try {
      await refreshContent()
      // Wait a moment for the task to start processing
      setTimeout(load, 2000)
    } finally {
      setRefreshing(false)
    }
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-semibold">Content Sources</h2>
        <Button variant="outline" size="sm" onClick={handleRefresh} disabled={refreshing}>
          <RefreshCw className={`h-4 w-4 mr-1 ${refreshing ? "animate-spin" : ""}`} />
          Refresh
        </Button>
      </div>

      <ContentFilter
        activeSource={sourceFilter}
        sortBy={sortBy}
        onSourceChange={(s) => { setSourceFilter(s); setPage(1) }}
        onSortChange={(s) => { setSortBy(s); setPage(1) }}
      />

      <TrendingFeed items={items} loading={loading} onGenerated={() => { /* post generated - user can view in Posts page */ }} />

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
