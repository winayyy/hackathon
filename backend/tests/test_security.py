
import os

# Provide test configuration before importing the application.
os.environ.setdefault("MYSQL_USER", "test_user")
os.environ.setdefault("MYSQL_PASSWORD", "test_password")
os.environ.setdefault("MYSQL_HOST", "127.0.0.1")
os.environ.setdefault("MYSQL_PORT", "3306")
os.environ.setdefault("MYSQL_DATABASE", "test_database")

import pytest
import sqlglot
from fastapi import HTTPException

from main import (
    MAX_ROWS,
    QueryRequest,
    get_sensitive_output_types,
    mask_sensitive_value,
    run_query,
    validate_query,
)


# --------------------------------------------------
# 1. Reject unsafe SQL
# --------------------------------------------------

@pytest.mark.parametrize(
    "query",
    [
        "INSERT INTO customers (name) VALUES ('Test')",
        "UPDATE customers SET name = 'Test'",
        "DELETE FROM customers",
        "DROP TABLE customers",
        "SELECT * FROM customers; DELETE FROM customers",
        "SELECT * INTO OUTFILE '/tmp/output.txt' FROM customers",
        "SELECT * FROM customers FOR UPDATE",
        "WITH c AS (DELETE FROM customers RETURNING *) SELECT * FROM c",
    ],
)
def test_rejects_unsafe_queries(query):
    with pytest.raises(HTTPException) as error:
        run_query(QueryRequest(query=query))

    assert error.value.status_code == 400


# --------------------------------------------------
# 2. PII masking tests
# --------------------------------------------------

def test_masks_email():
    assert (
        mask_sensitive_value("email", "alice@example.com")
        == "a***@example.com"
    )


def test_masks_phone():
    assert mask_sensitive_value("phone", "9876543210") == "***MASKED***"


def test_masks_password():
    assert mask_sensitive_value("password", "secret123") == "***MASKED***"


def test_preserves_null_values():
    assert mask_sensitive_value("email", None) is None


def test_preserves_non_sensitive_values():
    assert mask_sensitive_value("city", "Bengaluru") == "Bengaluru"


# --------------------------------------------------
# 3. Sensitive output aliases
# --------------------------------------------------

def test_detects_email_alias():
    parsed = sqlglot.parse_one(
        "SELECT email AS contact FROM customers",
        read="mysql",
    )

    assert get_sensitive_output_types(parsed)["contact"] == "email"


def test_detects_phone_alias():
    parsed = sqlglot.parse_one(
        "SELECT phone AS contact_number FROM customers",
        read="mysql",
    )

    assert get_sensitive_output_types(parsed)["contact_number"] == "sensitive"


def test_detects_sensitive_alias():
    parsed = sqlglot.parse_one(
        "SELECT password AS credential FROM customers",
        read="mysql",
    )

    assert get_sensitive_output_types(parsed)["credential"] == "sensitive"


# --------------------------------------------------
# 4. Result row limit tests
# --------------------------------------------------

def get_query_limit(query):
    parsed = validate_query(query)
    limit_node = parsed.args.get("limit")

    assert limit_node is not None
    return int(limit_node.expression.this)


def test_max_rows_constant():
    assert MAX_ROWS == 100


def test_adds_default_limit():
    assert get_query_limit("SELECT id FROM customers") == 100


def test_caps_limit_at_100():
    assert get_query_limit("SELECT id FROM customers LIMIT 500") == 100


def test_preserves_lower_limit():
    assert get_query_limit("SELECT id FROM customers LIMIT 10") == 10


@pytest.mark.parametrize(
    "query",
    [
        "SELECT id FROM customers LIMIT 1.5",
        "SELECT id FROM customers LIMIT 1 + 1",
    ],
)
def test_rejects_non_integer_limits(query):
    with pytest.raises(ValueError):
        validate_query(query)


# --------------------------------------------------
# 5. PII masking through SQL expressions
# --------------------------------------------------

def test_detects_qualified_email_column():
    parsed = sqlglot.parse_one(
        "SELECT customers.email AS contact FROM customers",
        read="mysql",
    )

    assert get_sensitive_output_types(parsed)["contact"] == "email"


def test_detects_email_inside_concat():
    parsed = sqlglot.parse_one(
        "SELECT CONCAT(email, '') AS contact FROM customers",
        read="mysql",
    )

    assert get_sensitive_output_types(parsed)["contact"] == "email"


def test_masks_customer_name():
    assert (
        mask_sensitive_value("customer_name", "Alice")
        == "***MASKED***"
    )


def test_detects_name_alias():
    parsed = sqlglot.parse_one(
        "SELECT name AS customer FROM customers",
        read="mysql",
    )

    assert get_sensitive_output_types(parsed)["customer"] == "sensitive"
