"use client"

import { Card } from "@/components/ui/card"
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
  AreaChart,
  Area,
} from "recharts"

const chartData = [
  { week: "Week 1", users: 4000, active: 2400, churn: 240 },
  { week: "Week 2", users: 5200, active: 3000, churn: 220 },
  { week: "Week 3", users: 6800, active: 4200, churn: 200 },
  { week: "Week 4", users: 7500, active: 5100, churn: 180 },
  { week: "Week 5", users: 8900, active: 6200, churn: 160 },
  { week: "Week 6", users: 10200, active: 7300, churn: 140 },
]

const pieData = [
  { name: "Active Users", value: 72 },
  { name: "Inactive", value: 28 },
]

const COLORS = ["#3B82F6", "#E5E7EB"]

export default function DataVisualization({ data }: { data: any }) {
  // Safe fallbacks if data is undefined or missing fields
  const safeChartData = (data && data.chartData) ? data.chartData : chartData
  const safePieData = (data && data.pieData) ? data.pieData : pieData
  const safeColors = (data && data.COLORS) ? data.COLORS : COLORS
  return (
    <div className="grid lg:grid-cols-3 gap-6">
      <Card className="lg:col-span-2 border-border bg-card p-8 shadow-3d card-gradient">
        <div className="mb-6">
          <h3 className="text-xl font-bold text-foreground">The Growth Momentum</h3>
          <p className="text-sm text-muted-foreground mt-1">Your users over time—the full picture</p>
        </div>
        <ResponsiveContainer width="100%" height={320}>
          <AreaChart data={safeChartData}>
            <defs>
              <linearGradient id="colorUsers" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#3B82F6" stopOpacity={0.3} />
                <stop offset="95%" stopColor="#3B82F6" stopOpacity={0} />
              </linearGradient>
            </defs>
            <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
            <XAxis dataKey="period" stroke="#9CA3AF" />
            <YAxis stroke="#9CA3AF" />
            <Tooltip
              contentStyle={{
                backgroundColor: "#ffffff",
                border: "1px solid #e5e7eb",
                borderRadius: "12px",
                boxShadow: "0 4px 16px rgb(0 0 0 / 0.1)",
              }}
              labelStyle={{ color: "#1f2937" }}
            />
            <Legend />
            <Area
              type="monotone"
              dataKey="users"
              stroke="#3B82F6"
              strokeWidth={3}
              fillOpacity={1}
              fill="url(#colorUsers)"
            />
            <Area type="monotone" dataKey="active" stroke="#2563EB" strokeWidth={2} fillOpacity={0} />
          </AreaChart>
        </ResponsiveContainer>
      </Card>

      <Card className="border-border bg-card p-8 shadow-3d card-gradient flex flex-col justify-center">
        <div className="mb-6">
          <h3 className="text-xl font-bold text-foreground">Who's Engaged</h3>
          <p className="text-sm text-muted-foreground mt-1">Active vs. dormant split</p>
        </div>
        <ResponsiveContainer width="100%" height={280}>
          <PieChart>
            <Pie
              data={safePieData}
              cx="50%"
              cy="50%"
              labelLine={false}
              label={({ name, value }) => `${name}: ${value}%`}
              outerRadius={90}
              innerRadius={45}
              fill="#3B82F6"
              dataKey="value"
            >
              {safePieData.map((entry: any, index: number) => (
                <Cell key={`cell-${index}`} fill={safeColors[index]} />
              ))}
            </Pie>
            <Tooltip formatter={(value) => `${value}%`} />
          </PieChart>
        </ResponsiveContainer>
      </Card>

      <Card className="lg:col-span-3 border-border bg-card p-8 shadow-3d card-gradient">
        <div className="mb-6">
          <h3 className="text-xl font-bold text-foreground">Churn Trajectory</h3>
          <p className="text-sm text-muted-foreground mt-1">Watch your churn decline—it's a good sign</p>
        </div>
        <ResponsiveContainer width="100%" height={280}>
          <BarChart data={safeChartData}>
            <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
            <XAxis dataKey="period" stroke="#9CA3AF" />
            <YAxis stroke="#9CA3AF" />
            <Tooltip
              contentStyle={{
                backgroundColor: "#ffffff",
                border: "1px solid #e5e7eb",
                borderRadius: "12px",
                boxShadow: "0 4px 16px rgb(0 0 0 / 0.1)",
              }}
              labelStyle={{ color: "#1f2937" }}
            />
            <Bar dataKey="churn" fill="#EF4444" radius={[12, 12, 0, 0]} />
          </BarChart>
        </ResponsiveContainer>
      </Card>
    </div>
  )
}
