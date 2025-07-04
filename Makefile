SHELL=/bin/bash

.PHONY: local
.PHONY: locald
.PHONY: docker
.PHONY: pre-commit
.PHONY: lint
.PHONY: tests
.PHONY: docs
.PHONY: docs-build
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
.PHONY: jupyter

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

# pre-commit
pre-commit:
        pre-commit run --all-files --config .pre-commit-config.yaml

# lint all files using pre-commit
lint: pre-commit

# run tests
tests:
	pytest -v

# run tests with coverage report
coverage:
	pytest -v --cov=anomstack --cov-report=term-missing

# setup local development environment and install dependencies
dev:
	pre-commit install

docs:
        cd docs && yarn start

# build the static documentation site
docs-build:
        cd docs && yarn build

requirements:
	pip-compile requirements.compile

dashboard:
	python dashboard/app.py

dashboard-uvicorn:
	uvicorn dashboard.app:app --host 0.0.0.0 --port 5003 --reload

dashboardd:
	nohup python dashboard/app.py > /dev/null 2>&1 &

dashboardd-uvicorn:
        nohup uvicorn dashboard.app:app --host 0.0.0.0 --port 5003 --reload > /dev/null 2>&1 &

requirements-install:
        pip install -r requirements.txt

# install development requirements
requirements-dev-install:
        pip install -r requirements-dev.txt

# launch Jupyter for working with notebooks
jupyter:
        jupyter lab --NotebookApp.allow_origin='*' --ip 0.0.0.0 --port 8888 --no-browser
