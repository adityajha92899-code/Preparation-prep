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

Continuous Integration:

The repository includes a GitHub Actions workflow at `.github/workflows/ci.yml` that runs tests and uploads coverage.

Environment:

Copy `.env.example` to `.env` and set `DATABASE_URL` and LLM keys if you want real LLM providers.
