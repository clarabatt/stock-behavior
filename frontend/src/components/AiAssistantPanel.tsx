import { useState, type KeyboardEvent } from 'react'
import { ChevronDown, ChevronRight, Sparkles } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Skeleton } from '@/components/ui/skeleton'
import { Textarea } from '@/components/ui/textarea'
import { askQuestion, type AskQuestionResponse } from '@/services/analysis'

export function AiAssistantPanel() {
  const [question, setQuestion] = useState('')
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState<AskQuestionResponse | null>(null)
  const [showSql, setShowSql] = useState(false)
  const [error, setError] = useState<string | null>(null)

  async function handleSubmit() {
    const trimmed = question.trim()
    if (!trimmed || loading) return

    setLoading(true)
    setResult(null)
    setError(null)
    try {
      const response = await askQuestion(trimmed)
      setResult(response)
      setShowSql(false)
    } catch (err) {
      setError((err as Error).message || 'Failed to get an answer.')
    } finally {
      setLoading(false)
    }
  }

  function handleKeyDown(e: KeyboardEvent<HTMLTextAreaElement>) {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSubmit()
    }
  }

  return (
    <Card className="shrink-0">
      <CardHeader className="pb-2">
        <CardTitle className="flex items-center gap-2 text-base">
          <Sparkles className="h-4 w-4" />
          Ask about the data
        </CardTitle>
      </CardHeader>
      <CardContent className="flex flex-col gap-3">
        <div className="flex gap-2">
          <Textarea
            value={question}
            onChange={e => setQuestion(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="e.g. What was the steepest single-day decline during the COVID crash?"
            rows={2}
            disabled={loading}
            className="flex-1"
          />
          <Button onClick={handleSubmit} disabled={loading || !question.trim()} className="self-end">
            {loading ? 'Asking…' : 'Ask'}
          </Button>
        </div>

        {loading && <Skeleton className="h-16 w-full" />}

        {!loading && error && <p className="text-xs text-destructive">{error}</p>}

        {!loading && result && (
          <div className="rounded-md bg-muted/50 p-3 text-sm">
            <p className="whitespace-pre-wrap leading-snug">{result.answer}</p>
            <button
              type="button"
              onClick={() => setShowSql(v => !v)}
              className="mt-2 flex items-center gap-1 text-xs text-muted-foreground hover:text-foreground"
            >
              {showSql ? <ChevronDown className="h-3 w-3" /> : <ChevronRight className="h-3 w-3" />}
              Show query used
            </button>
            {showSql && (
              <pre className="mt-2 overflow-x-auto rounded bg-background p-2 text-xs text-muted-foreground">
                {result.sql}
              </pre>
            )}
            <p className="mt-1 text-xs text-muted-foreground">{result.row_count} row(s) returned.</p>
          </div>
        )}
      </CardContent>
    </Card>
  )
}
