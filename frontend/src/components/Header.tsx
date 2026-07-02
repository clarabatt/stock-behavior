import { Link } from 'react-router-dom'
import { ChartCandlestick } from 'lucide-react'

export function Header() {
  return (
    <header className="flex h-14 shrink-0 items-center gap-3 border-b bg-background px-6">
      <Link to="/" className="flex items-center gap-2 font-heading font-semibold tracking-tight">
        <ChartCandlestick className="size-5 text-primary" />
        Stock Behavior
      </Link>
    </header>
  )
}
