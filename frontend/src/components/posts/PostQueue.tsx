import type { Post } from "@/api/posts"
import { Button } from "@/components/ui/button"
import { PostCard } from "./PostCard"

const statusTabs = ["all", "draft", "approved", "scheduled", "published", "rejected"]

interface PostQueueProps {
  posts: Post[]
  loading: boolean
  activeStatus: string
  onStatusChange: (status: string) => void
  onApprove: (id: string) => void
  onReject: (id: string) => void
  onEdit: (post: Post) => void
  onDelete: (id: string) => void
  onPublish?: (id: string) => void
  onSchedule?: (post: Post) => void
}

export function PostQueue({
  posts,
  loading,
  activeStatus,
  onStatusChange,
  onApprove,
  onReject,
  onEdit,
  onDelete,
  onPublish,
  onSchedule,
}: PostQueueProps) {
  return (
    <div className="space-y-4">
      <div className="flex gap-1 flex-wrap">
        {statusTabs.map((s) => (
          <Button
            key={s}
            variant={activeStatus === s ? "default" : "outline"}
            size="sm"
            onClick={() => onStatusChange(s)}
          >
            {s.charAt(0).toUpperCase() + s.slice(1)}
          </Button>
        ))}
      </div>

      {loading ? (
        <div className="space-y-4">
          {Array.from({ length: 3 }).map((_, i) => (
            <div key={i} className="h-32 rounded-lg bg-muted animate-pulse" />
          ))}
        </div>
      ) : posts.length === 0 ? (
        <p className="text-center py-12 text-muted-foreground">No posts found.</p>
      ) : (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
          {posts.map((post) => (
            <PostCard
              key={post.id}
              post={post}
              onApprove={onApprove}
              onReject={onReject}
              onEdit={onEdit}
              onDelete={onDelete}
              onPublish={onPublish}
              onSchedule={onSchedule}
            />
          ))}
        </div>
      )}
    </div>
  )
}
