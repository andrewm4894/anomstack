#!/bin/bash

# Debug script for Dagster gRPC connectivity issues in Fly.io deployment
#
# NOTE: By default, Anomstack uses direct Python module loading (no gRPC server).
# This script is useful if you have configured optional gRPC code servers.
# See ARCHITECTURE.md for information about enabling gRPC setup.
#
# Usage: Run this script inside your deployment container to diagnose issues
# with gRPC code servers (if you have enabled them).

echo "🔍 Dagster gRPC Connectivity Debugger"
echo "======================================="
echo "ℹ️  This script checks for gRPC code servers (optional configuration)"
echo "ℹ️  Default Anomstack setup uses direct Python module loading (no gRPC)"
echo ""

# Check environment
echo "📋 Environment Information:"
echo "DAGSTER_HOME: ${DAGSTER_HOME:-not set}"
echo "DAGSTER_CODE_SERVER_HOST: ${DAGSTER_CODE_SERVER_HOST:-not set}"
echo "PYTHONPATH: ${PYTHONPATH:-not set}"
echo ""

# Check if processes are running
echo "🔄 Process Status:"
echo "Code server (port 4000):"
if pgrep -f "dagster code-server" > /dev/null; then
    echo "  ✅ Code server process is running (PID: $(pgrep -f 'dagster code-server'))"
else
    echo "  ❌ Code server process is not running"
fi

echo "Webserver (port 3000):"
if pgrep -f "dagster-webserver" > /dev/null; then
    echo "  ✅ Webserver process is running (PID: $(pgrep -f 'dagster-webserver'))"
else
    echo "  ❌ Webserver process is not running"
fi

echo "Daemon:"
if pgrep -f "dagster-daemon" > /dev/null; then
    echo "  ✅ Daemon process is running (PID: $(pgrep -f 'dagster-daemon'))"
else
    echo "  ❌ Daemon process is not running"
fi
echo ""

# Check ports
echo "🌐 Port Status:"
echo "Port 4000 (code server):"
if netstat -tuln 2>/dev/null | grep ":4000" > /dev/null; then
    echo "  ✅ Port 4000 is listening"
    netstat -tuln | grep ":4000"
else
    echo "  ❌ Port 4000 is not listening"
fi

echo "Port 3000 (webserver):"
if netstat -tuln 2>/dev/null | grep ":3000" > /dev/null; then
    echo "  ✅ Port 3000 is listening"
    netstat -tuln | grep ":3000"
else
    echo "  ❌ Port 3000 is not listening"
fi
echo ""

# Test gRPC health check
echo "💓 gRPC Health Check:"
if dagster api grpc-health-check -p 4000 2>/dev/null; then
    echo "  ✅ gRPC health check passed"
else
    echo "  ❌ gRPC health check failed"
    echo "  Detailed error:"
    dagster api grpc-health-check -p 4000 2>&1 | head -5
fi
echo ""

# Test workspace loading
echo "📚 Workspace Configuration:"
if [ -f "$DAGSTER_HOME/workspace.yaml" ]; then
    echo "  ✅ Workspace file exists: $DAGSTER_HOME/workspace.yaml"
    echo "  Content preview:"
    head -15 "$DAGSTER_HOME/workspace.yaml" | sed 's/^/    /'
else
    echo "  ❌ Workspace file not found: $DAGSTER_HOME/workspace.yaml"
fi
echo ""

# Check log files for errors
echo "📄 Recent Log Entries:"
for logfile in /tmp/code_server.log /tmp/webserver.log /tmp/daemon.log; do
    if [ -f "$logfile" ]; then
        echo "  📄 $logfile (last 10 lines):"
        tail -10 "$logfile" 2>/dev/null | sed 's/^/    /' || echo "    Could not read log file"
        echo ""
    fi
done

# Test direct connection
echo "🔌 Direct Connection Test:"
if command -v telnet >/dev/null 2>&1; then
    echo "  Testing localhost:4000..."
    timeout 5 telnet localhost 4000 2>/dev/null && echo "  ✅ Connection successful" || echo "  ❌ Connection failed"
elif command -v nc >/dev/null 2>&1; then
    echo "  Testing localhost:4000..."
    timeout 5 nc -z localhost 4000 2>/dev/null && echo "  ✅ Connection successful" || echo "  ❌ Connection failed"
else
    echo "  ⚠️ No telnet or nc available for connection testing"
fi
echo ""

# System resources
echo "💾 System Resources:"
echo "  Memory usage:"
free -h 2>/dev/null | head -2 | sed 's/^/    /' || echo "    Memory info not available"
echo "  Disk usage for /data:"
df -h /data 2>/dev/null | sed 's/^/    /' || echo "    Disk info not available"
echo ""

echo "🏁 Debug complete!"
echo ""
echo "💡 Common fixes:"
echo "  1. Restart the deployment: fly deploy"
echo "  2. Check resource limits in fly.toml"
echo "  3. Review logs: fly logs"
echo "  4. Scale up if memory/CPU constrained: fly scale memory 8192"
