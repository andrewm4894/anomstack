import logging

import pandas as pd
from fasthtml.common import *
import fasthtml.common as fh
from monsterui.all import *
from fasthtml.svg import *
from utils import (
    plot_time_series,
    get_data,
    get_metric_batches,
)

from anomstack.config import specs
from anomstack.jinja.render import render

log = logging.getLogger("fasthtml")

app, rt = fast_app(
    hdrs=(
        Theme.blue.headers(),
        Script(src="https://cdn.plot.ly/plotly-2.32.0.min.js"),
        Style("""
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
        """),
    ),
    debug=True, 
    log=log
)

# Set up toasts
setup_toasts(app, duration=3)

app.state.specs = specs
app.state.metric_batches = get_metric_batches()
app.state.specs_enabled = {}
for metric_batch in app.state.metric_batches:
    app.state.specs_enabled[metric_batch] = specs[metric_batch]


@rt
def index():
    top_nav = TabContainer(
        *map(
            lambda x: Li(
                A(x, 
                  hx_get=f"/batch/{x}", 
                  hx_push_url="true", 
                  hx_target="#main-content",
                  hx_indicator="#loading",
                  hx_swap="outerHTML transition:true",
                  cls="uk-padding-small"  # Add padding to tabs
                )
            ),
            app.state.metric_batches,
        ),
        alt=True,  # Use alternative style
        cls="top-nav uk-margin-bottom",  # Add bottom margin
    )

    return (
        Title("Anomstack"),
        Div(
            Safe('<span class="htmx-indicator">Loading...</span>'), 
            id="loading", 
            cls="loading-indicator"
        ),
        Card(
            top_nav,
            Grid(
                Card(
                    Safe("Select a metric batch above."), 
                    id="main-content", 
                    cls="col-span-4"
                )
            ),
            cls="uk-margin-top"  # Add top margin to main card
        )
    )


@rt("/batch/{batch_name}")
def get_batch_view(batch_name: str, session, initial_load: int = 5):
    # Check if we already have this batch's data cached
    if not hasattr(app.state, "df_cache"):
        app.state.df_cache = {}
    if not hasattr(app.state, "chart_cache"):
        app.state.chart_cache = {}
    if not hasattr(app.state, "stats_cache"):
        app.state.stats_cache = {}

    # Add controls with improved styling
    controls = Card(
        Div(
            Button(
                DivLAligned(
                    UkIcon("refresh"),
                    "Refresh"
                ),
                hx_get=f"/batch/{batch_name}/refresh", 
                hx_target="#main-content",
                cls=ButtonT.secondary
            ),
            Form(
                Input(
                    type="search", 
                    name="search", 
                    placeholder="Search metrics...",
                    hx_post=f"/batch/{batch_name}/search",
                    hx_trigger="keyup changed delay:500ms",
                    hx_target="#charts-container",
                    hx_indicator="#loading",
                    cls="uk-input"
                ),
                style="display: inline-block; margin-left: 1rem;"
            ),
            Form(
                DivLAligned(
                    Input(
                        type="number",
                        name="alert_max_n",
                        value="30",
                        min="1",
                        max="1000",
                        placeholder="Last N points",
                        cls="uk-input",
                        style="width: 120px"
                    ),
                    Button(
                        "Apply", 
                        hx_post=f"/batch/{batch_name}/update-n",
                        hx_target="#main-content",
                        cls=ButtonT.secondary,
                        style="margin-left: 0.5rem"
                    ),
                ),
                style="display: inline-block; margin-left: 1rem;"
            ),
            style="display: flex; align-items: center;"
        ),
        cls="mb-4"
    )

    # Get or create dataframe cache with current alert_max_n
    if batch_name not in app.state.df_cache:
        app.state.df_cache[batch_name] = get_data(
            app.state.specs_enabled[batch_name], 
            alert_max_n=30  # Default value
        )
        
    # Calculate and cache metric stats if not already cached
    if batch_name not in app.state.stats_cache:
        df = app.state.df_cache[batch_name]
        metric_stats = []
        for metric_name in df["metric_name"].unique():
            df_metric = df[df["metric_name"] == metric_name]
            anomaly_rate = df_metric["metric_alert"].mean() if df_metric["metric_alert"].sum() > 0 else 0
            avg_score = df_metric["metric_score"].mean() if df_metric["metric_score"].sum() > 0 else 0
            metric_stats.append({
                "metric_name": metric_name,
                "anomaly_rate": anomaly_rate,
                "avg_score": avg_score
            })
        
        # Sort metrics by anomaly rate (primary) and avg score (secondary) in descending order
        metric_stats.sort(key=lambda x: (-x["anomaly_rate"], -x["avg_score"]))
        app.state.stats_cache[batch_name] = metric_stats

    # Use cached stats
    metric_stats = app.state.stats_cache[batch_name]
    total_metrics = len(metric_stats)

    # Create initial placeholders
    placeholders = []
    for i, stat in enumerate(metric_stats[:initial_load]):
        placeholders.append(
            Div(
                P(f"Loading {stat['metric_name']}..."),
                id=f"chart-{i}",
                hx_get=f"/batch/{batch_name}/chart/{i}",
                hx_trigger="load",
                hx_swap="outerHTML"
            )
        )
    
    # Add "Load More" button if there are more metrics to load
    if total_metrics > initial_load:
        remaining_count = total_metrics - initial_load
        placeholders.append(
            Div(
                Button(
                    f"Load {remaining_count} More Charts",
                    hx_get=f"/batch/{batch_name}/load-more/{initial_load}",
                    hx_target="#load-more-container",
                    hx_swap="outerHTML",
                ),
                id="load-more-container"
            )
        )

    return Card(
        controls,
        Div(*placeholders, id="charts-container"),
        id="main-content",
        cls="col-span-4"
    )


@rt("/batch/{batch_name}/chart/{chart_index}")
def get(batch_name: str, chart_index: int):
    # Get cached dataframe and stats
    df = app.state.df_cache[batch_name]
    metric_stats = app.state.stats_cache[batch_name]
    metric_name = metric_stats[chart_index]["metric_name"]
    
    # Get anomaly rate and avg score for the header
    anomaly_rate = metric_stats[chart_index]["anomaly_rate"]
    avg_score = metric_stats[chart_index]["avg_score"]
    
    # Generate or get cached chart
    if batch_name not in app.state.chart_cache:
        app.state.chart_cache[batch_name] = {}
    
    if chart_index not in app.state.chart_cache[batch_name]:
        df_metric = df[df["metric_name"] == metric_name]
        fig = plot_time_series(df_metric, metric_name).to_html(
            include_plotlyjs=False,
            full_html=False,
            config={
                "displayModeBar": False,
                "displaylogo": False,
                "modeBarButtonsToRemove": ["zoom2d", "pan2d", "select2d", "lasso2d", "zoomIn2d", "zoomOut2d", "autoScale2d", "resetScale2d"],
                "toImageButtonOptions": {"height": 500, "width": 700},
                "hovermode": "x unified",
                "hoverlabel": {"namelength": -1},
                "showLink": False,
                "responsive": True,
                "scrollZoom": False,
                "showTips": False,
                "staticPlot": False,
                "doubleClick": False,
                "showAxisDragHandles": False,
                "showAxisRangeEntryBoxes": False,
                "showSendToCloud": False,
                "showEditInChartStudio": False,
                "hovercompare": False,
                "hoverdistance": 100,
                "hoverHtml": True
            }
        )
        app.state.chart_cache[batch_name][chart_index] = fig

    # Wrap the figure in a styled card
    return Card(
        Safe(app.state.chart_cache[batch_name][chart_index]),
        header=Div(
            H4(metric_name),
            DivLAligned(
                P(f"Anomaly Rate: {anomaly_rate:.1%}", cls="text-sm text-muted-foreground"),
                P(f"Avg Score: {avg_score:.1%}", cls="text-sm text-muted-foreground"),
                style="gap: 1rem;"
            )
        ),
        id=f"chart-{chart_index}",
        cls="mb-4"
    )


@rt("/batch/{batch_name}/refresh")
def get(batch_name: str, session):
    # Clear both the data and stats cache for this batch
    if hasattr(app.state, "df_cache"):
        app.state.df_cache.pop(batch_name, None)
    if hasattr(app.state, "chart_cache"):
        app.state.chart_cache.pop(batch_name, None)
    if hasattr(app.state, "stats_cache"):
        app.state.stats_cache.pop(batch_name, None)
    
    # Call the main batch handler to get fresh data
    return get_batch_view(batch_name, session, initial_load=5)


@rt("/batch/{batch_name}/load-more/{start_index}")
def get(batch_name: str, start_index: int):
    metric_stats = app.state.stats_cache[batch_name]
    
    # Create placeholders for remaining charts
    placeholders = []
    for i, stat in enumerate(metric_stats[start_index:], start=start_index):
        placeholders.append(
            Div(
                P(f"Loading {stat['metric_name']}..."),
                id=f"chart-{i}",
                hx_get=f"/batch/{batch_name}/chart/{i}",
                hx_trigger="load",
                hx_swap="outerHTML"
            )
        )
    
    return Div(*placeholders, id="load-more-container")


@rt("/batch/{batch_name}/search")
def post(batch_name: str, search: str = ""):
    import re
    
    # Get cached stats
    metric_stats = app.state.stats_cache[batch_name]
    
    try:
        # Create regex pattern from search string
        pattern = re.compile(search, re.IGNORECASE) if search else None
        
        # Filter metrics based on search
        filtered_stats = [
            stat for stat in metric_stats 
            if not pattern or pattern.search(stat["metric_name"])
        ]
        
        # Create placeholders for matching metrics
        placeholders = []
        for i, stat in enumerate(filtered_stats):
            # Create a new chart placeholder with the correct chart data
            placeholders.append(
                Div(
                    P(f"Loading {stat['metric_name']}..."),
                    id=f"chart-{i}",
                    hx_get=f"/batch/{batch_name}/chart/{metric_stats.index(stat)}",  # Use original index
                    hx_trigger="load",
                    hx_swap="outerHTML"
                )
            )
        
        return Div(*placeholders) if placeholders else Div(P("No matching metrics found"))
    
    except re.error:
        # Handle invalid regex
        return Div(P("Invalid search pattern"))


@rt("/batch/{batch_name}/update-n")
def post(batch_name: str, alert_max_n: int = 30, session=None):
    # Clear caches for this batch
    if hasattr(app.state, "df_cache"):
        app.state.df_cache.pop(batch_name, None)
    if hasattr(app.state, "chart_cache"):
        app.state.chart_cache.pop(batch_name, None)
    if hasattr(app.state, "stats_cache"):
        app.state.stats_cache.pop(batch_name, None)
    
    # Get fresh data with new alert_max_n
    app.state.df_cache[batch_name] = get_data(
        app.state.specs_enabled[batch_name], 
        alert_max_n=alert_max_n
    )
    
    # Call the main batch handler with new alert_max_n
    return get_batch_view(batch_name, session, initial_load=5)


@rt("/batch/{batch_name}/vote/{metric_name}")
def post(batch_name: str, metric_name: str, timestamp: str, vote: str):
    # For now, just log the vote
    log.info(f"Vote received - Batch: {batch_name}, Metric: {metric_name}, Timestamp: {timestamp}, Vote: {vote}")
    return "Vote recorded"


serve(host="localhost", port=5003)
