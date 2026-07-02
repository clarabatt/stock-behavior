import { useEffect, useState } from 'react'
import { Pencil, Trash2, Plus } from 'lucide-react'
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
import { Input } from '@/components/ui/input'
import { Skeleton } from '@/components/ui/skeleton'
import { Textarea } from '@/components/ui/textarea'
import { fetchNotes, createNote, updateNote, deleteNote, type Note } from '@/services/notes'
import type { DateRange, PriceBar } from '@/types/stocks'

interface Props {
  ticker: string
  onClose: () => void
  onNotesChange?: () => void
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

function formatTime(epochMs: number): string {
  return new Date(epochMs).toLocaleTimeString(undefined, { hour: 'numeric', minute: '2-digit' })
}

function aggregateToDaily(bars: ChartPoint[]): ChartPoint[] {
  const byDate = new Map<string, ChartPoint>()
  for (const bar of bars) {
    byDate.set(new Date(bar.ts).toISOString().slice(0, 10), bar)
  }
  return Array.from(byDate.values())
}

function tooltipFormatter(value: number | string | readonly (number | string)[] | undefined): ReactNode {
  if (typeof value !== 'number') return String(value ?? '')
  return `$${value.toFixed(2)}`
}

const chartConfig = {
  close: { label: 'Price', color: '#3b82f6' },
} satisfies ChartConfig

function today(): string {
  return new Date().toISOString().slice(0, 10)
}

interface NoteCardProps {
  note: Note
  onEdit: (note: Note) => void
  onDelete: (id: string) => void
}

function NoteCard({ note, onEdit, onDelete }: NoteCardProps) {
  return (
    <div className="rounded-md bg-muted/50 p-2.5 text-sm">
      <div className="flex items-center justify-between mb-1">
        <span className="text-xs text-muted-foreground font-mono">{note.date}</span>
        <div className="flex gap-0.5">
          <Button size="icon-xs" variant="ghost" onClick={() => onEdit(note)}>
            <Pencil className="h-3 w-3" />
          </Button>
          <Button size="icon-xs" variant="ghost" onClick={() => onDelete(note.id)}>
            <Trash2 className="h-3 w-3" />
          </Button>
        </div>
      </div>
      <p className="whitespace-pre-wrap text-sm leading-snug">{note.body}</p>
    </div>
  )
}

export function ChartPanel({ ticker, onNotesChange }: Props) {
  const [dateRange, setDateRange] = useState<DateRange>('1M')
  const [chartData, setChartData] = useState<ChartPoint[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const [notes, setNotes] = useState<Note[]>([])
  const [notesLoading, setNotesLoading] = useState(true)
  const [showForm, setShowForm] = useState(false)
  const [editingNoteId, setEditingNoteId] = useState<string | null>(null)
  const [formDate, setFormDate] = useState(today())
  const [formBody, setFormBody] = useState('')
  const [formError, setFormError] = useState<string | null>(null)
  const [saving, setSaving] = useState(false)

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
        const points = bars.map(b => ({ ts: new Date(b.timestamp).getTime(), close: b.close }))
        setChartData(dateRange === '1M' || dateRange === '3M' ? aggregateToDaily(points) : points)
      })
      .catch(err => {
        if (!cancelled) setError((err as Error).message)
      })
      .finally(() => {
        if (!cancelled) setLoading(false)
      })

    return () => { cancelled = true }
  }, [ticker, dateRange])

  useEffect(() => {
    let cancelled = false
    setNotesLoading(true)
    fetchNotes(ticker)
      .then(data => { if (!cancelled) setNotes(data) })
      .catch(console.error)
      .finally(() => { if (!cancelled) setNotesLoading(false) })
    return () => { cancelled = true }
  }, [ticker])

  function openAddForm(date?: string) {
    setEditingNoteId(null)
    setFormDate(date ?? today())
    setFormBody('')
    setFormError(null)
    setShowForm(true)
  }

  function handleChartClick(data: { activeLabel?: string | number }) {
    const ts = Number(data?.activeLabel)
    if (!ts || isNaN(ts)) return
    const date = new Date(ts).toISOString().slice(0, 10)
    if (showForm && !editingNoteId) {
      setFormDate(date)
    } else if (!showForm) {
      openAddForm(date)
    }
  }

  function openEditForm(note: Note) {
    setEditingNoteId(note.id)
    setFormDate(note.date)
    setFormBody(note.body)
    setFormError(null)
    setShowForm(true)
  }

  function cancelForm() {
    setShowForm(false)
    setEditingNoteId(null)
    setFormError(null)
  }

  async function handleSave() {
    if (!formBody.trim()) {
      setFormError('Note body cannot be empty.')
      return
    }
    setSaving(true)
    setFormError(null)
    try {
      if (editingNoteId) {
        const updated = await updateNote(editingNoteId, formBody.trim())
        setNotes(prev => prev.map(n => n.id === editingNoteId ? updated : n))
      } else {
        const created = await createNote(ticker, formDate, formBody.trim())
        setNotes(prev => [created, ...prev].sort((a, b) => b.date.localeCompare(a.date)))
        onNotesChange?.()
      }
      cancelForm()
    } catch (err) {
      const msg = (err as Error).message
      setFormError(msg === '409' ? 'A note for this date already exists.' : 'Failed to save note.')
    } finally {
      setSaving(false)
    }
  }

  async function handleDelete(id: string) {
    try {
      await deleteNote(id)
      setNotes(prev => prev.filter(n => n.id !== id))
      onNotesChange?.()
    } catch {
      // silently ignore — note will still show until refresh
    }
  }

  const isIntraday = dateRange === '1D' || dateRange === '1W'
  const xTickFormatter = isIntraday ? formatTime : formatTs
  const labelFormatter = (_label: ReactNode, payload: ReadonlyArray<{ payload?: ChartPoint }>): ReactNode => {
    const ts = payload[0]?.payload?.ts
    if (typeof ts !== 'number') return ''
    const opts: Intl.DateTimeFormatOptions = isIntraday
      ? { month: 'long', day: 'numeric', year: 'numeric', hour: 'numeric', minute: '2-digit' }
      : { month: 'long', day: 'numeric', year: 'numeric' }
    return new Date(ts).toLocaleString(undefined, opts)
  }

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
              className="h-7 cursor-pointer px-2 text-xs"
              onClick={() => setDateRange(r)}
            >
              {r}
            </Button>
          ))}
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
          <ChartContainer config={chartConfig} className="h-full w-full cursor-crosshair">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={chartData} margin={{ top: 8, right: 8, bottom: 0, left: 8 }} onClick={handleChartClick}>
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
                  tickFormatter={xTickFormatter}
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
                  tickFormatter={xTickFormatter}
                  fill="var(--color-muted)"
                  stroke="var(--color-border)"
                />
              </AreaChart>
            </ResponsiveContainer>
          </ChartContainer>
        )}
      </CardContent>

      <div className="shrink-0 border-t px-4 py-3">
        <div className="flex items-center justify-between mb-2">
          <span className="text-sm font-medium">Notes</span>
          {!showForm && (
            <Button size="xs" variant="outline" onClick={openAddForm}>
              <Plus className="h-3 w-3 mr-1" />
              Add note
            </Button>
          )}
        </div>

        {showForm && (
          <div className="flex flex-col gap-2 mb-3">
            <Input
              type="date"
              value={formDate}
              onChange={e => setFormDate(e.target.value)}
              disabled={!!editingNoteId}
            />
            <Textarea
              value={formBody}
              onChange={e => setFormBody(e.target.value)}
              placeholder="Record your hypothesis…"
              rows={3}
            />
            {formError && <p className="text-xs text-destructive">{formError}</p>}
            <div className="flex gap-2">
              <Button size="sm" onClick={handleSave} disabled={saving}>
                {saving ? 'Saving…' : 'Save'}
              </Button>
              <Button size="sm" variant="ghost" onClick={cancelForm} disabled={saving}>
                Cancel
              </Button>
            </div>
          </div>
        )}

        <div className="flex flex-col gap-2 max-h-40 overflow-auto">
          {notesLoading
            ? <Skeleton className="h-10 w-full" />
            : notes.length === 0 && !showForm
              ? <p className="text-xs text-muted-foreground">No notes yet.</p>
              : notes.map(note => (
                  <NoteCard
                    key={note.id}
                    note={note}
                    onEdit={openEditForm}
                    onDelete={handleDelete}
                  />
                ))
          }
        </div>
      </div>
    </Card>
  )
}
