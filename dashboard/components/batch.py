"""
dashboard/components/batch.py

Batch-related components.

This module contains the components for the batch view.

"""

from fasthtml.common import *
from monsterui.all import *
from dashboard.app import app

def create_batches_dropdown(batch_name: str) -> DropDownNavContainer:
    """Create the metric batches dropdown menu."""
    return DropDownNavContainer(
        NavHeaderLi("metric batches"),
        *[
            Li(
                A(
                    name,
                    hx_get=f"/batch/{name}",
                    hx_push_url=f"/batch/{name}",
                    hx_target="#main-content",
                    hx_indicator="#loading",
                    cls=f"{'uk-active' if name == batch_name else ''}",
                )) for name in app.state.metric_batches
        ],
        uk_dropdown="pos: bottom-right; boundary: window; shift: true; flip: true;")

def create_batch_card(batch_name: str, stats: dict) -> Card:
    """Create a card displaying batch information."""
    metric_info = [
        (UkIcon("activity", cls="text-blue-500"), f"{stats['unique_metrics']} metrics"),
        (UkIcon("clock", cls="text-green-500"), f"{stats['latest_timestamp']}"),
        (UkIcon("bar-chart", cls="text-purple-500"), f"Avg Score: {stats['avg_score']:.1%}"),
        (UkIcon("alert-circle", cls="text-red-500"), f"{stats['alert_count']} alerts"),
    ]

    metric_divs = [
        DivLAligned(
            icon,
            P(text, cls=TextPresets.muted_sm),
            cls="space-x-2",
        ) for icon, text in metric_info
    ]

    return Card(
        DivLAligned(
            Div(
                Button(batch_name,
                       hx_get=f"/batch/{batch_name}",
                       hx_push_url=f"/batch/{batch_name}",
                       hx_target="#main-content",
                       hx_indicator="#loading",
                       cls=(ButtonT.primary, "w-full")),
                DividerLine(),
                DivLAligned(Div(*metric_divs, cls="space-y-1"), ),
                cls="w-full",
            ),
            cls="w-full",
        ),
        cls="px-2 py-0.5 hover:border-primary transition-colors duration-200",
    ) 