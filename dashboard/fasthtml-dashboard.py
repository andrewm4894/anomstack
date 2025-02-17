import logging

import pandas as pd
from fasthtml.common import *  # Bring in all of fasthtml
import fasthtml.common as fh  # Used to get unstyled components
from monsterui.all import *  # Bring in all of monsterui, including shadowing fasthtml components with styled components
from fasthtml.svg import *
from utils import get_enabled_dagster_jobs, plot_time_series

from anomstack.config import specs
from anomstack.jinja.render import render
from anomstack.sql.read import read_sql

log = logging.getLogger("fasthtml")

app, rt = fast_app(hdrs=Theme.blue.headers(), debug=True, log=log)

# Set up toasts
setup_toasts(app, duration=3)


def get_metric_batches():
    enabled_jobs = get_enabled_dagster_jobs(host="http://localhost", port="3000")
    ingest_jobs = [job for job in enabled_jobs if job.endswith("_ingest")]
    metric_batches = [job[:-7] for job in ingest_jobs if job.endswith("_ingest")]
    return metric_batches


def get_data(sql: str, db: str) -> pd.DataFrame:
    df = read_sql(sql, db=db)
    return df


app.state.specs = specs
app.state.metric_batches = get_metric_batches()
app.state.specs_enabled = {}
for metric_batch in app.state.metric_batches:
    app.state.specs_enabled[metric_batch] = specs[metric_batch]


@rt
def index():
    metric_batches = app.state.metric_batches
    print(f"{metric_batches=}")

    top_nav = TabContainer(
        *map(
            lambda x: Li(
                A(x, hx_get=f"/batch/{x}", hx_push_url="true", hx_target="#content")
            ),
            metric_batches,
        ),
        alt=True,
        cls="top-nav",
    )

    return (
        Title("Anomstack"),
        top_nav,
        Grid(Card(Safe("Select a metric batch"), id="content", cls="col-span-4")),
    )


@rt("/batch/{batch_name}")
def get(batch_name: str, session):

    add_toast(session, f"Loading {batch_name} data", "info")

    # Check if we already have this batch's data cached
    if not hasattr(app.state, "df_cache"):
        app.state.df_cache = {}
    if not hasattr(app.state, "chart_cache"):
        app.state.chart_cache = {}

    # Get or create dataframe cache
    if batch_name not in app.state.df_cache:
        sql = render(
            "dashboard_sql",
            app.state.specs_enabled[batch_name],
            params={"alert_max_n": 30},
        )
        db = app.state.specs_enabled[batch_name]["db"]
        app.state.df_cache[batch_name] = get_data(sql, db)
        add_toast(session, f"Loaded data for {batch_name}", "info")
    else:
        add_toast(session, f"Showing {batch_name} metrics", "success")

    # Use cached dataframe
    df = app.state.df_cache[batch_name]

    # Check if charts are already cached
    if batch_name not in app.state.chart_cache:
        metric_names = df["metric_name"].unique()
        figs = []
        for metric_name in metric_names:
            df_metric = df[df["metric_name"] == metric_name]
            fig = plot_time_series(df_metric, metric_name).to_html(
                include_plotlyjs=True, full_html=False, config={"displayModeBar": False}
            )
            figs.append(fig)
        app.state.chart_cache[batch_name] = figs

    # Use cached charts
    figs = app.state.chart_cache[batch_name]

    return Card(
        Button("Refresh", hx_get=f"/batch/{batch_name}/refresh", hx_target="#content"),
        *map(lambda x: Safe(x), figs),
        cls="col-span-4",
    )


@rt("/batch/{batch_name}/refresh")
def get(batch_name: str, session):
    add_toast(session, f"Refreshing {batch_name} data", "info")
    # Clear caches for this batch
    if hasattr(app.state, "df_cache"):
        app.state.df_cache.pop(batch_name, None)
    if hasattr(app.state, "chart_cache"):
        app.state.chart_cache.pop(batch_name, None)
    # Call the main batch handler to get fresh data
    return get(batch_name, session)


serve(host="localhost", port=5003)
