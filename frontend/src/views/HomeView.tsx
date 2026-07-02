import { useCallback, useEffect, useState } from 'react'
import { StockTable } from '@/components/StockTable'
import { ChartPanel } from '@/components/ChartPanel'
import { fetchNotes } from '@/services/notes'
import type { LatestPrice, LatestPriceRow } from '@/types/stocks'

export default function HomeView() {
  const [stocks, setStocks] = useState<LatestPriceRow[]>([])
  const [loading, setLoading] = useState(true)
  const [selectedTicker, setSelectedTicker] = useState<string | null>(null)
  const [tickersWithNotes, setTickersWithNotes] = useState<Set<string>>(new Set())

  useEffect(() => {
    fetch('/api/prices/latest')
      .then(r => r.json() as Promise<LatestPrice[]>)
      .then(data => {
        setStocks(
          data.map(p => ({
            ...p,
            changePercent: p.open !== 0 ? ((p.close - p.open) / p.open) * 100 : 0,
          })),
        )
      })
      .catch(console.error)
      .finally(() => setLoading(false))
  }, [])

  const refreshNoteIndicators = useCallback(() => {
    fetchNotes()
      .then(notes => setTickersWithNotes(new Set(notes.map(n => n.ticker))))
      .catch(console.error)
  }, [])

  useEffect(() => {
    refreshNoteIndicators()
  }, [refreshNoteIndicators])

  return (
    <div className="flex h-full min-h-0 flex-col gap-4 p-6">
      <div>
        <h1 className="font-heading text-2xl font-semibold tracking-tight">Stock Behavior</h1>
        <p className="text-sm text-muted-foreground">
          Live prices across the S&amp;P 500. Select a ticker to inspect its trend.
        </p>
      </div>

      <div
        className="grid min-h-0 flex-1 overflow-hidden rounded-xl bg-card shadow-sm ring-1 ring-foreground/10"
        style={{ gridTemplateColumns: selectedTicker ? '1fr 1fr' : '1fr' }}
      >
        <StockTable
          stocks={stocks}
          loading={loading}
          selectedTicker={selectedTicker}
          onSelect={setSelectedTicker}
          tickersWithNotes={tickersWithNotes}
        />
        {selectedTicker && (
          <ChartPanel
            ticker={selectedTicker}
            onClose={() => setSelectedTicker(null)}
            onNotesChange={refreshNoteIndicators}
          />
        )}
      </div>
    </div>
  )
}
