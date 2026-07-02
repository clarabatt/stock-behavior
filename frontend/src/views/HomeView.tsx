import { useEffect, useState } from 'react'
import { StockTable } from '@/components/StockTable'
import { ChartPanel } from '@/components/ChartPanel'
import type { LatestPrice, LatestPriceRow } from '@/types/stocks'

export default function HomeView() {
  const [stocks, setStocks] = useState<LatestPriceRow[]>([])
  const [loading, setLoading] = useState(true)
  const [selectedTicker, setSelectedTicker] = useState<string | null>(null)

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

  return (
    <div
      className="grid h-screen"
      style={{ gridTemplateColumns: selectedTicker ? '1fr 1fr' : '1fr' }}
    >
      <StockTable
        stocks={stocks}
        loading={loading}
        selectedTicker={selectedTicker}
        onSelect={setSelectedTicker}
      />
      {selectedTicker && (
        <ChartPanel
          ticker={selectedTicker}
          onClose={() => setSelectedTicker(null)}
        />
      )}
    </div>
  )
}
