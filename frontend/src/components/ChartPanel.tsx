import { useEffect, useState } from 'react'
import { X } from 'lucide-react'
import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Brush,
  ResponsiveContainer,
} from 'recharts'
import type { ReactNode } from 'react'
import {
  ChartContainer,
  ChartTooltip,
  ChartTooltipContent,
  type ChartConfig,
} from '@/components/ui/chart'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Skeleton } from '@/components/ui/skeleton'
import type { DateRange, PriceBar } from '@/types/stocks'

interface Props {
  ticker: string
  onClose: () => void
}

interface ChartPoint {
  ts: number
  close: number
}

const DATE_RANGES: DateRange[] = ['1D', '1W', '1M', '3M']

function dateRangeToIso(range: DateRange): { from: string; to: string } {
  const to = new Date()
  const from = new Date(to)
  if (range === '1D') from.setDate(from.getDate() - 1)
  else if (range === '1W') from.setDate(from.getDate() - 7)
  else if (range === '1M') from.setMonth(from.getMonth() - 1)
  else from.setMonth(from.getMonth() - 3)
  return { from: from.toISOString(), to: to.toISOString() }
}

function formatTs(epochMs: number): string {
  return new Date(epochMs).toLocaleDateString(undefined, { month: 'short', day: 'numeric' })
}

function labelFormatter(_label: ReactNode, payload: ReadonlyArray<{ payload?: ChartPoint }>): ReactNode {
  const ts = payload[0]?.payload?.ts
  if (typeof ts !== 'number') return ''
  return new Date(ts).toLocaleDateString(undefined, { month: 'long', day: 'numeric', year: 'numeric' })
}

function tooltipFormatter(value: number | string | readonly (number | string)[] | undefined): ReactNode {
  if (typeof value !== 'number') return String(value ?? '')
  return `$${value.toFixed(2)}`
}

const chartConfig = {
  close: { label: 'Price', color: '#3b82f6' },
} satisfies ChartConfig

export function ChartPanel({ ticker, onClose }: Props) {
  const [dateRange, setDateRange] = useState<DateRange>('1M')
  const [chartData, setChartData] = useState<ChartPoint[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    let cancelled = false
    setLoading(true)
    setError(null)

    const { from, to } = dateRangeToIso(dateRange)
    fetch(`/api/prices/${ticker}/history?from=${encodeURIComponent(from)}&to=${encodeURIComponent(to)}`)
      .then(r => {
        if (!r.ok) throw new Error(`${r.status}`)
        return r.json() as Promise<PriceBar[]>
      })
      .then(bars => {
        if (cancelled) return
        setChartData(bars.map(b => ({ ts: new Date(b.timestamp).getTime(), close: b.close })))
      })
      .catch(err => {
        if (!cancelled) setError((err as Error).message)
      })
      .finally(() => {
        if (!cancelled) setLoading(false)
      })

    return () => { cancelled = true }
  }, [ticker, dateRange])

  const lastClose = chartData[chartData.length - 1]?.close
  const firstClose = chartData[0]?.close
  const pctChange =
    lastClose !== undefined && firstClose !== undefined && firstClose !== 0
      ? ((lastClose - firstClose) / firstClose) * 100
      : null

  return (
    <Card className="flex flex-col h-full min-h-0 rounded-none border-0 border-l">
      <CardHeader className="flex-row items-center gap-3 shrink-0 pb-2">
        <CardTitle className="text-lg font-mono">{ticker}</CardTitle>
        {lastClose !== undefined && (
          <span className="text-2xl font-semibold">${lastClose.toFixed(2)}</span>
        )}
        {pctChange !== null && (
          <span className={`text-sm font-medium ${pctChange >= 0 ? 'text-green-600' : 'text-red-600'}`}>
            {pctChange >= 0 ? '+' : ''}{pctChange.toFixed(2)}%
          </span>
        )}
        <div className="ml-auto flex items-center gap-1">
          {DATE_RANGES.map(r => (
            <Button
              key={r}
              variant={dateRange === r ? 'default' : 'ghost'}
              size="sm"
              className="h-7 px-2 text-xs"
              onClick={() => setDateRange(r)}
            >
              {r}
            </Button>
          ))}
          <Button variant="ghost" size="icon" className="h-7 w-7 ml-1" onClick={onClose}>
            <X className="h-4 w-4" />
          </Button>
        </div>
      </CardHeader>

      <CardContent className="flex-1 min-h-0 pb-4">
        {loading && <Skeleton className="h-full w-full" />}
        {!loading && error && (
          <div className="flex items-center justify-center h-full text-sm text-muted-foreground">
            Failed to load price history.
          </div>
        )}
        {!loading && !error && chartData.length === 0 && (
          <div className="flex items-center justify-center h-full text-sm text-muted-foreground">
            No data for this range.
          </div>
        )}
        {!loading && !error && chartData.length > 0 && (
          <ChartContainer config={chartConfig} className="h-full w-full">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={chartData} margin={{ top: 8, right: 8, bottom: 0, left: 8 }}>
                <defs>
                  <linearGradient id="fillClose" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="var(--color-close)" stopOpacity={0.3} />
                    <stop offset="95%" stopColor="var(--color-close)" stopOpacity={0} />
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" vertical={false} />
                <XAxis
                  dataKey="ts"
                  type="number"
                  scale="time"
                  domain={['dataMin', 'dataMax']}
                  tickFormatter={formatTs}
                  tick={{ fontSize: 11 }}
                  tickLine={false}
                  axisLine={false}
                  minTickGap={60}
                />
                <YAxis
                  domain={['auto', 'auto']}
                  tickFormatter={(v: number) => `$${v.toFixed(0)}`}
                  tick={{ fontSize: 11 }}
                  tickLine={false}
                  axisLine={false}
                  width={55}
                />
                <ChartTooltip
                  content={
                    <ChartTooltipContent
                      labelFormatter={labelFormatter}
                      formatter={tooltipFormatter}
                    />
                  }
                />
                <Area
                  type="monotone"
                  dataKey="close"
                  stroke="var(--color-close)"
                  strokeWidth={2}
                  fill="url(#fillClose)"
                  dot={false}
                  activeDot={{ r: 4 }}
                />
                <Brush
                  dataKey="ts"
                  height={28}
                  tickFormatter={formatTs}
                  fill="var(--color-muted)"
                  stroke="var(--color-border)"
                />
              </AreaChart>
            </ResponsiveContainer>
          </ChartContainer>
        )}
      </CardContent>
    </Card>
  )
}
