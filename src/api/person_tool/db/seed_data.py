"""
Seed script to populate the database with test data.
Can be run standalone or via docker-compose.
"""
import asyncio
import logging
from datetime import date, timedelta

from asyncpg import Connection, create_pool

from person_tool.config import configure_logging, settings

configure_logging("INFO")
log = logging.getLogger(__name__)


async def seed_database(conn: Connection) -> None:
    """Seed the database with test data."""
    log.info("Starting database seeding...")

    # Check if schema exists, if not, provide helpful error
    try:
        schema_exists = await conn.fetchval(
            "SELECT EXISTS(SELECT 1 FROM information_schema.schemata WHERE schema_name = 'people')"
        )
        if not schema_exists:
            log.error("Schema 'people' does not exist. Please run the schema initialization first.")
            log.error("In Docker, the schema should be created automatically from SQL files.")
            log.error("If running locally, run: psql -U postgres -d PeopleDb -f person_tool/db/sql/schema.pgsql")
            raise RuntimeError("Database schema not initialized. Please run schema initialization first.")
    except Exception as e:
        if "does not exist" in str(e) or "relation" in str(e).lower():
            log.error("Database schema appears to be missing. Please initialize the schema first.")
            raise
        raise

    # Check if data already exists
    existing_employees = await conn.fetchval("SELECT COUNT(*) FROM people.employees")
    if existing_employees > 0:
        log.info(f"Database already contains {existing_employees} employees. Skipping seed.")
        return

    # Create employees with manager hierarchy
    log.info("Creating employees...")
    employees_data = [
        # C-level
        {
            "employee_id": "ceo001",
            "first_name": "Sarah",
            "last_name": "Johnson",
            "email": "sarah.johnson@company.com",
            "title": "Chief Executive Officer",
            "department": "Executive",
            "location": "San Francisco, CA",
            "manager_uid": None,
            "role": "SENIOR_MANAGER",
            "status": "ACTIVE",
            "hire_date": date(2020, 1, 15),
        },
        # VPs
        {
            "employee_id": "vp001",
            "first_name": "Michael",
            "last_name": "Chen",
            "email": "michael.chen@company.com",
            "title": "VP of Engineering",
            "department": "Engineering",
            "location": "Seattle, WA",
            "manager_uid": None,  # Will set after creation
            "role": "SENIOR_MANAGER",
            "status": "ACTIVE",
            "hire_date": date(2020, 3, 1),
        },
        {
            "employee_id": "vp002",
            "first_name": "Emily",
            "last_name": "Rodriguez",
            "email": "emily.rodriguez@company.com",
            "title": "VP of Product",
            "department": "Product",
            "location": "New York, NY",
            "manager_uid": None,
            "role": "SENIOR_MANAGER",
            "status": "ACTIVE",
            "hire_date": date(2020, 4, 1),
        },
        # Engineering Managers
        {
            "employee_id": "mgr001",
            "first_name": "David",
            "last_name": "Kim",
            "email": "david.kim@company.com",
            "title": "Engineering Manager",
            "department": "Engineering",
            "location": "Seattle, WA",
            "manager_uid": None,
            "role": "MANAGER",
            "status": "ACTIVE",
            "hire_date": date(2021, 1, 15),
        },
        {
            "employee_id": "mgr002",
            "first_name": "Jessica",
            "last_name": "Martinez",
            "email": "jessica.martinez@company.com",
            "title": "Engineering Manager",
            "department": "Engineering",
            "location": "Remote - US",
            "manager_uid": None,
            "role": "MANAGER",
            "status": "ACTIVE",
            "hire_date": date(2021, 2, 1),
        },
        # Individual Contributors
        {
            "employee_id": "ic001",
            "first_name": "Alex",
            "last_name": "Thompson",
            "email": "alex.thompson@company.com",
            "title": "Senior Software Engineer",
            "department": "Engineering",
            "location": "Seattle, WA",
            "manager_uid": None,
            "role": "IC",
            "status": "ACTIVE",
            "hire_date": date(2021, 6, 1),
        },
        {
            "employee_id": "ic002",
            "first_name": "Jordan",
            "last_name": "Lee",
            "email": "jordan.lee@company.com",
            "title": "Software Engineer",
            "department": "Engineering",
            "location": "Seattle, WA",
            "manager_uid": None,
            "role": "IC",
            "status": "ACTIVE",
            "hire_date": date(2022, 1, 10),
        },
        {
            "employee_id": "ic003",
            "first_name": "Taylor",
            "last_name": "Brown",
            "email": "taylor.brown@company.com",
            "title": "Software Engineer",
            "department": "Engineering",
            "location": "Remote - US",
            "manager_uid": None,
            "role": "IC",
            "status": "ACTIVE",
            "hire_date": date(2022, 3, 15),
        },
        {
            "employee_id": "ic004",
            "first_name": "Casey",
            "last_name": "Wilson",
            "email": "casey.wilson@company.com",
            "title": "Senior Software Engineer",
            "department": "Engineering",
            "location": "Remote - US",
            "manager_uid": None,
            "role": "IC",
            "status": "ACTIVE",
            "hire_date": date(2021, 9, 1),
        },
        {
            "employee_id": "ic005",
            "first_name": "Morgan",
            "last_name": "Davis",
            "email": "morgan.davis@company.com",
            "title": "Software Engineer",
            "department": "Engineering",
            "location": "Seattle, WA",
            "manager_uid": None,
            "role": "IC",
            "status": "ACTIVE",
            "hire_date": date(2022, 7, 1),
        },
        {
            "employee_id": "ic006",
            "first_name": "Riley",
            "last_name": "Garcia",
            "email": "riley.garcia@company.com",
            "title": "Software Engineer",
            "department": "Engineering",
            "location": "Remote - EU",
            "manager_uid": None,
            "role": "IC",
            "status": "ACTIVE",
            "hire_date": date(2023, 1, 15),
        },
        # HR
        {
            "employee_id": "hr001",
            "first_name": "Pat",
            "last_name": "Anderson",
            "email": "pat.anderson@company.com",
            "title": "HR Manager",
            "department": "Human Resources",
            "location": "San Francisco, CA",
            "manager_uid": None,
            "role": "HR",
            "status": "ACTIVE",
            "hire_date": date(2020, 5, 1),
        },
    ]

    employee_uids = {}
    for emp_data in employees_data:
        row = await conn.fetchrow(
            """
            INSERT INTO people.employees (
                employee_id, first_name, last_name, email, title, department,
                location, manager_uid, role, status, hire_date
            ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11)
            RETURNING uid
            """,
            emp_data["employee_id"],
            emp_data["first_name"],
            emp_data["last_name"],
            emp_data["email"],
            emp_data["title"],
            emp_data["department"],
            emp_data["location"],
            emp_data["manager_uid"],
            emp_data["role"],
            emp_data["status"],
            emp_data["hire_date"],
        )
        employee_uids[emp_data["employee_id"]] = row["uid"]

    # Set up manager relationships
    await conn.execute(
        "UPDATE people.employees SET manager_uid = $1 WHERE employee_id = $2",
        employee_uids["ceo001"],
        "vp001",
    )
    await conn.execute(
        "UPDATE people.employees SET manager_uid = $1 WHERE employee_id = $2",
        employee_uids["ceo001"],
        "vp002",
    )
    await conn.execute(
        "UPDATE people.employees SET manager_uid = $1 WHERE employee_id = $2",
        employee_uids["vp001"],
        "mgr001",
    )
    await conn.execute(
        "UPDATE people.employees SET manager_uid = $1 WHERE employee_id = $2",
        employee_uids["vp001"],
        "mgr002",
    )
    await conn.execute(
        "UPDATE people.employees SET manager_uid = $1 WHERE employee_id = $2",
        employee_uids["mgr001"],
        "ic001",
    )
    await conn.execute(
        "UPDATE people.employees SET manager_uid = $1 WHERE employee_id = $2",
        employee_uids["mgr001"],
        "ic002",
    )
    await conn.execute(
        "UPDATE people.employees SET manager_uid = $1 WHERE employee_id = $2",
        employee_uids["mgr001"],
        "ic003",
    )
    await conn.execute(
        "UPDATE people.employees SET manager_uid = $1 WHERE employee_id = $2",
        employee_uids["mgr002"],
        "ic004",
    )
    await conn.execute(
        "UPDATE people.employees SET manager_uid = $1 WHERE employee_id = $2",
        employee_uids["mgr002"],
        "ic005",
    )
    await conn.execute(
        "UPDATE people.employees SET manager_uid = $1 WHERE employee_id = $2",
        employee_uids["mgr002"],
        "ic006",
    )

    log.info(f"Created {len(employees_data)} employees")

    # Create skills catalog
    log.info("Creating skills catalog...")
    skills_data = [
        {
            "name": "Python",
            "category": "Programming Language",
            "description": "Python programming language",
            "tags": ["backend", "data-science", "automation"],
            "is_active": True,
        },
        {
            "name": "JavaScript",
            "category": "Programming Language",
            "description": "JavaScript programming language",
            "tags": ["frontend", "backend", "fullstack"],
            "is_active": True,
        },
        {
            "name": "TypeScript",
            "category": "Programming Language",
            "description": "TypeScript programming language",
            "tags": ["frontend", "backend", "type-safety"],
            "is_active": True,
        },
        {
            "name": "React",
            "category": "Framework",
            "description": "React UI framework",
            "tags": ["frontend", "ui", "javascript"],
            "is_active": True,
        },
        {
            "name": "FastAPI",
            "category": "Framework",
            "description": "FastAPI web framework",
            "tags": ["backend", "python", "api"],
            "is_active": True,
        },
        {
            "name": "PostgreSQL",
            "category": "Database",
            "description": "PostgreSQL relational database",
            "tags": ["database", "sql", "backend"],
            "is_active": True,
        },
        {
            "name": "Docker",
            "category": "DevOps",
            "description": "Containerization platform",
            "tags": ["devops", "containers", "deployment"],
            "is_active": True,
        },
        {
            "name": "Kubernetes",
            "category": "DevOps",
            "description": "Container orchestration",
            "tags": ["devops", "containers", "orchestration"],
            "is_active": True,
        },
        {
            "name": "AWS",
            "category": "Cloud",
            "description": "Amazon Web Services",
            "tags": ["cloud", "infrastructure", "devops"],
            "is_active": True,
        },
        {
            "name": "System Design",
            "category": "Architecture",
            "description": "System architecture and design",
            "tags": ["architecture", "design", "scalability"],
            "is_active": True,
        },
        {
            "name": "Agile",
            "category": "Methodology",
            "description": "Agile development methodology",
            "tags": ["methodology", "process", "management"],
            "is_active": True,
        },
        {
            "name": "Leadership",
            "category": "Soft Skills",
            "description": "Team leadership and management",
            "tags": ["management", "leadership", "soft-skills"],
            "is_active": True,
        },
    ]

    skill_uids = {}
    for skill_data in skills_data:
        row = await conn.fetchrow(
            """
            INSERT INTO people.skills_catalog (
                name, category, description, tags, is_active
            ) VALUES ($1, $2, $3, $4, $5)
            ON CONFLICT (name) DO UPDATE SET name = EXCLUDED.name
            RETURNING uid
            """,
            skill_data["name"],
            skill_data["category"],
            skill_data["description"],
            skill_data["tags"],
            skill_data["is_active"],
        )
        skill_uids[skill_data["name"]] = row["uid"]

    log.info(f"Created {len(skills_data)} skills")

    # Assign skills to employees
    log.info("Assigning skills to employees...")
    employee_skills = [
        # CEO - Leadership, Agile
        ("ceo001", "Leadership", 4),
        ("ceo001", "Agile", 3),
        # VP Engineering - Leadership, System Design, Python, AWS
        ("vp001", "Leadership", 4),
        ("vp001", "System Design", 4),
        ("vp001", "Python", 3),
        ("vp001", "AWS", 3),
        ("vp001", "Kubernetes", 2),
        # VP Product - Leadership, Agile
        ("vp002", "Leadership", 4),
        ("vp002", "Agile", 4),
        # Manager 1 - Leadership, Python, FastAPI, PostgreSQL
        ("mgr001", "Leadership", 3),
        ("mgr001", "Python", 4),
        ("mgr001", "FastAPI", 4),
        ("mgr001", "PostgreSQL", 3),
        ("mgr001", "Docker", 3),
        # Manager 2 - Leadership, JavaScript, React, TypeScript
        ("mgr002", "Leadership", 3),
        ("mgr002", "JavaScript", 4),
        ("mgr002", "TypeScript", 4),
        ("mgr002", "React", 4),
        ("mgr002", "Docker", 2),
        # IC 1 - Python, FastAPI, PostgreSQL, Docker
        ("ic001", "Python", 4),
        ("ic001", "FastAPI", 4),
        ("ic001", "PostgreSQL", 4),
        ("ic001", "Docker", 3),
        ("ic001", "AWS", 2),
        # IC 2 - Python, FastAPI, PostgreSQL
        ("ic002", "Python", 3),
        ("ic002", "FastAPI", 3),
        ("ic002", "PostgreSQL", 2),
        # IC 3 - JavaScript, React
        ("ic003", "JavaScript", 3),
        ("ic003", "React", 3),
        ("ic003", "TypeScript", 2),
        # IC 4 - JavaScript, React, TypeScript
        ("ic004", "JavaScript", 4),
        ("ic004", "React", 4),
        ("ic004", "TypeScript", 4),
        ("ic004", "Docker", 2),
        # IC 5 - Python, FastAPI
        ("ic005", "Python", 2),
        ("ic005", "FastAPI", 2),
        # IC 6 - JavaScript, React, TypeScript
        ("ic006", "JavaScript", 3),
        ("ic006", "React", 3),
        ("ic006", "TypeScript", 3),
    ]

    for emp_id, skill_name, level in employee_skills:
        # Use the employee's own UID as last_updated_by for simplicity
        employee_uid = employee_uids[emp_id]
        skill_uid = skill_uids[skill_name]
        await conn.execute(
            """
            INSERT INTO people.employee_skills (
                employee_uid, skill_uid, level, source, last_updated_by
            ) VALUES ($1, $2, $3, $4, $5)
            ON CONFLICT (employee_uid, skill_uid) DO NOTHING
            """,
            employee_uid,
            skill_uid,
            level,
            "MANAGER",
            employee_uid,
        )

    log.info(f"Assigned {len(employee_skills)} skill assignments")

    # Create teams
    log.info("Creating teams...")
    teams_data = [
        {
            "name": "Backend Engineering",
            "description": "Backend services and API development",
            "parent_team_uid": None,
            "leader_uid": employee_uids["mgr001"],
        },
        {
            "name": "Frontend Engineering",
            "description": "Frontend applications and UI development",
            "parent_team_uid": None,
            "leader_uid": employee_uids["mgr002"],
        },
        {
            "name": "Platform Team",
            "description": "Infrastructure and platform services",
            "parent_team_uid": None,
            "leader_uid": employee_uids["vp001"],
        },
    ]

    team_uids = {}
    for team_data in teams_data:
        row = await conn.fetchrow(
            """
            INSERT INTO people.teams (
                name, description, parent_team_uid, leader_uid
            ) VALUES ($1, $2, $3, $4)
            ON CONFLICT (name) DO UPDATE SET name = EXCLUDED.name
            RETURNING uid
            """,
            team_data["name"],
            team_data["description"],
            team_data["parent_team_uid"],
            team_data["leader_uid"],
        )
        team_uids[team_data["name"]] = row["uid"]

    # Set parent team relationships
    await conn.execute(
        "UPDATE people.teams SET parent_team_uid = $1 WHERE name = $2",
        team_uids["Platform Team"],
        "Backend Engineering",
    )
    await conn.execute(
        "UPDATE people.teams SET parent_team_uid = $1 WHERE name = $2",
        team_uids["Platform Team"],
        "Frontend Engineering",
    )

    # Add team memberships
    team_memberships = [
        ("Backend Engineering", "mgr001"),
        ("Backend Engineering", "ic001"),
        ("Backend Engineering", "ic002"),
        ("Backend Engineering", "ic005"),
        ("Frontend Engineering", "mgr002"),
        ("Frontend Engineering", "ic003"),
        ("Frontend Engineering", "ic004"),
        ("Frontend Engineering", "ic006"),
    ]

    for team_name, emp_id in team_memberships:
        await conn.execute(
            """
            INSERT INTO people.team_memberships (
                team_uid, employee_uid, is_primary, start_date
            ) VALUES ($1, $2, $3, $4)
            ON CONFLICT (team_uid, employee_uid) DO NOTHING
            """,
            team_uids[team_name],
            employee_uids[emp_id],
            True,
            date(2022, 1, 1),
        )

    log.info(f"Created {len(teams_data)} teams with memberships")

    # Create one-on-one sessions
    log.info("Creating one-on-one sessions...")
    today = date.today()
    one_on_ones = [
        {
            "manager_uid": employee_uids["mgr001"],
            "employee_uid": employee_uids["ic001"],
            "session_date": today - timedelta(days=7),
            "frequency": "WEEKLY",
            "agenda": "Project updates, career development",
            "shared_summary": "Discussed current sprint progress and upcoming goals",
        },
        {
            "manager_uid": employee_uids["mgr001"],
            "employee_uid": employee_uids["ic002"],
            "session_date": today - timedelta(days=14),
            "frequency": "BIWEEKLY",
            "agenda": "Performance review preparation",
            "shared_summary": "Reviewed Q4 performance and set goals for Q1",
        },
        {
            "manager_uid": employee_uids["mgr002"],
            "employee_uid": employee_uids["ic004"],
            "session_date": today - timedelta(days=3),
            "frequency": "WEEKLY",
            "agenda": "Technical challenges, team collaboration",
            "shared_summary": "Discussed architectural decisions for new feature",
        },
    ]

    session_uids = []
    for ooo in one_on_ones:
        row = await conn.fetchrow(
            """
            INSERT INTO people.one_on_one_sessions (
                manager_uid, employee_uid, session_date, frequency, agenda, shared_summary
            ) VALUES ($1, $2, $3, $4, $5, $6)
            RETURNING uid
            """,
            ooo["manager_uid"],
            ooo["employee_uid"],
            ooo["session_date"],
            ooo["frequency"],
            ooo["agenda"],
            ooo["shared_summary"],
        )
        session_uids.append(row["uid"])

    # Add notes to sessions
    if session_uids:
        await conn.execute(
            """
            INSERT INTO people.one_on_one_notes (
                session_uid, author_uid, visibility, content
            ) VALUES ($1, $2, $3, $4)
            """,
            session_uids[0],
            employee_uids["mgr001"],
            "SHARED",
            "Employee is making excellent progress on the authentication system. Should consider mentoring junior engineers.",
        )
        await conn.execute(
            """
            INSERT INTO people.one_on_one_notes (
                session_uid, author_uid, visibility, content
            ) VALUES ($1, $2, $3, $4)
            """,
            session_uids[0],
            employee_uids["ic001"],
            "PRIVATE",
            "Need to discuss work-life balance and potential promotion path.",
        )

    log.info(f"Created {len(one_on_ones)} one-on-one sessions")

    # Create action items
    log.info("Creating action items...")
    action_items = [
        {
            "session_uid": session_uids[0] if session_uids else None,
            "employee_uid": employee_uids["ic001"],
            "description": "Complete authentication system documentation",
            "owner_uid": employee_uids["ic001"],
            "due_date": today + timedelta(days=7),
            "status": "IN_PROGRESS",
        },
        {
            "session_uid": session_uids[0] if session_uids else None,
            "employee_uid": employee_uids["ic001"],
            "description": "Schedule mentoring session with junior engineer",
            "owner_uid": employee_uids["ic001"],
            "due_date": today + timedelta(days=14),
            "status": "OPEN",
        },
        {
            "session_uid": None,
            "employee_uid": employee_uids["ic004"],
            "description": "Review pull request for new feature",
            "owner_uid": employee_uids["ic004"],
            "due_date": today + timedelta(days=2),
            "status": "OPEN",
        },
    ]

    for item in action_items:
        await conn.execute(
            """
            INSERT INTO people.action_items (
                session_uid, employee_uid, description, owner_uid, due_date, status
            ) VALUES ($1, $2, $3, $4, $5, $6)
            """,
            item["session_uid"],
            item["employee_uid"],
            item["description"],
            item["owner_uid"],
            item["due_date"],
            item["status"],
        )

    log.info(f"Created {len(action_items)} action items")

    # Create jobs
    log.info("Creating jobs...")
    jobs_data = [
        {
            "id": "ENG-001",
            "title": "Senior Backend Engineer",
            "description": "We are looking for an experienced backend engineer to join our platform team.",
            "status": "OPEN",
        },
        {
            "id": "ENG-002",
            "title": "Frontend Engineer",
            "description": "Join our frontend team to build amazing user experiences.",
            "status": "OPEN",
        },
        {
            "id": "ENG-003",
            "title": "DevOps Engineer",
            "description": "Help us scale our infrastructure and improve our deployment processes.",
            "status": "CLOSED",
        },
    ]

    for job_data in jobs_data:
        await conn.execute(
            """
            INSERT INTO people.jobs (id, title, description, status)
            VALUES ($1, $2, $3, $4)
            ON CONFLICT (id) DO NOTHING
            """,
            job_data["id"],
            job_data["title"],
            job_data["description"],
            job_data["status"],
        )

    log.info(f"Created {len(jobs_data)} jobs")

    log.info("Database seeding completed successfully!")


async def main():
    """Main entry point for the seed script."""
    pool = await create_pool(
        user=settings.database.user,
        password=settings.database.password,
        database=settings.database.db,
        host=settings.database.host,
        port=settings.database.port,
        min_size=1,
        max_size=1,
    )

    try:
        async with pool.acquire() as conn:
            await seed_database(conn)
    finally:
        await pool.close()


if __name__ == "__main__":
    asyncio.run(main())

