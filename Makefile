SHELL=/bin/bash

.PHONY: dashboard
.PHONY: local
.PHONY: locald
.PHONY: docker
.PHONY: pre-commit
.PHONY: tests
.PHONY: docs
.PHONY: requirements
.PHONY: kill-locald

# start streamlit dashboard
dashboard:
	streamlit run ./dashboard.py --server.port 8501

# start dagster locally
local:
	dagster dev -f anomstack/main.py -w config/workspace.yaml

# start dagster locally as a daemon
locald:
	nohup dagster dev -f anomstack/main.py -w config/workspace.yaml > dagster.log 2>&1 &

# kill any running dagster process
kill-locald:
	kill -9 $(shell ps aux | grep dagster | grep -v grep | awk '{print $$2}')

# start docker containers
docker:
	docker compose up -d --build

# pre-commit
pre-commit:
	pre-commit run --all-files

# run tests
tests:
	pytest -v

# setup local development environment and install dependencies
dev:
	pre-commit install

docs:
	cd docs && yarn start

requirements:
	pip-compile requirements.compile
