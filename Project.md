> Goal: A full-stack web app for exploring S&P 500 company data, aimed at helping you analyze stock behavior.

## Must-have

1. **Data ingestion & freshness** — Pull S&P 500 stock price data from some source, and keep it updated as close to real-time as the data source allows.
2. **Visualization & data manipulation** — Present the data in both tabular and chart form, with interactive controls: filtering, sorting on columns (e.g., by ticker, sector, price change), and chart interactions like zoom/pan into a time range.
3. **Annotated notes** — Let you attach free-text notes to specific (date, company) pairs — essentially a lightweight journaling layer on top of the data, so you can record hypotheses about anomalies (spikes/drops) as you spot them.
4. **(Bonus) AI-assisted analysis** — An AI layer that can either (a) generate charts/tables from a natural-language request, or (b) answer natural-language questions about the underlying data (e.g., "steepest decline during COVID crash" or "top 10 by market cap 2020–2021").

## Explanation

I used a boilerplate that I've used in my personal projects. My goal was to have a faster start with an structure that I know works well and have a good developer experience. For example I used a docker compose setup that allows me to run the backend, frontend and database in a single command.

### Backend

Technologies used: FastAPI, Pydantic, SQLAlchemy, PostgreSQL and Alembic.

### Frontend

Technologies used: React, Vite, TypeScript, TailwindCSS and Chart.js.

### Tests

I use test on the backend to ensure at least the main functionality is working and to avoid regressions. I also use a test database that is isolated from the main database to avoid polluting the main database with test data.

In the beginning of my projects I avoid frontend tests because the features are not consolidated. I don't want to spend time writing tests for features that will be changed or removed. I prefer to write frontend tests when the features are more stable.

The backend tests are a must-have because the backend is the core of the project and it is where most of the logic is. Also they are easier to write and maintain, and they are faster to run than frontend tests.

I use Factories to create test data that are closer to the actual data. I prefer to use Factories instead of fixtures because I prefer descriptive tests that are easy to read and self-documenting. It avoids unexpected side effects.

### Data Ingestion

- **Source**: Used a free API yFinance (via `yfinance` Python package) to pull historical stock price data for S&P 500 companies.
  - It's free and enough for this project, but it has some limitations (e.g., rate limits, occasional missing data).
  - In a real project, I would consider a paid API because it would provide more reliable and complete data with better support and other forms of ingestion.
  - It also has a Python package that makes it easy to pull data and convert it into a Pandas DataFrame which is convenient
  - I'm using a Wikipedia page to pull the list of S&P 500 companies, which is a simple solution, but it would need to be changed to a more reliable source in a real project.

- **Frequency**: The backend will pull data on a schedule and store it in a local database. This allows the frontend to query the database for fast responses, rather than hitting the API directly.

- **User Access**: I removed the user access layer to speedup the development. In a real project, I would add user access to allow users to save their notes and have their own data.
