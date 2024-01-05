SHELL=/bin/bash

.PHONY: dashboard
.PHONY: local
.PHONY: docker
.PHONY: pre-commit
.PHONY: tests
.PHONY: docs

## start streamlit dashboard
dashboard:
	streamlit run ./dashboard.py --server.port 8501

## start dagster locally
local:
	dagster dev -f anomstack/main.py

## start docker containers
docker:
	docker compose up -d --build

## pre-commit
pre-commit:
	pre-commit run --all-files

## run tests
tests:
	pytest -v

## setup local development environment and install dependencies
dev:
	pre-commit install

docs:
	cd docs && yarn start
