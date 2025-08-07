"""
dashboard/app.py

Anomstack Dashboard

This is a dashboard for the Anomstack project. It is a web application
that allows you to view and analyze metrics from the Anomstack project.

It is built with FastHTML and MonsterUI.

"""

import logging
import os

from dotenv import load_dotenv
from fasthtml.common import Link, Script, Style, fast_app, serve
from monsterui.all import *

from dashboard.constants import POSTHOG_SCRIPT
from dashboard.state import AppState

# load the environment variables with custom env file support
def load_env_with_custom_path():
    """Load environment variables from custom path or default .env file."""
    from pathlib import Path
    
    env_file_path = os.getenv("ANOMSTACK_ENV_FILE_PATH")
    
    if env_file_path:
        env_path = Path(env_file_path)
        if env_path.exists():
            print(f"🎯 Using custom environment file: {env_file_path}")
            load_dotenv(env_path, override=True)
            print("✅ Custom environment file loaded")
        else:
            print(f"❌ Custom environment file not found: {env_file_path}")
            print("📄 Falling back to default .env file")
            load_dotenv(override=True)
    else:
        # Standard .env loading
        load_dotenv(override=True)

load_env_with_custom_path()

log = logging.getLogger("anomstack_dashboard")

# Get PostHog API key from environment
posthog_api_key = os.getenv("POSTHOG_API_KEY")
if posthog_api_key:
    from dashboard.constants import POSTHOG_SCRIPT

    POSTHOG_SCRIPT = POSTHOG_SCRIPT.replace("window.POSTHOG_API_KEY || ''", f"'{posthog_api_key}'")

# Define the app
app, rt = fast_app(
    hdrs=(
        Theme.blue.headers(),
        Script(src="https://cdn.jsdelivr.net/npm/apexcharts@latest"),
        Style("""
uk-chart {
    display: block !important;
    width: 100% !important;
    min-height: 300px !important;
    height: auto !important;
}
uk-chart .apexcharts-canvas {
    width: 100% !important;
    height: 100% !important;
}
        """),
        Script("""
function initializeCharts() {
    const elements = document.querySelectorAll('uk-chart:not([data-chart-initialized])');
    
    elements.forEach(function(element) {
        const script = element.querySelector('script[type="application/json"]');
        if (script) {
            try {
                const config = JSON.parse(script.textContent);
                
                // Add percentage formatting to score axis (second y-axis)
                if (config.yaxis && config.yaxis[1]) {
                    config.yaxis[1].labels = config.yaxis[1].labels || {};
                    config.yaxis[1].labels.formatter = function(val) {
                        return Math.round(val * 100) + '%';
                    };
                }
                
                // Ensure chart has dimensions
                element.style.minHeight = '300px';
                element.style.width = '100%';
                element.style.display = 'block';
                
                const chart = new ApexCharts(element, config);
                chart.render().then(() => {
                    element.setAttribute('data-chart-initialized', 'true');
                });
            } catch (e) {
                console.error('Error initializing chart:', e, element);
            }
        }
    });
}

// Wait for both DOM and ApexCharts to be ready
document.addEventListener('DOMContentLoaded', function() {
    // Check if ApexCharts is loaded
    if (typeof ApexCharts !== 'undefined') {
        initializeCharts();
    } else {
        // Wait a bit more for ApexCharts to load
        setTimeout(() => {
            if (typeof ApexCharts !== 'undefined') {
                initializeCharts();
            } else {
                console.error('ApexCharts library not loaded');
            }
        }, 1000);
    }
});

// Re-initialize charts after HTMX requests
document.addEventListener('htmx:afterSwap', initializeCharts);
document.addEventListener('htmx:afterSettle', initializeCharts);
        """),
        Script(POSTHOG_SCRIPT) if posthog_api_key else None,
        Link(
            rel="icon",
            type="image/svg+xml",
            href="data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIyNCIgaGVpZ2h0PSIyNCIgdmlld0JveD0iMCAwIDI0IDI0IiBmaWxsPSJub25lIiBzdHJva2U9ImN1cnJlbnRDb2xvciIgc3Ryb2tlLXdpZHRoPSIyIiBzdHJva2UtbGluZWNhcD0icm91bmQiIHN0cm9rZS1saW5lam9pbj0icm91bmQiIGNsYXNzPSJsdWNpZGUgbHVjaWRlLWNoYXJ0LWxpbmUiPjxwYXRoIGQ9Ik0zIDN2MTZhMiAyIDAgMCAwIDIgMmgxNiIvPjxwYXRoIGQ9Im0xOSA5LTUgNS00LTQtMyAzIi8+PC9zdmc+",
        ),
        Link(rel="stylesheet", href="dashboard/static/styles.css"),
    ),
    debug=os.getenv("ANOMSTACK_DASHBOARD_DEBUG", "false").lower() == "true",
    log=log,
)

# Set the app state
app.state = AppState()


# Add health check endpoint for Cloud Run
@rt("/health")
def health_check():
    """Quick health check endpoint for deployment."""
    return {"status": "ok", "service": "anomstack-dashboard"}


# Add lightweight root handler for deployment health checks
@rt("/")
def root_health_check(request):
    """Handle root path health checks from Cloud Run."""
    user_agent = request.headers.get("User-Agent", "")
    # Check if this is a health check request
    if (
        user_agent.startswith("GoogleHC")
        or user_agent.startswith("kube-probe")
        or user_agent.startswith("Google-Cloud-Tasks")
    ):
        return {"status": "healthy", "service": "anomstack-dashboard"}
    # Otherwise, let the regular index route handle it
    from dashboard.routes.index import index

    return index(request)


# Import routes after app is defined
from dashboard.routes import *

if __name__ == "__main__":
    try:
        print("Starting Anomstack dashboard on port 8080")
        serve(app, host="0.0.0.0", port=8080)
    except Exception as e:
        print(f"Failed to start dashboard: {e}")
        raise
