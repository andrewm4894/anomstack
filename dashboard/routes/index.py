from fasthtml.common import *
from monsterui.all import *
from fasthtml.svg import *
import pandas as pd
import logging
from dashboard.app import app, rt
from dashboard.components import create_batch_card
from dashboard.batch_stats import calculate_batch_stats
from dashboard.data import get_data

log = logging.getLogger("anomstack")


def _get_batch_data(batch_name: str) -> pd.DataFrame:
    """Get batch data, either from cache or by fetching."""
    if batch_name not in app.state.df_cache:
        try:
            df = get_data(app.state.specs_enabled[batch_name],
                          last_n=DEFAULT_LAST_N,
                          ensure_timestamp=True)
        except Exception as e:
            log.error(f"Error getting data for batch {batch_name}: {e}")
            df = pd.DataFrame(
                data=[],
                columns=["metric_name", "metric_timestamp", "metric_value"])
        app.state.df_cache[batch_name] = df
    return app.state.df_cache[batch_name]


def _get_sorted_batch_stats() -> tuple:
    """Calculate and sort batch statistics."""
    batch_stats = {}
    for batch_name in app.state.metric_batches:
        df = _get_batch_data(batch_name)
        batch_stats[batch_name] = calculate_batch_stats(df, batch_name)

    filtered_batches = {
        name: stats
        for name, stats in batch_stats.items()
        if stats["latest_timestamp"] != "No Data"
    }

    sorted_batch_names = sorted(
        filtered_batches.keys(),
        key=lambda x: (
            -filtered_batches[x]["alert_count"],
            -filtered_batches[x]["avg_score"],
        ),
    )

    return batch_stats, sorted_batch_names


def _create_main_content(batch_stats: dict, sorted_batch_names: list) -> Div:
    """Create the main dashboard content."""
    return Div(
        Card(
            DivLAligned(
                Div(
                    H2("Anomstack", cls="text-2xl font-bold pl-2"),
                    P(
                        "Painless open source anomaly detection for your metrics 📈📉🚀",
                        cls="text-muted-foreground pl-2",
                    ),
                    cls="flex flex-col",
                ),
                DivLAligned(
                    Button(
                        DivLAligned(UkIcon("refresh-ccw"), cls="space-x-2"),
                        cls=ButtonT.ghost,
                        hx_post="/refresh-all",
                        hx_target="#main-content",
                        hx_indicator="#loading",
                        uk_tooltip="Refresh all",
                    ),
                    A(
                        UkIcon("github"),
                        href="https://github.com/andrewm4894/anomstack",
                        cls=ButtonT.ghost,
                        uk_tooltip="View the source code on GitHub",
                        target="_blank",
                    ),
                    cls="space-x-2",
                ),
                cls="flex justify-between items-center mb-6",
            ),
            (Div(
                DivLAligned(
                    UkIcon("alert-triangle"),
                    P(
                        "No metric batches found. Is Dagster running?",
                        cls=TextPresets.muted_sm,
                    ),
                    cls="space-x-2 p-2 bg-yellow-50 text-yellow-700 rounded-md",
                ),
                cls="mb-6",
            ) if not app.state.metric_batches else Div(
                *[
                    create_batch_card(name, batch_stats[name])
                    for name in sorted_batch_names
                ],
                cls="homepage-grid",
            )),
            cls="p-2",
        ),
        id="main-content",
    )


@rt("/refresh-all")
def post(request: Request):
    """Refresh all batch data."""
    try:
        app.state.df_cache.clear()
        app.state.stats_cache.clear()
        app.state.chart_cache.clear()
        return [index(request)]
    except Exception as e:
        log.error(f"Error refreshing all batch data: {e}")
        return []


@rt
def index(request: Request):
    """Index route for the dashboard."""
    is_htmx = request.headers.get("HX-Request") == "true"

    script = Script(f"""
        if ({'true' if app.state.dark_mode else 'false'}) {{
            document.body.classList.add('dark-mode');
        }}
    """)

    batch_stats, sorted_batch_names = _get_sorted_batch_stats()
    main_content = _create_main_content(batch_stats, sorted_batch_names)

    if is_htmx:
        return main_content

    return (
        Title("Anomstack"),
        script,
        Div(
            Safe('<span class="htmx-indicator">Loading...</span>'),
            id="loading",
            cls="loading-indicator",
        ),
        main_content,
    )
