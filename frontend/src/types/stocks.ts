export interface LatestPrice {
  ticker: string
  name: string
  sector: string | null
  timestamp: string
  open: number
  high: number
  low: number
  close: number
  volume: number
}

export interface LatestPriceRow extends LatestPrice {
  changePercent: number
}

export interface PriceBar {
  timestamp: string
  open: number
  high: number
  low: number
  close: number
  volume: number
}

export type SortColumn = 'ticker' | 'name' | 'sector' | 'close' | 'change'
export type SortDirection = 'asc' | 'desc'
export type DateRange = '1D' | '1W' | '1M' | '3M'
