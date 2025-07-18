SHELL=/bin/bash

# =============================================================================
# LOCAL DEVELOPMENT
# =============================================================================

.PHONY: local locald kill-locald ps-locald dev

# start dagster locally (simple - just set DAGSTER_HOME directly)
local:
	DAGSTER_HOME=$$(pwd)/dagster_home dagster dev -f anomstack/main.py

# start dagster locally as a daemon with no log file
locald:
	nohup dagster dev -f anomstack/main.py > /dev/null 2>&1 &

# kill any running dagster process
kill-locald:
	kill -9 $(shell ps aux | grep dagster | grep -v grep | awk '{print $$2}')

# list any running dagster process
ps-locald:
	ps aux | grep dagster | grep -v grep

# setup local development environment and install dependencies
dev:
	pre-commit install

# =============================================================================
# DOCKER OPERATIONS
# =============================================================================

.PHONY: docker docker-dev docker-smart docker-build docker-dev-build docker-tag docker-push docker-build-push
.PHONY: docker-pull docker-clean docker-logs docker-logs-code docker-logs-dagit docker-logs-daemon docker-logs-dashboard
.PHONY: docker-shell-code docker-shell-dagit docker-shell-dashboard docker-restart-dashboard docker-restart-code
.PHONY: docker-stop docker-down docker-rm docker-prune

# start docker containers (now uses pre-built images)
docker:
	docker compose up -d

# smart docker start: try to pull, fallback to build if images don't exist
docker-smart:
	@echo "🔄 Attempting to pull pre-built images..."
	@if docker compose pull 2>/dev/null; then \
		echo "✅ Successfully pulled images, starting containers..."; \
		docker compose up -d; \
	else \
		echo "⚠️  Pull failed, building images locally..."; \
		make docker-dev-build && make docker-dev; \
	fi

# start docker containers with local development images
docker-dev:
	docker compose -f docker-compose.yaml -f docker-compose.dev.yaml up -d

# build docker images locally
docker-build:
	docker build -f docker/Dockerfile.anomstack_code -t anomstack_code_image .
	docker build -f docker/Dockerfile.dagster -t anomstack_dagster_image .
	docker build -f docker/Dockerfile.anomstack_dashboard -t anomstack_dashboard_image .

# build docker images for development
docker-dev-build:
	docker compose -f docker-compose.yaml -f docker-compose.dev.yaml build --no-cache

# tag docker images for Docker Hub
docker-tag:
	docker tag anomstack_code_image andrewm4894/anomstack_code:latest
	docker tag anomstack_dagster_image andrewm4894/anomstack_dagster:latest
	docker tag anomstack_dashboard_image andrewm4894/anomstack_dashboard:latest

# push docker images to Docker Hub
docker-push:
	docker push andrewm4894/anomstack_code:latest
	docker push andrewm4894/anomstack_dagster:latest
	docker push andrewm4894/anomstack_dashboard:latest

# build, tag, and push all images in one command
docker-build-push: docker-build docker-tag docker-push

# pull latest images from Docker Hub
docker-pull:
	docker pull andrewm4894/anomstack_code:latest
	docker pull andrewm4894/anomstack_dagster:latest
	docker pull andrewm4894/anomstack_dashboard:latest

# clean up unused docker resources
docker-clean:
	docker system prune -f
	docker volume prune -f

# view logs for all containers
docker-logs:
	docker compose logs -f

# view logs for specific service
docker-logs-code:
	docker compose logs -f anomstack_code

docker-logs-dagit:
	docker compose logs -f anomstack_dagit

docker-logs-daemon:
	docker compose logs -f anomstack_daemon

docker-logs-dashboard:
	docker compose logs -f anomstack_dashboard

# get shell access to running containers
docker-shell-code:
	docker compose exec anomstack_code /bin/bash

docker-shell-dagit:
	docker compose exec anomstack_dagit /bin/bash

docker-shell-dashboard:
	docker compose exec anomstack_dashboard /bin/bash

# restart specific services
docker-restart-dashboard:
	docker compose restart anomstack_dashboard

docker-restart-code:
	docker compose restart anomstack_code

# alias for docker-stop
docker-down:
	docker compose down

# remove all containers and networks
docker-rm:
	docker compose down --remove-orphans

# remove all containers, networks, and volumes (WARNING: this will delete data)
docker-prune:
	docker compose down -v --remove-orphans
	docker system prune -a -f

# =============================================================================
# DASHBOARD OPERATIONS
# =============================================================================

.PHONY: dashboard dashboardd dashboard-uvicorn dashboardd-uvicorn kill-dashboardd

# start dashboard locally
dashboard:
	python dashboard/app.py

# start dashboard with uvicorn
dashboard-uvicorn:
	uvicorn dashboard.app:app --host 0.0.0.0 --port 5003 --reload

# start dashboard locally as a daemon
dashboardd:
	nohup python dashboard/app.py > /dev/null 2>&1 &

# start dashboard with uvicorn as a daemon
dashboardd-uvicorn:
	nohup uvicorn dashboard.app:app --host 0.0.0.0 --port 5003 --reload > /dev/null 2>&1 &

# kill any running dashboard process
kill-dashboardd:
	kill $(shell ps aux | grep dashboard/app.py | grep -v grep | awk '{print $$2}') $(shell lsof -ti :5000)

# =============================================================================
# TESTING & QUALITY
# =============================================================================

.PHONY: tests coverage pre-commit

# run pre-commit hooks on all files
pre-commit:
	pre-commit run --all-files --config .pre-commit-config.yaml

# run tests
tests:
	pytest -v

# run tests with coverage report
coverage:
	pytest -v --cov=anomstack --cov-report=term-missing

# =============================================================================
# DOCUMENTATION
# =============================================================================

.PHONY: docs

# start documentation development server
docs:
	cd docs && yarn start

# =============================================================================
# DEPENDENCIES
# =============================================================================

.PHONY: requirements requirements-install

# compile requirements file
requirements:
	pip-compile requirements.compile

# install requirements
requirements-install:
	pip install -r requirements.txt

# =============================================================================
# UTILITIES
# =============================================================================

.PHONY: posthog-example kill-long-runs

# run the PostHog example ingest function
posthog-example:
	python scripts/posthog_example.py

# kill any dagster runs exceeding configured timeout
kill-long-runs:
	python scripts/kill_long_running_tasks.py

# run docker in dev mode with correct environment
docker-dev-env:
	docker compose -f docker-compose.yaml -f docker-compose.dev.yaml up -d

# stop docker containers
docker-stop:
	docker compose -f docker-compose.yaml -f docker-compose.dev.yaml down
