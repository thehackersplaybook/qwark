import pytest
from testcontainers.postgres import PostgresContainer
import psycopg2
from schema_tools import get_db_schema, get_query_info


@pytest.fixture(scope="module")
def postgres_container():
    """Start a temporary PostgreSQL container for tests."""
    with PostgresContainer("postgres:15-alpine") as postgres:
        conn_params = {
            "host": postgres.get_container_host_ip(),
            "port": postgres.get_exposed_port(postgres.port),
            "database": postgres.DBNAME,
            "user": postgres.USER,
            "password": postgres.PASSWORD,
        }
        yield conn_params


@pytest.fixture(scope="module")
def setup_schema(postgres_container):
    """Create test schema and tables, insert some test data."""
    conn = psycopg2.connect(**postgres_container)
    cur = conn.cursor()

    # Create tables
    cur.execute(
        """
        CREATE TABLE users (
            id SERIAL PRIMARY KEY,
            username VARCHAR(50) UNIQUE NOT NULL,
            email VARCHAR(100) UNIQUE NOT NULL
        );
    """
    )

    cur.execute(
        """
        CREATE TABLE orders (
            id SERIAL PRIMARY KEY,
            user_id INT REFERENCES users(id),
            total NUMERIC(10, 2) NOT NULL
        );
    """
    )

    conn.commit()
    cur.close()
    conn.close()


def test_fetch_schema_basic(postgres_container, setup_schema):
    conn = psycopg2.connect(**postgres_container)
    schema = get_db_schema(conn, schema_name="public")
    conn.close()

    # Should have 'users' and 'orders' tables
    assert "users" in schema
    assert "orders" in schema

    # Check columns in users table
    user_columns = {col["column_name"]: col for col in schema["users"]}
    assert user_columns["id"]["data_type"] == "integer"
    assert user_columns["username"]["data_type"] == "character varying"
    assert user_columns["email"]["is_nullable"] == "NO"

    # Check columns in orders table
    orders_columns = {col["column_name"]: col for col in schema["orders"]}
    assert orders_columns["user_id"]["data_type"] == "integer"
    assert orders_columns["total"]["data_type"] == "numeric"


def test_fetch_schema_nonexistent_schema(postgres_container):
    conn = psycopg2.connect(**postgres_container)
    result = get_db_schema(conn, schema_name="no_such_schema")
    conn.close()

    assert result == {"error": "Database query failed: no_such_schema."}


def test_get_query_info_basic(postgres_container, setup_schema):
    query = "SELECT * FROM users WHERE username = %s"
    params = ("alice",)

    plan = None
    with psycopg2.connect(**postgres_container) as conn:
        plan = get_query_info(
            connection_params={
                "host": postgres_container["host"],
                "port": postgres_container["port"],
                "database": postgres_container["database"],
                "user": postgres_container["user"],
                "password": postgres_container["password"],
            },
            query=query,
            params=params,
        )

    assert plan is not None
    assert "Plan" in plan
    assert plan["Plan"]["Node Type"] in {
        "Seq Scan",
        "Index Scan",
        "Index Only Scan",
        "Bitmap Heap Scan",
    }
    assert isinstance(plan["Plan"].get("Actual Rows", None), (int, float))
    assert "Execution Time" in plan
    assert "Buffers" in plan["Plan"]
    # Buffers info can have keys like Shared Hit Blocks, Shared Read Blocks etc.
    assert any(
        key in plan["Plan"]["Buffers"]
        for key in (
            "Shared Hit Blocks",
            "Shared Read Blocks",
            "Shared Dirtied Blocks",
            "Shared Written Blocks",
        )
    )
