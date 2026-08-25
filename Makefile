.PHONY: up down logs test api

up:
	docker compose up --build

down:
	docker compose down

logs:
	docker compose logs -f api

test:
	cd services/api && python -m pytest -q

api:
	cd services/api && uvicorn main:app --reload --port 8000
