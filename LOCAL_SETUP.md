# Local Development Setup (Without Docker)

This guide will help you run the full stack locally when Docker isn't available.

## Prerequisites

1. **Python 3.13+** - [Download](https://www.python.org/downloads/)
2. **Node.js 20+** - [Download](https://nodejs.org/)
3. **PostgreSQL 17+** - [Download](https://www.postgresql.org/download/windows/)
   - Or use Docker just for PostgreSQL: `docker run -d -p 5432:5432 -e POSTGRES_PASSWORD=postgres -e POSTGRES_DB=PeopleDb postgres:17-alpine`
4. **uv** (Python package manager) - Will be installed if needed

## Quick Start

### 1. Set Up Database

**Option A: Install PostgreSQL locally**
- Install PostgreSQL from https://www.postgresql.org/download/windows/
- Create database: `createdb PeopleDb` (or use pgAdmin)
- Default connection: `localhost:5432`, user: `postgres`, password: (your password)

**Option B: Use Docker just for PostgreSQL** (if Docker works for this)
```powershell
docker run -d --name postgres-db -p 5432:5432 -e POSTGRES_PASSWORD=postgres -e POSTGRES_DB=PeopleDb postgres:17-alpine
```

### 2. Initialize Database Schema

```powershell
# Navigate to API directory
cd src/api

# Run the schema initialization
# You'll need psql installed, or use pgAdmin to run the SQL files
psql -U postgres -d PeopleDb -f person_tool/db/sql/schema.pgsql
```

Or use the Python script:
```powershell
cd src/api
uv run python -m person_tool.db.seed_data
```

### 3. Configure Environment

Create `src/api/.env`:
```env
APP_VERSION=0.1.0
APP_NAME=person-tool
APP_PORT=8000
APP_HOST=0.0.0.0
APP_RELOAD=true
APP_LOG_LEVEL=INFO
APP_BASE_API_URL=/api/v1

POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=PeopleDb
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_MIN_POOL_SIZE=1
POSTGRES_MAX_POOL_SIZE=10
```

### 4. Start Backend

```powershell
cd src/api
uv sync
uv run uvicorn person_tool.main:app --reload
```

Backend will run on: http://localhost:8000

### 5. Seed Test Data (Optional)

In a new terminal:
```powershell
cd src/api
uv run python -m person_tool.db.seed_data
```

### 6. Start Frontend

In a new terminal:
```powershell
cd src/ui/person-tool
npm install
npm start
```

Frontend will run on: http://localhost:3000

## Using Helper Scripts

See `setup-local.ps1` and `start-local.ps1` for automated setup.

## Troubleshooting

- **Database connection errors**: Check PostgreSQL is running and credentials in `.env`
- **Port already in use**: Change ports in `.env` and `package.json`
- **Python version**: Ensure Python 3.13+ is installed: `python --version`
- **Node version**: Ensure Node 20+ is installed: `node --version`

