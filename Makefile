.PHONY: test

lint:
	docker compose exec -w /usr/src/app --env PYTHONPATH=./src:./test py mypy .

pytest:
	docker compose exec -w /usr/src/app --env PYTHONPATH=./src:./test py pytest -v

test: lint pytest
