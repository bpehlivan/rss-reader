run-app:
	uvicorn main:app --reload
db:
	docker-compose run --rm --service-ports -d database
bash:
	docker-compose run --rm app bash
down:
	docker-compose down --remove-orphans
up:
	docker-compose up
build:
	docker-compose build
