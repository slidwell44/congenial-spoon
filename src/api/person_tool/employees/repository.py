import json
from uuid import UUID

from asyncpg import Connection
from asyncpg.protocol.protocol import Record

from person_tool.employees.models import (
    CreateEmployeeRequest,
    EmployeeResponse,
    UpdateEmployeeRequest,
)


class EmployeeRepository:
    def __init__(self, conn: Connection) -> None:
        self.conn: Connection = conn

    async def list_employees(
        self,
        *,
        employee_id: str | None,
        first_name: str | None,
        last_name: str | None,
        department: str | None,
        manager_uid: UUID | None,
        role: str | None,
        status: str | None,
        limit: int,
        offset: int,
    ) -> list[EmployeeResponse] | None:
        rows: list[Record] = await self.conn.fetch(
            """
            SELECT uid,
                   employee_id,
                   first_name,
                   last_name,
                   email,
                   title,
                   department,
                   location,
                   manager_uid,
                   role,
                   status,
                   hire_date,
                   created_at,
                   updated_at
            FROM people.employees
            WHERE ($1::text IS NULL OR employee_id ILIKE '%' || $1 || '%')
              AND ($2::text IS NULL OR first_name ILIKE '%' || $2 || '%')
              AND ($3::text IS NULL OR last_name  ILIKE '%' || $3 || '%')
              AND ($4::text IS NULL OR department ILIKE '%' || $4 || '%')
              AND ($5::uuid IS NULL OR manager_uid = $5)
              AND ($6::text IS NULL OR role = $6)
              AND ($7::text IS NULL OR status = $7)
            ORDER BY last_name ASC, first_name ASC
            LIMIT $8 OFFSET $9
            """,
            employee_id,
            first_name,
            last_name,
            department,
            manager_uid,
            role,
            status,
            limit,
            offset,
        )
        if not rows:
            return None
        return [EmployeeResponse.model_validate(dict(row)) for row in rows]

    async def get_employee_by_uid(self, uid: UUID) -> EmployeeResponse | None:
        row: Record | None = await self.conn.fetchrow(
            """
            SELECT uid,
                   employee_id,
                   first_name,
                   last_name,
                   email,
                   title,
                   department,
                   location,
                   manager_uid,
                   role,
                   status,
                   hire_date,
                   created_at,
                   updated_at
            FROM people.employees
            WHERE uid = $1
            """,
            uid,
        )
        return EmployeeResponse.model_validate(dict(row)) if row else None

    async def create_employees(
        self, *, data: list[CreateEmployeeRequest]
    ) -> list[EmployeeResponse]:
        payload = json.dumps([item.model_dump() for item in data])
        rows: list[Record] = await self.conn.fetch(
            """
            WITH payload AS (
                SELECT *
                FROM jsonb_to_recordset($1::jsonb) AS t(
                    employee_id text,
                    first_name text,
                    last_name text,
                    email text,
                    title text,
                    department text,
                    location text,
                    manager_uid uuid,
                    role text,
                    status text,
                    hire_date date
                )
            )
            INSERT INTO people.employees (
                employee_id,
                first_name,
                last_name,
                email,
                title,
                department,
                location,
                manager_uid,
                role,
                status,
                hire_date
            )
            SELECT employee_id,
                   first_name,
                   last_name,
                   email,
                   title,
                   department,
                   location,
                   manager_uid,
                   role,
                   status,
                   hire_date
            FROM payload
            RETURNING uid,
                      employee_id,
                      first_name,
                      last_name,
                      email,
                      title,
                      department,
                      location,
                      manager_uid,
                      role,
                      status,
                      hire_date,
                      created_at,
                      updated_at;
            """,
            payload,
        )
        return [EmployeeResponse.model_validate(dict(row)) for row in rows]

    async def update_employee(
        self, *, data: UpdateEmployeeRequest
    ) -> EmployeeResponse | None:
        row: Record | None = await self.conn.fetchrow(
            """
            UPDATE people.employees
            SET employee_id = COALESCE($2, employee_id),
                first_name  = COALESCE($3, first_name),
                last_name   = COALESCE($4, last_name),
                email       = COALESCE($5, email),
                title       = COALESCE($6, title),
                department  = COALESCE($7, department),
                location    = COALESCE($8, location),
                manager_uid = COALESCE($9, manager_uid),
                role        = COALESCE($10, role),
                status      = COALESCE($11, status),
                hire_date   = COALESCE($12, hire_date),
                updated_at  = now()
            WHERE uid = $1
            RETURNING uid,
                      employee_id,
                      first_name,
                      last_name,
                      email,
                      title,
                      department,
                      location,
                      manager_uid,
                      role,
                      status,
                      hire_date,
                      created_at,
                      updated_at;
            """,
            data.uid,
            data.employee_id,
            data.first_name,
            data.last_name,
            data.email,
            data.title,
            data.department,
            data.location,
            data.manager_uid,
            data.role,
            data.status,
            data.hire_date,
        )
        if not row:
            return None
        return EmployeeResponse.model_validate(dict(row))

    async def delete_employee(self, uid: UUID) -> str:
        return await self.conn.execute(
            "DELETE FROM people.employees WHERE uid = $1",
            uid,
        )

    async def get_org_subtree(
        self, *, root_uid: UUID, max_depth: int
    ) -> list[dict[str, object]]:
        rows: list[Record] = await self.conn.fetch(
            """
            WITH RECURSIVE org AS (
                SELECT e.*, 0 AS depth
                FROM people.employees e
                WHERE e.uid = $1
                UNION ALL
                SELECT child.*, org.depth + 1
                FROM people.employees child
                JOIN org ON child.manager_uid = org.uid
                WHERE org.depth + 1 <= $2
            )
            SELECT uid,
                   employee_id,
                   first_name,
                   last_name,
                   email,
                   title,
                   department,
                   location,
                   manager_uid,
                   role,
                   status,
                   hire_date,
                   created_at,
                   updated_at,
                   depth
            FROM org
            ORDER BY depth, last_name, first_name;
            """,
            root_uid,
            max_depth,
        )
        return [
            {
                "employee": EmployeeResponse.model_validate(dict(row)),
                "depth": row["depth"],
            }
            for row in rows
        ]

    async def get_open_role_counts(
        self, *, manager_uids: list[UUID]
    ) -> dict[UUID, int]:
        if not manager_uids:
            return {}
        records: list[Record] = await self.conn.fetch(
            """
            SELECT ur.primary_uid AS manager_uid,
                   count(*)::int    AS open_role_count
            FROM people.user_relationships ur
            JOIN people.jobs j ON j.uid = ur.secondary_uid
            WHERE ur.relationship_type = 'USER_JOB'
              AND j.status ILIKE 'open%'
              AND ur.primary_uid = ANY($1::uuid[])
            GROUP BY ur.primary_uid
            """,
            manager_uids,
        )
        return {record["manager_uid"]: record["open_role_count"] for record in records}
