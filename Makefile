SHELL=/bin/bash

.PHONY: local
.PHONY: locald
.PHONY: docker
.PHONY: pre-commit
.PHONY: tests
.PHONY: docs
.PHONY: requirements
.PHONY: coverage
.PHONY: kill-locald
.PHONY: kill-dashboardd
.PHONY: ps-locald
.PHONY: dashboard
.PHONY: dashboardd
.PHONY: dashboard-uvicorn
.PHONY: dashboardd-uvicorn
.PHONY: requirements-install
.PHONY: requirements-dev-install
.PHONY: editable-install
.PHONY: setup
.PHONY: docker-down
.PHONY: notebook

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
	kill $(shell ps aux | grep dashboard/app.py | grep -v grep | awk '{print $$2}') $(shell lsof -ti :5000)

# list any running dagster process
ps-locald:
	ps aux | grep dagster | grep -v grep

# start docker containers
docker:
        docker compose up -d --build

# stop docker containers
docker-down:
        docker compose down

# open Jupyter notebooks
notebook:
        jupyter notebook

# pre-commit
pre-commit:
	pre-commit run --all-files --config .pre-commit-config.yaml

# run tests
tests:
	pytest -v

# run tests with coverage report
coverage:
	pytest -v --cov=anomstack --cov-report=term-missing

# setup local development environment and install dependencies
dev:
	pre-commit install

# run documentation site locally
docs:
        cd docs && yarn start

# compile requirements from pins
requirements:
        pip-compile requirements.compile

# run the dashboard
dashboard:
        python dashboard/app.py

# run the dashboard using uvicorn
dashboard-uvicorn:
        uvicorn dashboard.app:app --host 0.0.0.0 --port 5003 --reload

# run the dashboard as a daemon
dashboardd:
        nohup python dashboard/app.py > /dev/null 2>&1 &

# run the uvicorn dashboard as a daemon
dashboardd-uvicorn:
        nohup uvicorn dashboard.app:app --host 0.0.0.0 --port 5003 --reload > /dev/null 2>&1 &

# install runtime requirements
requirements-install:
        pip install -r requirements.txt

# install development requirements
requirements-dev-install:
        pip install -r requirements-dev.txt

# install anomstack in editable mode
editable-install:
        pip install -e .

# install all requirements and anomstack
setup: requirements-install requirements-dev-install editable-install
