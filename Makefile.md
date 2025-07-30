# Makefile Documentation

This document provides comprehensive documentation for the Anomstack Makefile, which contains targets for development, Docker operations, testing, and maintenance.

## Table of Contents

- [Overview](#overview)
- [Local Development](#local-development)
- [Docker Operations](#docker-operations)
- [Reset Operations](#reset-operations)
- [Dagster Storage Cleanup](#dagster-storage-cleanup)
- [Dashboard Operations](#dashboard-operations)
- [Testing & Quality](#testing--quality)
- [Documentation](#documentation)
- [Dependencies](#dependencies)
- [Utilities](#utilities)
- [Quick Reference](#quick-reference)

## Overview

The Makefile is organized into logical sections for different aspects of Anomstack development and deployment. Each section contains related targets that perform specific tasks.

**Prerequisites:**
- Docker and Docker Compose installed
- Python 3.x with required dependencies
- Node.js and Yarn (for documentation)

## Local Development

Targets for running Anomstack locally without Docker.

### `make local`
**Start Dagster locally (simple mode)**
- Sets `DAGSTER_HOME` to local `dagster_home/` directory
- Runs Dagster in development mode with hot reloading
- Uses the main Anomstack module (`anomstack/main.py`)

```bash
make local
```

*Use when: You want to develop and test locally with immediate feedback*

### `make locald`
**Start Dagster as background daemon**
- Same as `local` but runs in background
- Output redirected to `/dev/null`
- Useful for long-running local development

```bash
make locald
```

*Use when: You want Dagster running in background while you work on other things*

### `make kill-locald`
**Kill running Dagster processes**
- Finds and kills all local Dagster processes
- Uses `kill -9` for forceful termination

```bash
make kill-locald
```

*Use when: You need to stop background Dagster processes*

### `make ps-locald`
**List running Dagster processes**
- Shows all currently running Dagster processes
- Helpful for debugging multiple instances

```bash
make ps-locald
```

### `make dev`
**Setup development environment**
- Installs pre-commit hooks
- Prepares development dependencies

```bash
make dev
```

*Use when: Setting up a new development environment*

## Docker Operations

Comprehensive Docker management for containerized deployment.

### Starting Containers

#### `make docker`
**Start containers with pre-built images (Production)**
- Uses images from Docker Hub (`andrewm4894/*`)
- Fast startup, no building required
- Production-ready configuration

```bash
make docker
```

#### `make docker-dev`
**Start containers with local development images**
- Uses locally built images for development
- Includes development overrides
- Live code mounting for development

```bash
make docker-dev
```

#### `make docker-smart`
**Intelligent container startup**
- Tries to pull pre-built images first
- Falls back to local building if pull fails
- Best of both worlds approach

```bash
make docker-smart
```

### Building Images

#### `make docker-build`
**Build all images locally**
- Builds: `anomstack_code_image`, `anomstack_dagster_image`, `anomstack_dashboard_image`
- Uses individual Dockerfiles for each service
- Local tags for development use

```bash
make docker-build
```

#### `make docker-dev-build`
**Build development images with no cache**
- Uses docker-compose for coordinated building
- `--no-cache` ensures completely fresh builds
- Includes development configurations

```bash
make docker-dev-build
```

### Docker Hub Operations

#### `make docker-tag`
**Tag images for Docker Hub**
- Tags local images with Docker Hub repository names
- Prepares images for pushing to registry

```bash
make docker-tag
```

#### `make docker-push`
**Push images to Docker Hub**
- Uploads tagged images to Docker Hub
- Requires Docker Hub authentication

```bash
make docker-push
```

#### `make docker-build-push`
**Complete build and push workflow**
- Combines: `docker-build` → `docker-tag` → `docker-push`
- One-command CI/CD pipeline

```bash
make docker-build-push
```

#### `make docker-pull`
**Pull latest images from Docker Hub**
- Downloads latest versions of all images
- Updates local image cache

```bash
make docker-pull
```

### Container Management

#### `make docker-down` / `make docker-stop`
**Stop containers**
- Stops and removes containers
- Preserves volumes and networks
- Equivalent commands

```bash
make docker-down
# or
make docker-stop
```

#### `make docker-rm`
**Remove containers and networks**
- More thorough cleanup than `docker-down`
- Removes orphaned containers
- Preserves volumes

```bash
make docker-rm
```

#### `make docker-prune`
**⚠️ Nuclear cleanup - removes everything**
- Removes containers, networks, **and volumes**
- Runs Docker system prune
- **Deletes all data** - use with caution!

```bash
make docker-prune
```

### Debugging & Monitoring

#### `make docker-logs`
**View logs from all containers**
- Shows combined logs with following (`-f`)
- Color-coded by service

```bash
make docker-logs
```

#### Service-Specific Logs
**View logs from individual services**
```bash
make docker-logs-code      # Anomstack code service
make docker-logs-daemon    # Dagster daemon
make docker-logs-dashboard # Dashboard service
```

#### Shell Access
**Get shell access to running containers**
```bash
make docker-shell-code      # Shell into code container
make docker-shell-dagit     # Shell into webserver container
make docker-shell-dashboard # Shell into dashboard container
```

#### Service Restart
**Restart individual services**
```bash
make docker-restart-code      # Restart code service
make docker-restart-dashboard # Restart dashboard service
```

#### `make docker-clean`
**Clean unused Docker resources**
- Runs `docker system prune -f`
- Runs `docker volume prune -f`
- Frees disk space without removing data

```bash
make docker-clean
```

## Reset Operations

**🆕 NEW SECTION** - Comprehensive reset utilities for different cleanup levels.

All reset operations use the `scripts/utils/reset_docker.sh` script with safety checks and confirmations.

### `make reset-interactive`
**Interactive guided reset**
- Presents menu with clear options
- Shows current data usage
- Guides you through reset process
- **Recommended for most users**

```bash
make reset-interactive
```

### `make reset-gentle`
**Gentle reset (safest)**
- ✅ Preserves all data and volumes
- 🔄 Rebuilds containers with fresh images
- 🎯 Use when: You want fresh containers but keep data

```bash
make reset-gentle
```

### `make reset-medium`
**Medium reset (balanced)**
- ✅ Preserves Docker volumes and data files
- 🗑️ Removes containers and networks
- 🎯 Use when: Container issues but want to keep data

```bash
make reset-medium
```

### `make reset-nuclear`
**Nuclear reset (destructive)**
- ⚠️ **Removes ALL data** including volumes and local files
- 🗑️ Clears tmp/, storage/, history/, logs/
- 🎯 Use when: You want completely fresh start (like your 63GB cleanup case)

```bash
make reset-nuclear
```

### `make reset-full-nuclear`
**Full nuclear reset (maximum cleanup)**
- ⚠️ Everything from nuclear reset
- 🗑️ **Plus** complete Docker system cleanup
- 💾 Frees maximum possible disk space
- 🎯 Use when: You want absolute maximum cleanup

```bash
make reset-full-nuclear
```

## Dagster Storage Cleanup

**Purpose**: Manage Dagster storage accumulation to prevent disk space issues (like the 63GB+ buildup problem).

### `make dagster-cleanup-status`
**Show storage analysis and configuration status**
- 📊 Analyzes current tmp/ directory usage
- 🔢 Counts Dagster run directories  
- 💾 Reports storage sizes
- ✅ Checks if retention policies are configured
- 🔧 Verifies run monitoring settings

```bash
make dagster-cleanup-status
```

### `make dagster-cleanup-minimal`
**Safe cleanup - Remove old logs only**
- 🗑️ Removes compute logs older than 7 days
- ✅ Preserves all run metadata and artifacts
- 🛡️ Safe for production use
- 📅 **Recommended frequency**: Weekly

```bash
make dagster-cleanup-minimal
```

### `make dagster-cleanup-standard`
**Standard cleanup - Remove old runs**
- 🗑️ Removes run directories older than 30 days
- 📋 Cleans associated compute logs and artifacts
- 🐛 Keeps recent runs for debugging
- 📅 **Recommended frequency**: Monthly

```bash
make dagster-cleanup-standard
```

### `make dagster-cleanup-aggressive`
**Aggressive cleanup - Keep only recent data**
- 🗑️ Removes run directories older than 7 days
- 🔥 Aggressive log cleanup (3+ days old)
- ⏱️ Only keeps very recent data
- 🎯 **Use when**: Disk space is becoming an issue

```bash
make dagster-cleanup-aggressive
```

### `make dagster-cleanup-menu`
**Interactive cleanup menu**
- 🎛️ Interactive menu with all cleanup options
- 📊 Shows real-time storage analysis
- ☢️ Includes nuclear and CLI-based options
- 🎯 **Best for**: One-time cleanup or exploration

```bash
make dagster-cleanup-menu
```

**💡 Pro Tip**: Run `make dagster-cleanup-status` first to understand your current storage usage before choosing a cleanup level.

## Dashboard Operations

Targets for running the Anomstack dashboard independently.

### `make dashboard`
**Start dashboard locally with Python**
- Runs `python dashboard/app.py`
- Development server on default port
- Direct Python execution

```bash
make dashboard
```

### `make dashboard-uvicorn`
**Start dashboard with Uvicorn ASGI server**
- Production-ready ASGI server
- Runs on `0.0.0.0:5003` with auto-reload
- Better performance than direct Python

```bash
make dashboard-uvicorn
```

### Background Dashboard

#### `make dashboardd`
**Start dashboard as background daemon (Python)**
```bash
make dashboardd
```

#### `make dashboardd-uvicorn`
**Start dashboard as background daemon (Uvicorn)**
```bash
make dashboardd-uvicorn
```

#### `make kill-dashboardd`
**Kill running dashboard processes**
```bash
make kill-dashboardd
```

## Testing & Quality

Targets for code quality and testing.

### `make pre-commit`
**Run pre-commit hooks on all files**
- Runs linting, formatting, and checks
- Uses `.pre-commit-config.yaml` configuration
- Ensures code quality standards

```bash
make pre-commit
```

### `make tests`
**Run test suite**
- Executes pytest with verbose output
- Runs all tests in `tests/` directory

```bash
make tests
```

### `make coverage`
**Run tests with coverage report**
- Generates code coverage analysis
- Shows which code is tested
- Displays missing coverage areas

```bash
make coverage
```

## Documentation

**Purpose**: Manage the Docusaurus documentation site for Anomstack.

### `make docs-install`
**Install documentation dependencies**
- Runs `npm install` in the docs directory
- Required before first use or after dependency changes
- Sets up Docusaurus and all required packages

```bash
make docs-install
```

### `make docs` / `make docs-start`
**Start development server with live reload**
- Starts Docusaurus development server on `http://localhost:3000`
- Enables live editing with hot reload
- Perfect for writing and previewing documentation changes

```bash
make docs
# or
make docs-start
```

### `make docs-build`
**Build static documentation site**
- Creates production-ready static files
- Outputs to `docs/build/` directory
- Required before serving or deploying

```bash
make docs-build
```

### `make docs-serve`
**Serve built documentation locally**
- Serves the built static site locally
- Good for testing the production build
- Requires `make docs-build` to be run first

```bash
make docs-serve
```

### `make docs-clear`
**Clear documentation build cache**
- Clears Docusaurus build cache
- Useful when experiencing build issues
- Forces a fresh build on next command

```bash
make docs-clear
```

**💡 Typical workflow:**
1. `make docs-install` (first time only)
2. `make docs` (for development with live reload)
3. `make docs-build` (when ready to test production build)
4. `make docs-serve` (to test the built site)

## Dependencies

### `make requirements`
**Compile requirements file**
- Uses `pip-compile` to generate `requirements.txt`
- Based on `requirements.compile` source file
- Pins dependency versions for reproducibility

```bash
make requirements
```

### `make requirements-install`
**Install Python dependencies**
- Installs packages from `requirements.txt`
- Ensures consistent environment setup

```bash
make requirements-install
```

## Utilities

Miscellaneous utility targets for maintenance and examples.

### `make posthog-example`
**Run PostHog integration example**
- Tests PostHog credentials and connectivity
- Runs example ingest function
- Useful for validating PostHog setup

```bash
make posthog-example
```

### `make kill-long-runs`
**Kill long-running Dagster tasks**
- Identifies and kills tasks exceeding timeout
- Prevents runaway processes
- Uses `scripts/kill_long_running_tasks.py`

```bash
make kill-long-runs
```

### Fly.io Disk Space Management

#### `make fly-cleanup-preview`
**Preview disk cleanup on Fly instance (dry run)**
- Shows what files would be removed
- Safe way to check cleanup impact
- Requires `FLY_APP` environment variable

```bash
export FLY_APP=anomstack-demo
make fly-cleanup-preview
```

#### `make fly-cleanup`
**Clean up disk space on Fly instance**
- Removes old artifacts (6+ hours)
- Removes old logs (24+ hours)
- Cleans database and runs VACUUM
- Reports disk usage before/after

```bash
export FLY_APP=anomstack-demo
make fly-cleanup
```

#### `make fly-cleanup-aggressive`
**Emergency disk cleanup (aggressive mode)**
- Removes artifacts older than 1 hour
- Removes ALL log files
- Use only when disk is critically full
- More thorough than normal cleanup

```bash
export FLY_APP=anomstack-demo
make fly-cleanup-aggressive
```

### Legacy Targets

#### `make docker-dev-env`
**Legacy: Run Docker in development mode**
```bash
make docker-dev-env  # Use `make docker-dev` instead
```

## Quick Reference

### Most Common Workflows

**🚀 Quick Start (Development):**
```bash
make docker-dev
```

**🚀 Quick Start (Production):**
```bash
make docker
```

**🧹 Clean Restart:**
```bash
make reset-interactive  # Choose your reset level
```

**🔍 Debug Issues:**
```bash
make docker-logs                    # View all logs
make docker-shell-code             # Get shell access
make docker-restart-dashboard      # Restart specific service
```

**📊 Development Workflow:**
```bash
make dev                    # Setup environment
make pre-commit            # Check code quality
make tests                 # Run tests
make docker-dev            # Start development
```

**🚢 CI/CD Workflow:**
```bash
make docker-build-push     # Build and push to registry
make docker-pull           # Pull latest images
make docker                # Start with latest images
```

### Emergency Commands

**🆘 Something's broken:**
```bash
make reset-interactive     # Guided reset options
```

**💾 Free disk space:**
```bash
make reset-full-nuclear    # Maximum cleanup
```

**🔥 Kill everything:**
```bash
make kill-locald           # Kill local processes
make kill-dashboardd       # Kill dashboard processes
make kill-long-runs        # Kill long-running tasks
```

---

## Tips & Best Practices

1. **Start with `make reset-interactive`** - It provides guidance and shows data usage
2. **Use `make docker-smart`** - Intelligently handles image availability
3. **Check logs first** - `make docker-logs` often reveals the issue
4. **Use gentle resets** - Start with `reset-gentle` before more destructive options
5. **Regular cleanup** - `make docker-clean` frees space without losing data
6. **Development cycle** - Use `make docker-dev` for active development

## Getting Help

- Run `make reset-interactive` for guided Docker operations
- Check `scripts/utils/README.md` for detailed reset documentation
- Use `make docker-logs` to diagnose container issues
- Most targets have descriptive comments in the Makefile itself
