"""
dashboard/components/header.py

Header components.

This module contains the components for the dashboard header.

"""

from fasthtml.common import Div, H2, P, A
from monsterui.all import DivLAligned, TextPresets, UkIcon


def create_header() -> Div:
    """Create the dashboard header.

    Returns:
        Div: The dashboard header.
    """
    return DivLAligned(
        H2(
            "Anomstack",
            P(
                "Painless open source anomaly detection for your metrics 📈📉🚀",
                cls=TextPresets.muted_sm,
            ),
            cls="mb-2",
        ),
        A(
            DivLAligned(UkIcon("github")),
            href="https://github.com/andrewm4894/anomstack",
            target="_blank",
            cls="uk-button uk-button-secondary",
            uk_tooltip="View on GitHub",
        ),
        style="justify-content: space-between;",
        cls="mb-6",
    ) 