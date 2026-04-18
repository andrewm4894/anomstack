"""
dashboard/components/batch.py

Batch-related components.

This module contains the components for the batch view.

"""

from __future__ import annotations

from fasthtml.common import A, Div, Li, P
from monsterui.all import (
    Button,
    ButtonT,
    Card,
    CodeSpan,
    DividerLine,
    DivLAligned,
    DropDownNavContainer,
    H3,
    NavHeaderLi,
    Subtitle,
    TextPresets,
    UkIcon,
)

from dashboard.app import app
from dashboard.presentation import format_batch_name, format_metric_count


def create_batches_dropdown(batch_name: str) -> DropDownNavContainer:
    """Create the metric batches dropdown menu.

    Args:
        batch_name (str): The name of the batch to highlight.

    Returns:
        DropDownNavContainer: The dropdown menu.
    """
    return DropDownNavContainer(
        NavHeaderLi("metric batches"),
        *[
            Li(
                A(
                    format_batch_name(name),
                    hx_get=f"/batch/{name}",
                    hx_push_url=f"/batch/{name}",
                    hx_target="#main-content",
                    hx_indicator="#loading",
                    cls=f"{'uk-active' if name == batch_name else ''}",
                )
            )
            for name in app.state.metric_batches
        ],
        uk_dropdown="pos: bottom-right; boundary: window; shift: true; flip: true;",
    )


def create_batch_card(batch_name: str, stats: dict) -> Card:
    """Create a card displaying batch information.

    Args:
        batch_name (str): The name of the batch.
        stats (dict): The statistics for the batch.

    Returns:
        Card: The card.
    """
    stat_blocks = [
        ("Metrics", format_metric_count(stats["unique_metrics"]), UkIcon("activity")),
        ("Freshness", stats["latest_timestamp"], UkIcon("clock")),
        ("Avg score", f"{stats['avg_score']:.1%}", UkIcon("bar-chart")),
        ("Alerts", f"{int(stats['alert_count'])}", UkIcon("alert-circle")),
    ]

    metric_divs = [
        Div(
            DivLAligned(icon, P(label, cls="batch-stat-label"), cls="space-x-2"),
            P(value, cls="batch-stat-value"),
            cls="batch-stat-block",
        )
        for label, value, icon in stat_blocks
    ]

    return Card(
        Div(
            CodeSpan(batch_name),
            H3(format_batch_name(batch_name), cls="mt-3 mb-1"),
            Subtitle("Metrics, freshness, and recent anomaly activity"),
            Div(DividerLine(), cls="my-4"),
            Div(*metric_divs, cls="batch-card-stats"),
            cls="w-full",
        ),
        footer=Button(
            DivLAligned(
                P("Open batch"),
                UkIcon("arrow-right"),
                cls="space-x-2 justify-center",
            ),
            hx_get=f"/batch/{batch_name}",
            hx_push_url=f"/batch/{batch_name}",
            hx_target="#main-content",
            hx_indicator="#loading",
            cls=(ButtonT.primary, "w-full"),
        ),
        cls="batch-card",
    )


def create_controls(batch_name: str) -> Div:
    """Create the controls for the batch view.

    Args:
        batch_name (str): The name of the batch.

    Returns:
        Div: The controls.
    """
    return Div(
        DivLAligned(
            Button(
                "Refresh",
                hx_get=f"/batch/{batch_name}/refresh",
                hx_target="#main-content",
                hx_indicator="#loading",
                cls=ButtonT.secondary,
            ),
            cls="space-x-2 mb-4",
        ),
    )
