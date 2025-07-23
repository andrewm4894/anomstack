#!/bin/bash

# Anomstack Startup Script for Fly.io with improved gRPC connectivity
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

# Function to check if code server is healthy
check_code_server_health() {
    local retries=0
    local max_retries=30
    while [ $retries -lt $max_retries ]; do
        if dagster api grpc-health-check -p 4000 >/dev/null 2>&1; then
            echo "✅ Code server is healthy"
            return 0
        fi
        echo "⏳ Waiting for code server to be ready... (attempt $((retries + 1))/$max_retries)"
        sleep 2
        retries=$((retries + 1))
    done
    echo "❌ Code server failed to start after $max_retries attempts"
    return 1
}

# Function to start process with retry logic
start_process_with_retry() {
    local name=$1
    local command=$2
    local logfile=$3
    local max_retries=3
    local retry=0
    
    while [ $retry -lt $max_retries ]; do
        echo "🔧 Starting $name (attempt $((retry + 1))/$max_retries)..."
        nohup $command > $logfile 2>&1 &
        local pid=$!
        echo "$name PID: $pid"
        
        # Give it a moment to crash if it's going to
        sleep 3
        
        if kill -0 $pid 2>/dev/null; then
            echo "✅ $name started successfully"
            echo $pid
            return 0
        else
            echo "⚠️ $name failed to start, retrying..."
            retry=$((retry + 1))
        fi
    done
    
    echo "❌ Failed to start $name after $max_retries attempts"
    return 1
}

echo "🔧 Starting code server..."
CODE_SERVER_PID=$(start_process_with_retry "Code Server" "dagster code-server start -h 0.0.0.0 -p 4000 -f anomstack/main.py" "/tmp/code_server.log")
if [ $? -ne 0 ]; then
    echo "❌ Failed to start code server, exiting"
    exit 1
fi

echo "⏳ Waiting for code server to be ready..."
if ! check_code_server_health; then
    echo "❌ Code server health check failed, exiting"
    exit 1
fi

echo "🌐 Starting webserver..."
WEBSERVER_PID=$(start_process_with_retry "Webserver" "dagster-webserver -h 0.0.0.0 -p 3000 -w /opt/dagster/dagster_home/workspace.yaml" "/tmp/webserver.log")
if [ $? -ne 0 ]; then
    echo "❌ Failed to start webserver, exiting"
    exit 1
fi

echo "⚙️ Starting daemon..."
DAEMON_PID=$(start_process_with_retry "Daemon" "dagster-daemon run -w /opt/dagster/dagster_home/workspace.yaml" "/tmp/daemon.log")
if [ $? -ne 0 ]; then
    echo "❌ Failed to start daemon, exiting"
    exit 1
fi

echo "📊 Starting dashboard..."
DASHBOARD_PID=$(start_process_with_retry "Dashboard" "uvicorn dashboard.app:app --host 0.0.0.0 --port 8080" "/tmp/dashboard.log")
if [ $? -ne 0 ]; then
    echo "❌ Failed to start dashboard, exiting"
    exit 1
fi

echo "🌐 Starting nginx reverse proxy..."
nginx -t && nginx -g "daemon off;" &
NGINX_PID=$!

echo "✅ All services started successfully!"
echo "Code Server PID: $CODE_SERVER_PID"
echo "Webserver PID: $WEBSERVER_PID" 
echo "Daemon PID: $DAEMON_PID"
echo "Dashboard PID: $DASHBOARD_PID"
echo "Nginx PID: $NGINX_PID"

# Function to handle shutdown gracefully
cleanup() {
    echo "🛑 Shutting down services..."
    kill $NGINX_PID $DASHBOARD_PID $DAEMON_PID $WEBSERVER_PID $CODE_SERVER_PID 2>/dev/null || true
    wait
    exit 0
}

# Trap signals for graceful shutdown
trap cleanup SIGTERM SIGINT

# Monitor processes and restart if they crash
while true; do
    # Check if critical processes are still running
    if ! kill -0 $CODE_SERVER_PID 2>/dev/null; then
        echo "❌ Code server crashed, restarting..."
        CODE_SERVER_PID=$(start_process_with_retry "Code Server" "dagster code-server start -h 0.0.0.0 -p 4000 -f anomstack/main.py" "/tmp/code_server.log")
    fi
    
    if ! kill -0 $WEBSERVER_PID 2>/dev/null; then
        echo "❌ Webserver crashed, restarting..."
        WEBSERVER_PID=$(start_process_with_retry "Webserver" "dagster-webserver -h 0.0.0.0 -p 3000 -w /opt/dagster/dagster_home/workspace.yaml" "/tmp/webserver.log")
    fi
    
    if ! kill -0 $DAEMON_PID 2>/dev/null; then
        echo "❌ Daemon crashed, restarting..."
        DAEMON_PID=$(start_process_with_retry "Daemon" "dagster-daemon run -w /opt/dagster/dagster_home/workspace.yaml" "/tmp/daemon.log")
    fi
    
    if ! kill -0 $DASHBOARD_PID 2>/dev/null; then
        echo "❌ Dashboard crashed, restarting..."
        DASHBOARD_PID=$(start_process_with_retry "Dashboard" "uvicorn dashboard.app:app --host 0.0.0.0 --port 8080" "/tmp/dashboard.log")
    fi
    
    sleep 30
done
