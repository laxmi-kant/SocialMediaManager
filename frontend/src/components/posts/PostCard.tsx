import { Calendar, Check, Clock, Edit, ExternalLink, Send, Trash2, X } from "lucide-react"
import type { Post } from "@/api/posts"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader } from "@/components/ui/card"

const statusColors: Record<string, string> = {
  draft: "bg-yellow-100 text-yellow-700",
  approved: "bg-green-100 text-green-700",
  scheduled: "bg-blue-100 text-blue-700",
  published: "bg-emerald-100 text-emerald-700",
  rejected: "bg-red-100 text-red-700",
  failed: "bg-red-100 text-red-700",
}

const platformLabels: Record<string, string> = {
  twitter: "Twitter/X",
  linkedin: "LinkedIn",
}

interface PostCardProps {
  post: Post
  onApprove?: (id: string) => void
  onReject?: (id: string) => void
  onEdit?: (post: Post) => void
  onDelete?: (id: string) => void
  onPublish?: (id: string) => void
  onSchedule?: (post: Post) => void
}

export function PostCard({ post, onApprove, onReject, onEdit, onDelete, onPublish, onSchedule }: PostCardProps) {
  const charLimit = post.target_platform === "twitter" ? 280 : 3000

  return (
    <Card>
      <CardHeader className="pb-2">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <span className="text-xs font-medium text-muted-foreground">
              {platformLabels[post.target_platform] || post.target_platform}
            </span>
            <span className={`text-xs px-2 py-0.5 rounded-full font-medium ${statusColors[post.status] || ""}`}>
              {post.status}
            </span>
          </div>
          <span className="text-xs text-muted-foreground">
            {post.content_text.length}/{charLimit}
          </span>
        </div>
      </CardHeader>
      <CardContent>
        <p className="text-sm whitespace-pre-wrap mb-3">{post.content_text}</p>

        {post.hashtags && post.hashtags.length > 0 && (
          <div className="flex gap-1 mb-3 flex-wrap">
            {post.hashtags.map((tag) => (
              <span key={tag} className="text-xs text-primary">{tag}</span>
            ))}
          </div>
        )}

        {post.scheduled_for && (
          <p className="text-xs text-muted-foreground flex items-center gap-1 mb-3">
            <Clock className="h-3 w-3" />
            Scheduled: {new Date(post.scheduled_for).toLocaleString()}
          </p>
        )}

        <div className="flex gap-1 flex-wrap">
          {post.status === "draft" && (
            <>
              {onApprove && (
                <Button size="sm" variant="outline" onClick={() => onApprove(post.id)}>
                  <Check className="h-3 w-3 mr-1" /> Approve
                </Button>
              )}
              {onReject && (
                <Button size="sm" variant="outline" onClick={() => onReject(post.id)}>
                  <X className="h-3 w-3 mr-1" /> Reject
                </Button>
              )}
            </>
          )}
          {post.status === "approved" && (
            <>
              {onPublish && (
                <Button size="sm" variant="default" onClick={() => onPublish(post.id)}>
                  <Send className="h-3 w-3 mr-1" /> Publish Now
                </Button>
              )}
              {onSchedule && (
                <Button size="sm" variant="outline" onClick={() => onSchedule(post)}>
                  <Calendar className="h-3 w-3 mr-1" /> Schedule
                </Button>
              )}
            </>
          )}
          {onEdit && !["published", "failed"].includes(post.status) && (
            <Button size="sm" variant="ghost" onClick={() => onEdit(post)}>
              <Edit className="h-3 w-3" />
            </Button>
          )}
          {onDelete && post.status !== "published" && (
            <Button size="sm" variant="ghost" onClick={() => onDelete(post.id)} className="ml-auto text-destructive">
              <Trash2 className="h-3 w-3" />
            </Button>
          )}
        </div>
      </CardContent>
    </Card>
  )
}
