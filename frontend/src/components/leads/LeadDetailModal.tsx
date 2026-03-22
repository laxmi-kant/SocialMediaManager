import { useState } from "react"
import { ExternalLink, Mail, MapPin, Building2, Briefcase, Tag, Save } from "lucide-react"
import { toast } from "sonner"
import type { Lead } from "@/api/leads"
import { updateLead } from "@/api/leads"
import { Button } from "@/components/ui/button"
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog"

const statusBadge: Record<string, string> = {
  OPEN_TO_WORK: "bg-green-100 text-green-700",
  HIRING: "bg-blue-100 text-blue-700",
  BUSINESS: "bg-purple-100 text-purple-700",
  GENERAL: "bg-gray-100 text-gray-700",
}

interface LeadDetailModalProps {
  lead: Lead | null
  open: boolean
  onClose: () => void
  onUpdated: () => void
}

export function LeadDetailModal({ lead, open, onClose, onUpdated }: LeadDetailModalProps) {
  const [notes, setNotes] = useState(lead?.notes || "")
  const [tagInput, setTagInput] = useState("")
  const [tags, setTags] = useState<string[]>(lead?.tags || [])
  const [saving, setSaving] = useState(false)

  // Reset state when lead changes
  if (lead && notes === "" && lead.notes) setNotes(lead.notes)

  const handleAddTag = () => {
    const tag = tagInput.trim()
    if (tag && !tags.includes(tag)) {
      setTags([...tags, tag])
    }
    setTagInput("")
  }

  const handleRemoveTag = (tag: string) => {
    setTags(tags.filter((t) => t !== tag))
  }

  const handleSave = async () => {
    if (!lead) return
    setSaving(true)
    try {
      await updateLead(lead.id, { tags, notes: notes || undefined })
      toast.success("Lead updated")
      onUpdated()
      onClose()
    } catch {
      toast.error("Failed to update lead")
    } finally {
      setSaving(false)
    }
  }

  if (!lead) return null

  return (
    <Dialog open={open} onOpenChange={(o) => !o && onClose()}>
      <DialogContent className="max-w-lg">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            {lead.name || "Unknown Lead"}
            {lead.ai_status && (
              <span className={`text-[10px] px-1.5 py-0.5 rounded-full ${statusBadge[lead.ai_status] || statusBadge.GENERAL}`}>
                {lead.ai_status.replace(/_/g, " ")}
              </span>
            )}
          </DialogTitle>
        </DialogHeader>

        <div className="space-y-4">
          {lead.headline && (
            <p className="text-sm text-muted-foreground">{lead.headline}</p>
          )}

          <div className="grid grid-cols-2 gap-2 text-sm">
            {lead.current_company && (
              <div className="flex items-center gap-1.5 text-muted-foreground">
                <Building2 className="h-3.5 w-3.5" />
                {lead.current_company}
              </div>
            )}
            {lead.location && (
              <div className="flex items-center gap-1.5 text-muted-foreground">
                <MapPin className="h-3.5 w-3.5" />
                {lead.location}
              </div>
            )}
            {lead.industry && (
              <div className="flex items-center gap-1.5 text-muted-foreground">
                <Briefcase className="h-3.5 w-3.5" />
                {lead.industry}
              </div>
            )}
            {lead.email && (
              <div className="flex items-center gap-1.5 text-muted-foreground">
                <Mail className="h-3.5 w-3.5" />
                {lead.email}
              </div>
            )}
          </div>

          {lead.profile_url && (
            <a
              href={lead.profile_url}
              target="_blank"
              rel="noopener noreferrer"
              className="text-xs text-primary hover:underline flex items-center gap-1"
            >
              <ExternalLink className="h-3 w-3" />
              View LinkedIn Profile
            </a>
          )}

          {/* Engagements */}
          {lead.engagements.length > 0 && (
            <div>
              <h4 className="text-xs font-medium mb-1.5">Engagements ({lead.engagements.length})</h4>
              <div className="space-y-1 max-h-32 overflow-y-auto">
                {lead.engagements.map((e) => (
                  <div key={e.id} className="text-xs bg-muted rounded p-1.5 flex justify-between">
                    <span className="font-medium">{e.engagement_type}</span>
                    <span className="text-muted-foreground">
                      {new Date(e.engaged_at).toLocaleDateString()}
                    </span>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Tags */}
          <div>
            <h4 className="text-xs font-medium mb-1.5 flex items-center gap-1">
              <Tag className="h-3 w-3" /> Tags
            </h4>
            <div className="flex flex-wrap gap-1 mb-2">
              {tags.map((tag) => (
                <span
                  key={tag}
                  className="text-[10px] px-1.5 py-0.5 bg-primary/10 text-primary rounded-full cursor-pointer hover:bg-destructive/10 hover:text-destructive"
                  onClick={() => handleRemoveTag(tag)}
                >
                  {tag} &times;
                </span>
              ))}
            </div>
            <div className="flex gap-1">
              <input
                type="text"
                value={tagInput}
                onChange={(e) => setTagInput(e.target.value)}
                onKeyDown={(e) => e.key === "Enter" && (e.preventDefault(), handleAddTag())}
                placeholder="Add tag..."
                className="flex-1 px-2 py-1 border border-border rounded text-xs bg-background"
              />
              <Button size="sm" variant="outline" onClick={handleAddTag} className="h-7 text-xs">
                Add
              </Button>
            </div>
          </div>

          {/* Notes */}
          <div>
            <h4 className="text-xs font-medium mb-1.5">Notes</h4>
            <textarea
              value={notes}
              onChange={(e) => setNotes(e.target.value)}
              placeholder="Add notes about this lead..."
              className="w-full min-h-[60px] p-2 border border-border rounded-md text-sm bg-background resize-y"
            />
          </div>

          <div className="flex justify-end">
            <Button size="sm" onClick={handleSave} disabled={saving}>
              <Save className="h-3 w-3 mr-1" />
              {saving ? "Saving..." : "Save Changes"}
            </Button>
          </div>
        </div>
      </DialogContent>
    </Dialog>
  )
}
