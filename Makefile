.PHONY: test

pytest:
	docker compose exec -w /usr/src/app --env PYTHONPATH=./src:./test py pytest
