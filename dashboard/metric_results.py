"""Consistent filtering and pagination for every chart-list refresh."""

import re

from fasthtml.common import Div, P
from monsterui.all import Button, ButtonT

from dashboard.charts import ChartManager
from dashboard.constants import DEFAULT_LOAD_N_CHARTS


def filter_metrics(stats, search):
    """Retain source indices so lazy chart requests resolve the correct metric."""
    pattern = re.compile(search, re.IGNORECASE) if search else None
    return [
        (i, stat)
        for i, stat in enumerate(stats)
        if not pattern or pattern.search(stat["metric_name"])
    ]


def metric_results(state, batch_name, start=0, limit=DEFAULT_LOAD_N_CHARTS, append=False, oob=True):
    """Render a filtered page and its matching pagination control."""
    message = None
    try:
        matches = filter_metrics(
            state.stats_cache[batch_name], state.search_term.get(batch_name, "")
        )
    except re.error:
        matches = []
        message = "Invalid search pattern. Check your regular expression or clear the search."
    start = max(0, start)
    page = matches[start : start + limit]
    remaining = max(0, len(matches) - (start + limit))
    charts = [
        ChartManager.create_chart_placeholder(stat["metric_name"], i, batch_name)
        for i, stat in page
    ]
    if not matches:
        charts = [
            P(
                message or "No matching metrics. Clear the search or try a wider time window.",
                role="status",
                cls="text-muted-foreground p-4 text-center col-span-full",
            )
        ]
    pagination = Div(
        Button(
            f"Load next {min(limit, remaining)} of {remaining}",
            hx_get=f"/batch/{batch_name}/load-more/{start + limit}",
            hx_target="#charts-container",
            hx_swap="beforeend",
            hx_indicator="#loading",
            hx_disabled_elt="this",
            cls=ButtonT.secondary,
            style="width: 100%; margin-top: 1rem;",
        )
        if remaining
        else P(
            f"{len(matches)} matching metrics"
            if state.search_term.get(batch_name)
            else f"{len(matches)} metrics",
            cls="text-sm text-muted-foreground text-center p-2",
            role="status",
        ),
        id="load-more-container",
        hx_swap_oob="true" if oob else None,
    )
    if append:
        return [*charts, pagination]
    return [
        Div(
            *charts,
            id="charts-container",
            cls=f"grid grid-cols-{2 if state.two_columns else 1} gap-4",
        ),
        pagination,
    ]
