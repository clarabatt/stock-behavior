export interface Note {
  id: string
  ticker: string
  company_name: string
  date: string
  body: string
  created_at: string
  updated_at: string
}

export async function fetchNotes(ticker?: string): Promise<Note[]> {
  const url = ticker ? `/api/notes?ticker=${encodeURIComponent(ticker)}` : '/api/notes'
  const res = await fetch(url)
  if (res.status === 401) return []
  if (!res.ok) throw new Error(`${res.status}`)
  return res.json() as Promise<Note[]>
}

export async function createNote(ticker: string, date: string, body: string): Promise<Note> {
  const res = await fetch('/api/notes', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ ticker, date, body }),
  })
  if (!res.ok) throw new Error(`${res.status}`)
  return res.json() as Promise<Note>
}

export async function updateNote(id: string, body: string): Promise<Note> {
  const res = await fetch(`/api/notes/${id}`, {
    method: 'PATCH',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ body }),
  })
  if (!res.ok) throw new Error(`${res.status}`)
  return res.json() as Promise<Note>
}

export async function deleteNote(id: string): Promise<void> {
  const res = await fetch(`/api/notes/${id}`, { method: 'DELETE' })
  if (!res.ok) throw new Error(`${res.status}`)
}
