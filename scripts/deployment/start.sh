#!/bin/bash

# Anomstack Startup Script for Fly.io
set -e

echo "🚀 Starting Anomstack services..."

# Set environment variables
export DAGSTER_HOME="/opt/dagster/dagster_home"
export PYTHONPATH="/opt/dagster/app"

# Change to the app directory
cd /opt/dagster/app

echo "📁 Checking files..."
ls -la /opt/dagster/dagster_home/

# Setup nginx authentication from environment variables
echo "🔐 Setting up authentication..."
ADMIN_USERNAME="${ANOMSTACK_ADMIN_USERNAME:-admin}"
ADMIN_PASSWORD="${ANOMSTACK_ADMIN_PASSWORD:-anomstack2024}"

# Create htpasswd file with environment variables
htpasswd -bc /etc/nginx/.htpasswd "$ADMIN_USERNAME" "$ADMIN_PASSWORD"
echo "✅ Authentication configured for user: $ADMIN_USERNAME"

echo "🔧 Starting code server..."
nohup dagster code-server start -h 0.0.0.0 -p 4000 -f anomstack/main.py > /tmp/code_server.log 2>&1 &
CODE_SERVER_PID=$!

echo "⏳ Waiting for code server to start..."
sleep 10

echo "🌐 Starting webserver..."
nohup dagster-webserver -h 0.0.0.0 -p 3000 -w /opt/dagster/dagster_home/workspace.yaml > /tmp/webserver.log 2>&1 &
WEBSERVER_PID=$!

echo "⚙️ Starting daemon..."
nohup dagster-daemon run -w /opt/dagster/dagster_home/workspace.yaml > /tmp/daemon.log 2>&1 &
DAEMON_PID=$!

echo "📊 Starting dashboard..."
nohup uvicorn dashboard.app:app --host 0.0.0.0 --port 8080 > /tmp/dashboard.log 2>&1 &
DASHBOARD_PID=$!

echo "🌐 Starting nginx reverse proxy..."
nginx -t && nginx -g "daemon off;" > /tmp/nginx.log 2>&1 &
NGINX_PID=$!

echo "✅ All services started!"
echo "Code Server PID: $CODE_SERVER_PID"
echo "Webserver PID: $WEBSERVER_PID"
echo "Daemon PID: $DAEMON_PID"
echo "Dashboard PID: $DASHBOARD_PID"
echo "Nginx PID: $NGINX_PID"

# Keep the script running
wait
