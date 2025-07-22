from psycopg2.extras import DictCursor
from psycopg2 import OperationalError, DatabaseError
from typing import Dict, Optional, Tuple, Any
from .models import ExplainPlan, SchemaDict, ColumnInfo


def get_db_schema(
    conn: Any, schema_name: str = "public"  # psycopg2.extensions.connection
) -> SchemaDict | Dict[str, str]:
    """
    Fetch the schema metadata for all tables in a given PostgreSQL schema.

    Args:
        conn: psycopg2 database connection.
        schema_name: target schema name (default 'public').

    Returns:
        SchemaDict mapping table names to list of ColumnInfo, or error dict.
    """
    query = """
        SELECT
            table_name,
            column_name,
            data_type,
            is_nullable,
            column_default
        FROM
            information_schema.columns
        WHERE
            table_schema = %s
        ORDER BY
            table_name,
            ordinal_position;
    """

    schema: SchemaDict = {}

    try:
        with conn.cursor(cursor_factory=DictCursor) as cur:
            cur.execute(query, (schema_name,))
            rows = cur.fetchall()
            for row in rows:
                table = row["table_name"]
                col_info: ColumnInfo = {
                    "column_name": row["column_name"],
                    "data_type": row["data_type"],
                    "is_nullable": row["is_nullable"],
                    "column_default": row["column_default"],
                }
                schema.setdefault(table, []).append(col_info)

    except OperationalError as oe:
        return {"error": f"Failed to connect to the database: {oe}."}
    except DatabaseError as de:
        return {"error": f"Database query failed: {de}."}
    except Exception as e:
        return {"error": f"Unexpected error occurred: {e}."}

    return schema


def get_query_info(
    conn: Any,  # psycopg2.extensions.connection
    query: str,
    params: Optional[Tuple[Any, ...]] = None,
) -> ExplainPlan | Dict[str, str]:
    """
    Run EXPLAIN (ANALYZE, BUFFERS, FORMAT JSON) on the provided query.

    Return structured info.

    Args:
        conn: psycopg2 database connection.
        query: SQL query string to explain.
        params: Optional tuple of parameters for parameterized queries.

    Returns:
        Parsed ExplainPlan dict containing query plan and execution metrics,
        or error dict on failure.
    """
    explain_query = f"EXPLAIN (ANALYZE, BUFFERS, FORMAT JSON) {query}"

    try:
        with conn.cursor(cursor_factory=DictCursor) as cur:
            cur.execute(explain_query, params)
            result = cur.fetchone()
            if not result:
                raise ValueError("Empty result from EXPLAIN")

            explain_json: ExplainPlan = result["QUERY PLAN"][0]
            return explain_json

    except DatabaseError as e:
        return {"error": f"Failed to execute EXPLAIN: {e}."}
    except Exception as e:
        return {"error": f"Unexpected error in get_query_info: {e}."}
