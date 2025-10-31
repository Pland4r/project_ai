"use client"

import type React from "react"

import { useState, useRef } from "react"
import { Upload, TrendingUp, BarChart3, Brain, Zap } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Card } from "@/components/ui/card"
import DataVisualization from "@/components/data-visualization"
import AIInsights from "@/components/ai-insights"
import StatsSummary from "@/components/stats-summary"
// @ts-ignore
import { uploadFile, analyzeData } from "@/lib/apiService"

export default function Home() {
  const [isLoading, setIsLoading] = useState(false)
  const [analysisComplete, setAnalysisComplete] = useState(false)
  const [fileName, setFileName] = useState("")
  const [analysisResults, setAnalysisResults] = useState<any>(null)
  const fileInputRef = useRef<HTMLInputElement>(null)

  const handleFileUpload = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0]
    if (!file) return

    setFileName(file.name)
    setIsLoading(true)

    try {
      // Upload the file to the backend
      const uploadResponse = await uploadFile(file)
      const filePath = uploadResponse.file_path

      // Analyze the uploaded file
      const analysisResponse = await analyzeData(filePath)
      setAnalysisResults(analysisResponse)
      setAnalysisComplete(true)
    } catch (error) {
      console.error("Error during file processing:", error)
      // Optionally, set an error state and display it
    } finally {
      setIsLoading(false)
    }
  }

  const triggerFileInput = () => {
    fileInputRef.current?.click()
  }

  return (
    <main className="min-h-screen bg-background">
      <header className="sticky top-0 z-40 border-b border-border bg-card/95 backdrop-blur smooth-transition">
        <div className="max-w-7xl mx-auto px-6 py-5">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-primary via-primary to-secondary flex items-center justify-center shadow-lg transform transition-transform hover:scale-105">
                <TrendingUp className="w-6 h-6 text-white" />
              </div>
              <div>
                <h1 className="text-xl font-bold bg-gradient-to-r from-primary to-secondary bg-clip-text text-transparent">
                  GrowthAI
                </h1>
                <p className="text-xs text-muted-foreground">Unlock Your Growth Potential</p>
              </div>
            </div>
          </div>
        </div>
      </header>

      <div className="max-w-7xl mx-auto px-6 py-12">
        {!analysisComplete ? (
          /* Upload section with enhanced copy and 3D effects */
          <div className="space-y-8">
            <div className="text-center space-y-4">
              <h2 className="text-5xl font-bold text-foreground text-balance leading-tight">
                Data Becomes Destiny
                <span className="block bg-gradient-to-r from-primary via-secondary to-primary bg-clip-text text-transparent">
                  Watch Your Growth Evolve
                </span>
              </h2>
              <p className="text-lg text-muted-foreground max-w-2xl mx-auto leading-relaxed">
                Upload your data, get brilliant insights. No spreadsheets. No guessing. Just pure, actionable
                intelligence crafted by advanced AI.
              </p>
            </div>

            <Card className="border-border bg-card p-12 shadow-3d card-gradient">
              <div className="flex flex-col items-center justify-center gap-6">
                <div className="w-24 h-24 rounded-3xl bg-gradient-to-br from-primary/20 to-secondary/10 flex items-center justify-center transform transition-transform duration-300 hover:scale-110">
                  <Upload className="w-12 h-12 text-primary" />
                </div>

                <div className="text-center space-y-3">
                  <h3 className="text-2xl font-bold text-foreground">Drop Your Data Here</h3>
                  <p className="text-muted-foreground text-sm">
                    CSV, Excel, or any data file. We'll handle the heavy lifting.
                  </p>
                </div>

                <input
                  ref={fileInputRef}
                  type="file"
                  accept=".csv,.xlsx,.xls"
                  onChange={handleFileUpload}
                  className="hidden"
                />

                <Button
                  onClick={triggerFileInput}
                  disabled={isLoading}
                  size="lg"
                  className="bg-gradient-to-r from-primary to-secondary hover:shadow-lg text-white px-8 py-3 rounded-xl transform transition-all duration-300 hover:scale-105 disabled:opacity-70"
                >
                  {isLoading ? (
                    <>
                      <span className="animate-spin mr-2">⚡</span>
                      Running Analysis...
                    </>
                  ) : (
                    <>
                      <Upload className="w-5 h-5 mr-2" />
                      Select Your File
                    </>
                  )}
                </Button>
              </div>
            </Card>

            <div className="grid md:grid-cols-3 gap-6">
              <Card className="border-border bg-card p-6 shadow-3d smooth-transition card-gradient group">
                <div className="flex gap-4">
                  <div className="w-12 h-12 rounded-xl bg-primary/10 flex items-center justify-center flex-shrink-0 group-hover:bg-primary/20 transition-colors">
                    <BarChart3 className="w-6 h-6 text-primary" />
                  </div>
                  <div>
                    <h4 className="font-semibold text-foreground mb-1">Crystal Clear Analytics</h4>
                    <p className="text-sm text-muted-foreground">See patterns others miss. Predict what's next.</p>
                  </div>
                </div>
              </Card>

              <Card className="border-border bg-card p-6 shadow-3d smooth-transition card-gradient group">
                <div className="flex gap-4">
                  <div className="w-12 h-12 rounded-xl bg-secondary/10 flex items-center justify-center flex-shrink-0 group-hover:bg-secondary/20 transition-colors">
                    <Brain className="w-6 h-6 text-secondary" />
                  </div>
                  <div>
                    <h4 className="font-semibold text-foreground mb-1">AI That Actually Listens</h4>
                    <p className="text-sm text-muted-foreground">Insights tailored to your unique story.</p>
                  </div>
                </div>
              </Card>

              <Card className="border-border bg-card p-6 shadow-3d smooth-transition card-gradient group">
                <div className="flex gap-4">
                  <div className="w-12 h-12 rounded-xl bg-chart-3/10 flex items-center justify-center flex-shrink-0 group-hover:bg-chart-3/20 transition-colors">
                    <Zap className="w-6 h-6 text-chart-3" />
                  </div>
                  <div>
                    <h4 className="font-semibold text-foreground mb-1">Speed That Matters</h4>
                    <p className="text-sm text-muted-foreground">From upload to insights in under a minute.</p>
                  </div>
                </div>
              </Card>
            </div>
          </div>
        ) : (
          /* Analysis results */
          <div className="space-y-8">
            <div className="flex items-center justify-between">
              <div>
                <h2 className="text-3xl font-bold text-foreground mb-2">Your Growth Blueprint</h2>
                <p className="text-muted-foreground">
                  Analyzing: <span className="font-semibold text-foreground">{fileName}</span>
                </p>
              </div>
              <Button
                onClick={() => {
                  setAnalysisComplete(false)
                  setFileName("")
                  if (fileInputRef.current) fileInputRef.current.value = ""
                }}
                variant="outline"
                className="border-border text-foreground hover:bg-muted smooth-transition"
              >
                Upload Another File
              </Button>
            </div>

            <StatsSummary data={analysisResults?.metrics} />
            <DataVisualization data={analysisResults?.visualizationData} />
            <AIInsights summary={analysisResults?.ai_summary} />
          </div>
        )}
      </div>
    </main>
  )
}
