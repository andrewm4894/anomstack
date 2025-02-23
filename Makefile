SHELL=/bin/bash

.PHONY: local
.PHONY: locald
.PHONY: docker
.PHONY: pre-commit
.PHONY: tests
.PHONY: docs
.PHONY: requirements
.PHONY: kill-locald
.PHONY: kill-dashboardd
.PHONY: ps-locald
.PHONY: dashboard
.PHONY: dashboardd

# start dagster locally
local:
	dagster dev -f anomstack/main.py

# start dagster locally as a daemon with no log file
locald:
	nohup dagster dev -f anomstack/main.py > /dev/null 2>&1 &

# kill any running dagster process
kill-locald:
	kill -9 $(shell ps aux | grep dagster | grep -v grep | awk '{print $$2}')

# kill any running dashboard process
kill-dashboardd:
	kill -9 $(shell ps aux | grep dashboard/dashboard.py | grep -v grep | awk '{print $$2}')

# list any running dagster process
ps-locald:
	ps aux | grep dagster | grep -v grep

# start docker containers
docker:
	docker compose up -d --build

# pre-commit
pre-commit:
	pre-commit run --all-files --config .pre-commit-config.yaml

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

dashboard:
	python dashboard/app.py

dashboardd:
	nohup python dashboard/app.py > /dev/null 2>&1 &
