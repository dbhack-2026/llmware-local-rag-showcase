.PHONY: install run test lint docker

install:
	python -m pip install -r requirements-dev.txt

run:
	uvicorn app.main:app --reload --port 8080

test:
	pytest -q

lint:
	ruff check app tests

docker:
	docker build -t llmware-local-rag:local .
