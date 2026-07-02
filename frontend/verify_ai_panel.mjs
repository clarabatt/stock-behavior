import { chromium } from 'playwright'

const browser = await chromium.launch()
const page = await browser.newPage()
const consoleErrors = []
page.on('console', msg => { if (msg.type() === 'error') consoleErrors.push(msg.text()) })

await page.goto('http://localhost:5173', { waitUntil: 'networkidle' })
await page.waitForSelector('text=Ask about the data', { timeout: 15000 })

const textarea = page.locator('textarea[placeholder*="steepest"]')
await textarea.fill('which company had the steepest single-day decline?')

await page.screenshot({ path: '/tmp/ai_panel_before.png' })

await page.getByRole('button', { name: /ask/i }).click()

// loading skeleton should appear
const skeletonVisible = await page.locator('[data-slot="skeleton"]').first().isVisible().catch(() => false)
console.log('Skeleton visible right after submit:', skeletonVisible)

await page.waitForSelector('text=Show query used', { timeout: 30000 })
await page.screenshot({ path: '/tmp/ai_panel_answer.png' })

await page.getByText('Show query used').click()
await page.waitForSelector('pre')
await page.screenshot({ path: '/tmp/ai_panel_sql_revealed.png' })

const answerText = await page.locator('.bg-muted\\/50 p').first().innerText()
const sqlText = await page.locator('pre').innerText()
const rowCountText = await page.locator('text=/row\\(s\\) returned/').innerText()

console.log('Answer:', answerText)
console.log('SQL:', sqlText)
console.log('Row count line:', rowCountText)
console.log('Console errors:', consoleErrors)

await browser.close()
