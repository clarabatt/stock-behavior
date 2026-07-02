import { useMemo, useState } from 'react'
import { ChevronUp, ChevronDown, ChevronsUpDown } from 'lucide-react'
import { Input } from '@/components/ui/input'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import { Badge } from '@/components/ui/badge'
import { Skeleton } from '@/components/ui/skeleton'
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table'
import type { LatestPriceRow, SortColumn, SortDirection } from '@/types/stocks'

interface Props {
  stocks: LatestPriceRow[]
  loading: boolean
  selectedTicker: string | null
  onSelect: (ticker: string) => void
}

function SortIcon({ column, active, direction }: { column: SortColumn; active: SortColumn; direction: SortDirection }) {
  if (column !== active) return <ChevronsUpDown className="ml-1 h-3 w-3 text-muted-foreground" />
  return direction === 'asc'
    ? <ChevronUp className="ml-1 h-3 w-3" />
    : <ChevronDown className="ml-1 h-3 w-3" />
}

function ChangeCell({ pct }: { pct: number }) {
  const formatted = `${pct >= 0 ? '+' : ''}${pct.toFixed(2)}%`
  if (pct > 0) return <Badge className="bg-green-100 text-green-800 hover:bg-green-100 font-mono">{formatted}</Badge>
  if (pct < 0) return <Badge className="bg-red-100 text-red-800 hover:bg-red-100 font-mono">{formatted}</Badge>
  return <Badge variant="secondary" className="font-mono">{formatted}</Badge>
}

export function StockTable({ stocks, loading, selectedTicker, onSelect }: Props) {
  const [search, setSearch] = useState('')
  const [sectorFilter, setSectorFilter] = useState('all')
  const [sortColumn, setSortColumn] = useState<SortColumn>('ticker')
  const [sortDirection, setSortDirection] = useState<SortDirection>('asc')

  const sectors = useMemo(
    () => [...new Set(stocks.map(s => s.sector).filter((s): s is string => s !== null))].sort(),
    [stocks],
  )

  const rows = useMemo(() => {
    const q = search.toLowerCase()
    let filtered = stocks.filter(s => {
      const matchesSearch = !q || s.ticker.toLowerCase().includes(q) || s.name.toLowerCase().includes(q)
      const matchesSector = sectorFilter === 'all' || s.sector === sectorFilter
      return matchesSearch && matchesSector
    })

    filtered = [...filtered].sort((a, b) => {
      const dir = sortDirection === 'asc' ? 1 : -1
      if (sortColumn === 'ticker') return a.ticker.localeCompare(b.ticker) * dir
      if (sortColumn === 'name') return a.name.localeCompare(b.name) * dir
      if (sortColumn === 'sector') {
        if (a.sector === null && b.sector === null) return 0
        if (a.sector === null) return 1
        if (b.sector === null) return -1
        return a.sector.localeCompare(b.sector) * dir
      }
      if (sortColumn === 'close') return (a.close - b.close) * dir
      return (a.changePercent - b.changePercent) * dir
    })

    return filtered
  }, [stocks, search, sectorFilter, sortColumn, sortDirection])

  function handleSort(col: SortColumn) {
    if (col === sortColumn) {
      setSortDirection(d => d === 'asc' ? 'desc' : 'asc')
    } else {
      setSortColumn(col)
      setSortDirection('asc')
    }
  }

  return (
    <div className="flex flex-col h-full min-h-0">
      <div className="flex gap-2 p-3 border-b shrink-0">
        <Input
          placeholder="Search ticker or name…"
          value={search}
          onChange={e => setSearch(e.target.value)}
          className="max-w-64"
        />
        <Select value={sectorFilter} onValueChange={setSectorFilter}>
          <SelectTrigger className="w-52">
            <SelectValue placeholder="All sectors" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">All sectors</SelectItem>
            {sectors.map(s => <SelectItem key={s} value={s}>{s}</SelectItem>)}
          </SelectContent>
        </Select>
        <span className="ml-auto text-sm text-muted-foreground self-center">
          {loading ? '…' : `${rows.length} companies`}
        </span>
      </div>

      <div className="overflow-auto flex-1 min-h-0">
        <Table>
          <TableHeader className="sticky top-0 bg-background z-10">
            <TableRow>
              {([
                ['ticker', 'Ticker'],
                ['name', 'Company'],
                ['sector', 'Sector'],
                ['close', 'Price'],
                ['change', 'Change'],
              ] as [SortColumn, string][]).map(([col, label]) => (
                <TableHead
                  key={col}
                  className="cursor-pointer select-none whitespace-nowrap"
                  onClick={() => handleSort(col)}
                >
                  <span className="inline-flex items-center">
                    {label}
                    <SortIcon column={col} active={sortColumn} direction={sortDirection} />
                  </span>
                </TableHead>
              ))}
              <TableHead>Volume</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {loading
              ? Array.from({ length: 12 }).map((_, i) => (
                  <TableRow key={i}>
                    {Array.from({ length: 6 }).map((_, j) => (
                      <TableCell key={j}><Skeleton className="h-4 w-full" /></TableCell>
                    ))}
                  </TableRow>
                ))
              : rows.map(s => (
                  <TableRow
                    key={s.ticker}
                    className={`cursor-pointer ${selectedTicker === s.ticker ? 'bg-muted' : ''}`}
                    onClick={() => onSelect(s.ticker)}
                  >
                    <TableCell className="font-mono font-semibold">{s.ticker}</TableCell>
                    <TableCell className="max-w-48 truncate">{s.name}</TableCell>
                    <TableCell className="text-muted-foreground text-sm">{s.sector ?? '—'}</TableCell>
                    <TableCell className="font-mono">${s.close.toFixed(2)}</TableCell>
                    <TableCell><ChangeCell pct={s.changePercent} /></TableCell>
                    <TableCell className="font-mono text-muted-foreground text-sm">
                      {s.volume.toLocaleString()}
                    </TableCell>
                  </TableRow>
                ))}
          </TableBody>
        </Table>
      </div>
    </div>
  )
}
