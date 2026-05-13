from __future__ import annotations

from typing import Any

from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine


class DatabaseClient:

    def __init__(self, database_url: str) -> None:
        self.engine: Engine = create_engine(database_url, future=True)

    def fetch_item_by_id(self, item_id: str) -> dict[str, Any] | None:
        sql = text(
            """
            SELECT id, title, description, owner_id
            FROM item
            WHERE id = :item_id
            """
        )
        with self.engine.connect() as conn:
            row = conn.execute(sql, {"item_id": item_id}).mappings().first()
        return None if row is None else dict(row)
