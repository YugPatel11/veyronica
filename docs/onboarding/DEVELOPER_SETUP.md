# Nexus Developer Onboarding Guide (< 30 Minutes)

Welcome to the **Nexus Autonomous Academic Operations Platform** engineering team! This guide walks you through setting up your local environment from scratch in under 30 minutes.

---

## 1. Prerequisites Checklist

Ensure you have the following installed on your machine:
- **Git:** >= 2.40
- **Docker & Docker Compose:** Docker Desktop >= 25.0
- **Python:** 3.12+ (Verify with `python --version`)
- **Node.js:** 20.x or 22.x LTS (Verify with `node -v`)
- **npm:** 10.x+

---

## 2. 5-Minute Quick Start (Docker Environment)

If you just want to run the full stack immediately:

```bash
# 1. Clone the repository
git clone https://github.com/your-org/nexus.git
cd nexus

# 2. Copy the environment configuration
cp .env.example .env

# 3. Start all services in background
docker compose up -d

# 4. Access the web applications
# - Frontend:    http://localhost:3000
# - Backend API: http://localhost:8000/docs
# - Mailpit:     http://localhost:8025
# - MinIO:       http://localhost:9001
```

---

## 3. Local Development Setup (Hot Reloading)

For daily feature development, run PostgreSQL and Redis in Docker while running the Python backend and Next.js frontend on your host machine.

### Step 3.1: Start Supporting Infrastructure
```bash
docker compose up -d postgres redis minio mailpit
```

### Step 3.2: Backend Setup (FastAPI & Python 3.12)
```bash
# Navigate to backend directory
cd backend

# Create and activate virtual environment
python -m venv .venv

# On Linux/macOS:
source .venv/bin/activate
# On Windows (PowerShell):
.venv\Scripts\Activate.ps1

# Install dependencies in editable mode
pip install --upgrade pip
pip install -e .

# Run database migrations & seed initial demo data
python -m app.db.seed

# Start FastAPI dev server with auto-reload
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```
API Documentation is live at: `http://localhost:8000/docs`

### Step 3.3: Frontend Setup (Next.js 15 & React 19)
```bash
# In a new terminal window:
cd frontend

# Install npm dependencies
npm install

# Start Next.js development server with Turbopack
npm run dev
```
Frontend UI is live at: `http://localhost:3000`

---

## 4. Running the Test Suites

### Backend Unit & Integration Tests
```bash
cd backend
pytest -v
```

### Frontend Component Tests & Type Checking
```bash
cd frontend
npm run type-check
npm run test
npm run lint
```

### Component Storybook
```bash
cd frontend
npm run storybook
```
Storybook will launch on `http://localhost:6006`.

---

## 5. Mock Enterprise Systems

Nexus integrates with simulated external legacy systems for ERP, LMS, and CRM:
- Located under `mock-systems/`
- Start all mock adapters:
  ```bash
  python mock-systems/shared/mock_server.py --port 9090
  ```

---

## 6. Common Development Commands Cheat Sheet

| Task | Command |
|:---|:---|
| Run backend tests | `pytest backend/tests/unit -v` |
| Run frontend tests | `npm --prefix frontend test` |
| Type check frontend | `npm --prefix frontend run type-check` |
| Build frontend bundle | `npm --prefix frontend run build` |
| Re-seed database | `python backend/app/db/seed.py` |
| Run load test target | `python backend/tests/load/verify_targets.py` |
| Backup database | `python backend/scripts/backup_restore.py --backup` |

---

## 7. Troubleshooting & FAQ

- **Port 5432 or 6379 already in use?**
  Change `POSTGRES_PORT` or `REDIS_PORT` in your `.env` file.
- **Next.js Turbopack cache issue?**
  Run `rm -rf frontend/.next` and restart `npm run dev`.
- **Database migration error?**
  Run `python backend/app/db/seed.py --reset` to recreate tables.
