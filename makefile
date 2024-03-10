run-app:
	uvicorn main:app --reload
db:
	docker-compose run --rm --service-ports -d database
cache:
	docker-compose run --rm --service-ports -d cache
bash:
	docker-compose run --rm app bash
down:
	docker-compose down --remove-orphans
up:
	docker-compose up
build:
	docker-compose build
test:
	docker-compose run --rm app pytest
migrate:
	alembic upgrade head
migrations:
	alembic revision --autogenerate
