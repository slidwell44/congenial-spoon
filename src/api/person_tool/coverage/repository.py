from collections import defaultdict
from datetime import datetime, timezone
from uuid import UUID

from asyncpg import Connection
from asyncpg.protocol.protocol import Record

from person_tool.coverage.models import (
    CoveragePerson,
    CoverageReport,
    CreateRoleSkillProfile,
    ProfileType,
    RoleSkillProfileResponse,
    RoleSkillRequirement,
    SkillCoverageStat,
)


class CoverageRepository:
    def __init__(self, conn: Connection) -> None:
        self.conn = conn

    async def create_role_skill_profile(
        self, request: CreateRoleSkillProfile
    ) -> RoleSkillProfileResponse:
        profile_row = await self.conn.fetchrow(
            """
            INSERT INTO people.role_skill_profiles (
                profile_type,
                name,
                description,
                owner_uid,
                context
            ) VALUES ($1, $2, $3, $4, $5)
            RETURNING uid,
                      profile_type,
                      name,
                      description,
                      owner_uid,
                      context,
                      created_at,
                      updated_at;
            """,
            request.profile_type.value,
            request.name,
            request.description,
            request.owner_uid,
            request.context,
        )
        profile_uid = profile_row["uid"]

        for requirement in request.requirements:
            await self.conn.execute(
                """
                INSERT INTO people.role_skill_requirements (
                    profile_uid,
                    skill_uid,
                    required_level,
                    required_headcount
                ) VALUES ($1, $2, $3, $4)
                ON CONFLICT (profile_uid, skill_uid)
                DO UPDATE SET
                    required_level = EXCLUDED.required_level,
                    required_headcount = EXCLUDED.required_headcount
                """,
                profile_uid,
                requirement.skill_uid,
                requirement.required_level,
                requirement.required_headcount,
            )

        return await self.get_profile(profile_uid=profile_uid)

    async def get_profile(self, profile_uid: UUID) -> RoleSkillProfileResponse:
        profile_row = await self.conn.fetchrow(
            """
            SELECT uid,
                   profile_type,
                   name,
                   description,
                   owner_uid,
                   context,
                   created_at,
                   updated_at
            FROM people.role_skill_profiles
            WHERE uid = $1
            """,
            profile_uid,
        )
        if not profile_row:
            raise ValueError("Profile not found")

        requirement_rows: list[Record] = await self.conn.fetch(
            """
            SELECT skill_uid,
                   required_level,
                   required_headcount
            FROM people.role_skill_requirements
            WHERE profile_uid = $1
            """,
            profile_uid,
        )

        requirements = [
            RoleSkillRequirement(
                skill_uid=row["skill_uid"],
                required_level=row["required_level"],
                required_headcount=row["required_headcount"],
            )
            for row in requirement_rows
        ]

        profile = RoleSkillProfileResponse.model_validate(
            {
                **dict(profile_row),
                "profile_type": ProfileType(profile_row["profile_type"]),
                "requirements": requirements,
            }
        )
        return profile

    async def generate_coverage_report(
        self, *, manager_uid: UUID, profile_uid: UUID, depth: int
    ) -> CoverageReport:
        profile = await self.get_profile(profile_uid=profile_uid)
        skill_uids = [req.skill_uid for req in profile.requirements]

        skill_lookup_rows: list[Record] = await self.conn.fetch(
            """
            SELECT uid, name
            FROM people.skills_catalog
            WHERE uid = ANY($1::uuid[])
            """,
            skill_uids,
        )
        skill_names = {row["uid"]: row["name"] for row in skill_lookup_rows}

        rows: list[Record] = await self.conn.fetch(
            """
            WITH RECURSIVE org AS (
                SELECT e.uid,
                       e.first_name,
                       e.last_name,
                       0 AS depth
                FROM people.employees e
                WHERE e.uid = $1
                UNION ALL
                SELECT child.uid,
                       child.first_name,
                       child.last_name,
                       org.depth + 1
                FROM people.employees child
                JOIN org ON child.manager_uid = org.uid
                WHERE org.depth + 1 <= $2
            )
            SELECT org.uid AS employee_uid,
                   org.first_name,
                   org.last_name,
                   es.skill_uid,
                   es.level
            FROM org
            JOIN people.employee_skills es ON es.employee_uid = org.uid
            WHERE es.skill_uid = ANY($3::uuid[])
            """,
            manager_uid,
            depth,
            skill_uids,
        )

        coverage_map: dict[UUID, list[CoveragePerson]] = defaultdict(list)
        for row in rows:
            name = f"{row['first_name']} {row['last_name']}"
            coverage_map[row["skill_uid"]].append(
                CoveragePerson(
                    employee_uid=row["employee_uid"],
                    employee_name=name,
                    level=row["level"],
                )
            )

        stats: list[SkillCoverageStat] = []
        for requirement in profile.requirements:
            qualified = [
                person
                for person in coverage_map.get(requirement.skill_uid, [])
                if person.level >= requirement.required_level
            ]
            stats.append(
                SkillCoverageStat(
                    skill_uid=requirement.skill_uid,
                    skill_name=skill_names.get(requirement.skill_uid, "Unknown"),
                    required_headcount=requirement.required_headcount,
                    required_level=requirement.required_level,
                    actual_headcount=len(qualified),
                    qualified_people=qualified,
                    single_point_of_failure=len(qualified) == 1,
                )
            )

        return CoverageReport(
            manager_uid=manager_uid,
            profile_uid=profile_uid,
            generated_at=datetime.now(timezone.utc),
            stats=stats,
        )

