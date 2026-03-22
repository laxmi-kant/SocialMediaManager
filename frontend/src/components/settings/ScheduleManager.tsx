import { useCallback, useEffect, useState } from "react"
import { Plus, Power, Trash2 } from "lucide-react"
import { toast } from "sonner"
import {
  type Schedule,
  createSchedule,
  deleteSchedule,
  fetchSchedules,
  updateSchedule,
} from "@/api/schedules"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Label } from "@/components/ui/label"

const cronPresets = [
  { label: "Every weekday 9 AM", value: "0 9 * * 1-5" },
  { label: "Twice daily (9 AM, 5 PM)", value: "0 9,17 * * *" },
  { label: "Every 6 hours", value: "0 */6 * * *" },
  { label: "Daily at noon", value: "0 12 * * *" },
]

const contentTypeOptions = ["tech_insight", "joke", "news_commentary", "github_spotlight", "tip"]

export function ScheduleManager() {
  const [schedules, setSchedules] = useState<Schedule[]>([])
  const [loading, setLoading] = useState(true)
  const [showCreate, setShowCreate] = useState(false)

  // Create form state
  const [name, setName] = useState("")
  const [platform, setPlatform] = useState("twitter")
  const [selectedTypes, setSelectedTypes] = useState<string[]>(["tech_insight"])
  const [cronExpr, setCronExpr] = useState("0 9 * * 1-5")
  const [autoApprove, setAutoApprove] = useState(false)

  const load = useCallback(async () => {
    setLoading(true)
    try {
      const resp = await fetchSchedules()
      setSchedules(resp.items)
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    load()
  }, [load])

  const handleCreate = async () => {
    if (!name.trim() || selectedTypes.length === 0) return
    await createSchedule({
      name,
      platform,
      content_types: selectedTypes,
      cron_expression: cronExpr,
      auto_approve: autoApprove,
    })
    toast.success("Schedule created")
    setShowCreate(false)
    setName("")
    load()
  }

  const handleToggle = async (schedule: Schedule) => {
    await updateSchedule(schedule.id, { is_active: !schedule.is_active })
    toast.success(schedule.is_active ? "Schedule paused" : "Schedule activated")
    load()
  }

  const handleDelete = async (id: string) => {
    await deleteSchedule(id)
    toast.success("Schedule deleted")
    load()
  }

  const toggleType = (t: string) => {
    setSelectedTypes((prev) =>
      prev.includes(t) ? prev.filter((x) => x !== t) : [...prev, t]
    )
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h3 className="text-lg font-medium">Content Schedules</h3>
        <Button size="sm" onClick={() => setShowCreate(!showCreate)}>
          <Plus className="h-3 w-3 mr-1" />
          New Schedule
        </Button>
      </div>

      {showCreate && (
        <Card>
          <CardContent className="pt-4 space-y-3">
            <div>
              <Label>Schedule Name</Label>
              <input
                value={name}
                onChange={(e) => setName(e.target.value)}
                className="w-full p-2 border border-border rounded-md text-sm bg-background mt-1"
                placeholder="e.g., Morning Tech Posts"
              />
            </div>
            <div className="grid grid-cols-2 gap-3">
              <div>
                <Label>Platform</Label>
                <select
                  value={platform}
                  onChange={(e) => setPlatform(e.target.value)}
                  className="w-full p-2 border border-border rounded-md text-sm bg-background mt-1"
                >
                  <option value="twitter">Twitter/X</option>
                  <option value="linkedin">LinkedIn</option>
                </select>
              </div>
              <div>
                <Label>Schedule</Label>
                <select
                  value={cronExpr}
                  onChange={(e) => setCronExpr(e.target.value)}
                  className="w-full p-2 border border-border rounded-md text-sm bg-background mt-1"
                >
                  {cronPresets.map((p) => (
                    <option key={p.value} value={p.value}>{p.label}</option>
                  ))}
                </select>
              </div>
            </div>
            <div>
              <Label>Content Types</Label>
              <div className="flex gap-2 mt-1 flex-wrap">
                {contentTypeOptions.map((t) => (
                  <Button
                    key={t}
                    size="sm"
                    variant={selectedTypes.includes(t) ? "default" : "outline"}
                    onClick={() => toggleType(t)}
                    className="text-xs"
                  >
                    {t.replace("_", " ")}
                  </Button>
                ))}
              </div>
            </div>
            <div className="flex items-center gap-2">
              <input
                type="checkbox"
                id="autoApprove"
                checked={autoApprove}
                onChange={(e) => setAutoApprove(e.target.checked)}
              />
              <Label htmlFor="autoApprove" className="text-sm">Auto-approve generated posts</Label>
            </div>
            <div className="flex gap-2 justify-end">
              <Button variant="outline" size="sm" onClick={() => setShowCreate(false)}>Cancel</Button>
              <Button size="sm" onClick={handleCreate} disabled={!name.trim() || selectedTypes.length === 0}>
                Create Schedule
              </Button>
            </div>
          </CardContent>
        </Card>
      )}

      {loading ? (
        <div className="space-y-3">
          {[0, 1].map((i) => (
            <div key={i} className="h-20 rounded-lg bg-muted animate-pulse" />
          ))}
        </div>
      ) : schedules.length === 0 ? (
        <p className="text-center py-8 text-muted-foreground">
          No schedules yet. Create one to auto-generate posts.
        </p>
      ) : (
        <div className="space-y-3">
          {schedules.map((s) => (
            <Card key={s.id}>
              <CardHeader className="py-3 pb-1">
                <div className="flex items-center justify-between">
                  <CardTitle className="text-sm">{s.name}</CardTitle>
                  <div className="flex items-center gap-1">
                    <span className={`text-xs px-2 py-0.5 rounded-full ${s.is_active ? "bg-green-100 text-green-700" : "bg-gray-100 text-gray-500"}`}>
                      {s.is_active ? "Active" : "Paused"}
                    </span>
                  </div>
                </div>
              </CardHeader>
              <CardContent className="py-2">
                <div className="flex items-center gap-4 text-xs text-muted-foreground mb-2">
                  <span>{s.platform === "twitter" ? "Twitter/X" : "LinkedIn"}</span>
                  <span>{s.cron_expression}</span>
                  <span>{s.content_types.join(", ")}</span>
                  {s.auto_approve && <span className="text-green-600">Auto-approve</span>}
                </div>
                <div className="flex gap-1">
                  <Button size="sm" variant="ghost" onClick={() => handleToggle(s)}>
                    <Power className="h-3 w-3 mr-1" />
                    {s.is_active ? "Pause" : "Activate"}
                  </Button>
                  <Button size="sm" variant="ghost" onClick={() => handleDelete(s.id)} className="text-destructive">
                    <Trash2 className="h-3 w-3" />
                  </Button>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}
    </div>
  )
}
