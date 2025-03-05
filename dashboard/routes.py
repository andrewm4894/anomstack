"""
Routes for the dashboard.
"""

import logging
import pandas as pd
from fasthtml.common import *
from monsterui.all import *
from fasthtml.svg import *

from app import app, rt
from constants import *
from data import get_data
from components import _create_controls, create_batch_card, create_header
from charts import ChartManager
from batch_stats import calculate_batch_stats


log = logging.getLogger("anomstack")


@rt("/refresh-all")
def post(request: Request):
    """
    Refresh all batch data.
    """
    # Add loading toast
    loading_toast = add_toast("Refreshing all batch data...", "info")
    
    try:
        # Clear all batch caches
        app.state.df_cache.clear()
        app.state.stats_cache.clear()
        app.state.chart_cache.clear()
        
        # Get the updated content
        response = index(request)
        
        # Add success toast
        success_toast = add_toast("Successfully refreshed all batch data", "success")
        
        return [loading_toast, response, success_toast]
        
    except Exception as e:
        # Add error toast
        error_toast = add_toast(f"Error refreshing batch data: {str(e)}", "error")
        return [loading_toast, error_toast]


@rt
def index(request: Request):
    """
    Index route for the dashboard.
    """
    # Check if this is an HTMX request
    is_htmx = request.headers.get("HX-Request") == "true"

    # Add dark mode class to body if enabled
    script = Script(
        f"""
        if ({'true' if app.state.dark_mode else 'false'}) {{
            document.body.classList.add('dark-mode');
        }}
    """
    )

    # Add toast container for notifications
    toast_container = Div(id="toast-container", cls=(ToastHT.end, ToastVT.top))

    # Calculate batch stats
    batch_stats = {}
    for batch_name in app.state.metric_batches:
        if batch_name not in app.state.df_cache:
            try:
                # Add loading toast
                loading_toast = Toast(
                    f"Loading data for batch {batch_name}...", 
                    alert_cls=AlertT.info,
                    cls=(ToastHT.end, ToastVT.top)
                )
                
                df = get_data(
                    app.state.specs_enabled[batch_name], max_n=DEFAULT_ALERT_MAX_N
                )
                
                # Add success toast
                success_toast = Toast(
                    f"Successfully loaded data for {batch_name}", 
                    alert_cls=AlertT.success,
                    cls=(ToastHT.end, ToastVT.top)
                )
                
            except Exception as e:
                log.error(f"Error getting data for batch {batch_name}: {e}")
                # Add error toast
                error_toast = Toast(
                    f"Error loading data for {batch_name}: {str(e)}", 
                    alert_cls=AlertT.error,
                    cls=(ToastHT.end, ToastVT.top)
                )
                df = pd.DataFrame(data=[], columns=['metric_name', 'metric_timestamp', 'metric_value'])
            app.state.df_cache[batch_name] = df
        else:
            df = app.state.df_cache[batch_name]

        batch_stats[batch_name] = calculate_batch_stats(df, batch_name)

    # Filter out metric batches where latest_timestamp is "No Data"
    filtered_batches = {
        name: stats
        for name, stats in batch_stats.items()
        if stats["latest_timestamp"] != "No Data"
    }

    # Sort the filtered metric batches by alert count (primary) and avg score (secondary)
    sorted_batch_names = sorted(
        filtered_batches.keys(),
        key=lambda x: (
            -filtered_batches[x]["alert_count"],  # Negative for descending order
            -filtered_batches[x]["avg_score"]     # Negative for descending order
        )
    )

    main_content = Div(
        Card(
            DivLAligned(
                H2("Anomstack", cls="text-2xl font-bold pl-2"),
                DivLAligned(
                    Button(
                        DivLAligned(
                            UkIcon("refresh-ccw"),
                            cls="space-x-2"
                        ),
                        cls=ButtonT.ghost,  # Using ghost style to match header aesthetics
                        hx_post="/refresh-all",
                        hx_target="#main-content",
                        hx_indicator="#loading",
                        uk_tooltip="Refresh all"
                    ),
                    A(
                        UkIcon("github"),
                        href="https://github.com/andrewm4894/anomstack",
                        cls=ButtonT.ghost,
                        uk_tooltip="View the source code on GitHub"
                    ),
                    cls="space-x-2"
                ),
                cls="flex justify-between items-center mb-6"
            ),
            # Show warning if no metric batches
            (
                Div(
                    DivLAligned(
                        UkIcon("alert-triangle"),
                        P(
                            "No metric batches found. Is Dagster running?",
                            cls=TextPresets.muted_sm,
                        ),
                        cls="space-x-2 p-4 bg-yellow-50 text-yellow-700 rounded-md",
                    ),
                    cls="mb-6",
                )
                if not app.state.metric_batches
                else Grid(
                    *[create_batch_card(name, batch_stats[name]) for name in sorted_batch_names],
                    cols=3,
                    gap=4,
                )
            ),
            cls="p-6",
        ),
        id="main-content",
    )

    # For HTMX requests, return only the main content
    if is_htmx:
        return main_content

    # For full page loads, return the complete layout with toast container
    return (
        Title("Anomstack"),
        script,
        toast_container,  # Add toast container
        Div(
            Safe('<span class="htmx-indicator">Loading...</span>'),
            id="loading",
            cls="loading-indicator",
        ),
        main_content,
    )


@rt("/batch/{batch_name}")
def get_batch_view(batch_name: str, session, initial_load: int = DEFAULT_LOAD_N_CHARTS):
    """
    Get the batch view for a given batch name.
    """
    # First, ensure we have the data and stats calculated
    if batch_name not in app.state.df_cache:
        app.state.df_cache[batch_name] = get_data(
            app.state.specs_enabled[batch_name], max_n=DEFAULT_ALERT_MAX_N
        )
        app.state.calculate_metric_stats(batch_name)
    elif batch_name not in app.state.stats_cache:
        app.state.calculate_metric_stats(batch_name)

    metric_stats = app.state.stats_cache[batch_name]
    total_metrics = len(metric_stats)
    remaining_metrics = total_metrics - initial_load

    script = Script(
        f"""
        document.querySelectorAll('.top-nav li').forEach(li => {{
            li.classList.remove('uk-active');
            if (li.querySelector('a').textContent.trim() === '{batch_name}') {{
                li.classList.add('uk-active');
            }}
        }});
        window.scrollTo({{ top: 0, behavior: 'smooth' }});
    """
    )

    # Update the load more button text
    load_next = min(DEFAULT_LOAD_N_CHARTS, remaining_metrics)
    return Div(
        _create_controls(batch_name),
        Div(
            *[
                ChartManager.create_chart_placeholder(
                    stat["metric_name"], i, batch_name
                )
                for i, stat in enumerate(metric_stats[:initial_load])
            ],
            id="charts-container",
            cls=f"grid grid-cols-{2 if app.state.two_columns else 1} gap-4",
        ),
        # Load More button with updated text
        Div(
            Button(
                f"Load next {load_next} of {remaining_metrics}",
                hx_get=f"/batch/{batch_name}/load-more/{initial_load}",
                hx_target="#charts-container",
                hx_swap="beforeend",
                hx_indicator="#loading",
                cls=ButtonT.secondary,
                style="width: 100%; margin-top: 1rem;",
                disabled=remaining_metrics <= 0,
            ),
            id="load-more-container",
        ),
        script,
    )


@rt("/batch/{batch_name}/chart/{chart_index}")
def get(batch_name: str, chart_index: int):
    """
    Get the chart for a given batch name and chart index.
    """
    df = app.state.df_cache[batch_name]
    metric_stats = app.state.stats_cache[batch_name]
    metric_name = metric_stats[chart_index]["metric_name"]
    anomaly_rate = metric_stats[chart_index]["anomaly_rate"]
    avg_score = metric_stats[chart_index]["avg_score"]

    if batch_name not in app.state.chart_cache:
        app.state.chart_cache[batch_name] = {}

    if chart_index not in app.state.chart_cache[batch_name]:
        df_metric = df[df["metric_name"] == metric_name]
        fig = ChartManager.create_chart(df_metric, chart_index)
        app.state.chart_cache[batch_name][chart_index] = fig

    return Card(
        Style(
            """
            .uk-card-header {
                padding: 1rem;  /* Consistent padding */
            }
            .uk-card-body {
                padding: 1rem;  /* Consistent padding */
            }
        """
        ),
        Safe(app.state.chart_cache[batch_name][chart_index]),
        header=Div(
            H4(metric_name, cls="mb-1"),
            DivLAligned(
                P(
                    f"Anomaly Rate: {anomaly_rate:.1%}",
                    cls="text-sm text-muted-foreground",
                ),
                P(f"Avg Score: {avg_score:.1%}", cls="text-sm text-muted-foreground"),
                style="gap: 1rem;",
            ),
        ),
        id=f"chart-{chart_index}",
        cls="mb-1",
    )


@rt("/batch/{batch_name}/refresh")
def get(batch_name: str, session):
    """
    Refresh the batch view for a given batch name.
    """
    # Add loading toast
    loading_toast = add_toast(f"Refreshing data for {batch_name}...", "info")
    
    try:
        app.state.clear_batch_cache(batch_name)
        response = get_batch_view(batch_name, session, initial_load=DEFAULT_LOAD_N_CHARTS)
        
        # Add success toast
        success_toast = add_toast(f"Successfully refreshed {batch_name}", "success")
        
        # Return both the response and the toasts
        return [loading_toast, response, success_toast]
        
    except Exception as e:
        # Add error toast
        error_toast = add_toast(f"Error refreshing {batch_name}: {str(e)}", "error")
        return [loading_toast, error_toast]


@rt("/batch/{batch_name}/load-more/{start_index}")
def get(batch_name: str, start_index: int):
    """
    Load more charts for a given batch name and start index.
    """
    metric_stats = app.state.stats_cache[batch_name]
    remaining_metrics = len(metric_stats) - (start_index + DEFAULT_LOAD_N_CHARTS)
    load_next = min(DEFAULT_LOAD_N_CHARTS, remaining_metrics)

    return [
        *[
            ChartManager.create_chart_placeholder(stat["metric_name"], i, batch_name)
            for i, stat in enumerate(
                metric_stats[start_index : start_index + DEFAULT_LOAD_N_CHARTS],
                start=start_index,
            )
        ],
        # Update the load more button with new count and disabled state
        Div(
            Button(
                (
                    f"Load next {load_next} of {remaining_metrics}"
                    if remaining_metrics > 0
                    else "No more metrics"
                ),
                hx_get=f"/batch/{batch_name}/load-more/{start_index + DEFAULT_LOAD_N_CHARTS}",
                hx_target="#charts-container",
                hx_swap="beforeend",
                hx_indicator="#loading",
                cls=ButtonT.secondary,
                style="width: 100%; margin-top: 1rem;",
                disabled=remaining_metrics <= 0,
            ),
            id="load-more-container",
            hx_swap_oob="true",
        ),
    ]


@rt("/batch/{batch_name}/search")
def post(batch_name: str, search: str = ""):
    """
    Search for a given batch name and search string.
    """
    import re

    metric_stats = app.state.stats_cache[batch_name]
    try:
        pattern = re.compile(search, re.IGNORECASE) if search else None
        filtered_stats = [
            stat
            for stat in metric_stats
            if not pattern or pattern.search(stat["metric_name"])
        ]
        placeholders = []
        for i, stat in enumerate(filtered_stats):
            placeholders.append(
                ChartManager.create_chart_placeholder(
                    stat["metric_name"], i, batch_name
                )
            )
        return (
            Div(*placeholders) if placeholders else Div(P("No matching metrics found"))
        )
    except re.error:
        return Div(P("Invalid search pattern"))


@rt("/batch/{batch_name}/update-n")
def post(batch_name: str, alert_max_n: int = DEFAULT_ALERT_MAX_N, session=None):
    """
    Update the number of alerts for a given batch name.
    """
    app.state.alert_max_n[batch_name] = alert_max_n
    app.state.clear_batch_cache(batch_name)

    app.state.df_cache[batch_name] = get_data(
        app.state.specs_enabled[batch_name], max_n=alert_max_n
    )
    app.state.calculate_metric_stats(batch_name)

    # Return the full page content with proper URL update
    return get_batch_view(
        batch_name, session=session, initial_load=DEFAULT_LOAD_N_CHARTS
    )


@rt("/batch/{batch_name}/toggle-size")
def post(batch_name: str, session=None):
    """
    Toggle the size of the charts for a given batch name.
    """
    app.state.small_charts = not app.state.small_charts
    app.state.chart_cache.clear()  # Clear cache to regenerate charts
    return get_batch_view(
        batch_name, session=session, initial_load=DEFAULT_LOAD_N_CHARTS
    )


@rt("/batch/{batch_name}/toggle-theme")
def post(batch_name: str, session=None):
    """
    Toggle the theme of the dashboard for a given batch name.
    """
    app.state.dark_mode = not app.state.dark_mode
    app.state.chart_cache.clear()  # Clear cache to regenerate charts

    # Add script to toggle dark mode class on body
    script = Script(
        """
        document.body.classList.toggle('dark-mode');
    """
    )

    response = get_batch_view(
        batch_name, session=session, initial_load=DEFAULT_LOAD_N_CHARTS
    )
    return Div(script, response)


@rt("/batch/{batch_name}/toggle-columns")
def post(batch_name: str, session=None):
    """
    Toggle the number of columns for a given batch name.
    """
    app.state.two_columns = not app.state.two_columns
    return get_batch_view(
        batch_name, session=session, initial_load=DEFAULT_LOAD_N_CHARTS
    )


@rt("/batch/{batch_name}/toggle-markers")
def post(batch_name: str, session=None):
    """
    Toggle the markers for a given batch name.
    """
    app.state.show_markers = not app.state.show_markers
    app.state.chart_cache.clear()  # Clear cache to regenerate charts
    return get_batch_view(
        batch_name, session=session, initial_load=DEFAULT_LOAD_N_CHARTS
    )


@rt("/batch/{batch_name}/toggle-legend")
def post(batch_name: str, session=None):
    """
    Toggle the legend for a given batch name.
    """
    app.state.show_legend = not app.state.show_legend
    app.state.chart_cache.clear()  # Clear cache to regenerate charts
    return get_batch_view(
        batch_name, session=session, initial_load=DEFAULT_LOAD_N_CHARTS
    )


@rt("/batch/{batch_name}/toggle-line-width")
def post(batch_name: str, session=None):
    """
    Toggle between narrow (1px) and normal (2px) line width.
    """
    app.state.narrow_lines = not getattr(app.state, 'narrow_lines', False)
    app.state.line_width = 1 if app.state.narrow_lines else 2
    app.state.chart_cache.clear()  # Clear cache to regenerate charts
    return get_batch_view(
        batch_name, session=session, initial_load=DEFAULT_LOAD_N_CHARTS
    )


# Add helper function to create toast messages for other routes
def add_toast(message: str, type: str = "info") -> Toast:
    """Create a toast notification"""
    alert_types = {
        "info": AlertT.info,
        "success": AlertT.success,
        "warning": AlertT.warning,
        "error": AlertT.error
    }
    return Toast(
        message,
        alert_cls=alert_types.get(type, AlertT.info),
        cls=(ToastHT.end, ToastVT.top),
        hx_swap_oob="beforeend",
        hx_target="#toast-container"
    )


# Add new test toast route
@rt("/test-toast")
def post(request: Request):
    """Test route to trigger different types of toasts."""
    return [
        add_toast("This is an info toast", "info"),
        add_toast("This is a success toast", "success"),
        add_toast("This is a warning toast", "warning"),
        add_toast("This is an error toast", "error")
    ]
