"""
dashboard/app.py

Anomstack Dashboard

This is a dashboard for the Anomstack project. It is a web application that allows you to view and analyze metrics from the Anomstack project.

It is built with FastHTML and MonsterUI.

"""

import logging
import os
from dotenv import load_dotenv
from fasthtml.common import fast_app, Script, Link, serve
from monsterui.all import *

from dashboard.state import AppState
from dashboard.constants import POSTHOG_SCRIPT

# load the environment variables
try:
    load_dotenv(override=True)
except Exception as e:
    print(f"Warning: Could not load .env file: {e}")

log = logging.getLogger("anomstack_dashboard")

# Get PostHog API key from environment
posthog_api_key = os.getenv('POSTHOG_API_KEY')
if posthog_api_key:
    from dashboard.constants import POSTHOG_SCRIPT
    POSTHOG_SCRIPT = POSTHOG_SCRIPT.replace("window.POSTHOG_API_KEY || ''",
                                            f"'{posthog_api_key}'")

# Define the app
app, rt = fast_app(
    hdrs=(
        Theme.blue.headers(),
        Script(src="https://cdn.plot.ly/plotly-2.32.0.min.js"),
        Script(POSTHOG_SCRIPT) if posthog_api_key else None,
        Link(
            rel="icon",
            type="image/svg+xml",
            href=
            "data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIyNCIgaGVpZ2h0PSIyNCIgdmlld0JveD0iMCAwIDI0IDI0IiBmaWxsPSJub25lIiBzdHJva2U9ImN1cnJlbnRDb2xvciIgc3Ryb2tlLXdpZHRoPSIyIiBzdHJva2UtbGluZWNhcD0icm91bmQiIHN0cm9rZS1saW5lam9pbj0icm91bmQiIGNsYXNzPSJsdWNpZGUgbHVjaWRlLWNoYXJ0LWxpbmUiPjxwYXRoIGQ9Ik0zIDN2MTZhMiAyIDAgMCAwIDIgMmgxNiIvPjxwYXRoIGQ9Im0xOSA5LTUgNS00LTQtMyAzIi8+PC9zdmc+",
        ),
        Link(rel="stylesheet", href="dashboard/static/styles.css"),
    ),
    debug=os.getenv("ANOMSTACK_DASHBOARD_DEBUG", "false").lower() == "true",
    log=log,
)

# Set the app state
app.state = AppState()

# Add health check endpoints
@rt("/")
def health_check():
    return {"status": "healthy", "message": "Anomstack dashboard is running"}

@rt("/health")
def health():
    return {"status": "ok"}

# Import routes after app is defined
from dashboard.routes import *

if __name__ == "__main__":
    print("Starting Anomstack dashboard on port 80...")
    try:
        serve(app, host="0.0.0.0", port=80)
    except Exception as e:
        print(f"Failed to start dashboard: {e}")
        raise
