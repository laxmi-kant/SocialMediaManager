import { useCallback, useEffect, useState } from "react"
import { useSearchParams } from "react-router-dom"
import { toast } from "sonner"
import {
  type PlatformAccount,
  disconnectPlatform,
  fetchPlatforms,
  getLinkedInAuthUrl,
  getTwitterAuthUrl,
} from "@/api/platforms"
import { PlatformCard } from "@/components/settings/PlatformCard"
import { ScheduleManager } from "@/components/settings/ScheduleManager"
import { ConfirmDialog } from "@/components/common/ConfirmDialog"
import { Separator } from "@/components/ui/separator"

export default function SettingsPage() {
  const [platforms, setPlatforms] = useState<PlatformAccount[]>([])
  const [loading, setLoading] = useState(true)
  const [disconnectTarget, setDisconnectTarget] = useState<string | null>(null)
  const [searchParams, setSearchParams] = useSearchParams()

  const load = useCallback(async () => {
    setLoading(true)
    try {
      const resp = await fetchPlatforms()
      setPlatforms(resp.platforms)
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    load()
  }, [load])

  // Handle OAuth redirect params
  useEffect(() => {
    const connected = searchParams.get("connected")
    const error = searchParams.get("error")
    if (connected) {
      toast.success(`${connected.charAt(0).toUpperCase() + connected.slice(1)} connected successfully!`)
      setSearchParams({})
      load()
    }
    if (error) {
      toast.error(`Connection failed: ${error}`)
      setSearchParams({})
    }
  }, [searchParams, setSearchParams, load])

  const handleConnect = (platform: string) => {
    const url = platform === "twitter" ? getTwitterAuthUrl() : getLinkedInAuthUrl()
    window.location.href = url
  }

  const handleDisconnect = async () => {
    if (!disconnectTarget) return
    await disconnectPlatform(disconnectTarget)
    setDisconnectTarget(null)
    toast.success("Platform disconnected")
    load()
  }

  const getAccount = (platform: string) => platforms.find((p) => p.platform === platform) || null

  return (
    <div className="space-y-6">
      <h2 className="text-2xl font-semibold">Settings</h2>

      <div>
        <h3 className="text-lg font-medium mb-3">Platform Connections</h3>
        {loading ? (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {[0, 1].map((i) => (
              <div key={i} className="h-40 rounded-lg bg-muted animate-pulse" />
            ))}
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <PlatformCard
              platform="twitter"
              account={getAccount("twitter")}
              onConnect={() => handleConnect("twitter")}
              onDisconnect={setDisconnectTarget}
            />
            <PlatformCard
              platform="linkedin"
              account={getAccount("linkedin")}
              onConnect={() => handleConnect("linkedin")}
              onDisconnect={setDisconnectTarget}
            />
          </div>
        )}
      </div>

      <Separator />

      <ScheduleManager />

      <ConfirmDialog
        open={!!disconnectTarget}
        title="Disconnect Platform"
        description="Are you sure you want to disconnect this platform? You will need to reconnect to publish posts."
        confirmLabel="Disconnect"
        variant="destructive"
        onConfirm={handleDisconnect}
        onCancel={() => setDisconnectTarget(null)}
      />
    </div>
  )
}
