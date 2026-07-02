# Project: Stock Behavior

> Goal: A full-stack web app for exploring S&P 500 company data, aimed at helping you analyze stock behavior.

## Must-have

1. **Data ingestion & freshness** — Pull S&P 500 stock price data from some source, and keep it updated as close to real-time as the data source allows.
2. **Visualization & data manipulation** — Present the data in both tabular and chart form, with interactive controls: filtering, sorting on columns (e.g., by ticker, sector, price change), and chart interactions like zoom/pan into a time range.
3. **Annotated notes** — Let you attach free-text notes to specific (date, company) pairs — essentially a lightweight journaling layer on top of the data, so you can record hypotheses about anomalies (spikes/drops) as you spot them.
4. **(Bonus) AI-assisted analysis** — An AI layer that can either (a) generate charts/tables from a natural-language request, or (b) answer natural-language questions about the underlying data (e.g., "steepest decline during COVID crash" or "top 10 by market cap 2020–2021").

## Technology

I used a boilerplate that I've used in my personal projects. My goal was to have a faster start with an structure that I know works well and have a good developer experience. For example I used a docker compose setup that allows me to run the backend, frontend and database in a single command.

### Backend

Technologies used: FastAPI, Pydantic, SQLAlchemy, PostgreSQL and Alembic.

- I like to use Pydantic models to validate the data that is coming from the database and from the API endpoints.
- Alembic is a must in my opinion to not corrupt the database and to have a version control of the database schema.
- I added indexes to the stock_prices table to improve the performance of the queries that are used to fetch the data for the frontend.
- I used a repository pattern to separate the database access logic from the business logic.
- The app is simple, so no need to separate in more layers. Routes, Services and Repositories are enough to have a clean architecture. I prefer to keep it simple and not over-engineer the app.

### Frontend

Technologies used: React, Vite, TypeScript, TailwindCSS and Chart.js.

- I decided to use classic rest endpoints because of the time constraints. I would have used websockets to push the data to the frontend as soon as it is ingested, instead of having the frontend pull the data from the backend. That would make the data "real-time" and a better user experience.
- I could use pagination to improve the performance of the list query, but considering the we are only dealing with 500 companies, I decided to keep it simple and return all the data in a single query. Also the frontend is splitting the data in two queries, one for the list and another for the chart, so the data is not too big to be returned in a single query.

### Tests

I used tests on the backend to ensure at least the main functionality is working and to avoid regressions.
In the beginning of my projects I avoid frontend tests because the features are not consolidated. I don't want to spend time writing tests for features that will be changed or removed, so I prefer to write frontend tests when the features are more stable.
The backend tests are a must-have because the backend is where most of the logic is. They are easier to write and maintain, and they are faster to run than frontend tests.

**Test setup**
I used a test database that is isolated from the main db to avoid polluting it with test data.
I used Factories to create test data that are closer to the actual data. I prefer to use Factories instead of fixtures because I prefer descriptive tests that are easy to read and self-documenting. It avoids unexpected side effects.

## Features

### Data Ingestion

- **Source**: Used a free API yFinance (via `yfinance` Python package) to pull historical stock price data for S&P 500 companies.
  - It's free and enough for this project, but it has some limitations (e.g., rate limits, occasional missing data).
  - In a real project, I would consider a paid API because it would provide more reliable and complete data with better support and other forms of ingestion.
  - It also has a Python package that makes it easy to pull data and convert it into a Pandas DataFrame which is convenient
  - I'm using a Wikipedia page to pull the list of S&P 500 companies, which is a simple solution, but it would need to be changed to a more reliable source in a real project.

- **Frequency**: The backend will pull data on a schedule and store it in a local database. This allows the frontend to query the database for fast responses, rather than hitting the API directly.

- **User Access**: I removed the user access layer to speedup the development. In a real project, I would add user access to allow users to save their notes and have their own data.

### Data Visualization

- I felt the chart a bit truncated because it was showing the same day twice, one for the open price and another for the close price.
  - When the view is 1 day or 1 week, it maked sense to show all the data points with the time.
  - When the view is 1 month or more, it makes more sense to show only the close price for each day.

### Notes

- You can add notes to specific (date, company) pairs by clicking on the chart or by clicking on the "Add Note" button in the list view. The notes are stored in the database and can be retrieved later. You can also edit and delete notes.

### AI Insights

- I decided to use an approach where the AI agent can create SQL queries to fetch the data from the database and then use the data to answer the user's questions. This approach is more flexible and allows the AI to answer a wider range of questions but it has some trade-offs:
  - It has a higher risk of SQL injection attacks. I put some measures to mitigate this risk, but it is still a risk. In a real project I would analyze the trade-off between flexibility and security and decide which approach to use based on the requirements of the project.
  - Another approach would be to use defined actions that the AI can use to fetch the data from the database. This approach is more secure but it has a limited range of questions that the AI can answer.

- Questions examples:
  - Which company had the steepest single-day decline?
  - What did AAPL close at?
  - Top 5 companies by trading volume this week
  - Which tech stocks gained the most over the past month?
