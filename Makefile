.PHONY: run test seed docker-up lint

run:
	venv\Scripts\activate && python -m uvicorn app.main:app --reload --port 8000

test:
	venv\Scripts\activate && python -m pytest -q

seed:
	python scripts/seed_kb.py

docker-up:
	docker-compose up --build
