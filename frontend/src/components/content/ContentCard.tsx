import { useState } from "react"
import { toast } from "sonner"
import { ExternalLink, Sparkles, TrendingUp, User } from "lucide-react"
import type { ContentSource } from "@/api/content"
import { generatePost } from "@/api/posts"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"

const sourceLabels: Record<string, string> = {
  hackernews: "Hacker News",
  reddit: "Reddit",
  devto: "Dev.to",
  joke: "Joke",
  github: "GitHub",
}

const sourceColors: Record<string, string> = {
  hackernews: "bg-orange-100 text-orange-700",
  reddit: "bg-red-100 text-red-700",
  devto: "bg-indigo-100 text-indigo-700",
  joke: "bg-yellow-100 text-yellow-700",
  github: "bg-gray-100 text-gray-700",
}

interface ContentCardProps {
  item: ContentSource
  onGenerated?: () => void
}

export function ContentCard({ item, onGenerated }: ContentCardProps) {
  const [generating, setGenerating] = useState(false)
  const [platform, setPlatform] = useState<"twitter" | "linkedin">("twitter")
  const [showGenerate, setShowGenerate] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const handleGenerate = async () => {
    setGenerating(true)
    setError(null)
    try {
      const contentType = item.source_type === "joke" ? "joke" : "news"
      await generatePost(item.id, {
        target_platform: platform,
        content_type: contentType,
        tone: "professional",
      })
      setShowGenerate(false)
      toast.success("Post generated! View it in the Posts page.")
      onGenerated?.()
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : "Generation failed"
      setError(msg)
    } finally {
      setGenerating(false)
    }
  }

  return (
    <Card className="hover:shadow-md transition-shadow">
      <CardHeader className="pb-2">
        <div className="flex items-center justify-between">
          <span
            className={`text-xs px-2 py-0.5 rounded-full font-medium ${sourceColors[item.source_type] || "bg-gray-100 text-gray-700"}`}
          >
            {sourceLabels[item.source_type] || item.source_type}
          </span>
          <div className="flex items-center gap-1 text-xs text-muted-foreground">
            <TrendingUp className="h-3 w-3" />
            {item.score}
          </div>
        </div>
        <CardTitle className="text-sm leading-snug mt-1">{item.title}</CardTitle>
      </CardHeader>
      <CardContent>
        {item.content && (
          <p className="text-xs text-muted-foreground line-clamp-2 mb-2">{item.content}</p>
        )}
        <div className="flex items-center justify-between text-xs text-muted-foreground">
          {item.author && (
            <span className="flex items-center gap-1">
              <User className="h-3 w-3" />
              {item.author}
            </span>
          )}
          {item.url && (
            <a
              href={item.url}
              target="_blank"
              rel="noopener noreferrer"
              className="flex items-center gap-1 hover:text-primary"
            >
              <ExternalLink className="h-3 w-3" />
              Source
            </a>
          )}
        </div>
        {item.tags && item.tags.length > 0 && (
          <div className="flex gap-1 mt-2 flex-wrap">
            {item.tags.map((tag) => (
              <span key={tag} className="text-[10px] px-1.5 py-0.5 bg-muted rounded">
                {tag}
              </span>
            ))}
          </div>
        )}

        {showGenerate ? (
          <div className="mt-3 p-2 border border-border rounded-md space-y-2">
            <div className="flex gap-2">
              <Button
                size="sm"
                variant={platform === "twitter" ? "default" : "outline"}
                onClick={() => setPlatform("twitter")}
                className="text-xs h-7"
              >
                Twitter/X
              </Button>
              <Button
                size="sm"
                variant={platform === "linkedin" ? "default" : "outline"}
                onClick={() => setPlatform("linkedin")}
                className="text-xs h-7"
              >
                LinkedIn
              </Button>
            </div>
            {error && <p className="text-xs text-destructive">{error}</p>}
            <div className="flex gap-2 justify-end">
              <Button size="sm" variant="ghost" onClick={() => setShowGenerate(false)} className="text-xs h-7">
                Cancel
              </Button>
              <Button size="sm" onClick={handleGenerate} disabled={generating} className="text-xs h-7">
                {generating ? "Generating..." : "Generate"}
              </Button>
            </div>
          </div>
        ) : (
          <Button
            size="sm"
            variant="outline"
            className="mt-3 w-full text-xs"
            onClick={() => setShowGenerate(true)}
          >
            <Sparkles className="h-3 w-3 mr-1" />
            Generate Post
          </Button>
        )}
      </CardContent>
    </Card>
  )
}
