import json
from collections import defaultdict
from uuid import UUID

from asyncpg import Connection
from asyncpg.protocol.protocol import Record

from person_tool.skills.models import (
    CreateSkillRequest,
    EmployeeSkillAssignmentRequest,
    EmployeeSkillResponse,
    SkillMatrixResponse,
    SkillMatrixRow,
    SkillResponse,
    SkillSource,
    UpdateSkillRequest,
)
from person_tool.utils.audit import log_audit_event


class SkillRepository:
    def __init__(self, conn: Connection) -> None:
        self.conn = conn

    async def list_catalog(
        self,
        *,
        search: str | None,
        category: str | None,
        is_active: bool | None,
        limit: int,
        offset: int,
    ) -> list[SkillResponse] | None:
        rows: list[Record] = await self.conn.fetch(
            """
            SELECT uid,
                   name,
                   category,
                   description,
                   tags,
                   is_active,
                   created_at,
                   updated_at
            FROM people.skills_catalog
            WHERE ($1::text IS NULL OR name ILIKE '%' || $1 || '%' OR $1 ILIKE ANY(tags))
              AND ($2::text IS NULL OR category ILIKE '%' || $2 || '%')
              AND ($3::bool IS NULL OR is_active = $3)
            ORDER BY name ASC
            LIMIT $4 OFFSET $5
            """,
            search,
            category,
            is_active,
            limit,
            offset,
        )
        if not rows:
            return None
        return [SkillResponse.model_validate(dict(row)) for row in rows]

    async def create_skills(self, *, data: list[CreateSkillRequest]) -> list[SkillResponse]:
        payload = json.dumps([item.model_dump() for item in data])
        rows: list[Record] = await self.conn.fetch(
            """
            WITH payload AS (
                SELECT *
                FROM jsonb_to_recordset($1::jsonb) AS t(
                    name text,
                    category text,
                    description text,
                    tags jsonb,
                    is_active boolean
                )
            )
            INSERT INTO people.skills_catalog (
                name,
                category,
                description,
                tags,
                is_active
            )
            SELECT
                name,
                category,
                description,
                COALESCE(
                    (
                        SELECT array_agg(value::text)
                        FROM jsonb_array_elements_text(COALESCE(tags, '[]'::jsonb)) AS value
                    ),
                    ARRAY[]::text[]
                ),
                COALESCE(is_active, TRUE)
            FROM payload
            RETURNING uid,
                      name,
                      category,
                      description,
                      tags,
                      is_active,
                      created_at,
                      updated_at;
            """,
            payload,
        )
        return [SkillResponse.model_validate(dict(row)) for row in rows]

    async def update_skill(self, *, data: UpdateSkillRequest) -> SkillResponse | None:
        row = await self.conn.fetchrow(
            """
            UPDATE people.skills_catalog
            SET name        = COALESCE($2, name),
                category    = COALESCE($3, category),
                description = COALESCE($4, description),
                tags        = COALESCE($5, tags),
                is_active   = COALESCE($6, is_active),
                updated_at  = now()
            WHERE uid = $1
            RETURNING uid,
                      name,
                      category,
                      description,
                      tags,
                      is_active,
                      created_at,
                      updated_at;
            """,
            data.uid,
            data.name,
            data.category,
            data.description,
            data.tags,
            data.is_active,
        )
        return SkillResponse.model_validate(dict(row)) if row else None

    async def list_employee_skills(
        self, *, employee_uid: UUID
    ) -> list[EmployeeSkillResponse]:
        rows: list[Record] = await self.conn.fetch(
            """
            SELECT es.uid,
                   es.employee_uid,
                   es.skill_uid,
                   sc.name AS skill_name,
                   es.level,
                   es.source,
                   es.notes,
                   es.last_updated_by,
                   es.last_updated_at
            FROM people.employee_skills es
            JOIN people.skills_catalog sc ON sc.uid = es.skill_uid
            WHERE es.employee_uid = $1
            ORDER BY sc.name ASC
            """,
            employee_uid,
        )
        return [EmployeeSkillResponse.model_validate(dict(row)) for row in rows]

    async def upsert_employee_skill(
        self,
        *,
        employee_uid: UUID,
        request: EmployeeSkillAssignmentRequest,
        actor_uid: UUID,
    ) -> EmployeeSkillResponse:
        previous = await self.conn.fetchrow(
            """
            SELECT uid,
                   level,
                   notes
            FROM people.employee_skills
            WHERE employee_uid = $1
              AND skill_uid = $2
            """,
            employee_uid,
            request.skill_uid,
        )

        row = await self.conn.fetchrow(
            """
            INSERT INTO people.employee_skills (
                employee_uid,
                skill_uid,
                level,
                source,
                notes,
                last_updated_by,
                last_updated_at
            )
            VALUES ($1, $2, $3, $4, $5, $6, now())
            ON CONFLICT (employee_uid, skill_uid)
            DO UPDATE SET
                level = EXCLUDED.level,
                source = EXCLUDED.source,
                notes = EXCLUDED.notes,
                last_updated_by = EXCLUDED.last_updated_by,
                last_updated_at = now()
            RETURNING uid,
                      employee_uid,
                      skill_uid,
                      (SELECT name FROM people.skills_catalog WHERE uid = skill_uid) AS skill_name,
                      level,
                      source,
                      notes,
                      last_updated_by,
                      last_updated_at;
            """,
            employee_uid,
            request.skill_uid,
            request.level,
            request.source.value,
            request.notes,
            actor_uid,
        )

        if previous and (
            previous["level"] != request.level or previous["notes"] != request.notes
        ):
            await self.conn.execute(
                """
                INSERT INTO people.employee_skill_history (
                    employee_skill_uid,
                    previous_level,
                    new_level,
                    previous_notes,
                    new_notes,
                    changed_by
                ) VALUES ($1, $2, $3, $4, $5, $6)
                """,
                previous["uid"],
                previous["level"],
                request.level,
                previous["notes"],
                request.notes,
                actor_uid,
            )

        await log_audit_event(
            self.conn,
            entity_type="EmployeeSkill",
            entity_uid=row["uid"],
            action="UPSERT",
            performed_by=actor_uid,
            before=dict(previous) if previous else None,
            after=dict(row),
        )

        return EmployeeSkillResponse.model_validate(dict(row))

    async def get_skill_matrix(
        self,
        *,
        manager_uid: UUID,
        skill_uids: list[UUID] | None,
        min_level: int | None,
        depth: int,
    ) -> SkillMatrixResponse:
        rows: list[Record] = await self.conn.fetch(
            """
            WITH RECURSIVE org AS (
                SELECT e.uid,
                       e.first_name,
                       e.last_name,
                       e.title,
                       e.manager_uid,
                       0 AS depth
                FROM people.employees e
                WHERE e.uid = $1
                UNION ALL
                SELECT child.uid,
                       child.first_name,
                       child.last_name,
                       child.title,
                       child.manager_uid,
                       org.depth + 1
                FROM people.employees child
                JOIN org ON child.manager_uid = org.uid
                WHERE org.depth + 1 <= $2
            )
            SELECT org.uid               AS employee_uid,
                   org.first_name,
                   org.last_name,
                   org.title,
                   es.uid                AS employee_skill_uid,
                   es.skill_uid,
                   sc.name               AS skill_name,
                   es.level,
                   es.source,
                   es.notes,
                   es.last_updated_by,
                   es.last_updated_at
            FROM org
            LEFT JOIN people.employee_skills es ON es.employee_uid = org.uid
            LEFT JOIN people.skills_catalog sc ON sc.uid = es.skill_uid
            WHERE ($3::uuid[] IS NULL OR es.skill_uid = ANY($3))
              AND ($4::int IS NULL OR es.level >= $4)
            ORDER BY org.last_name, org.first_name, sc.name;
            """,
            manager_uid,
            depth,
            skill_uids,
            min_level,
        )

        grouped: dict[UUID, list[EmployeeSkillResponse]] = defaultdict(list)
        employee_meta: dict[UUID, tuple[str, str]] = {}

        for row in rows:
            employee_uid = row["employee_uid"]
            full_name = f"{row['first_name']} {row['last_name']}"
            employee_meta[employee_uid] = (full_name, row["title"])
            if row["employee_skill_uid"]:
                skill = EmployeeSkillResponse(
                    uid=row["employee_skill_uid"],
                    employee_uid=employee_uid,
                    skill_uid=row["skill_uid"],
                    skill_name=row["skill_name"],
                    level=row["level"],
                    source=SkillSource(row["source"]),
                    notes=row["notes"],
                    last_updated_by=row["last_updated_by"],
                    last_updated_at=row["last_updated_at"],
                )
                grouped[employee_uid].append(skill)

        matrix_rows = [
            SkillMatrixRow(
                employee_uid=uid,
                employee_name=employee_meta[uid][0],
                title=employee_meta[uid][1],
                skills=grouped.get(uid, []),
            )
            for uid in employee_meta
        ]

        return SkillMatrixResponse(rows=matrix_rows)

