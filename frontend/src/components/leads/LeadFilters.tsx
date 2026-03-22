import { Search } from "lucide-react"
import { Button } from "@/components/ui/button"

const statusFilters = ["all", "OPEN_TO_WORK", "HIRING", "BUSINESS", "GENERAL"]

const statusLabels: Record<string, string> = {
  all: "All",
  OPEN_TO_WORK: "Open to Work",
  HIRING: "Hiring",
  BUSINESS: "Business",
  GENERAL: "General",
}

interface LeadFiltersProps {
  search: string
  onSearchChange: (value: string) => void
  aiStatus: string
  onStatusChange: (value: string) => void
}

export function LeadFilters({ search, onSearchChange, aiStatus, onStatusChange }: LeadFiltersProps) {
  return (
    <div className="space-y-3">
      <div className="relative">
        <Search className="absolute left-2.5 top-2.5 h-4 w-4 text-muted-foreground" />
        <input
          type="text"
          placeholder="Search by name, headline, or company..."
          value={search}
          onChange={(e) => onSearchChange(e.target.value)}
          className="w-full pl-9 pr-3 py-2 border border-border rounded-md text-sm bg-background"
        />
      </div>
      <div className="flex gap-1 flex-wrap">
        <span className="text-xs text-muted-foreground self-center mr-1">Status:</span>
        {statusFilters.map((s) => (
          <Button
            key={s}
            size="sm"
            variant={aiStatus === s ? "default" : "outline"}
            onClick={() => onStatusChange(s)}
            className="text-xs h-7"
          >
            {statusLabels[s]}
          </Button>
        ))}
      </div>
    </div>
  )
}
