import { useState } from "react"
import { Button } from "@/components/ui/button"
import { Label } from "@/components/ui/label"

interface SchedulePickerProps {
  onSchedule: (scheduledFor: string) => void
  onCancel: () => void
}

export function SchedulePicker({ onSchedule, onCancel }: SchedulePickerProps) {
  // Default to tomorrow at 9:00 AM local time
  const tomorrow = new Date()
  tomorrow.setDate(tomorrow.getDate() + 1)
  tomorrow.setHours(9, 0, 0, 0)
  const defaultValue = tomorrow.toISOString().slice(0, 16)

  const [datetime, setDatetime] = useState(defaultValue)

  const handleSubmit = () => {
    const dt = new Date(datetime)
    if (dt <= new Date()) return
    onSchedule(dt.toISOString())
  }

  return (
    <div className="space-y-3 p-3 border border-border rounded-md">
      <div>
        <Label>Schedule Date & Time</Label>
        <input
          type="datetime-local"
          value={datetime}
          onChange={(e) => setDatetime(e.target.value)}
          min={new Date().toISOString().slice(0, 16)}
          className="w-full p-2 border border-border rounded-md text-sm bg-background mt-1"
        />
      </div>
      <div className="flex gap-2 justify-end">
        <Button variant="outline" size="sm" onClick={onCancel}>
          Cancel
        </Button>
        <Button size="sm" onClick={handleSubmit}>
          Schedule
        </Button>
      </div>
    </div>
  )
}
