import os
from types import SimpleNamespace

os.environ.setdefault("MYSQL_USER", "test_user")
os.environ.setdefault("MYSQL_PASSWORD", "test_password")
os.environ.setdefault("MYSQL_HOST", "127.0.0.1")
os.environ.setdefault("MYSQL_PORT", "3306")
os.environ.setdefault("MYSQL_DATABASE", "dataops_demo")

import main
from fastapi.testclient import TestClient


class FakeResult:
    def __init__(self, columns, rows):
        self.columns = columns
        self.rows = rows

    def keys(self):
        return self.columns

    def fetchmany(self, size):
        return self.rows[:size]


class FakeConnection:
    def __init__(self, result):
        self.result = result
        self.calls = 0

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False

    def execute(self, statement):
        self.calls += 1

        # First call sets the MySQL execution timeout.
        if self.calls == 1:
            return FakeResult([], [])

        # Second call returns the simulated query results.
        return self.result


class FakeEngine:
    def __init__(self, columns, rows):
        self.result = FakeResult(columns, rows)

    def connect(self):
        return FakeConnection(self.result)


client = TestClient(main.app)


def make_row(**values):
    return SimpleNamespace(_mapping=values)


def test_api_masks_customer_pii(monkeypatch):
    columns = ["id", "name", "email", "city", "status"]

    rows = [
        make_row(
            id=1,
            name="Aarav Sharma",
            email="aarav@example.com",
            city="Bengaluru",
            status="active",
        )
    ]

    monkeypatch.setattr(
        main, "engine", FakeEngine(columns, rows)
    )

    response = client.post(
        "/api/query",
        json={"query": "SELECT * FROM customers LIMIT 5"},
    )

    assert response.status_code == 200

    data = response.json()
    assert data["row_count"] == 1
    assert data["rows"][0]["name"] == "***MASKED***"
    assert data["rows"][0]["email"] == "a***@example.com"
    assert data["rows"][0]["city"] == "Bengaluru"


def test_api_rejects_update():
    response = client.post(
        "/api/query",
        json={
            "query": "UPDATE customers SET city = 'Test'"
        },
    )

    assert response.status_code == 400
    assert "Only SELECT queries are allowed" in response.json()["detail"]


def test_api_never_returns_more_than_100_rows(monkeypatch):
    columns = ["id", "name", "email", "city", "status"]

    rows = [
        make_row(
            id=i,
            name=f"Customer {i}",
            email=f"customer{i}@example.com",
            city="Bengaluru",
            status="active",
        )
        for i in range(101)
    ]

    monkeypatch.setattr(
        main, "engine", FakeEngine(columns, rows)
    )

    response = client.post(
        "/api/query",
        json={"query": "SELECT * FROM customers LIMIT 500"},
    )

    assert response.status_code == 200

    data = response.json()
    assert data["row_count"] == 100
    assert len(data["rows"]) == 100