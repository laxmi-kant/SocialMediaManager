import type { LeadStats as LeadStatsType } from "@/api/leads"
import { Card, CardContent } from "@/components/ui/card"

interface LeadStatsProps {
  stats: LeadStatsType | null
}

export function LeadStats({ stats }: LeadStatsProps) {
  if (!stats) return null

  return (
    <div className="grid grid-cols-4 gap-3">
      <Card>
        <CardContent className="pt-4 pb-3 text-center">
          <p className="text-2xl font-bold">{stats.total_leads}</p>
          <p className="text-xs text-muted-foreground">Total Leads</p>
        </CardContent>
      </Card>
      <Card>
        <CardContent className="pt-4 pb-3 text-center">
          <p className="text-2xl font-bold text-green-600">{stats.open_to_work}</p>
          <p className="text-xs text-muted-foreground">Open to Work</p>
        </CardContent>
      </Card>
      <Card>
        <CardContent className="pt-4 pb-3 text-center">
          <p className="text-2xl font-bold text-blue-600">{stats.hiring}</p>
          <p className="text-xs text-muted-foreground">Hiring</p>
        </CardContent>
      </Card>
      <Card>
        <CardContent className="pt-4 pb-3 text-center">
          <p className="text-2xl font-bold text-purple-600">{stats.has_email}</p>
          <p className="text-xs text-muted-foreground">Has Email</p>
        </CardContent>
      </Card>
    </div>
  )
}
