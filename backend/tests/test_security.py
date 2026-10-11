import os

# Allow tests to import the application without requiring a live database.
os.environ.setdefault("MYSQL_USER", "test_user")
os.environ.setdefault("MYSQL_PASSWORD", "test_password")
os.environ.setdefault("MYSQL_HOST", "127.0.0.1")
os.environ.setdefault("MYSQL_PORT", "3306")
os.environ.setdefault("MYSQL_DATABASE", "dataops_demo")

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




# SQL security tests: these requests must fail before reaching MySQL.
@pytest.mark.parametrize(
    "query",
    [
        "INSERT INTO customers (name) VALUES ('Test')",
        "UPDATE customers SET city = 'Test'",
        "DELETE FROM customers",
        "DROP TABLE customers",
        "SELECT 1; SELECT 2",
        "SELECT * FROM customers INTO OUTFILE '/tmp/export.csv'",
        "SELECT * FROM customers FOR UPDATE",
    ],
)
def test_rejects_unsafe_queries(query):
    with pytest.raises(HTTPException) as error:
        run_query(QueryRequest(query=query))

    assert error.value.status_code == 400


# PII masking tests.
def test_masks_email_and_preserves_domain():
    assert mask_sensitive_value(
        "email", "vinay@example.com"
    ) == "v***@example.com"


def test_masks_phone_number():
    assert mask_sensitive_value(
        "phone_number", "9876543210"
    ) == "***MASKED***"


def test_masks_password():
    assert mask_sensitive_value(
        "password", "secret123"
    ) == "***MASKED***"


def test_preserves_null_values():
    assert mask_sensitive_value("email", None) is None


def test_does_not_mask_regular_columns():
    assert mask_sensitive_value("city", "Bengaluru") == "Bengaluru"

def test_detects_email_alias():
    parsed = sqlglot.parse_one(
        "SELECT email AS contact FROM customers",
        read="mysql",
    )

    sensitive_types = get_sensitive_output_types(parsed)

    assert sensitive_types["contact"] == "email"


def test_masks_email_even_when_aliased():
    assert mask_sensitive_value(
        "contact",
        "vinay@example.com",
        "email",
    ) == "v***@example.com"


def test_detects_phone_alias():
    parsed = sqlglot.parse_one(
        "SELECT phone_number AS contact FROM customers",
        read="mysql",
    )

    sensitive_types = get_sensitive_output_types(parsed)

    assert sensitive_types["contact"] == "sensitive"

def test_max_rows_is_100():
    assert MAX_ROWS == 100

def get_query_limit(query):
    parsed = validate_query(query)
    limit_node = parsed.args.get("limit")

    assert limit_node is not None
    return int(limit_node.expression.this)


def test_query_without_limit_defaults_to_100():
    assert get_query_limit("SELECT * FROM customers") == 100


def test_query_limit_over_100_is_capped():
    assert get_query_limit(
        "SELECT * FROM customers LIMIT 500"
    ) == 100


def test_query_limit_under_100_is_preserved():
    assert get_query_limit(
        "SELECT * FROM customers LIMIT 10"
    ) == 10


@pytest.mark.parametrize(
    "query",
    [
        "SELECT * FROM customers LIMIT 1.5",
        "SELECT * FROM customers LIMIT 1 + 1",
    ],
)
def test_rejects_non_integer_limits(query):
    with pytest.raises(ValueError):
        validate_query(query)
    
def test_detects_qualified_email_alias():
    parsed = sqlglot.parse_one(
        "SELECT customers.email AS contact FROM customers",
        read="mysql",
    )

    sensitive_types = get_sensitive_output_types(parsed)

    assert sensitive_types["contact"] == "email"


def test_detects_email_inside_expression_alias():
    parsed = sqlglot.parse_one(
        "SELECT CONCAT(customers.email, '') AS contact FROM customers",
        read="mysql",
    )

    sensitive_types = get_sensitive_output_types(parsed)

    assert sensitive_types["contact"] == "email"

def test_masks_customer_name():
    assert mask_sensitive_value(
        "name", "Aarav Sharma"
    ) == "***MASKED***"


def test_detects_name_alias():
    parsed = sqlglot.parse_one(
        "SELECT name AS customer FROM customers",
        read="mysql",
    )

    sensitive_types = get_sensitive_output_types(parsed)

    assert sensitive_types["customer"] == "sensitive"