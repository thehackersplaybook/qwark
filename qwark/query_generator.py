from typing import Optional, List, Tuple
from openai import OpenAI
from pydantic import BaseModel
from .models import SchemaDict, GeneratedQuery


class GeneratedQueryOutput(BaseModel):
    error: Optional[str] = None
    query: str
    explanation: str


def generate_query(
    openai_client: OpenAI,
    prompt: str,
    schema: SchemaDict,
    model: str = "gpt-4.1-nano",
    instructions: str = "Generate a SQL query that will answer the prompt.",
) -> GeneratedQuery:
    """
    Generate a single query for a given prompt and schema.

    Args:
        openai_client: OpenAI client
        prompt: Prompt to generate a query for
        schema: Schema of the database
        model: Model to use for generating queries

    Returns:
        GeneratedQuery: Generated query and explanation.
    """
    try:
        response = openai_client.responses.parse(
            model=model,
            input=[
                {
                    "role": "system",
                    "content": f"""
                    You are a helpful assistant that generates SQL queries.
                    You are given a prompt and a schema.
                    You need to generate a SQL query that will answer the prompt.
                    The schema is: {schema}
                    Custom Instructions: {instructions}
                    """,
                },
                {
                    "role": "user",
                    "content": f"""
                    Prompt: {prompt}
                    """,
                },
            ],
            text_format=GeneratedQueryOutput,
        )

        if response.output_parsed is None:
            return GeneratedQuery(
                error="Failed to parse response", query="", explanation="NA"
            )

        generated_query_dict = response.output_parsed.model_dump()

        return GeneratedQuery(
            error=None,
            query=generated_query_dict.get("query", ""),
            explanation=generated_query_dict.get("explanation", "NA"),
        )
    except Exception as e:
        return GeneratedQuery(error=str(e), query="", explanation="NA")


def generate_candidate_queries(
    openai_client: OpenAI,
    sql_query: str,
    schema: SchemaDict,
    model: str = "gpt-4.1-nano",
    num_queries: int = 3,
) -> Tuple[str, List[GeneratedQuery]]:
    """
    Generate a list of candidate queries for a given SQL query.

    Args:
        openai_client: OpenAI client
        sql_query: SQL query to generate candidate queries for
        schema: Schema of the database
        model: Model to use for generating queries
        num_queries: Number of candidate queries to generate

    Returns:
        Tuple[str, List[GeneratedQuery]]: Tuple containing the best query and a
            list of candidate queries.
        If the query generation fails, the first element of the tuple is an error
            message and the second element is an empty list.
    """
    try:
        all_errors: List[str] = []
        generated_queries: List[GeneratedQuery] = []
        for _ in range(num_queries):
            generated_queries_str = "\n".join(
                [query["query"] for query in generated_queries]
            )
            candidate_query = generate_query(
                openai_client=openai_client,
                prompt=f"SQL Query: {sql_query}",
                schema=schema,
                model=model,
                instructions=f"""
                Given the query, generate an optimized version of the query that
                will answer the prompt.
                Do not generate any of the generated queries.
                Generated Queries: {generated_queries_str}
                """,
            )

            if candidate_query["error"]:
                all_errors.append(candidate_query["error"])
                continue

            generated_queries.append(candidate_query)

        if len(generated_queries) == 0:
            deduped_errors = list(set(all_errors))
            error_str = ",".join(deduped_errors)
            return f"Query generation failed. Errors: {error_str}", []

        return generated_queries[0]["query"], generated_queries
    except Exception as e:
        return f"Failed to generate candidate queries: {e}.", []
