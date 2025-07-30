"""
dashboard/routes/batch.py

Batch View

This module contains the route for the batch view.

"""

from fasthtml.common import H4, Div, P, Safe, Script, Style, Table, Td, Th, Tr
from monsterui.all import Button, ButtonT, Card, DivLAligned, UkIcon
import pandas as pd

from anomstack.df.wrangle import extract_metadata
from dashboard.app import app, log, rt
from dashboard.charts import ChartManager
from dashboard.components import create_controls
from dashboard.constants import DEFAULT_LAST_N, DEFAULT_LOAD_N_CHARTS
from dashboard.data import get_data


def get_batch_data(batch_name: str) -> pd.DataFrame:
    """Get batch data, either from cache or by fetching.

    Args:
        batch_name (str): The name of the batch.

    Returns:
        pd.DataFrame: The batch data.
    """
    try:
        return get_data(
            app.state.specs_enabled[batch_name],
            last_n=app.state.last_n.get(batch_name, DEFAULT_LAST_N),
            ensure_timestamp=True,
        )
    except Exception as e:
        log.error(f"Error getting data for batch {batch_name}: {e}")
        return pd.DataFrame(data=[], columns=["metric_name", "metric_timestamp", "metric_value"])


@rt("/batch/{batch_name}")
def get_batch_view(batch_name: str, initial_load: int = DEFAULT_LOAD_N_CHARTS):
    """Get the batch view.

    Args:
        batch_name (str): The name of the batch.
        initial_load (int): The number of charts to load initially.

    Returns:
        Div: The batch view.
    """
    if batch_name not in app.state.df_cache or batch_name not in app.state.stats_cache:
        app.state.df_cache[batch_name] = get_batch_data(batch_name)
        app.state.calculate_metric_stats(batch_name)

    metric_stats = app.state.stats_cache[batch_name]
    remaining_metrics = len(metric_stats) - initial_load

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

    load_next = min(DEFAULT_LOAD_N_CHARTS, remaining_metrics)
    return Div(
        create_controls(batch_name),
        Div(
            *[
                ChartManager.create_chart_placeholder(stat["metric_name"], i, batch_name)
                for i, stat in enumerate(metric_stats[:initial_load])
            ],
            id="charts-container",
            cls=f"grid grid-cols-{2 if app.state.two_columns else 1} gap-4",
        ),
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
    """Get chart for a batch and index.

    Args:
        batch_name (str): The name of the batch.
        chart_index (int): The index of the chart.

    Returns:
        Card: The chart.
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
        df_metric = extract_metadata(df_metric, "anomaly_explanation")
        fig = ChartManager.create_chart(df_metric, chart_index)
        app.state.chart_cache[batch_name][chart_index] = fig

    return Card(
        Style(
            """
            .uk-card-header { padding: 1rem; }
            .uk-card-body { padding: 1rem; }
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
def refresh_batch(batch_name: str):
    """Refresh data for a specific batch.

    Args:
        batch_name (str): The name of the batch to refresh.

    Returns:
        Div: The refreshed batch view.
    """
    # Clear cached data for this batch
    if batch_name in app.state.df_cache:
        del app.state.df_cache[batch_name]
    if batch_name in app.state.stats_cache:
        del app.state.stats_cache[batch_name]
    if batch_name in app.state.chart_cache:
        del app.state.chart_cache[batch_name]

    # Return the batch view with fresh data
    return get_batch_view(batch_name)


@rt("/batch/{batch_name}/anomalies")
def get_anomaly_list(batch_name: str, page: int = 1, per_page: int = 50):
    """Get the anomaly list view for a batch.

    Args:
        batch_name (str): The name of the batch.
        page (int): The page number to display.
        per_page (int): Number of anomalies to show per page.

    Returns:
        Div: The anomaly list view.
    """
    log.info(f"Accessing anomaly list for batch: {batch_name}")

    if batch_name not in app.state.df_cache:
        log.info(f"Cache miss for batch {batch_name}, fetching data...")
        app.state.df_cache[batch_name] = get_batch_data(batch_name)
        app.state.calculate_metric_stats(batch_name)

    df = app.state.df_cache[batch_name]
    log.info(f"Found {len(df)} rows in dataframe")

    # Filter for both standard anomalies and LLM alerts
    df_anomalies = df[(df["metric_alert"] == 1) | (df["metric_llmalert"] == 1)].copy()
    log.info(f"Found {len(df_anomalies)} anomalies (including LLM alerts)")

    # Sort by timestamp descending
    df_anomalies = df_anomalies.sort_values("metric_timestamp", ascending=False)

    # Calculate pagination
    total_anomalies = len(df_anomalies)
    total_pages = (total_anomalies + per_page - 1) // per_page
    page = max(1, min(page, total_pages))  # Ensure page is within valid range
    start_idx = (page - 1) * per_page
    end_idx = min(start_idx + per_page, total_anomalies)

    # Get the current page of anomalies
    df_page = df_anomalies.iloc[start_idx:end_idx]

    # Create table rows
    rows = []
    for _, row in df_page.iterrows():
        metric_name = row["metric_name"]
        timestamp = row["metric_timestamp"]

        # Get the metric data for this anomaly
        df_metric = df[df["metric_name"] == metric_name].copy()
        df_metric = df_metric.sort_values("metric_timestamp")
        fig = ChartManager.create_sparkline(df_metric, anomaly_timestamp=timestamp)

        # Create safe feedback key by replacing problematic characters
        safe_metric = (
            metric_name.replace(":", "_").replace(" ", "_").replace(".", "_").replace("+", "_")
        )
        safe_timestamp = (
            str(timestamp).replace(":", "_").replace(" ", "_").replace("+", "_").replace(".", "_")
        )
        feedback_key = f"{batch_name}-{safe_metric}-{safe_timestamp}"

        # Get the metric stats for this metric
        metric_stats = next(
            (
                stat
                for stat in app.state.stats_cache[batch_name]
                if stat["metric_name"] == metric_name
            ),
            None,
        )

        # Determine initial state based on thumbsup_sum and thumbsdown_sum
        thumbsup_sum = metric_stats["thumbsup_sum"] if metric_stats else 0
        thumbsdown_sum = metric_stats["thumbsdown_sum"] if metric_stats else 0

        # If there's existing feedback in app.state, use that instead
        if hasattr(app.state, "anomaly_feedback") and feedback_key in app.state.anomaly_feedback:
            feedback = app.state.anomaly_feedback[feedback_key]
        else:
            # Otherwise use the database feedback counts
            if thumbsup_sum > thumbsdown_sum:
                feedback = "positive"
            elif thumbsdown_sum > thumbsup_sum:
                feedback = "negative"
            else:
                feedback = None

        log.info(f"Creating feedback buttons for key: {feedback_key}, current feedback: {feedback}")

        rows.append(
            Tr(
                Td(
                    Div(
                        metric_name,
                        cls="truncate max-w-[120px] sm:max-w-[180px] mx-auto",
                        uk_tooltip=metric_name,
                    ),
                    cls="font-medium text-center w-full",
                ),
                Td(
                    timestamp.strftime("%Y-%m-%d %H:%M:%S"),
                    cls="text-muted-foreground text-center sm:w-[160px] w-[100px] hidden md:table-cell",
                ),
                Td(
                    Div(
                        Safe(fig),
                        Style(
                            "svg { display: block; margin: auto; height: 100% !important; width: 100% !important; }"
                        ),
                        cls="absolute inset-0 flex justify-center items-center h-full w-full p-0 m-0",
                    ),
                    cls="w-[300px] h-[50px] text-center p-0 m-0 relative overflow-hidden",
                ),
                Td(
                    DivLAligned(
                        Button(
                            UkIcon("thumbs-up", cls="sm:w-5 sm:h-5 w-4 h-4"),
                            hx_post=f"/batch/{batch_name}/anomaly/{metric_name}/{timestamp}/thumbs-up",
                            hx_target=f"#feedback-{feedback_key}",
                            hx_swap="outerHTML",
                            cls=(ButtonT.primary if feedback == "positive" else ButtonT.secondary)
                            + " sm:p-2 p-1",
                            id=f"feedback-{feedback_key}-positive",
                        ),
                        Button(
                            UkIcon("thumbs-down", cls="sm:w-5 sm:h-5 w-4 h-4"),
                            hx_post=f"/batch/{batch_name}/anomaly/{metric_name}/{timestamp}/thumbs-down",
                            hx_target=f"#feedback-{feedback_key}",
                            hx_swap="outerHTML",
                            cls=(ButtonT.primary if feedback == "negative" else ButtonT.secondary)
                            + " sm:p-2 p-1",
                            id=f"feedback-{feedback_key}-negative",
                        ),
                        cls="space-x-1 sm:space-x-2 justify-center",
                        id=f"feedback-{feedback_key}",
                    ),
                    cls="w-[120px] text-center",
                ),
                cls="hover:bg-muted/50 transition-colors",
            )
        )

    log.info(f"Created {len(rows)} table rows for page {page}")

    # Create pagination controls
    pagination = Div(
        DivLAligned(
            Button(
                UkIcon("chevron-left"),
                hx_get=f"/batch/{batch_name}/anomalies?page={page-1}",
                hx_target="#anomaly-list",
                cls=ButtonT.secondary,
                disabled=page <= 1,
            ),
            P(
                f"Page {page} of {total_pages}",
                cls="text-sm text-muted-foreground mx-4",
            ),
            Button(
                UkIcon("chevron-right"),
                hx_get=f"/batch/{batch_name}/anomalies?page={page+1}",
                hx_target="#anomaly-list",
                cls=ButtonT.secondary,
                disabled=page >= total_pages,
            ),
            cls="justify-center mt-4",
        ),
    )

    return Div(
        create_controls(batch_name),
        Card(
            Div(
                Table(
                    Tr(
                        Th("Metric", cls="font-medium text-center sm:w-[180px] w-[120px]"),
                        Th(
                            "Timestamp",
                            cls="font-medium text-center sm:w-[160px] w-[100px] hidden sm:table-cell",
                        ),
                        Th("Trend", cls="sm:w-[300px] w-[140px] text-center"),
                        Th("Feedback", cls="sm:w-[120px] w-[80px] font-medium text-center"),
                        cls="border-b",
                    ),
                    *rows,
                    cls="w-full divide-y min-w-full table-fixed",
                ),
                cls="overflow-x-auto -mx-4 sm:mx-0",
            ),
            header=Div(
                H4("Anomalies", cls="mb-1"),
                P(
                    f"Showing {len(rows)} of {total_anomalies} anomalies",
                    cls="text-sm text-muted-foreground",
                ),
            ),
            cls="mb-4",
        ),
        pagination,
        id="anomaly-list",
    )


@rt("/batch/{batch_name}/anomaly/{metric_name}/{timestamp}/thumbs-up", methods=["POST"])
def submit_thumbs_up(batch_name: str, metric_name: str, timestamp: str):
    """Submit positive feedback for an anomaly.

    Args:
        batch_name (str): The name of the batch.
        metric_name (str): The name of the metric.
        timestamp (str): The timestamp of the anomaly.

    Returns:
        Div: The updated feedback buttons.
    """
    log.info(
        f"Thumbs up endpoint called for batch={batch_name}, metric={metric_name}, timestamp={timestamp}"
    )

    # Create safe feedback key by replacing problematic characters
    safe_metric = (
        metric_name.replace(":", "_").replace(" ", "_").replace(".", "_").replace("+", "_")
    )
    safe_timestamp = (
        timestamp.replace(":", "_").replace(" ", "_").replace("+", "_").replace(".", "_")
    )
    feedback_key = f"{batch_name}-{safe_metric}-{safe_timestamp}"

    if not hasattr(app.state, "anomaly_feedback"):
        app.state.anomaly_feedback = {}
    app.state.anomaly_feedback[feedback_key] = "positive"

    log.info(f"Stored positive feedback for key: {feedback_key}")

    # Save feedback to metrics table
    spec = app.state.specs_enabled[batch_name]
    db = spec["db"]
    table_key = spec["table_key"]

    # Create feedback dataframe
    df_feedback = pd.DataFrame(
        {
            "metric_timestamp": [pd.to_datetime(timestamp)],
            "metric_batch": [batch_name],
            "metric_name": [metric_name],
            "metric_type": ["thumbsup"],
            "metric_value": [1],
            "metadata": [""],
        }
    )

    # Save to database
    from anomstack.df.save import save_df
    from anomstack.df.wrangle import wrangle_df
    from anomstack.validate.validate import validate_df

    df_feedback = wrangle_df(df_feedback)
    df_feedback = validate_df(df_feedback)
    save_df(df_feedback, db, table_key)

    log.info(f"Saved positive feedback to {db} {table_key}")

    # Return both buttons with updated states
    return DivLAligned(
        Button(
            UkIcon("thumbs-up", cls="sm:w-5 sm:h-5 w-4 h-4"),
            hx_post=f"/batch/{batch_name}/anomaly/{metric_name}/{timestamp}/thumbs-up",
            hx_target=f"#feedback-{feedback_key}",
            hx_swap="outerHTML",
            cls=ButtonT.primary + " sm:p-2 p-1",
            id=f"feedback-{feedback_key}-positive",
        ),
        Button(
            UkIcon("thumbs-down", cls="sm:w-5 sm:h-5 w-4 h-4"),
            hx_post=f"/batch/{batch_name}/anomaly/{metric_name}/{timestamp}/thumbs-down",
            hx_target=f"#feedback-{feedback_key}",
            hx_swap="outerHTML",
            cls=ButtonT.secondary + " sm:p-2 p-1",
            id=f"feedback-{feedback_key}-negative",
        ),
        cls="space-x-1 sm:space-x-2 justify-center",
        id=f"feedback-{feedback_key}",
    )


@rt("/batch/{batch_name}/anomaly/{metric_name}/{timestamp}/thumbs-down", methods=["POST"])
def submit_thumbs_down(batch_name: str, metric_name: str, timestamp: str):
    """Submit negative feedback for an anomaly.

    Args:
        batch_name (str): The name of the batch.
        metric_name (str): The name of the metric.
        timestamp (str): The timestamp of the anomaly.

    Returns:
        Div: The updated feedback buttons.
    """
    log.info(
        f"Thumbs down endpoint called for batch={batch_name}, metric={metric_name}, timestamp={timestamp}"
    )

    # Create safe feedback key by replacing problematic characters
    safe_metric = (
        metric_name.replace(":", "_").replace(" ", "_").replace(".", "_").replace("+", "_")
    )
    safe_timestamp = (
        timestamp.replace(":", "_").replace(" ", "_").replace("+", "_").replace(".", "_")
    )
    feedback_key = f"{batch_name}-{safe_metric}-{safe_timestamp}"

    if not hasattr(app.state, "anomaly_feedback"):
        app.state.anomaly_feedback = {}
    app.state.anomaly_feedback[feedback_key] = "negative"

    log.info(f"Stored negative feedback for key: {feedback_key}")

    # Save feedback to metrics table
    spec = app.state.specs_enabled[batch_name]
    db = spec["db"]
    table_key = spec["table_key"]

    # Create feedback dataframe
    df_feedback = pd.DataFrame(
        {
            "metric_timestamp": [pd.to_datetime(timestamp)],
            "metric_batch": [batch_name],
            "metric_name": [metric_name],
            "metric_type": ["thumbsdown"],
            "metric_value": [1],
            "metadata": [""],
        }
    )

    # Save to database
    from anomstack.df.save import save_df
    from anomstack.df.wrangle import wrangle_df
    from anomstack.validate.validate import validate_df

    df_feedback = wrangle_df(df_feedback)
    df_feedback = validate_df(df_feedback)
    save_df(df_feedback, db, table_key)

    log.info(f"Saved negative feedback to {db} {table_key}")

    # Return both buttons with updated states
    return DivLAligned(
        Button(
            UkIcon("thumbs-up", cls="sm:w-5 sm:h-5 w-4 h-4"),
            hx_post=f"/batch/{batch_name}/anomaly/{metric_name}/{timestamp}/thumbs-up",
            hx_target=f"#feedback-{feedback_key}",
            hx_swap="outerHTML",
            cls=ButtonT.secondary + " sm:p-2 p-1",
            id=f"feedback-{feedback_key}-positive",
        ),
        Button(
            UkIcon("thumbs-down", cls="sm:w-5 sm:h-5 w-4 h-4"),
            hx_post=f"/batch/{batch_name}/anomaly/{metric_name}/{timestamp}/thumbs-down",
            hx_target=f"#feedback-{feedback_key}",
            hx_swap="outerHTML",
            cls=ButtonT.primary + " sm:p-2 p-1",
            id=f"feedback-{feedback_key}-negative",
        ),
        cls="space-x-1 sm:space-x-2 justify-center",
        id=f"feedback-{feedback_key}",
    )
