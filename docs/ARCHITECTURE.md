## People Tool Architecture

### Platform Overview
- **Backend**: FastAPI service (`src/api/person_tool`) backed by PostgreSQL via `asyncpg`.
- **Frontend**: React single-page app (`src/ui/person-tool`) that talks to the API through `/api`.
- **Infrastructure**: Docker compose for local dev (API + Postgres), with env-configured SSO/identity placeholders.

### Domain Modules
1. **Employees & Org**
   - Employees table extends classic HR data (title, department, manager, role, status).
   - Teams + memberships capture matrix structures.
   - Org service exposes:
     - Company/org subtree recursion for managers (`GET /org/tree`).
     - “My Org” aggregations (directs, managers, IC counts, open roles).
2. **Skills**
   - Skill catalog with categories/tags and configurable proficiency levels.
   - Employee skills w/ history + audit trail (`source`, `last_updated_by`).
   - Skill search/filter endpoints and skills matrix (rows = people, columns = selected skills).
3. **1:1s**
   - Session, notes, and action-item tables capture shared vs private artifacts.
   - CRUD endpoints enforce visibility rules via RBAC helper dependency.
   - Exports (PDF/CSV) are queued for later phases.
4. **Coverage & Hiring Insights**
   - Role/project skill profiles declare required levels + headcount.
   - Coverage endpoint compares a manager’s org against selected profile(s) and surfaces SPOFs & deficits.
5. **System & Audit**
   - Unified audit table logs changes to sensitive entities.
   - Health/config endpoints stay under `/system`.

### Access Control
- Lightweight RBAC layer reads `X-User-Id` + `X-User-Role` headers (for now) and enforces:
  - Admin/HR: global read/write.
  - Senior manager: full chain under them.
  - Manager: direct + indirect reports (summary only for deeper levels).
  - IC: self + shared 1:1 notes and approved skills.
- Hooks ready for SSO in a future phase.

### Data Flow (MVP)
1. **Managers** load dashboard → API pulls org subtree + skill/1:1 summaries.
2. **Skill updates** via manager or IC proposals → service writes to `employee_skills` and logs history + audit.
3. **1:1 session** creation writes session, optional notes, action items; UI surfaces upcoming/past sessions.
4. **Coverage view** selects team + profile → aggregates skills and returns gaps + suggested hires.

### API Surface (MVP)
- `/employees` CRUD + filters, `/employees/{uid}/profile`, `/employees/{uid}/org`.
- `/skills/catalog`, `/skills/search`, `/employees/{uid}/skills`, `/skills/matrix`.
- `/one-on-ones` sessions, notes, action items.
- `/coverage/teams/{manager_uid}` with optional `profile_uid`.
- `/profiles/role-skill` for defining requirements.

### Frontend Structure
- React router with three core routes:
  1. **Dashboard** (`/`) – org snapshot, nudges for overdue 1:1s, open action items.
  2. **Employee Profile** (`/employees/:id`) – sections for basics, skills, 1:1 history, action items.
  3. **Skills Matrix / Coverage** (`/skills-matrix`) – filterable matrix + coverage cards.
- Shared context handles current user + auth headers; query hooks wrap fetch/axios.

### Non-Functional Notes
- All endpoints instrumented with process-time middleware + structured logs.
- Future: add Celery/Redis worker for exports + reminders; integrate HRIS sync job.

This outline maps directly to the SRS and guides the implementation work in this repo.

