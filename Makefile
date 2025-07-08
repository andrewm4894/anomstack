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
.PHONY: posthog-example
.PHONY: docker-build
.PHONY: docker-tag
.PHONY: docker-push
.PHONY: docker-build-push
.PHONY: docker-pull
.PHONY: docker-clean
.PHONY: docker-logs
.PHONY: docker-shell
.PHONY: docker-stop
.PHONY: docker-rm
.PHONY: docker-prune

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

# start docker containers (now uses pre-built images)
docker:
	docker compose up -d

# start docker containers with local development images
docker-dev:
	docker compose -f docker-compose.yaml -f docker-compose.dev.yaml up -d

# build docker images locally
docker-build:
	docker build -f docker/Dockerfile.anomstack_code -t anomstack_code_image .
	docker build -f docker/Dockerfile.dagster -t anomstack_dagster_image .
	docker build -f docker/Dockerfile.anomstack_dashboard -t anomstack_dashboard_image .

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

# stop all containers
docker-stop:
	docker compose down

# remove all containers and networks
docker-rm:
	docker compose down --remove-orphans

# remove all containers, networks, and volumes (WARNING: this will delete data)
docker-prune:
	docker compose down -v --remove-orphans
	docker system prune -a -f

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

docs:
	cd docs && yarn start

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

# run the PostHog example ingest function
posthog-example:
	python scripts/posthog_example.py
