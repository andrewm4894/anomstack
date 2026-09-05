SHELL=/bin/bash

# =============================================================================
# LOCAL DEVELOPMENT
# =============================================================================

.PHONY: local locald kill-locald ps-locald dev

# start dagster locally (simple - just set DAGSTER_HOME directly)
local:
	export DAGSTER_HOME=`pwd`/dagster_home; dagster dev -f anomstack/main.py

# start dagster locally as a daemon with no log file
locald:
	export DAGSTER_HOME=`pwd`/dagster_home; nohup dagster dev -f anomstack/main.py > /dev/null 2>&1 &

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

.PHONY: docker docker-dev docker-smart docker-build docker-dev-build docker-clean
.PHONY: docker-logs docker-logs-code docker-logs-dagit docker-logs-daemon docker-logs-dashboard
.PHONY: docker-shell-code docker-shell-dagit docker-shell-dashboard docker-restart-dashboard docker-restart-code docker-restart reload-config enable-auto-reload enable-config-watcher
.PHONY: docker-stop docker-down docker-rm docker-prune

# start docker containers (now uses pre-built images)
docker:
	docker compose up -d

# smart docker start: build images locally and start containers
docker-smart:
	@echo "🔄 Building images locally and starting containers..."
	docker compose build --no-cache
	docker compose up -d

# start docker containers with local development images
docker-dev:
	docker compose -f docker-compose.yaml -f docker-compose.dev.yaml up -d

# build docker images locally
docker-build:
	docker build -f docker/Dockerfile.dagster -t anomstack_consolidated_image .
	docker build -f docker/Dockerfile.anomstack_dashboard -t anomstack_dashboard_image .

# build docker images for development
docker-dev-build:
	docker compose -f docker-compose.yaml -f docker-compose.dev.yaml build --no-cache

# The following commands are commented out as we no longer publish to Docker Hub
# Users should build images locally instead

# tag docker images for Docker Hub
# docker-tag:
# 	docker tag anomstack_code_image andrewm4894/anomstack_code:latest
# 	docker tag anomstack_dagster_image andrewm4894/anomstack_dagster:latest
# 	docker tag anomstack_dashboard_image andrewm4894/anomstack_dashboard:latest

# push docker images to Docker Hub
# docker-push:
# 	docker push andrewm4894/anomstack_code:latest
# 	docker push andrewm4894/anomstack_dagster:latest
# 	docker push andrewm4894/anomstack_dashboard:latest

# build, tag, and push all images in one command
# docker-build-push: docker-build docker-tag docker-push

# pull latest images from Docker Hub
# docker-pull:
# 	docker pull andrewm4894/anomstack_code:latest
# 	docker pull andrewm4894/anomstack_dagster:latest
# 	docker pull andrewm4894/anomstack_dashboard:latest

# clean up unused docker resources
docker-clean:
	docker system prune -f
	docker volume prune -f

# view logs for all containers
docker-logs:
	docker compose logs -f

# view logs for specific service
docker-logs-webserver:
	docker compose logs -f anomstack_webserver

docker-logs-dagit:
	docker compose logs -f anomstack_dagit

docker-logs-daemon:
	docker compose logs -f anomstack_daemon

docker-logs-dashboard:
	docker compose logs -f anomstack_dashboard

# get shell access to running containers
docker-shell-webserver:
	docker compose exec anomstack_webserver /bin/bash

docker-shell-dagit:
	docker compose exec anomstack_dagit /bin/bash

docker-shell-dashboard:
	docker compose exec anomstack_dashboard /bin/bash

# restart specific services
docker-restart-dashboard:
	docker compose restart anomstack_dashboard

docker-restart-webserver:
	docker compose restart anomstack_webserver

docker-restart-daemon:
	docker compose restart anomstack_daemon

# restart all containers (useful for .env changes)
docker-restart:
	docker compose restart

# reload configuration without restarting containers (hot reload)
reload-config:
	@echo "🔄 Reloading Anomstack configuration..."
	python3 scripts/configuration/reload_config.py

# enable automatic config reloading via Dagster scheduled job
enable-auto-reload:
	@echo "🤖 Enabling automatic configuration reloading..."
	@echo "ANOMSTACK_AUTO_CONFIG_RELOAD=true" >> .env
	@echo "ANOMSTACK_CONFIG_RELOAD_STATUS=RUNNING" >> .env
	@echo "✅ Auto reload enabled! Restart containers: make docker-restart"

# enable smart config file watcher sensor
enable-config-watcher:
	@echo "👁️ Enabling smart configuration file watcher..."
	@echo "ANOMSTACK_CONFIG_WATCHER=true" >> .env
	@echo "✅ Config watcher enabled! Restart containers: make docker-restart"

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
# FLY.IO DEPLOYMENT
# =============================================================================
#
# Docker Caching Notes:
# - Standard deploy targets use --no-cache but may still use cached Docker layers
# - Use *-fresh targets if you encounter caching issues (cleans local cache first)
# - Use fly-build-test to test builds locally before deploying
# - Use fly-docker-clean if you need to clear Docker cache manually
#

.PHONY: fly-validate fly-preview fly-deploy fly-status fly-logs fly-ssh
.PHONY: fly-preview-demo fly-preview-production fly-preview-development
.PHONY: fly-deploy-demo fly-deploy-production fly-deploy-development
.PHONY: fly-deploy-demo-fresh fly-deploy-production-fresh fly-deploy-development-fresh
.PHONY: fly-build-test fly-docker-clean

# validate fly.io configuration
fly-validate:
	./scripts/deployment/validate_fly_config.sh

# preview what environment variables will be set as Fly secrets
fly-preview:
	./scripts/deployment/preview_fly_secrets.sh

# preview deployment with demo profile
fly-preview-demo:
	./scripts/deployment/preview_fly_secrets.sh --profile demo

# preview deployment with production profile
fly-preview-production:
	./scripts/deployment/preview_fly_secrets.sh --profile production

# preview deployment with development profile
fly-preview-development:
	./scripts/deployment/preview_fly_secrets.sh --profile development

# deploy to fly.io (reads .env file automatically)
fly-deploy:
	./scripts/deployment/deploy_fly.sh

# deploy to fly.io with demo profile (enables demo metric batches)
fly-deploy-demo:
	./scripts/deployment/deploy_fly.sh --profile demo

# deploy to fly.io with production profile (production-ready settings)
fly-deploy-production:
	./scripts/deployment/deploy_fly.sh --profile production

# deploy to fly.io with development profile (all examples enabled)
fly-deploy-development:
	./scripts/deployment/deploy_fly.sh --profile development

# deploy with fresh build (clears local Docker cache first) - demo profile
fly-deploy-demo-fresh:
	@echo "🧹 Cleaning local Docker cache to ensure fresh build..."
	docker system prune -f --filter "until=1h"
	@echo "🧹 Cleaning Docker builder cache..."
	docker builder prune -f 2>/dev/null || true
	./scripts/deployment/deploy_fly.sh --profile demo --force-rebuild

# deploy with fresh build (clears local Docker cache first) - production profile
fly-deploy-production-fresh:
	@echo "🧹 Cleaning local Docker cache to ensure fresh build..."
	docker system prune -f --filter "until=1h"
	@echo "🧹 Cleaning Docker builder cache..."
	docker builder prune -f 2>/dev/null || true
	./scripts/deployment/deploy_fly.sh --profile production --force-rebuild

# deploy with fresh build (clears local Docker cache first) - development profile
fly-deploy-development-fresh:
	@echo "🧹 Cleaning local Docker cache to ensure fresh build..."
	docker system prune -f --filter "until=1h"
	@echo "🧹 Cleaning Docker builder cache..."
	docker builder prune -f 2>/dev/null || true
	./scripts/deployment/deploy_fly.sh --profile development --force-rebuild

# test fly.io build locally before deploying (helps catch issues early)
fly-build-test:
	@echo "🧪 Testing Fly.io build locally..."
	@GIT_COMMIT_HASH=$$(git rev-parse --short HEAD 2>/dev/null || echo "unknown") && \
	echo "📝 Git commit hash: $$GIT_COMMIT_HASH" && \
	docker build --no-cache -f docker/Dockerfile.fly --build-arg ANOMSTACK_BUILD_HASH="$$GIT_COMMIT_HASH" -t anomstack-fly-test .
	@echo "✅ Build successful! Testing container startup..."
	@echo "🚀 Starting container on port 3001 (http://localhost:3001)..."
	@echo "Press Ctrl+C to stop the test container"
	docker run --rm -p 3001:80 --name anomstack-fly-test anomstack-fly-test

# clean Docker cache (useful when encountering caching issues)
fly-docker-clean:
	@echo "🧹 Cleaning Docker cache (keeps last 24h of images)..."
	docker system prune -f --filter "until=24h"
	@echo "🧹 Removing old anomstack images..."
	docker images | grep anomstack | awk '{print $$3}' | xargs -r docker rmi -f 2>/dev/null || true
	@echo "✅ Docker cache cleaned"

# check fly.io app status (requires app name as FLY_APP env var)
fly-status:
	@if [ -z "$$FLY_APP" ]; then echo "Set FLY_APP environment variable"; exit 1; fi
	fly status -a $$FLY_APP

# view fly.io app logs (requires app name as FLY_APP env var)
fly-logs:
	@if [ -z "$$FLY_APP" ]; then echo "Set FLY_APP environment variable"; exit 1; fi
	fly logs -f -a $$FLY_APP

# ssh into fly.io app (requires app name as FLY_APP env var)
fly-ssh:
	@if [ -z "$$FLY_APP" ]; then echo "Set FLY_APP environment variable"; exit 1; fi
	fly ssh console -a $$FLY_APP

# =============================================================================
# RESET OPERATIONS
# =============================================================================

.PHONY: reset-gentle reset-medium reset-nuclear reset-full-nuclear reset-interactive

# interactive reset with guided options
reset-interactive:
	@scripts/utils/reset_docker.sh

# gentle reset: rebuild containers with fresh images (safest)
reset-gentle:
	@scripts/utils/reset_docker.sh gentle

# medium reset: remove containers, keep data volumes
reset-medium:
	@scripts/utils/reset_docker.sh medium

# nuclear reset: remove everything including local data
reset-nuclear:
	@scripts/utils/reset_docker.sh nuclear

# full nuclear reset: nuclear + full docker system cleanup (maximum cleanup)
reset-full-nuclear:
	@scripts/utils/reset_docker.sh full-nuclear

# =============================================================================
# DAGSTER STORAGE CLEANUP
# =============================================================================

.PHONY: dagster-cleanup-status dagster-cleanup-minimal dagster-cleanup-standard dagster-cleanup-aggressive

# show current dagster storage usage and configuration status
dagster-cleanup-status:
	@scripts/utils/cleanup_dagster_storage.sh status

# minimal dagster cleanup - remove old logs only (safe)
dagster-cleanup-minimal:
	@scripts/utils/cleanup_dagster_storage.sh minimal

# standard dagster cleanup - remove runs older than 30 days
dagster-cleanup-standard:
	@scripts/utils/cleanup_dagster_storage.sh standard

# aggressive dagster cleanup - remove runs older than 7 days
dagster-cleanup-aggressive:
	@scripts/utils/cleanup_dagster_storage.sh aggressive

# interactive dagster cleanup menu
dagster-cleanup-menu:
	@scripts/utils/cleanup_dagster_storage.sh menu

# =============================================================================
# DASHBOARD OPERATIONS
# =============================================================================

.PHONY: dashboard dashboardd dashboard-uvicorn dashboardd-uvicorn dashboard-local-dev kill-dashboardd seed-local-db

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

# seed local development database with dummy data
seed-local-db:
	@echo "🌱 Seeding local development database (python_ingest_simple only)..."
	source venv/bin/activate && python scripts/development/seed_local_db.py --metric-batches "python_ingest_simple" --db-path tmpdata/anomstack-local-dev.db --hours 72 --interval 10 --force

seed-local-db-all:
	@echo "🌱 Seeding database with ALL metric batches (python_ingest_simple, netdata, posthog, yfinance, currency)..."
	source venv/bin/activate && python scripts/development/seed_local_db.py --metric-batches "python_ingest_simple,netdata,posthog,yfinance,currency" --db-path tmpdata/anomstack-all.db --hours 72 --interval 10 --force

seed-local-db-custom:
	@echo "🌱 Use: make seed-local-db-custom BATCHES='python_ingest_simple,netdata' DB_PATH='tmpdata/my.db'"
	@echo "   Default BATCHES: python_ingest_simple"
	@echo "   Default DB_PATH: tmpdata/anomstack-custom.db"
	source venv/bin/activate && python scripts/development/seed_local_db.py --metric-batches "$(or $(BATCHES),python_ingest_simple)" --db-path "$(or $(DB_PATH),tmpdata/anomstack-custom.db)" --hours 72 --interval 10 --force

# start dashboard in local development mode with seeded database (all batches)
dashboard-local-dev:
	@echo "🚀 Starting dashboard in local development mode..."
	@echo "📊 Using comprehensive database with python_ingest_simple, netdata, posthog, yfinance, AND currency metrics"
	@if [ ! -f "tmpdata/anomstack-all.db" ]; then \
		echo "⚠️  All-batches database not found. Creating it first..."; \
		$(MAKE) seed-local-db-all; \
	fi
	source venv/bin/activate && ANOMSTACK_ENV_FILE_PATH=profiles/local-dev-all.env uvicorn dashboard.app:app --host 0.0.0.0 --port 5003 --reload

# kill any running dashboard process
kill-dashboardd:
	kill $(shell ps aux | grep dashboard/app.py | grep -v grep | awk '{print $$2}') $(shell lsof -ti :5000)

# =============================================================================
# TESTING & QUALITY
# =============================================================================

.PHONY: tests test-examples coverage pre-commit

# run pre-commit hooks on all files
pre-commit:
	pre-commit run --all-files --config .pre-commit-config.yaml

# run tests (includes documentation link checking)
tests:
	source venv/bin/activate && pytest -v
	@echo ""
	@echo "🔍 Running documentation link tests..."
	@$(MAKE) docs-test

# run only example ingest function tests
test-examples:
	source venv/bin/activate && pytest -v tests/test_examples.py

# run tests with coverage report
coverage:
	source venv/bin/activate && pytest -v --cov=anomstack --cov-report=term-missing

# =============================================================================
# DOCUMENTATION
# =============================================================================

.PHONY: docs docs-start docs-build docs-serve docs-clear docs-install docs-test

# start documentation development server (alias for docs-start)
docs:
	@$(MAKE) docs-start

# install documentation dependencies
docs-install:
	cd docs && npm install

# start development server with live reload
docs-start:
	cd docs && npm start

# build static documentation site (includes broken link checking)
docs-build:
	cd docs && npm run build

# test documentation for broken links (uses Docusaurus native link checking)
docs-test:
	@echo "🔍 Testing documentation for broken links..."
	@echo "Using Docusaurus native broken link detection (onBrokenLinks: 'throw')"
	@$(MAKE) docs-build
	@echo "✅ Documentation build succeeded - no broken links found!"

# serve built documentation locally
docs-serve:
	cd docs && npm run serve

# clear documentation build cache
docs-clear:
	cd docs && npm run clear

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

.PHONY: posthog-example hackernews-example run-example list-examples kill-long-runs

# run the PostHog example ingest function (legacy)
posthog-example:
	python scripts/examples/run_example.py posthog

# run the HackerNews example ingest function (legacy)
hackernews-example:
	python scripts/examples/run_example.py hackernews

# run any example using unified script
run-example:
	@if [ -z "$(EXAMPLE)" ]; then \
		echo "Usage: make run-example EXAMPLE=<name>"; \
		echo ""; \
		echo "Popular examples:"; \
		echo "  • hackernews     - HackerNews stories"; \
		echo "  • earthquake     - USGS earthquake data"; \
		echo "  • iss_location   - Space station location"; \
		echo "  • posthog        - Analytics (requires credentials)"; \
		echo ""; \
		echo "📋 To see all 26 examples: make list-examples"; \
	else \
		python scripts/examples/run_example.py $(EXAMPLE); \
	fi

# list all available examples
list-examples:
	python scripts/examples/run_example.py --list


# kill any dagster runs exceeding configured timeout
kill-long-runs:
	python scripts/maintenance/kill_long_running_tasks.py

# clean up disk space on fly instance (requires SSH access)
fly-cleanup:
	@echo "🧹 Running disk cleanup on Fly instance..."
	@echo "This will SSH into your Fly instance and run cleanup"
	@if [ -z "$$FLY_APP" ]; then echo "Set FLY_APP environment variable"; exit 1; fi
	fly ssh console -a $$FLY_APP -C "cd /opt/dagster/app && python scripts/maintenance/cleanup_disk_space.py"

# preview cleanup on fly instance (dry run)
fly-cleanup-preview:
	@echo "🔍 Previewing disk cleanup on Fly instance..."
	@if [ -z "$$FLY_APP" ]; then echo "Set FLY_APP environment variable"; exit 1; fi
	fly ssh console -a $$FLY_APP -C "cd /opt/dagster/app && python scripts/maintenance/cleanup_disk_space.py --dry-run"

# aggressive cleanup for emergency situations
fly-cleanup-aggressive:
	@echo "⚡ Running AGGRESSIVE disk cleanup on Fly instance..."
	@echo "This will remove more files - use only if disk is critically full"
	@if [ -z "$$FLY_APP" ]; then echo "Set FLY_APP environment variable"; exit 1; fi
	fly ssh console -a $$FLY_APP -C "cd /opt/dagster/app && python scripts/maintenance/cleanup_disk_space.py --aggressive"

# run docker in dev mode with correct environment
docker-dev-env:
	docker compose -f docker-compose.yaml -f docker-compose.dev.yaml up -d

# stop docker containers
docker-stop:
	docker compose -f docker-compose.yaml -f docker-compose.dev.yaml down

# Reproducible Python 3.12 development environment (requires uv).
.PHONY: setup-local stack test-local update-dependencies
setup-local:
	uv venv --python 3.12 --allow-existing .venv
	uv pip install --python .venv/bin/python -c constraints.txt -r requirements.txt -r requirements-dashboard.txt -r requirements-dev.txt

stack:
	.venv/bin/python scripts/development/local_stack.py

test-local:
	CI=true .venv/bin/python -m pytest tests/

update-dependencies:
	uv pip compile requirements.txt requirements-dashboard.txt requirements-dev.txt --no-emit-package anomstack --universal --upgrade --python-version 3.12 -o constraints.txt
