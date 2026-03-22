import { Button } from "@/components/ui/button"

const sources = [
  { value: "", label: "All" },
  { value: "hackernews", label: "Hacker News" },
  { value: "reddit", label: "Reddit" },
  { value: "devto", label: "Dev.to" },
  { value: "joke", label: "Jokes" },
  { value: "github", label: "GitHub" },
]

interface ContentFilterProps {
  activeSource: string
  sortBy: string
  onSourceChange: (source: string) => void
  onSortChange: (sort: string) => void
}

export function ContentFilter({ activeSource, sortBy, onSourceChange, onSortChange }: ContentFilterProps) {
  return (
    <div className="flex flex-wrap items-center gap-2">
      <div className="flex gap-1">
        {sources.map((s) => (
          <Button
            key={s.value}
            variant={activeSource === s.value ? "default" : "outline"}
            size="sm"
            onClick={() => onSourceChange(s.value)}
          >
            {s.label}
          </Button>
        ))}
      </div>
      <div className="ml-auto flex gap-1">
        <Button
          variant={sortBy === "fetched_at" ? "default" : "outline"}
          size="sm"
          onClick={() => onSortChange("fetched_at")}
        >
          Latest
        </Button>
        <Button
          variant={sortBy === "score" ? "default" : "outline"}
          size="sm"
          onClick={() => onSortChange("score")}
        >
          Top
        </Button>
      </div>
    </div>
  )
}
