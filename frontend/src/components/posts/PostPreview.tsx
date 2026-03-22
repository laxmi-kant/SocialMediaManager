import { Linkedin, Twitter } from "lucide-react"
import { Card, CardContent, CardHeader } from "@/components/ui/card"

interface PostPreviewProps {
  text: string
  platform: string
  hashtags?: string[]
}

export function PostPreview({ text, platform, hashtags }: PostPreviewProps) {
  const isTwitter = platform === "twitter"

  return (
    <Card className="max-w-md">
      <CardHeader className="pb-2">
        <div className="flex items-center gap-2">
          {isTwitter ? (
            <Twitter className="h-4 w-4 text-sky-500" />
          ) : (
            <Linkedin className="h-4 w-4 text-blue-600" />
          )}
          <span className="text-sm font-medium">
            {isTwitter ? "Twitter/X Preview" : "LinkedIn Preview"}
          </span>
        </div>
      </CardHeader>
      <CardContent>
        <div className={`text-sm ${isTwitter ? "" : "whitespace-pre-wrap"}`}>
          {text}
        </div>
        {hashtags && hashtags.length > 0 && (
          <div className="mt-2 text-sm text-primary">
            {hashtags.join(" ")}
          </div>
        )}
      </CardContent>
    </Card>
  )
}
