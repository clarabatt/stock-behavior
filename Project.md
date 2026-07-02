> Goal: A full-stack web app for exploring S&P 500 company data, aimed at helping you analyze stock behavior.

## Must-have

1. **Data ingestion & freshness** — Pull S&P 500 stock price data from some source, and keep it updated as close to real-time as the data source allows (this likely means periodic polling/refresh rather than true tick-by-tick, since "real-time" free market data is rarely truly instant).
2. **Visualization & data manipulation** — Present the data in both tabular and chart form, with interactive controls: filtering, sorting on columns (e.g., by ticker, sector, price change), and chart interactions like zoom/pan into a time range.
3. **Annotated notes** — Let you attach free-text notes to specific (date, company) pairs — essentially a lightweight journaling layer on top of the data, so you can record hypotheses about anomalies (spikes/drops) as you spot them.
4. **(Bonus) AI-assisted analysis** — An AI layer that can either (a) generate charts/tables from a natural-language request, or (b) answer natural-language questions about the underlying data (e.g., "steepest decline during COVID crash" or "top 10 by market cap 2020–2021").

##

1. Real time
   1. every 5 minutes when the market is open.
