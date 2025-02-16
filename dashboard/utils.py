
import logging
import os

import plotly.graph_objects as go
import requests
from dotenv import load_dotenv
from plotly.subplots import make_subplots

log = logging.getLogger("fasthtml")


def plot_time_series(df, metric_name) -> go.Figure:
    """
    Plot a time series with metric value and metric score.
    """

    # Create a figure with secondary y-axis
    fig = make_subplots(specs=[[{"secondary_y": True}]])

    # Add traces/lines for metric_value, metric_score, and metric_alert
    fig.add_trace(
        go.Scatter(x=df["metric_timestamp"], y=df["metric_value"], name="Metric Value"),
        secondary_y=False,
    )

    fig.add_trace(
        go.Scatter(
            x=df["metric_timestamp"],
            y=df["metric_score"],
            name="Metric Score",
            line=dict(dash="dot"),
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
                marker=dict(color="red", size=5),
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
                marker=dict(color="orange", size=5),
            ),
            secondary_y=True,
        )

    # Update x-axis and y-axes to remove gridlines, set the y-axis range
    # for metric score, and format as percentage
    fig.update_xaxes(showgrid=False, zeroline=False)
    fig.update_yaxes(showgrid=False, zeroline=False, secondary_y=False)
    fig.update_yaxes(
        showgrid=False,
        zeroline=False,
        range=[0, 1.1],
        tickformat=".0%",
        secondary_y=True,
    )

    # Set x-axis title
    fig.update_xaxes(title_text="Timestamp")

    # Set y-axes titles
    fig.update_yaxes(title_text="Metric Value", secondary_y=False)
    fig.update_yaxes(title_text="Metric Score", secondary_y=True)

    # Move legend to the top of the plot
    fig.update_layout(
        title_text=f"{metric_name} (n={len(df)})",
        hovermode="x",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        autosize=True,
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
