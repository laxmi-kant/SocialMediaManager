import type { ContentSource } from "@/api/content"
import { ContentCard } from "./ContentCard"

interface TrendingFeedProps {
  items: ContentSource[]
  loading: boolean
  onGenerated?: () => void
}

export function TrendingFeed({ items, loading, onGenerated }: TrendingFeedProps) {
  if (loading) {
    return (
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {Array.from({ length: 6 }).map((_, i) => (
          <div key={i} className="h-40 rounded-lg bg-muted animate-pulse" />
        ))}
      </div>
    )
  }

  if (items.length === 0) {
    return (
      <div className="text-center py-12 text-muted-foreground">
        No content found. Try refreshing or changing filters.
      </div>
    )
  }

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
      {items.map((item) => (
        <ContentCard key={item.id} item={item} onGenerated={onGenerated} />
      ))}
    </div>
  )
}
