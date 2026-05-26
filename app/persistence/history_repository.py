import json
from typing import Any

import psycopg

from app.persistence.database import get_database_url


def save_history(
    source_code: str,
    generated_code: str | None,
    report: dict[str, Any],
    status: str,
) -> str:
    query = """
        INSERT INTO modernization_history (source_code, generated_code, report, status)
        VALUES (%s, %s, %s::jsonb, %s)
        RETURNING id::text
    """
    with psycopg.connect(get_database_url()) as connection:
        with connection.cursor() as cursor:
            cursor.execute(query, (source_code, generated_code, json.dumps(report), status))
            row = cursor.fetchone()
            if row is None:
                raise RuntimeError("modernization_history insert did not return an id")
            connection.commit()
            return str(row[0])

