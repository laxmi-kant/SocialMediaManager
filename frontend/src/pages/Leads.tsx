import { useCallback, useEffect, useState } from "react"
import { Download } from "lucide-react"
import { toast } from "sonner"
import {
  type Lead,
  type LeadStats as LeadStatsType,
  deleteLead,
  fetchLeadStats,
  fetchLeads,
  getExportUrl,
} from "@/api/leads"
import { LeadDetailModal } from "@/components/leads/LeadDetailModal"
import { LeadFilters } from "@/components/leads/LeadFilters"
import { LeadStats } from "@/components/leads/LeadStats"
import { LeadTable } from "@/components/leads/LeadTable"
import { ConfirmDialog } from "@/components/common/ConfirmDialog"
import { Button } from "@/components/ui/button"

export default function Leads() {
  const [leads, setLeads] = useState<Lead[]>([])
  const [stats, setStats] = useState<LeadStatsType | null>(null)
  const [loading, setLoading] = useState(true)
  const [search, setSearch] = useState("")
  const [aiStatus, setAiStatus] = useState("all")
  const [page, setPage] = useState(1)
  const [totalPages, setTotalPages] = useState(0)
  const [selected, setSelected] = useState<Lead | null>(null)
  const [deleteTarget, setDeleteTarget] = useState<Lead | null>(null)

  const load = useCallback(async () => {
    setLoading(true)
    try {
      const [resp, statsResp] = await Promise.all([
        fetchLeads({
          search: search || undefined,
          ai_status: aiStatus === "all" ? undefined : aiStatus,
          page,
          page_size: 20,
        }),
        fetchLeadStats(),
      ])
      setLeads(resp.items)
      setTotalPages(resp.pages)
      setStats(statsResp)
    } finally {
      setLoading(false)
    }
  }, [search, aiStatus, page])

  useEffect(() => {
    const timer = setTimeout(() => load(), search ? 300 : 0)
    return () => clearTimeout(timer)
  }, [load, search])

  const handleDelete = async () => {
    if (!deleteTarget) return
    try {
      await deleteLead(deleteTarget.id)
      toast.success("Lead deleted")
      setDeleteTarget(null)
      load()
    } catch {
      toast.error("Failed to delete lead")
    }
  }

  const handleExport = () => {
    const url = getExportUrl(aiStatus === "all" ? undefined : aiStatus)
    window.open(url, "_blank")
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-semibold">Leads</h2>
        <Button size="sm" variant="outline" onClick={handleExport}>
          <Download className="h-3.5 w-3.5 mr-1" />
          Export CSV
        </Button>
      </div>

      <LeadStats stats={stats} />

      <LeadFilters
        search={search}
        onSearchChange={(v) => { setSearch(v); setPage(1) }}
        aiStatus={aiStatus}
        onStatusChange={(v) => { setAiStatus(v); setPage(1) }}
      />

      {loading ? (
        <div className="space-y-2">
          {[0, 1, 2, 3].map((i) => (
            <div key={i} className="h-14 rounded-lg bg-muted animate-pulse" />
          ))}
        </div>
      ) : leads.length === 0 ? (
        <p className="text-center py-12 text-muted-foreground">
          No leads found. Leads are collected automatically from your published post engagements.
        </p>
      ) : (
        <LeadTable
          leads={leads}
          onSelect={setSelected}
          onDelete={setDeleteTarget}
        />
      )}

      {totalPages > 1 && (
        <div className="flex justify-center gap-2 pt-2">
          <Button variant="outline" size="sm" disabled={page <= 1} onClick={() => setPage(page - 1)}>
            Previous
          </Button>
          <span className="text-sm text-muted-foreground flex items-center">
            Page {page} of {totalPages}
          </span>
          <Button variant="outline" size="sm" disabled={page >= totalPages} onClick={() => setPage(page + 1)}>
            Next
          </Button>
        </div>
      )}

      <LeadDetailModal
        lead={selected}
        open={!!selected}
        onClose={() => setSelected(null)}
        onUpdated={load}
      />

      <ConfirmDialog
        open={!!deleteTarget}
        title="Delete Lead"
        description={`Are you sure you want to delete ${deleteTarget?.name || "this lead"}? This action cannot be undone.`}
        confirmLabel="Delete"
        variant="destructive"
        onConfirm={handleDelete}
        onCancel={() => setDeleteTarget(null)}
      />
    </div>
  )
}
