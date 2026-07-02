import { useEffect } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { ChartCandlestick, LogOut } from 'lucide-react'
import { useAuthStore } from '@/stores/auth'
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar'
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu'

function initials(name: string): string {
  return name
    .split(' ')
    .map(part => part[0])
    .slice(0, 2)
    .join('')
    .toUpperCase()
}

export function Header() {
  const { user, loading, fetchUser, clear } = useAuthStore()
  const navigate = useNavigate()

  useEffect(() => {
    fetchUser()
  }, [fetchUser])

  async function handleSignOut() {
    await fetch('/auth/logout', { method: 'POST', credentials: 'include' })
    clear()
    navigate('/login')
  }

  return (
    <header className="flex h-14 shrink-0 items-center gap-3 border-b bg-background px-6">
      <Link to="/" className="flex items-center gap-2 font-heading font-semibold tracking-tight">
        <ChartCandlestick className="size-5 text-primary" />
        Stock Behavior
      </Link>

      <div className="ml-auto flex items-center gap-3">
        {!loading && user && (
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <button className="flex items-center gap-2 rounded-full outline-none focus-visible:ring-3 focus-visible:ring-ring/50">
                <Avatar size="sm">
                  {user.picture_url && <AvatarImage src={user.picture_url} alt={user.full_name} />}
                  <AvatarFallback>{initials(user.full_name)}</AvatarFallback>
                </Avatar>
              </button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end" className="w-56">
              <DropdownMenuLabel className="flex flex-col gap-0.5">
                <span className="font-medium text-foreground">{user.full_name}</span>
                <span className="font-normal text-muted-foreground">{user.email}</span>
              </DropdownMenuLabel>
              <DropdownMenuSeparator />
              <DropdownMenuItem onClick={handleSignOut} variant="destructive">
                <LogOut />
                Sign out
              </DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
        )}
      </div>
    </header>
  )
}
