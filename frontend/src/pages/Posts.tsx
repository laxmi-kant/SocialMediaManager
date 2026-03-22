import { useCallback, useEffect, useState } from "react"
import { toast } from "sonner"
import {
  type Post,
  approvePost,
  deletePost,
  fetchPosts,
  publishPost,
  rejectPost,
  schedulePost,
  updatePost,
} from "@/api/posts"
import { PostEditor } from "@/components/posts/PostEditor"
import { PostQueue } from "@/components/posts/PostQueue"
import { SchedulePicker } from "@/components/posts/SchedulePicker"
import { ConfirmDialog } from "@/components/common/ConfirmDialog"
import { Button } from "@/components/ui/button"

export default function Posts() {
  const [posts, setPosts] = useState<Post[]>([])
  const [loading, setLoading] = useState(true)
  const [statusFilter, setStatusFilter] = useState("all")
  const [page, setPage] = useState(1)
  const [totalPages, setTotalPages] = useState(0)
  const [editing, setEditing] = useState<Post | null>(null)
  const [scheduling, setScheduling] = useState<Post | null>(null)
  const [deleteTarget, setDeleteTarget] = useState<string | null>(null)

  const load = useCallback(async () => {
    setLoading(true)
    try {
      const resp = await fetchPosts({
        status: statusFilter === "all" ? undefined : statusFilter,
        page,
        page_size: 20,
      })
      setPosts(resp.items)
      setTotalPages(resp.pages)
    } finally {
      setLoading(false)
    }
  }, [statusFilter, page])

  useEffect(() => {
    load()
  }, [load])

  const handleApprove = async (id: string) => {
    await approvePost(id)
    toast.success("Post approved")
    load()
  }

  const handleReject = async (id: string) => {
    await rejectPost(id)
    toast.info("Post rejected")
    load()
  }

  const handleDelete = (id: string) => {
    setDeleteTarget(id)
  }

  const confirmDelete = async () => {
    if (!deleteTarget) return
    await deletePost(deleteTarget)
    setDeleteTarget(null)
    toast.success("Post deleted")
    load()
  }

  const handleSave = async (text: string, hashtags: string[]) => {
    if (!editing) return
    await updatePost(editing.id, { content_text: text, hashtags })
    setEditing(null)
    load()
  }

  const handlePublish = async (id: string) => {
    try {
      await publishPost(id)
      toast.success("Post published!")
      load()
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : "Publishing failed"
      toast.error(msg)
    }
  }

  const handleSchedule = async (scheduledFor: string) => {
    if (!scheduling) return
    try {
      await schedulePost(scheduling.id, scheduledFor)
      toast.success("Post scheduled")
      setScheduling(null)
      load()
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : "Scheduling failed"
      toast.error(msg)
    }
  }

  return (
    <div className="space-y-4">
      <h2 className="text-2xl font-semibold">Posts</h2>

      {editing ? (
        <PostEditor
          initialText={editing.content_text}
          initialHashtags={editing.hashtags || []}
          platform={editing.target_platform}
          onSave={handleSave}
          onCancel={() => setEditing(null)}
        />
      ) : scheduling ? (
        <div>
          <h3 className="text-lg font-medium mb-2">
            Schedule: {scheduling.content_text.slice(0, 50)}...
          </h3>
          <SchedulePicker
            onSchedule={handleSchedule}
            onCancel={() => setScheduling(null)}
          />
        </div>
      ) : (
        <>
          <PostQueue
            posts={posts}
            loading={loading}
            activeStatus={statusFilter}
            onStatusChange={(s) => { setStatusFilter(s); setPage(1) }}
            onApprove={handleApprove}
            onReject={handleReject}
            onEdit={setEditing}
            onDelete={handleDelete}
            onPublish={handlePublish}
            onSchedule={setScheduling}
          />

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
        </>
      )}
      <ConfirmDialog
        open={!!deleteTarget}
        title="Delete Post"
        description="Are you sure you want to delete this post? This action cannot be undone."
        confirmLabel="Delete"
        variant="destructive"
        onConfirm={confirmDelete}
        onCancel={() => setDeleteTarget(null)}
      />
    </div>
  )
}
