# MAANG Prep Builder (scaffold)

Minimal scaffold of the MAANG Prep Builder application.

Quick start:

1. Create and activate virtualenv (Windows):

```powershell
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

2. Copy `.env.example` to `.env` and fill keys.

3. Run the app:

```powershell
python -m uvicorn app.main:app --reload --port 8000
```

Docker (recommended for clean local run):

```bash
docker-compose up --build
```

Run tests locally:

```bash
venv\Scripts\activate
python -m pytest -q
```

Frontend setup:

```bash
cd frontend
npm install
npm run dev
```

Open the app at `http://localhost:3000` and the backend API at `http://localhost:8000/api/v1`.

Docker (recommended for clean local run):

The repository includes a GitHub Actions workflow at `.github/workflows/ci.yml` that runs tests and uploads coverage.

Environment:

Copy `.env.example` to `.env` and set `DATABASE_URL` plus `GOOGLE_AI_KEY` for real Google AI integration.

Secrets & GitHub:

1. Add your Google AI key to `.env` or GitHub Secrets (`GOOGLE_AI_KEY`).
2. Push to GitHub and enable Actions to run CI.

Quick demo:

```bash
python scripts/run_demo.py
```
