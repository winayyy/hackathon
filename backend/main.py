
import os
import sqlite3
from datetime import date, datetime, time
from decimal import Decimal
from pathlib import Path
from time import perf_counter

import sqlglot
from sqlglot import exp
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from sqlalchemy import create_engine, text
from sqlalchemy.engine import URL


# --------------------------------------------------
# 1. Load environment variables
# --------------------------------------------------

load_dotenv()

app = FastAPI(
    title="DataOps Console API",
    description="Local read-only database query dashboard",
    version="1.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
)


# --------------------------------------------------
# 2. Configure MySQL connection
# --------------------------------------------------

database_url = URL.create(
    drivername="mysql+pymysql",
    username=os.environ["MYSQL_USER"],
    password=os.environ["MYSQL_PASSWORD"],
    host=os.getenv("MYSQL_HOST", "127.0.0.1"),
    port=int(os.getenv("MYSQL_PORT", "3306")),
    database=os.environ["MYSQL_DATABASE"],
)

engine = create_engine(
    database_url,
    pool_pre_ping=True,
    pool_size=2,
    max_overflow=0,
    connect_args={"connect_timeout": 5},
)

MAX_ROWS = 100
QUERY_TIMEOUT_MS = 5000


# --------------------------------------------------
# 3. Query history storage (separate SQLite database)
# --------------------------------------------------

HISTORY_DB_PATH = Path(__file__).resolve().parent / "query_history.db"


def initialize_history_db():
    with sqlite3.connect(HISTORY_DB_PATH, timeout=2) as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS query_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                query_preview TEXT NOT NULL,
                executed_at TEXT NOT NULL,
                status TEXT NOT NULL,
                duration_ms INTEGER NOT NULL,
                row_count INTEGER NOT NULL
            )
            """
        )


def redact_query_for_history(query: str) -> str:
    """Redact SQL literal values before saving a query preview."""
    try:
        statements = sqlglot.parse(query, read="mysql")

        if len(statements) != 1 or statements[0] is None:
            return "[Query text withheld: invalid or multiple statements]"

        parsed = statements[0]

        def redact_literals(node):
            if isinstance(node, exp.Literal):
                # Keep a numeric LIMIT readable.
                if isinstance(node.parent, exp.Limit) and node.is_int:
                    return node

                # Replace string, numeric and other literal values.
                return exp.Placeholder()

            return node

        redacted = parsed.transform(redact_literals)
        return redacted.sql(dialect="mysql")

    except Exception:
        # If redaction fails, never save the original SQL.
        return "[Query text withheld: unable to redact safely]"


def record_query_history(
    query: str,
    status: str,
    duration_ms: int = 0,
    row_count: int = 0,
):
    """Save query metadata, never query results."""
    try:
        query_preview = redact_query_for_history(query)

        with sqlite3.connect(HISTORY_DB_PATH, timeout=2) as connection:
            connection.execute(
                """
                INSERT INTO query_history (
                    query_preview,
                    executed_at,
                    status,
                    duration_ms,
                    row_count
                )
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    query_preview,
                    datetime.now().astimezone().isoformat(timespec="seconds"),
                    status,
                    max(0, duration_ms),
                    max(0, row_count),
                ),
            )

    except sqlite3.Error:
        # A history failure must not break the query API.
        pass


initialize_history_db()


# --------------------------------------------------
# 4. Validate SQL queries
# --------------------------------------------------

def validate_query(query: str) -> exp.Select:
    statements = sqlglot.parse(query, read="mysql")

    if len(statements) != 1 or statements[0] is None:
        raise ValueError("Submit exactly one SQL statement.")

    parsed = statements[0]

    # Only SELECT statements are allowed.
    if not isinstance(parsed, exp.Select):
        raise ValueError("Only SELECT queries are allowed.")

    # Reject write or schema-changing operations anywhere
    # in the SQL tree, including nested queries and CTEs.
    forbidden_operations = (
        exp.Insert,
        exp.Update,
        exp.Delete,
        exp.Create,
        exp.Drop,
        exp.Alter,
        exp.Merge,
    )

    for node in parsed.walk():
        if isinstance(node, forbidden_operations):
            raise ValueError(
                "Write or schema-changing operations are not allowed."
            )

    # Reject SELECT INTO.
    if parsed.find(exp.Into):
        raise ValueError("SELECT INTO is not allowed.")

    # Reject locking reads.
    if parsed.args.get("locks"):
        raise ValueError("Locking queries are not allowed.")

    # Enforce a maximum of 100 rows.
    limit_node = parsed.args.get("limit")

    if limit_node is None:
        parsed = parsed.limit(MAX_ROWS)
    else:
        limit_expression = limit_node.expression

        if (
            not isinstance(limit_expression, exp.Literal)
            or not limit_expression.is_int
        ):
            raise ValueError("Use a numeric LIMIT of at most 100.")

        requested_limit = int(limit_expression.this)

        if requested_limit < 0:
            raise ValueError("LIMIT cannot be negative.")

        parsed = parsed.limit(min(requested_limit, MAX_ROWS))

    return parsed


# --------------------------------------------------
# 5. Request model
# --------------------------------------------------

class QueryRequest(BaseModel):
    query: str = Field(min_length=1, max_length=10000)


# --------------------------------------------------
# 6. PII masking
# --------------------------------------------------

def sensitive_field_type(column_name):
    column = column_name.lower().replace("_", "")

    if "email" in column:
        return "email"

    sensitive_fields = (
        "name",
        "phone",
        "mobile",
        "ssn",
        "socialsecurity",
        "password",
        "token",
    )

    if any(field in column for field in sensitive_fields):
        return "sensitive"

    return None


def mask_sensitive_value(column_name, value, sensitive_type=None):
    if value is None:
        return None

    field_type = sensitive_type or sensitive_field_type(column_name)

    if field_type == "email":
        email = str(value)

        if "@" in email:
            local, domain = email.rsplit("@", 1)

            if local:
                return f"{local[0]}***@{domain}"

            return f"***@{domain}"

        return "***MASKED***"

    if field_type == "sensitive":
        return "***MASKED***"

    return value


def get_sensitive_output_types(parsed):
    sensitive_output_types = {}

    for projection in parsed.expressions:
        output_name = projection.alias_or_name

        if not output_name:
            continue

        source_types = {
            field_type
            for column in projection.find_all(exp.Column)
            if (field_type := sensitive_field_type(column.name))
        }

        if source_types:
            output_type = (
                next(iter(source_types))
                if len(source_types) == 1
                else "sensitive"
            )

            sensitive_output_types[output_name.lower()] = output_type

    return sensitive_output_types


# --------------------------------------------------
# 7. Convert database values to JSON-safe values
# --------------------------------------------------

def serialize_value(value):
    if value is None:
        return None

    if isinstance(value, (datetime, date, time)):
        return value.isoformat()

    if isinstance(value, Decimal):
        return float(value)

    if isinstance(value, bytes):
        return value.hex()

    return value


# --------------------------------------------------
# 8. Health check
# --------------------------------------------------

@app.get("/health")
def health_check():
    return {
        "status": "ok",
        "application": "DataOps Console API",
    }


# --------------------------------------------------
# 9. Database connection check
# --------------------------------------------------

@app.get("/api/db-health")
def database_health():
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))

        return {
            "status": "connected",
            "database": os.environ["MYSQL_DATABASE"],
        }

    except Exception:
        raise HTTPException(
            status_code=503,
            detail="Database connection failed. Check local configuration.",
        )


# --------------------------------------------------
# 10. Query history API
# --------------------------------------------------

@app.get("/api/query-history")
def get_query_history():
    try:
        with sqlite3.connect(HISTORY_DB_PATH, timeout=2) as connection:
            connection.row_factory = sqlite3.Row

            rows = connection.execute(
                """
                SELECT
                    id,
                    query_preview,
                    executed_at,
                    status,
                    duration_ms,
                    row_count
                FROM query_history
                ORDER BY id DESC
                LIMIT 50
                """
            ).fetchall()

        return [dict(row) for row in rows]

    except sqlite3.Error:
        raise HTTPException(
            status_code=503,
            detail="Query history is temporarily unavailable.",
        )


# --------------------------------------------------
# 11. Execute validated read-only queries
# --------------------------------------------------

@app.post("/api/query")
def run_query(request: QueryRequest):
    started_at = perf_counter()

    # Validate before connecting to MySQL.
    try:
        parsed = validate_query(request.query)
        safe_sql = parsed.sql(dialect="mysql")
        sensitive_output_types = get_sensitive_output_types(parsed)

    except (ValueError, sqlglot.errors.ParseError) as exc:
        record_query_history(
            request.query,
            status="rejected",
            duration_ms=round((perf_counter() - started_at) * 1000),
        )

        raise HTTPException(status_code=400, detail=str(exc))

    # Execute the validated query.
    try:
        with engine.connect() as connection:
            # Apply a MySQL execution-time limit.
            connection.execute(
                text(
                    f"SET SESSION MAX_EXECUTION_TIME = {QUERY_TIMEOUT_MS}"
                )
            )

            result = connection.execute(text(safe_sql))
            columns = list(result.keys())
            rows = []

            for database_row in result.fetchmany(MAX_ROWS + 1):
                # Defensive row-count check.
                if len(rows) >= MAX_ROWS:
                    break

                row = {}

                for column in columns:
                    value = serialize_value(
                        database_row._mapping[column]
                    )

                    # Mask sensitive values before returning the response.
                    value = mask_sensitive_value(
                        column,
                        value,
                        sensitive_output_types.get(column.lower()),
                    )

                    row[column] = value

                rows.append(row)

        record_query_history(
            request.query,
            status="success",
            duration_ms=round((perf_counter() - started_at) * 1000),
            row_count=len(rows),
        )

        return {
            "columns": columns,
            "rows": rows,
            "row_count": len(rows),
        }

    except Exception:
        record_query_history(
            request.query,
            status="failed",
            duration_ms=round((perf_counter() - started_at) * 1000),
        )

        raise HTTPException(
            status_code=400,
            detail=(
                "Query execution failed. "
                "Check the SQL and database connection."
            ),
        )
