from __future__ import annotations

import json
from typing import Any
from uuid import UUID

from asyncpg import Connection


async def log_audit_event(
    conn: Connection,
    *,
    entity_type: str,
    entity_uid: UUID,
    action: str,
    performed_by: UUID | None,
    before: dict[str, Any] | None = None,
    after: dict[str, Any] | None = None,
) -> None:
    await conn.execute(
        """
        INSERT INTO people.audit_log (
            entity_type,
            entity_uid,
            action,
            performed_by,
            before_data,
            after_data
        ) VALUES ($1, $2, $3, $4, $5, $6)
        """,
        entity_type,
        entity_uid,
        action,
        performed_by,
        json.dumps(before, default=str) if before else None,
        json.dumps(after, default=str) if after else None,
    )

