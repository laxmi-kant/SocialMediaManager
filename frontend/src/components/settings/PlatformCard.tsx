import { Linkedin, Twitter, Unplug } from "lucide-react"
import type { PlatformAccount } from "@/api/platforms"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"

const platformConfig: Record<string, { label: string; icon: typeof Twitter; color: string }> = {
  twitter: { label: "Twitter / X", icon: Twitter, color: "text-sky-500" },
  linkedin: { label: "LinkedIn", icon: Linkedin, color: "text-blue-600" },
}

interface PlatformCardProps {
  platform: string
  account: PlatformAccount | null
  onConnect: () => void
  onDisconnect: (id: string) => void
}

export function PlatformCard({ platform, account, onConnect, onDisconnect }: PlatformCardProps) {
  const config = platformConfig[platform] || { label: platform, icon: Twitter, color: "text-gray-500" }
  const Icon = config.icon
  const isConnected = !!account && account.is_active

  return (
    <Card>
      <CardHeader className="pb-2">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Icon className={`h-5 w-5 ${config.color}`} />
            <CardTitle className="text-base">{config.label}</CardTitle>
          </div>
          <span
            className={`text-xs px-2 py-0.5 rounded-full font-medium ${
              isConnected ? "bg-green-100 text-green-700" : "bg-gray-100 text-gray-500"
            }`}
          >
            {isConnected ? "Connected" : "Not Connected"}
          </span>
        </div>
      </CardHeader>
      <CardContent>
        {isConnected && account ? (
          <div className="space-y-2">
            <p className="text-sm text-muted-foreground">
              Connected as <span className="font-medium text-foreground">{account.display_name}</span>
            </p>
            {account.token_expires_at && (
              <p className="text-xs text-muted-foreground">
                Token expires: {new Date(account.token_expires_at).toLocaleDateString()}
              </p>
            )}
            <Button variant="outline" size="sm" onClick={() => onDisconnect(account.id)} className="mt-2">
              <Unplug className="h-3 w-3 mr-1" />
              Disconnect
            </Button>
          </div>
        ) : (
          <div>
            <p className="text-sm text-muted-foreground mb-3">
              Connect your {config.label} account to publish posts.
            </p>
            <Button size="sm" onClick={onConnect}>
              Connect {config.label}
            </Button>
          </div>
        )}
      </CardContent>
    </Card>
  )
}
