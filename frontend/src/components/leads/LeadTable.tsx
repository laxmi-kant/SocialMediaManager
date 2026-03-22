import { ExternalLink, MoreHorizontal, Trash2 } from "lucide-react"
import type { Lead } from "@/api/leads"
import { Button } from "@/components/ui/button"

const statusBadge: Record<string, string> = {
  OPEN_TO_WORK: "bg-green-100 text-green-700",
  HIRING: "bg-blue-100 text-blue-700",
  BUSINESS: "bg-purple-100 text-purple-700",
  GENERAL: "bg-gray-100 text-gray-700",
}

interface LeadTableProps {
  leads: Lead[]
  onSelect: (lead: Lead) => void
  onDelete: (lead: Lead) => void
}

export function LeadTable({ leads, onSelect, onDelete }: LeadTableProps) {
  return (
    <div className="border rounded-lg overflow-hidden">
      <table className="w-full text-sm">
        <thead>
          <tr className="border-b bg-muted/50">
            <th className="text-left py-2.5 px-3 font-medium">Name</th>
            <th className="text-left py-2.5 px-3 font-medium hidden md:table-cell">Company</th>
            <th className="text-left py-2.5 px-3 font-medium hidden lg:table-cell">Location</th>
            <th className="text-left py-2.5 px-3 font-medium">Status</th>
            <th className="text-left py-2.5 px-3 font-medium hidden md:table-cell">Engagements</th>
            <th className="py-2.5 px-3 w-16"></th>
          </tr>
        </thead>
        <tbody>
          {leads.map((lead) => (
            <tr
              key={lead.id}
              className="border-b hover:bg-muted/30 cursor-pointer"
              onClick={() => onSelect(lead)}
            >
              <td className="py-2.5 px-3">
                <div>
                  <p className="font-medium">{lead.name || "Unknown"}</p>
                  <p className="text-xs text-muted-foreground truncate max-w-[200px]">
                    {lead.headline || "No headline"}
                  </p>
                </div>
              </td>
              <td className="py-2.5 px-3 hidden md:table-cell text-muted-foreground">
                {lead.current_company || "—"}
              </td>
              <td className="py-2.5 px-3 hidden lg:table-cell text-muted-foreground">
                {lead.location || "—"}
              </td>
              <td className="py-2.5 px-3">
                {lead.ai_status ? (
                  <span className={`text-[10px] px-1.5 py-0.5 rounded-full ${statusBadge[lead.ai_status] || statusBadge.GENERAL}`}>
                    {lead.ai_status.replace(/_/g, " ")}
                  </span>
                ) : (
                  <span className="text-xs text-muted-foreground">—</span>
                )}
              </td>
              <td className="py-2.5 px-3 hidden md:table-cell text-muted-foreground">
                {lead.engagements.length}
              </td>
              <td className="py-2.5 px-3">
                <div className="flex gap-1" onClick={(e) => e.stopPropagation()}>
                  {lead.profile_url && (
                    <a href={lead.profile_url} target="_blank" rel="noopener noreferrer">
                      <Button size="icon" variant="ghost" className="h-7 w-7">
                        <ExternalLink className="h-3 w-3" />
                      </Button>
                    </a>
                  )}
                  <Button
                    size="icon"
                    variant="ghost"
                    className="h-7 w-7 text-destructive"
                    onClick={() => onDelete(lead)}
                  >
                    <Trash2 className="h-3 w-3" />
                  </Button>
                </div>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}
