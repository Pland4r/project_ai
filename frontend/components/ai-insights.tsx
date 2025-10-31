"use client"

import { Card } from "@/components/ui/card"
import { Brain, TrendingUp, Target, Zap } from "lucide-react"

function markdownToHtml(md: string): string {
  if (!md) return ""
  const escape = (s: string) => s.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;")
  let html = escape(md)
  // headings
  html = html.replace(/^###\s+(.*)$/gm, '<h3 class="text-lg font-bold mt-4 mb-2">$1</h3>')
  html = html.replace(/^##\s+(.*)$/gm, '<h2 class="text-xl font-bold mt-5 mb-3">$1</h2>')
  html = html.replace(/^#\s+(.*)$/gm, '<h1 class="text-2xl font-bold mt-6 mb-4">$1</h1>')
  // bold
  html = html.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
  // lists
  html = html.replace(/^(?:- |\d+\. )(.*)$/gm, '<li>$1</li>')
  html = html.replace(/(<li>.*<\/li>\n?)+/g, (m) => `<ul class="list-disc ml-6 space-y-1">${m}</ul>`) 
  // paragraphs: split on double newlines and wrap
  html = html
    .split(/\n\n+/)
    .map((block) =>
      /^(<h\d|<ul|<li)/.test(block.trim()) ? block : `<p class="mb-3">${block.replace(/\n/g, '<br/>')}</p>`
    )
    .join("")
  return html
}

export default function AIInsights({ summary }: { summary: string }) {
  return (
    <div className="grid lg:grid-cols-3 gap-6">
      <Card className="lg:col-span-3 border-border bg-gradient-to-br from-card via-card to-primary/5 p-8 shadow-3d">
        <div className="flex items-start gap-4 mb-6">
          <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-primary to-secondary flex items-center justify-center flex-shrink-0 shadow-lg">
            <Brain className="w-6 h-6 text-white" />
          </div>
          <div>
            <h3 className="text-xl font-bold text-foreground">What Your Data Reveals</h3>
            <p className="text-sm text-muted-foreground">Our AI's unfiltered take on your momentum</p>
          </div>
        </div>
        <div className="prose prose-sm max-w-none text-foreground/85 leading-relaxed" dangerouslySetInnerHTML={{ __html: markdownToHtml(summary) }} />
      </Card>

      <Card className="border-border bg-card p-8 shadow-3d card-gradient">
        <div className="flex items-start gap-3 mb-5">
          <TrendingUp className="w-6 h-6 text-primary flex-shrink-0 mt-0.5" />
          <h3 className="text-lg font-bold text-foreground">What's Next</h3>
        </div>
        <ul className="space-y-3.5 text-sm text-foreground/75">
          <li className="flex gap-3 p-3 rounded-lg bg-primary/5 hover:bg-primary/10 transition-colors">
            <span className="text-primary font-bold flex-shrink-0 mt-0.5">→</span>
            <span>Push marketing spend up 15-20%. You've got momentum—ride it.</span>
          </li>
          <li className="flex gap-3 p-3 rounded-lg bg-primary/5 hover:bg-primary/10 transition-colors">
            <span className="text-primary font-bold flex-shrink-0 mt-0.5">→</span>
            <span>Personalization is your next frontier. Target churn below 2.5%.</span>
          </li>
          <li className="flex gap-3 p-3 rounded-lg bg-primary/5 hover:bg-primary/10 transition-colors">
            <span className="text-primary font-bold flex-shrink-0 mt-0.5">→</span>
            <span>Lock in those first-week wins. Better onboarding = longer lifetime.</span>
          </li>
        </ul>
      </Card>

      <Card className="border-border bg-card p-8 shadow-3d card-gradient">
        <div className="flex items-start gap-3 mb-5">
          <Zap className="w-6 h-6 text-chart-5 flex-shrink-0 mt-0.5" />
          <h3 className="text-lg font-bold text-foreground">The Numbers That Matter</h3>
        </div>
        <ul className="space-y-3.5 text-sm text-foreground/75">
          <li className="flex gap-3 p-3 rounded-lg bg-chart-5/5 hover:bg-chart-5/10 transition-colors">
            <span className="text-chart-5 font-bold flex-shrink-0 mt-0.5">✓</span>
            <span>+10.2K new users landed. Acquisition is steady and strong.</span>
          </li>
          <li className="flex gap-3 p-3 rounded-lg bg-chart-5/5 hover:bg-chart-5/10 transition-colors">
            <span className="text-chart-5 font-bold flex-shrink-0 mt-0.5">✓</span>
            <span>Churn's down 42%. Your retention story is the real headline.</span>
          </li>
          <li className="flex gap-3 p-3 rounded-lg bg-chart-5/5 hover:bg-chart-5/10 transition-colors">
            <span className="text-chart-5 font-bold flex-shrink-0 mt-0.5">✓</span>
            <span>72% engagement ratio. Your base is actively using you.</span>
          </li>
        </ul>
      </Card>

      <Card className="border-border bg-card p-8 shadow-3d card-gradient">
        <div className="flex items-start gap-3 mb-5">
          <Target className="w-6 h-6 text-secondary flex-shrink-0 mt-0.5" />
          <h3 className="text-lg font-bold text-foreground">Executive Summary</h3>
        </div>
        <div className="space-y-4">
          <div className="p-3 rounded-lg bg-secondary/5 hover:bg-secondary/10 transition-colors">
            <p className="text-xs text-muted-foreground mb-1">Monthly Growth</p>
            <p className="text-2xl font-bold text-foreground">+12.5%</p>
          </div>
          <div className="p-3 rounded-lg bg-secondary/5 hover:bg-secondary/10 transition-colors">
            <p className="text-xs text-muted-foreground mb-1">Active Engagement</p>
            <p className="text-2xl font-bold text-foreground">72%</p>
          </div>
          <div className="p-3 rounded-lg bg-secondary/5 hover:bg-secondary/10 transition-colors">
            <p className="text-xs text-muted-foreground mb-1">Churn Improvement</p>
            <p className="text-2xl font-bold text-foreground">-42%</p>
          </div>
        </div>
      </Card>
    </div>
  )
}
