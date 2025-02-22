import logging
import os
import pandas as pd

import plotly.graph_objects as go
import requests
from dotenv import load_dotenv
from plotly.subplots import make_subplots
from anomstack.jinja.render import render
from anomstack.sql.read import read_sql


log = logging.getLogger("fasthtml")


def plot_time_series(df, metric_name) -> go.Figure:
    """
    Plot a time series with metric value and metric score.
    """
    # Common styling configurations
    common_font = dict(size=10, color="#64748b")
    common_title_font = dict(size=12, color="#64748b")
    common_grid = dict(
        showgrid=True,
        gridwidth=1,
        gridcolor="rgba(0,0,0,0.1)",
        zeroline=False,
        tickfont=common_font,
        title_font=common_title_font,
    )

    # Create figure with secondary y-axis
    fig = make_subplots(specs=[[{"secondary_y": True}]])

    # Add main metric value trace
    fig.add_trace(
        go.Scatter(
            x=df["metric_timestamp"],
            y=df["metric_value"],
            name="Metric Value",
            mode="lines+markers",
            line=dict(color="#2563eb", width=2),
            marker=dict(size=6, color="#2563eb", symbol="circle"),
        ),
        secondary_y=False,
    )

    # Add metric score trace
    fig.add_trace(
        go.Scatter(
            x=df["metric_timestamp"],
            y=df["metric_score"],
            name="Metric Score",
            line=dict(color="#64748b", width=2, dash="dot"),
        ),
        secondary_y=True,
    )

    # Add alert and change markers if they exist
    for condition, props in {
        "metric_alert": dict(name="Metric Alert", color="#dc2626"),
        "metric_change": dict(name="Metric Change", color="#f97316"),
    }.items():
        condition_df = df[df[condition] == 1]
        if not condition_df.empty:
            fig.add_trace(
                go.Scatter(
                    x=condition_df["metric_timestamp"],
                    y=condition_df[condition],
                    mode="markers",
                    name=props["name"],
                    marker=dict(color=props["color"], size=8, symbol="circle"),
                ),
                secondary_y=True,
            )

    # Update axes
    fig.update_xaxes(title_text="Timestamp", **common_grid)
    fig.update_yaxes(title_text="Metric Value", secondary_y=False, **common_grid)
    fig.update_yaxes(
        title_text="Metric Score",
        secondary_y=True,
        showgrid=False,
        range=[0, 1.1],
        tickformat=".0%",
        **{k: v for k, v in common_grid.items() if k != "showgrid"}
    )

    # Update layout
    fig.update_layout(
        plot_bgcolor="white",
        paper_bgcolor="white",
        hovermode="x unified",
        hoverdistance=100,
        legend=dict(
            orientation="h",
            yanchor="top",
            y=1.02,
            xanchor="center",
            x=0.5,
            bgcolor="rgba(255,255,255,0.8)",
            bordercolor="rgba(0,0,0,0.1)",
            borderwidth=1,
            font=common_font
        )
    )

    return fig


def get_enabled_dagster_jobs(host: str = "localhost", port: str = "3000") -> list:
    """
    Fetches all enabled jobs (with active schedules) from a Dagster instance
    using the GraphQL API.

    Args:
        host (str): The host of the Dagster instance
            (e.g., http://localhost).
        port (str): The port of the Dagster instance
            (e.g., 3000).

    Returns:
        list: A list of enabled job names.
    """

    load_dotenv('./.env')

    # Resolve DAGSTER_HOME to an absolute path
    dagster_home = os.getenv("DAGSTER_HOME", "./")
    dagster_home_absolute = os.path.abspath(dagster_home)
    os.environ["DAGSTER_HOME"] = dagster_home_absolute

    # Infer Dagster GraphQL API URL from environment variable or default to localhost
    dagster_graphql_url = f"{host}:{port}/graphql"

    query = """
    query {
      workspaceOrError {
        __typename
        ... on Workspace {
          locationEntries {
            name
            locationOrLoadError {
              ... on RepositoryLocation {
                repositories {
                  name
                  jobs {
                    name
                    isJob
                    schedules {
                      name
                      scheduleState {
                        status
                      }
                    }
                  }
                }
              }
            }
          }
        }
      }
    }
    """

    try:
        response = requests.post(dagster_graphql_url, json={"query": query})
        if response.status_code == 200:
            data = response.json()
            enabled_jobs = []
            for location in data["data"]["workspaceOrError"]["locationEntries"]:
                if "locationOrLoadError" in location and "repositories" in location["locationOrLoadError"]:  # noqa: E501
                    for repo in location["locationOrLoadError"]["repositories"]:
                        for job in repo["jobs"]:
                            # Check if the job has any active schedules
                            has_active_schedule = any(
                                schedule["scheduleState"]["status"] == "RUNNING"
                                for schedule in job["schedules"]
                            )
                            if has_active_schedule:
                                enabled_jobs.append(job["name"])
            return enabled_jobs
        else:
            log.info(f"Error: Received status code {response.status_code}")
            log.info(f"Response: {response.text}")
            return []
    except requests.exceptions.RequestException as e:
        log.info(f"Error connecting to Dagster GraphQL API: {e}")
        return []


def get_data(spec: dict, alert_max_n: int = 30) -> pd.DataFrame:
    sql = render(
        "dashboard_sql",
        spec,
        params={"alert_max_n": alert_max_n},
    )
    db = spec["db"]
    df = read_sql(sql, db=db)
    return df


def get_metric_batches():
    enabled_jobs = get_enabled_dagster_jobs(host="http://localhost", port="3000")
    ingest_jobs = [job for job in enabled_jobs if job.endswith("_ingest")]
    metric_batches = [job[:-7] for job in ingest_jobs if job.endswith("_ingest")]
    return metric_batches