"use client"

import { Card } from "@/components/ui/card"
import { ArrowUp, ArrowDown } from "lucide-react"

export default function StatsSummary({ data }: { data: any }) {
  // Helpers to improve presentation
  const toTitleCase = (input: string) =>
    input
      .replace(/_/g, " ")
      .toLowerCase()
      .replace(/\b\w/g, (c) => c.toUpperCase())

  const formatNumber = (num: number) =>
    new Intl.NumberFormat(undefined, { maximumFractionDigits: 2 }).format(num)

  const formatValue = (key: string, value: any) => {
    if (typeof value === "number") return formatNumber(value)
    if (typeof value === "boolean") return value ? "Yes" : "No"
    if (value == null) return "—"
    if (typeof value === "object") {
      // Special handling for cohort analysis objects
      const keys = Object.keys(value)
      if (key.toLowerCase().includes("cohort")) return `${keys.length} cohorts`
      return `${keys.length} items`
    }
    return String(value)
  }

  // Normalize data: accept array of stats or an object of key -> value
  const normalized: Array<{ label: string; value: any; trend?: string; positive?: boolean; change?: string }> = Array.isArray(data)
    ? data.map((s: any) => ({
        label: toTitleCase(String(s.label ?? "")),
        value: formatValue(String(s.label ?? ""), s.value ?? s.val ?? s.amount ?? s.count),
        trend: s.trend,
        positive: s.positive,
        change: s.change,
      }))
    : data && typeof data === "object"
    ? Object.entries(data).map(([key, value]) => ({ label: toTitleCase(key), value: formatValue(key, value) }))
    : []

  return (
    <div className="grid md:grid-cols-4 gap-6">
      {normalized.map((stat: any, idx: number) => (
        <Card key={idx} className="border-border bg-card p-6 shadow-3d smooth-transition card-gradient">
          <p className="text-xs font-semibold text-muted-foreground mb-3 uppercase tracking-wider">{stat.label}</p>
          <div className="flex items-end justify-between">
            <div>
              <p className="text-4xl font-bold bg-gradient-to-r from-foreground to-foreground/80 bg-clip-text text-transparent mb-2">
                {typeof stat.value === "number" ? stat.value : String(stat.value)}
              </p>
              {stat.trend && <p className="text-xs text-muted-foreground">{stat.trend}</p>}
            </div>
            {typeof stat.positive === "boolean" && stat.change && (
              <div
                className={`flex items-center gap-1.5 px-2 py-1 rounded-lg ${stat.positive ? "bg-chart-5/10 text-chart-5" : "bg-destructive/10 text-destructive"}`}
              >
                {stat.positive ? <ArrowUp className="w-4 h-4" /> : <ArrowDown className="w-4 h-4" />}
                <span className="text-sm font-bold">{stat.change}</span>
              </div>
            )}
          </div>
        </Card>
      ))}
    </div>
  )
}
