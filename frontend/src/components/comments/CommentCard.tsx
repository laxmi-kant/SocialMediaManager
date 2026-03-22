import { useState } from "react"
import { MessageSquare, Send, Sparkles, User } from "lucide-react"
import { toast } from "sonner"
import type { Comment } from "@/api/comments"
import { generateReply, sendReply } from "@/api/comments"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader } from "@/components/ui/card"

const sentimentColors: Record<string, string> = {
  positive: "bg-green-100 text-green-700",
  negative: "bg-red-100 text-red-700",
  neutral: "bg-gray-100 text-gray-700",
  question: "bg-blue-100 text-blue-700",
}

interface CommentCardProps {
  comment: Comment
  onReplied?: () => void
}

export function CommentCard({ comment, onReplied }: CommentCardProps) {
  const [replyText, setReplyText] = useState("")
  const [generating, setGenerating] = useState(false)
  const [sending, setSending] = useState(false)
  const [showReply, setShowReply] = useState(false)

  const handleGenerate = async () => {
    setGenerating(true)
    try {
      const reply = await generateReply(comment.id)
      setReplyText(reply.reply_text)
      setShowReply(true)
    } catch {
      toast.error("Failed to generate reply")
    } finally {
      setGenerating(false)
    }
  }

  const handleSend = async () => {
    if (!replyText.trim()) return
    setSending(true)
    try {
      await sendReply(comment.id, replyText)
      toast.success("Reply sent!")
      setShowReply(false)
      setReplyText("")
      onReplied?.()
    } catch {
      toast.error("Failed to send reply")
    } finally {
      setSending(false)
    }
  }

  const hasReplies = comment.replies.length > 0
  const latestReply = hasReplies ? comment.replies[comment.replies.length - 1] : null

  return (
    <Card>
      <CardHeader className="pb-2">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <User className="h-4 w-4 text-muted-foreground" />
            <span className="text-sm font-medium">{comment.commenter_name || "Anonymous"}</span>
            {comment.commenter_profile_url && (
              <a
                href={comment.commenter_profile_url}
                target="_blank"
                rel="noopener noreferrer"
                className="text-xs text-primary hover:underline"
              >
                View Profile
              </a>
            )}
          </div>
          <div className="flex gap-1">
            {comment.sentiment && (
              <span className={`text-[10px] px-1.5 py-0.5 rounded-full ${sentimentColors[comment.sentiment] || "bg-gray-100 text-gray-700"}`}>
                {comment.sentiment}
              </span>
            )}
            {comment.comment_type && (
              <span className="text-[10px] px-1.5 py-0.5 rounded-full bg-gray-100 text-gray-700">
                {comment.comment_type}
              </span>
            )}
          </div>
        </div>
      </CardHeader>
      <CardContent>
        <p className="text-sm mb-3">{comment.comment_text}</p>

        {comment.commented_at && (
          <p className="text-xs text-muted-foreground mb-2">
            {new Date(comment.commented_at).toLocaleString()}
          </p>
        )}

        {latestReply && latestReply.status === "sent" && (
          <div className="bg-muted p-2 rounded-md mb-2">
            <p className="text-xs text-muted-foreground mb-1">
              <MessageSquare className="h-3 w-3 inline mr-1" />
              Reply ({latestReply.reply_mode})
            </p>
            <p className="text-sm">{latestReply.reply_text}</p>
          </div>
        )}

        {showReply ? (
          <div className="space-y-2 mt-2">
            <textarea
              value={replyText}
              onChange={(e) => setReplyText(e.target.value)}
              className="w-full min-h-[80px] p-2 border border-border rounded-md text-sm bg-background resize-y"
              placeholder="Write your reply..."
            />
            <div className="flex gap-2 justify-end">
              <Button size="sm" variant="outline" onClick={() => setShowReply(false)}>
                Cancel
              </Button>
              <Button size="sm" onClick={handleSend} disabled={sending || !replyText.trim()}>
                <Send className="h-3 w-3 mr-1" />
                {sending ? "Sending..." : "Send Reply"}
              </Button>
            </div>
          </div>
        ) : (
          <div className="flex gap-1 mt-2">
            <Button size="sm" variant="outline" onClick={handleGenerate} disabled={generating}>
              <Sparkles className="h-3 w-3 mr-1" />
              {generating ? "Generating..." : "AI Reply"}
            </Button>
            <Button size="sm" variant="ghost" onClick={() => setShowReply(true)}>
              <MessageSquare className="h-3 w-3 mr-1" />
              Manual Reply
            </Button>
          </div>
        )}
      </CardContent>
    </Card>
  )
}
