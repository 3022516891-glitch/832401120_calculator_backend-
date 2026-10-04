from app.database import execute_query, get_connection


def add_record(expression: str, result: int | float, angle_mode: str = "DEG") -> None:
    with get_connection() as connection:
        execute_query(connection,
            "INSERT INTO calculation_history (expression, result, angle_mode) VALUES (?, ?, ?)",
            (expression, result, angle_mode),
        )


def get_all_records(
    keyword: str | None = None, favorite_only: bool = False,
    page: int | None = None, page_size: int = 10,
) -> list[dict] | dict:
    conditions: list[str] = []
    parameters: list[str | int] = []
    if keyword:
        conditions.append("(expression LIKE ? OR CAST(result AS TEXT) LIKE ?)")
        search_value = f"%{keyword}%"
        parameters.extend([search_value, search_value])
    if favorite_only:
        conditions.append("is_favorite = 1")
    where_clause = f"WHERE {' AND '.join(conditions)}" if conditions else ""

    with get_connection() as connection:
        total = execute_query(connection,
            f"SELECT COUNT(*) AS total FROM calculation_history {where_clause}", parameters
        ).fetchone()["total"]
        limit_clause = "LIMIT ? OFFSET ?" if page is not None else ""
        query_parameters = parameters + [page_size, (page - 1) * page_size] if page is not None else parameters
        rows = execute_query(connection,
            f"""
            SELECT id, expression, result, is_favorite, created_at, angle_mode
            FROM calculation_history {where_clause}
            ORDER BY id DESC {limit_clause}
            """,
            query_parameters,
        ).fetchall()
    items = [
        {**dict(row), "is_favorite": bool(row["is_favorite"])}
        for row in rows
    ]
    if page is None:
        return items
    return {"items": items, "total": total, "page": page, "page_size": page_size}


def clear_history() -> int:
    with get_connection() as connection:
        return connection.execute("DELETE FROM calculation_history").rowcount


def set_favorite(record_id: int, is_favorite: bool) -> dict | None:
    with get_connection() as connection:
        cursor = execute_query(connection,
            "UPDATE calculation_history SET is_favorite = ? WHERE id = ?",
            (int(is_favorite), record_id),
        )
        if cursor.rowcount == 0:
            return None
        row = execute_query(connection,
            """
            SELECT id, expression, result, is_favorite, created_at, angle_mode
            FROM calculation_history WHERE id = ?
            """,
            (record_id,),
        ).fetchone()
    record = dict(row)
    record["is_favorite"] = bool(record["is_favorite"])
    return record


def remove_record(record_id: int) -> bool:
    with get_connection() as connection:
        cursor = execute_query(connection,
            "DELETE FROM calculation_history WHERE id = ?", (record_id,)
        )
        return cursor.rowcount > 0
