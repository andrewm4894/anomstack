"""
Version information for Anomstack.

Provides build/deployment version tracking.
"""

import os
import subprocess
from datetime import datetime
from pathlib import Path


def get_git_commit_hash() -> str:
    """Get the current git commit hash."""
    try:
        # Try to get commit hash from git
        result = subprocess.run(
            ["git", "rev-parse", "--short", "HEAD"],
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent.parent,
        )
        if result.returncode == 0:
            return result.stdout.strip()
    except Exception:
        pass
    
    # Fallback to environment variable if set (useful for Docker builds)
    return os.getenv("ANOMSTACK_BUILD_HASH", "unknown")


def get_build_time() -> str:
    """Get build timestamp."""
    # Check if build time is set in environment (Docker builds)
    build_time = os.getenv("ANOMSTACK_BUILD_TIME")
    if build_time:
        return build_time
    
    # Fallback to current time
    return datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")


def get_version_info() -> dict:
    """Get complete version information."""
    return {
        "commit_hash": get_git_commit_hash(),
        "build_time": get_build_time(),
        "architecture": "3-container (gRPC-free)",
        "python_module_loading": True,
    }


def get_version_string() -> str:
    """Get a simple version string for display."""
    info = get_version_info()
    return f"{info['commit_hash']} ({info['build_time']})"