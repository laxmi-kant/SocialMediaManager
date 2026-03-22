import { useState } from "react"
import { Button } from "@/components/ui/button"
import { Label } from "@/components/ui/label"

interface PostEditorProps {
  initialText: string
  initialHashtags: string[]
  platform: string
  onSave: (text: string, hashtags: string[]) => void
  onCancel: () => void
}

export function PostEditor({ initialText, initialHashtags, platform, onSave, onCancel }: PostEditorProps) {
  const [text, setText] = useState(initialText)
  const [hashtagInput, setHashtagInput] = useState(initialHashtags.join(" "))
  const charLimit = platform === "twitter" ? 280 : 3000

  return (
    <div className="space-y-4">
      <div>
        <div className="flex justify-between mb-1">
          <Label>Post Content</Label>
          <span className={`text-xs ${text.length > charLimit ? "text-destructive" : "text-muted-foreground"}`}>
            {text.length}/{charLimit}
          </span>
        </div>
        <textarea
          value={text}
          onChange={(e) => setText(e.target.value)}
          className="w-full min-h-[120px] p-3 border border-border rounded-md text-sm resize-y bg-background"
          placeholder="Post content..."
        />
      </div>
      <div>
        <Label>Hashtags</Label>
        <input
          value={hashtagInput}
          onChange={(e) => setHashtagInput(e.target.value)}
          className="w-full p-2 border border-border rounded-md text-sm bg-background mt-1"
          placeholder="#AI #Tech #Programming"
        />
      </div>
      <div className="flex gap-2 justify-end">
        <Button variant="outline" size="sm" onClick={onCancel}>
          Cancel
        </Button>
        <Button size="sm" onClick={() => onSave(text, hashtagInput.split(/\s+/).filter(Boolean))} disabled={text.length > charLimit}>
          Save
        </Button>
      </div>
    </div>
  )
}
