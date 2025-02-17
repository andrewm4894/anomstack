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
    anomaly_rate = df["metric_alert"].mean() if df["metric_alert"].sum() > 0 else 0
    avg_score = df["metric_score"].mean() if df["metric_score"].sum() > 0 else 0

    # Create a figure with secondary y-axis
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    
    # Create custom hover template with voting buttons
    hovertemplate = (
        "<b>%{x}</b><br>"
        "Value: %{y}<br>"
        "Score: %{customdata[0]:.1%}<br>"
        "<button onclick=\"submitVote('" + metric_name + "', '%{x}', 'up')\" "
        "style='color: green; border: none; background: none; cursor: pointer;'>"
        "👍"
        "</button>"
        "<button onclick=\"submitVote('" + metric_name + "', '%{x}', 'down')\" "
        "style='color: red; border: none; background: none; cursor: pointer;'>"
        "👎"
        "</button>"
        "<extra></extra>"
    )

    # Add traces with custom hover template
    fig.add_trace(
        go.Scatter(
            x=df["metric_timestamp"], 
            y=df["metric_value"],
            customdata=df[["metric_score"]],
            name="Metric Value",
            line=dict(color="#2563eb", width=2),
            hovertemplate=hovertemplate
        ),
        secondary_y=False,
    )

    fig.add_trace(
        go.Scatter(
            x=df["metric_timestamp"],
            y=df["metric_score"],
            name="Metric Score",
            line=dict(color="#64748b", width=2, dash="dot"),  # Muted color for score
        ),
        secondary_y=True,
    )

    alert_df = df[df["metric_alert"] == 1]
    if not alert_df.empty:
        fig.add_trace(
            go.Scatter(
                x=alert_df["metric_timestamp"],
                y=alert_df["metric_alert"],
                mode="markers",
                name="Metric Alert",
                marker=dict(color="#dc2626", size=8, symbol="circle"),  # Red alert markers
            ),
            secondary_y=True,
        )

    change_df = df[df["metric_change"] == 1]
    if not change_df.empty:
        fig.add_trace(
            go.Scatter(
                x=change_df["metric_timestamp"],
                y=change_df["metric_change"],
                mode="markers",
                name="Metric Change",
                marker=dict(color="#f97316", size=8, symbol="circle"),  # Orange change markers
            ),
            secondary_y=True,
        )

    # Update axes styling
    fig.update_xaxes(
        showgrid=True,
        gridwidth=1,
        gridcolor="rgba(0,0,0,0.1)",
        zeroline=False,
        tickfont=dict(size=10, color="#64748b"),
        title_font=dict(size=12, color="#64748b")
    )
    
    fig.update_yaxes(
        showgrid=True,
        gridwidth=1,
        gridcolor="rgba(0,0,0,0.1)",
        zeroline=False,
        tickfont=dict(size=10, color="#64748b"),
        title_font=dict(size=12, color="#64748b"),
        secondary_y=False
    )
    
    fig.update_yaxes(
        showgrid=False,
        zeroline=False,
        range=[0, 1.1],
        tickformat=".0%",
        tickfont=dict(size=10, color="#64748b"),
        title_font=dict(size=12, color="#64748b"),
        secondary_y=True,
    )

    # Set axis titles
    fig.update_xaxes(title_text="Timestamp")
    fig.update_yaxes(title_text="Metric Value", secondary_y=False)
    fig.update_yaxes(title_text="Metric Score", secondary_y=True)

    # Update layout to ensure hover works well
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
            font=dict(size=10, color="#64748b")
        ),
        # Add JavaScript for vote handling
        annotations=[dict(
            text="""
                <script>
                function submitVote(metricName, timestamp, vote) {
                    const url = `/batch/${window.location.pathname.split('/')[2]}/vote/${metricName}`;
                    fetch(url, {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/x-www-form-urlencoded',
                        },
                        body: `timestamp=${timestamp}&vote=${vote}`
                    });
                }
                </script>
            """,
            showarrow=False,
            x=0,
            y=0,
            xref='paper',
            yref='paper',
            xanchor='left',
            yanchor='bottom',
            font=dict(size=1),
        )],
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