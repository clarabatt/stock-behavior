import { Outlet } from 'react-router-dom'
import { Header } from '@/components/Header'

export default function App() {
  return (
    <div className="flex h-screen min-h-0 flex-col">
      <Header />
      <main className="flex-1 min-h-0">
        <Outlet />
      </main>
    </div>
  )
}
