build-docker:
	docker-compose build --no-cache

up-docker:
	docker-compose up -d

down:
	docker-compose down

migrate-docker:
	docker-compose run fastapi-app alembic upgrade head

test-docker:
	docker-compose run api pytest

coverage-docker:
	docker-compose run api pytest --cov=app --cov-report=html
