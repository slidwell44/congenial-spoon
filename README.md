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

### Backend
```bash
cd src/api
uv sync           # or uv pip install -r pyproject.toml
cp .env.example .env   # populate APP_*/POSTGRES_* settings
uvicorn person_tool.main:app --reload
```

Key endpoints (default `http://localhost:8000/api/v1`):
- `GET /employees`, `POST /employees`, `GET /employees/{uid}/org`
- `GET/POST /skills/catalog`, `GET /skills/matrix`
- `GET/POST /one-on-ones/...`
- `POST /coverage/profiles`, `GET /coverage/teams/{managerUid}?profileUid=...`

### Frontend
```bash
cd src/ui/person-tool
npm install
npm start
```

Set `REACT_APP_API_BASE` if the API runs on a non-default host.

## Docker Compose

The easiest way to run the full stack with test data:

```bash
docker compose up
```

This will:
- Start PostgreSQL database (port 5432)
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