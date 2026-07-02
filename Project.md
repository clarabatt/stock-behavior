> Goal: A full-stack web app for exploring S&P 500 company data, aimed at helping you analyze stock behavior.

## Must-have

1. **Data ingestion & freshness** — Pull S&P 500 stock price data from some source, and keep it updated as close to real-time as the data source allows.
2. **Visualization & data manipulation** — Present the data in both tabular and chart form, with interactive controls: filtering, sorting on columns (e.g., by ticker, sector, price change), and chart interactions like zoom/pan into a time range.
3. **Annotated notes** — Let you attach free-text notes to specific (date, company) pairs — essentially a lightweight journaling layer on top of the data, so you can record hypotheses about anomalies (spikes/drops) as you spot them.
4. **(Bonus) AI-assisted analysis** — An AI layer that can either (a) generate charts/tables from a natural-language request, or (b) answer natural-language questions about the underlying data (e.g., "steepest decline during COVID crash" or "top 10 by market cap 2020–2021").

## Choices

### Data Ingestion

- **Source**: Used a free API yFinance (via `yfinance` Python package) to pull historical stock price data for S&P 500 companies.
  - It's free and enough for this project, but it has some limitations (e.g., rate limits, occasional missing data).
  - In a real project, I would consider a paid API because it would provide more reliable and complete data with better support and other forms of ingestion.
  - It also has a Python package that makes it easy to pull data and convert it into a Pandas DataFrame which is convenient

- **Frequency**: The backend will pull data on a schedule and store it in a local database. This allows the frontend to query the database for fast responses, rather than hitting the API directly.
