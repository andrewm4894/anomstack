# Devcontainer Configurations

[![Open Dev Codespace](https://img.shields.io/badge/Codespace-Dev-blue?logo=github)](https://github.com/codespaces/new/andrewm4894/anomstack?devcontainer_path=.devcontainer/devcontainer.dev.json)

This directory contains multiple devcontainer configurations for different use cases.

## 📋 Available Configurations

### 1. `devcontainer.json` - **User/Demo** (Default)
- **Purpose**: Quick start for new users or demos
- **Docker Strategy**: Pulls pre-built images from Docker Hub
- **Speed**: ⚡ Fast startup (30-60 seconds)
- **Use Cases**:
  - New users trying out anomstack
  - Demos and presentations
  - Quick testing without development setup

### 2. `devcontainer.dev.json` - **Development**
- **Purpose**: Full development environment
- **Docker Strategy**: Builds images locally with source code changes
- **Speed**: 🐌 Slower startup (3-5 minutes)
- **Use Cases**:
  - Active development on anomstack
  - Testing code changes
  - Contributing to the project

## 🚀 How to Use

### GitHub Codespaces

1. **Default (User/Demo)**: Just click "Create codespace" - uses `devcontainer.json`
2. **Development**: Use the **Dev Codespace** link above or when creating a codespace click "..." → "Configure dev container" → select `devcontainer.dev.json`

### VS Code Dev Containers

1. **Default**: Open folder in VS Code → "Reopen in Container"
2. **Development**:
   - Open Command Palette (`Ctrl+Shift+P`)
   - "Dev Containers: Reopen in Container"
   - Select `devcontainer.dev.json`

### Manual Selection

You can also rename the files to switch defaults:
```bash
# Switch to development as default
mv devcontainer.json devcontainer.user.json
mv devcontainer.dev.json devcontainer.json
```

## 🏗️ What Each Configuration Does

### Both Configurations
- Set up VS Code extensions for Python, Docker, and development
- Forward ports: 3000 (Dagster), 5001 (Dashboard), 5432 (PostgreSQL)
- Run initialization and post-create scripts
- Enable Docker-in-Docker support

### Key Differences
| Feature | User/Demo | Development |
|---------|-----------|-------------|
| Docker Images | Pull from Hub | Build locally |
| Startup Time | ~60 seconds | ~5 minutes |
| Code Changes | View only | Full development |
| Extensions | Basic set | Extended dev tools |

## 🎯 Recommendations

- **First time users**: Use default `devcontainer.json`
- **Regular development**: Use `devcontainer.dev.json`
- **Demos/presentations**: Use default `devcontainer.json`
- **Contributing**: Use `devcontainer.dev.json`

## 🔧 Services Available

Both configurations provide:
- **Dagster Webserver**: [http://localhost:3000](http://localhost:3000)
- **Anomstack Dashboard**: [http://localhost:5001](http://localhost:5001)
- **PostgreSQL Database**: `localhost:5432`

## 📚 Documentation

For more information, see the main [README.md](../README.md) and [DOCKER.md](../DOCKER.md) files.
