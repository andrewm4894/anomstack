"""
Anomstack Dashboard

This is a dashboard for the Anomstack project. It is a web application that allows you to view and analyze metrics from the Anomstack project.

It is built with FastHTML and MonsterUI.

"""

import logging
import os
from dotenv import load_dotenv
from fasthtml.common import *
from monsterui.all import *
from fasthtml.svg import *

from dashboard.constants import *
from dashboard.state import AppState
from dashboard.data import get_data

# load the environment variables
load_dotenv(override=True)

log = logging.getLogger("anomstack")

app, rt = fast_app(
    hdrs=(
        Theme.blue.headers(),
        Script(src="https://cdn.plot.ly/plotly-2.32.0.min.js"),
        Link(
            rel="icon",
            type="image/svg+xml",
            href=
            "data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIyNCIgaGVpZ2h0PSIyNCIgdmlld0JveD0iMCAwIDI0IDI0IiBmaWxsPSJub25lIiBzdHJva2U9ImN1cnJlbnRDb2xvciIgc3Ryb2tlLXdpZHRoPSIyIiBzdHJva2UtbGluZWNhcD0icm91bmQiIHN0cm9rZS1saW5lam9pbj0icm91bmQiIGNsYXNzPSJsdWNpZGUgbHVjaWRlLWNoYXJ0LWxpbmUiPjxwYXRoIGQ9Ik0zIDN2MTZhMiAyIDAgMCAwIDIgMmgxNiIvPjxwYXRoIGQ9Im0xOSA5LTUgNS00LTQtMyAzIi8+PC9zdmc+",
        ),
        Link(rel="stylesheet", href="dashboard/static/styles.css"),
    ),
    debug=True,
    log=log,
)

# Set the app state
app.state = AppState()

# Import routes after app is defined
from dashboard.routes import *

if __name__ == "__main__":
    serve(app, port=int(os.getenv("ANOMSTACK_DASHBOARD_PORT", 5001)))
