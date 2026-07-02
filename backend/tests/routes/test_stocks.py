from datetime import datetime, timezone

from fastapi.testclient import TestClient


def test_list_companies_returns_active_companies(client: TestClient, CompanyFactory):
    CompanyFactory(ticker="AAPL", name="Apple Inc.", sector="Technology")
    CompanyFactory(ticker="DELIST", is_active=False)

    response = client.get("/api/companies")
    assert response.status_code == 200
    data = response.json()
    tickers = [c["ticker"] for c in data]
    assert "AAPL" in tickers
    assert "DELIST" not in tickers


def test_list_companies_returns_expected_fields(client: TestClient, CompanyFactory):
    CompanyFactory(ticker="AAPL", name="Apple Inc.", sector="Technology", industry="Hardware")

    response = client.get("/api/companies")
    assert response.status_code == 200
    company = next(c for c in response.json() if c["ticker"] == "AAPL")
    assert company["name"] == "Apple Inc."
    assert company["sector"] == "Technology"
    assert "id" in company


def test_latest_prices_returns_one_row_per_company(client: TestClient, CompanyFactory, StockPriceFactory):
    aapl = CompanyFactory(ticker="AAPL")
    msft = CompanyFactory(ticker="MSFT")
    ts = datetime(2026, 7, 2, 14, 30, 0, tzinfo=timezone.utc)
    StockPriceFactory(aapl, timestamp=ts, close=196.0)
    StockPriceFactory(msft, timestamp=ts, close=420.0)

    response = client.get("/api/prices/latest")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2


def test_latest_prices_returns_most_recent_close(client: TestClient, CompanyFactory, StockPriceFactory):
    company = CompanyFactory(ticker="AAPL")
    ts_old = datetime(2026, 7, 2, 14, 0, 0, tzinfo=timezone.utc)
    ts_new = datetime(2026, 7, 2, 14, 30, 0, tzinfo=timezone.utc)
    StockPriceFactory(company, timestamp=ts_old, close=100.0)
    StockPriceFactory(company, timestamp=ts_new, close=103.0)

    response = client.get("/api/prices/latest")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["close"] == 103.0
    assert data[0]["ticker"] == "AAPL"


def test_latest_prices_empty_when_no_data(client: TestClient):
    response = client.get("/api/prices/latest")
    assert response.status_code == 200
    assert response.json() == []


def test_price_history_returns_404_for_unknown_ticker(client: TestClient):
    response = client.get("/api/prices/ZZZZ/history?from=2026-07-01T00:00:00Z&to=2026-07-02T00:00:00Z")
    assert response.status_code == 404


def test_price_history_returns_prices_in_range(client: TestClient, CompanyFactory, StockPriceFactory):
    from datetime import timedelta
    company = CompanyFactory(ticker="AAPL")
    base = datetime(2026, 7, 2, 14, 0, 0, tzinfo=timezone.utc)
    for i in range(5):
        StockPriceFactory(company, timestamp=base + timedelta(minutes=5 * i))

    from_str = "2026-07-02T14:00:00Z"
    to_str = "2026-07-02T14:10:00Z"
    response = client.get(f"/api/prices/AAPL/history?from={from_str}&to={to_str}")
    assert response.status_code == 200
    assert len(response.json()) == 3
