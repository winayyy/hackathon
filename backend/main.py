
import os
from datetime import date, datetime, time
from decimal import Decimal

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
    version="1.0.0",
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
# 3. Request model
# --------------------------------------------------

class QueryRequest(BaseModel):
    query: str = Field(min_length=1, max_length=10000)


# --------------------------------------------------
# 4. Basic PII masking
# --------------------------------------------------

def mask_sensitive_value(column_name, value):
    if value is None:
        return None

    column = column_name.lower().replace("_", "")

    # Mask email addresses while preserving their domain.
    if "email" in column:
        email = str(value)

        if "@" in email:
            local, domain = email.rsplit("@", 1)
            return f"{local[:1]}***@{domain}" if local else f"***@{domain}"

        return "***MASKED***"

    # Mask other commonly sensitive column names.
    sensitive_fields = (
        "phone",
        "mobile",
        "ssn",
        "socialsecurity",
        "password",
        "token",
    )

    if any(field in column for field in sensitive_fields):
        return "***MASKED***"

    return value


# --------------------------------------------------
# 5. Convert database values to JSON-safe values
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
# 6. Health check
# --------------------------------------------------

@app.get("/health")
def health_check():
    return {
        "status": "ok",
        "application": "DataOps Console API",
    }


# --------------------------------------------------
# 7. Database connection check
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
        # Do not expose credentials or internal connection details.
        raise HTTPException(
            status_code=503,
            detail="Database connection failed. Check local configuration.",
        )


# --------------------------------------------------
# 8. Validate and execute read-only queries
# --------------------------------------------------

@app.post("/api/query")
def run_query(request: QueryRequest):
    # Parse and validate the SQL before executing it.
    try:
        statements = sqlglot.parse(request.query, read="mysql")

        if len(statements) != 1 or statements[0] is None:
            raise ValueError("Submit exactly one SQL statement.")

        parsed = statements[0]

        # Only SELECT statements are accepted.
        if not isinstance(parsed, exp.Select):
            raise ValueError("Only SELECT queries are allowed.")

        # Reject SELECT INTO and locking reads.
        if parsed.find(exp.Into):
            raise ValueError("SELECT INTO is not allowed.")

        if parsed.args.get("locks"):
            raise ValueError("Locking queries are not allowed.")

        # Enforce the result-row limit.
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

        safe_sql = parsed.sql(dialect="mysql")

    except (ValueError, sqlglot.errors.ParseError) as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    # Execute the validated query.
    try:
        with engine.connect() as connection:
            # MySQL-specific execution time limit.
            connection.execute(
                text(f"SET SESSION MAX_EXECUTION_TIME = {QUERY_TIMEOUT_MS}")
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
                    value = serialize_value(database_row._mapping[column])

                    # Apply masking before returning results to the frontend.
                    value = mask_sensitive_value(column, value)

                    row[column] = value

                rows.append(row)

        return {
            "columns": columns,
            "rows": rows,
            "row_count": len(rows),
        }

    except Exception:
        # Avoid exposing database credentials, SQL internals, or stack traces.
        raise HTTPException(
            status_code=400,
            detail="Query execution failed. Check the SQL and database connection.",
        )
