"""
Anomstack Dashboard

This is a dashboard for the Anomstack project. It is a web application that allows you to view and analyze metrics from the Anomstack project.

It is built with FastHTML and MonsterUI.

"""

import logging

from fasthtml.common import *
from monsterui.all import *
from fasthtml.svg import *

from routes import *
from components import *
from constants import *
from state import AppState


log = logging.getLogger("anomstack")


app, rt = fast_app(
    hdrs=(
        Theme.blue.headers(),
        Script(src="https://cdn.plot.ly/plotly-2.32.0.min.js"),
        Link(
            rel="icon",
            type="image/svg+xml",
            href="data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIyNCIgaGVpZ2h0PSIyNCIgdmlld0JveD0iMCAwIDI0IDI0IiBmaWxsPSJub25lIiBzdHJva2U9ImN1cnJlbnRDb2xvciIgc3Ryb2tlLXdpZHRoPSIyIiBzdHJva2UtbGluZWNhcD0icm91bmQiIHN0cm9rZS1saW5lam9pbj0icm91bmQiIGNsYXNzPSJsdWNpZGUgbHVjaWRlLWNoYXJ0LWxpbmUiPjxwYXRoIGQ9Ik0zIDN2MTZhMiAyIDAgMCAwIDIgMmgxNiIvPjxwYXRoIGQ9Im0xOSA5LTUgNS00LTQtMyAzIi8+PC9zdmc+",
        ),
        Style(
            """
            /* Light mode defaults */
            body {
                background-color: #ffffff;
                color: #1a1a1a;
                transition: all 0.3s ease;
            }
            
            .loading-indicator {
                display: none;
                position: fixed;
                top: 1rem;
                right: 1rem;
                z-index: 1000;
            }
            .loading-indicator .htmx-indicator {
                padding: 0.5rem 1rem;
                background: #fff;
                border-radius: 4px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            }
            .loading-indicator .htmx-indicator.htmx-request {
                display: inline-block;
            }
            .top-nav {
                border-bottom: 1px solid #e5e7eb;
                background: #f8fafc;
            }
            .top-nav li {
                margin: 0;
            }
            .top-nav li a {
                font-weight: 500;
                color: #4b5563;
                transition: all 0.2s;
            }
            .top-nav li a:hover {
                color: #1e40af;
                background: #f1f5f9;
            }
            .top-nav li.uk-active a {
                color: #1e40af;
                border-bottom: 2px solid #1e40af;
            }
            
            /* Dark mode styles */
            body.dark-mode {
                background-color: #1a1a1a;
                color: #e5e7eb;
            }
            
            body.dark-mode .uk-card {
                background-color: #262626;
                border-color: #404040;
                color: #e5e7eb;
            }
            
            body.dark-mode .uk-card-header {
                border-color: #404040;
            }
            
            body.dark-mode .top-nav {
                background: #262626;
                border-color: #404040;
            }
            
            body.dark-mode .top-nav li a {
                color: #e5e7eb;
            }
            
            body.dark-mode .top-nav li a:hover {
                color: #60a5fa;
                background: #333333;
            }
            
            body.dark-mode .top-nav li.uk-active a {
                color: #60a5fa;
                border-color: #60a5fa;
            }
            
            body.dark-mode .uk-input,
            body.dark-mode .uk-select,
            body.dark-mode .uk-textarea,
            body.dark-mode .uk-button-secondary {
                background-color: #333333;
                border-color: #404040;
                color: #e5e7eb;
            }
            
            body.dark-mode .uk-dropdown {
                background-color: #262626;
                border-color: #404040;
                color: #e5e7eb;
            }
            
            body.dark-mode .uk-dropdown li a {
                color: #e5e7eb;
            }
            
            body.dark-mode .uk-dropdown li a:hover {
                background-color: #333333;
            }
            
            body.dark-mode .loading-indicator .htmx-indicator {
                background: #262626;
                color: #e5e7eb;
                box-shadow: 0 2px 4px rgba(255,255,255,0.1);
            }
            
            /* Ensure text colors are readable in dark mode */
            body.dark-mode h1,
            body.dark-mode h2,
            body.dark-mode h3,
            body.dark-mode h4,
            body.dark-mode h5,
            body.dark-mode h6,
            body.dark-mode p {
                color: #e5e7eb;
            }
            
            body.dark-mode .text-muted-foreground,
            body.dark-mode .uk-text-muted {
                color: #9ca3af;
            }
            
            /* Update dark mode button styles */
            body.dark-mode .uk-button-default,
            body.dark-mode .uk-button-secondary {
                background-color: #1f1f1f;  /* Darker background */
                color: #e5e7eb;
                border-color: #2d2d2d;  /* Slightly lighter border */
            }
            
            body.dark-mode .uk-button-default:hover,
            body.dark-mode .uk-button-secondary:hover {
                background-color: #2d2d2d;  /* Darker hover state */
                color: #ffffff;
                border-color: #404040;
            }
            
            body.dark-mode .uk-button-primary {
                background-color: #0f2d66;  /* Darker blue */
                color: #ffffff;
                border: none;
            }
            
            body.dark-mode .uk-button-primary:hover {
                background-color: #1a3f80;  /* Slightly lighter on hover */
            }
            
            /* Switch styles */
            .uk-toggle-switch {
                appearance: none;
                position: relative;
                width: 32px;  /* Reduced from 40px */
                height: 18px; /* Reduced from 24px */
                border-radius: 9px;  /* Reduced from 12px */
                background-color: #e5e7eb;
                cursor: pointer;
                transition: all 0.3s ease;
            }

            .uk-toggle-switch:checked {
                background-color: #1e40af;
            }

            .uk-toggle-switch::before {
                content: '';
                position: absolute;
                left: 2px;
                top: 2px;
                width: 14px;  /* Reduced from 20px */
                height: 14px; /* Reduced from 20px */
                border-radius: 50%;
                background-color: white;
                transition: transform 0.3s ease;
            }

            .uk-toggle-switch:checked::before {
                transform: translateX(14px); /* Reduced from 16px */
            }

            /* Dark mode switch styles */
            body.dark-mode .uk-toggle-switch {
                background-color: #4b5563;
            }

            body.dark-mode .uk-toggle-switch:checked {
                background-color: #60a5fa;
            }

            body.dark-mode .uk-toggle-switch::before {
                background-color: #e5e7eb;
            }
        """
        ),
    ),
    debug=True,
    log=log,
)


setup_toasts(app, duration=3)

app.state = AppState()

serve(host="localhost", port=5003)
