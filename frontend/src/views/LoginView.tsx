import { ChartCandlestick } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'

export default function LoginView() {
  return (
    <div className="flex h-screen items-center justify-center bg-muted/30 p-6">
      <Card className="w-full max-w-sm">
        <CardHeader className="items-center gap-2 text-center">
          <div className="mb-1 flex size-10 items-center justify-center rounded-xl bg-primary text-primary-foreground">
            <ChartCandlestick className="size-5" />
          </div>
          <CardTitle className="text-xl">Stock Behavior</CardTitle>
          <CardDescription>
            Sign in to explore S&amp;P 500 price behavior and your saved notes.
          </CardDescription>
        </CardHeader>
        <CardContent>
          <Button asChild size="lg" className="w-full">
            <a href="/auth/google/login">Sign in with Google</a>
          </Button>
        </CardContent>
      </Card>
    </div>
  )
}
