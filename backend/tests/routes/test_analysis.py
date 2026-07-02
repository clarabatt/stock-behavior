import json
from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from backend.database.models import User
from backend.services.ai_analysis import SqlExecutionTimeout, SqlSafetyError, validate_sql


@pytest.fixture(autouse=True)
def gemini_configured():
    with patch("backend.services.ai_analysis.settings.gemini_api_key", "test-key"):
        yield


def _sql_response(sql: str, explanation: str = "explanation") -> MagicMock:
    return MagicMock(text=json.dumps({"sql": sql, "explanation": explanation}))


def _text_response(text: str) -> MagicMock:
    return MagicMock(text=text)


def test_ask_question_returns_answer_backed_by_real_data(
    client: TestClient, dev_user: User, CompanyFactory, StockPriceFactory
):
    company = CompanyFactory(ticker="AAPL", name="Apple Inc.")
    StockPriceFactory(company, close=196.0)

    mock_client = MagicMock()
    mock_client.models.generate_content.side_effect = [
        _sql_response(
            "SELECT close FROM stock_prices JOIN companies "
            "ON companies.id = stock_prices.company_id WHERE companies.ticker = 'AAPL'"
        ),
        _text_response("AAPL closed at $196.00."),
    ]

    with patch("backend.services.ai_analysis._get_client", return_value=mock_client):
        response = client.post("/api/analysis/ask", json={"question": "What did AAPL close at?"})

    assert response.status_code == 200
    data = response.json()
    assert data["answer"] == "AAPL closed at $196.00."
    assert data["row_count"] == 1
    assert "stock_prices" in data["sql"]

    synthesis_call = mock_client.models.generate_content.call_args_list[1]
    assert "196.0" in synthesis_call.kwargs["contents"]


def test_ask_question_retries_once_and_recovers_from_unsafe_sql(
    client: TestClient, dev_user: User, CompanyFactory
):
    CompanyFactory(ticker="AAPL")

    mock_client = MagicMock()
    mock_client.models.generate_content.side_effect = [
        _sql_response("SELECT * FROM users"),
        _sql_response("SELECT ticker FROM companies"),
        _text_response("Here are the tickers."),
    ]

    with patch("backend.services.ai_analysis._get_client", return_value=mock_client):
        response = client.post("/api/analysis/ask", json={"question": "List tickers"})

    assert response.status_code == 200
    sql_calls = [
        c for c in mock_client.models.generate_content.call_args_list
        if c.kwargs["model"] == "gemini-2.5-pro"
    ]
    assert len(sql_calls) == 2

    body = response.text
    assert "users" not in body
    assert "@" not in body


def test_ask_question_422_when_sql_unsafe_after_retry(
    client: TestClient, dev_user: User, CompanyFactory
):
    CompanyFactory(ticker="AAPL")

    mock_client = MagicMock()
    mock_client.models.generate_content.side_effect = [
        _sql_response("SELECT * FROM users"),
        _sql_response("SELECT * FROM users"),
    ]

    with patch("backend.services.ai_analysis._get_client", return_value=mock_client):
        response = client.post("/api/analysis/ask", json={"question": "Show me everything"})

    assert response.status_code == 422
    detail = response.json()["detail"]
    assert detail == "I couldn't safely answer that question. Try rephrasing it."
    assert "users" not in detail
    assert "SELECT" not in detail

    sql_calls = [
        c for c in mock_client.models.generate_content.call_args_list
        if c.kwargs["model"] == "gemini-2.5-pro"
    ]
    assert len(sql_calls) == 2
    synthesis_calls = [
        c for c in mock_client.models.generate_content.call_args_list
        if c.kwargs["model"] == "gemini-2.5-flash"
    ]
    assert len(synthesis_calls) == 0


def test_ask_question_422_on_execution_timeout(
    client: TestClient, dev_user: User, CompanyFactory
):
    CompanyFactory(ticker="AAPL")

    mock_client = MagicMock()
    mock_client.models.generate_content.side_effect = [
        _sql_response("SELECT close FROM stock_prices"),
    ]

    with (
        patch("backend.services.ai_analysis._get_client", return_value=mock_client),
        patch(
            "backend.services.ai_analysis.execute_readonly_query",
            side_effect=SqlExecutionTimeout("timed out"),
        ),
    ):
        response = client.post("/api/analysis/ask", json={"question": "Scan everything"})

    assert response.status_code == 422
    assert "scanning too much data" in response.json()["detail"]
    assert mock_client.models.generate_content.call_count == 1


@pytest.mark.parametrize(
    "sql",
    [
        "INSERT INTO companies (ticker) VALUES ('X')",
        "UPDATE companies SET ticker = 'X'",
        "DELETE FROM companies",
        "DROP TABLE companies",
        "SELECT 1; DROP TABLE companies",
        "SELECT * FROM users",
        "SELECT * FROM annotated_notes",
        "SELECT setval('some_seq', 1)",
        "SELECT pg_sleep(5)",
        "",
    ],
)
def test_validate_sql_rejects_unsafe_queries(sql: str):
    with pytest.raises(SqlSafetyError):
        validate_sql(sql)


def test_validate_sql_accepts_and_normalizes_safe_query():
    result = validate_sql(
        "SELECT close FROM stock_prices JOIN companies "
        "ON companies.id = stock_prices.company_id WHERE companies.ticker = 'AAPL';"
    )
    assert ";" not in result
    assert "stock_prices" in result
