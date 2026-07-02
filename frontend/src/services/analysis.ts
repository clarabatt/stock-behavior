export interface AskQuestionResponse {
  answer: string
  sql: string
  row_count: number
}

export async function askQuestion(question: string): Promise<AskQuestionResponse> {
  const res = await fetch('/api/analysis/ask', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ question }),
  })
  if (!res.ok) {
    const detail = await res.json().catch(() => null)
    throw new Error(detail?.detail ?? `${res.status}`)
  }
  return res.json() as Promise<AskQuestionResponse>
}
