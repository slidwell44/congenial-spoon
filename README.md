# People Tool

Full-stack reference implementation of the People Tool SRS: org charts, employee profiles, skills, 1:1s, and coverage insights.

## Architecture

| Layer   | Stack | Highlights |
|---------|-------|------------|
| API     | FastAPI + asyncpg | Modular services for employees, skills, 1:1s, coverage reports, jobs, and system health. |
| DB      | PostgreSQL        | `people` schema with employees, teams, skills catalog, employee skills/history, 1:1 sessions/notes/action items, role/project skill profiles, audit log. |
| Frontend| React 19 + React Router | Manager dashboard, employee profile view, skills matrix, API-backed hooks with mock fallbacks. |

Audit logging hooks capture sensitive operations (skills, 1:1 notes, action items).

## Local Development

### Quick Start (Recommended)

1. **Run setup script:**
   ```powershell
   .\setup-local.ps1
   ```

2. **Initialize database:**
   ```powershell
   .\init-db.ps1
   ```

3. **Start the application:**
   ```powershell
   .\start-local.ps1
   ```

This will start both backend and frontend in separate terminal windows.

### Manual Setup

#### Backend
```bash
cd src/api
uv sync           # Install dependencies
# Create .env file with database settings (see setup script)
uv run uvicorn person_tool.main:app --reload
```

#### Frontend
```bash
cd src/ui/person-tool
npm install
npm start
```

#### Database Setup
1. Install PostgreSQL or use Docker: `docker run -d -p 5432:5432 -e POSTGRES_PASSWORD=postgres -e POSTGRES_DB=PeopleDb postgres:17-alpine`
2. Initialize schema: `.\init-db.ps1` or manually run SQL files
3. Seed test data: `cd src/api && uv run python -m person_tool.db.seed_data`

Key endpoints (default `http://localhost:8000/api/v1`):
- `GET /employees`, `POST /employees`, `GET /employees/{uid}/org`
- `GET/POST /skills/catalog`, `GET /skills/matrix`
- `GET/POST /one-on-ones/...`
- `POST /coverage/profiles`, `GET /coverage/teams/{managerUid}?profileUid=...`

Set `REACT_APP_API_BASE` if the API runs on a non-default host.

## Docker Compose (Recommended)

The easiest way to run the full stack with test data:

**Quick Start:**
```powershell
.\start-app.ps1
```

Or manually:
```bash
docker compose up
```

This will:
- Start PostgreSQL database (port 5432)
- Initialize the database schema automatically
- Seed the database with test data (employees, skills, teams, one-on-ones, etc.)
- Start the FastAPI backend (port 8000)
- Start the React frontend (port 3000)

Access the application:
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

The seed script automatically populates the database with:
- 12 employees (CEO, VPs, managers, and individual contributors)
- 12 skills (Python, JavaScript, React, PostgreSQL, etc.)
- Skill assignments for employees
- 3 teams (Backend Engineering, Frontend Engineering, Platform Team)
- One-on-one sessions and action items
- Sample job postings

To reset the database and re-seed:
```bash
docker compose down -v  # Remove volumes
docker compose up        # Start fresh
```

## Testing

- Backend: `cd src/api && pytest`
- Frontend: `cd src/ui/person-tool && npm test`

## License
MIT License — see `LICENSE`.