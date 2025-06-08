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
load_dotenv(override=True)

log = logging.getLogger("anomstack_dashboard")

# Get PostHog API key from environment
posthog_api_key = os.getenv("POSTHOG_API_KEY")
if posthog_api_key:
    from dashboard.constants import POSTHOG_SCRIPT

    POSTHOG_SCRIPT = POSTHOG_SCRIPT.replace(
        "window.POSTHOG_API_KEY || ''", f"'{posthog_api_key}'"
    )

# Define the app
app, rt = fast_app(
    hdrs=(
        Theme.blue.headers(),
        Script(src="https://cdn.plot.ly/plotly-2.32.0.min.js"),
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


# Import routes after app is defined
from dashboard.routes import *


if __name__ == "__main__":
    import logging
    import sys

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )
    logger = logging.getLogger(__name__)

    try:
        # Test critical imports first
        from dashboard.routes import *

        logger.info("Routes imported successfully")
        logger.info("Starting Anomstack dashboard on port 8080...")
        logger.info(f"Debug mode: {os.getenv('ANOMSTACK_DASHBOARD_DEBUG', 'false')}")

        # Add startup timeout and more detailed error handling
        serve(app, host="0.0.0.0", port=8080, workers=1)

    except ImportError as e:
        logger.error(f"Import error during startup: {e}")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Failed to start dashboard: {e}")
        logger.exception("Full traceback:")
        sys.exit(1)
