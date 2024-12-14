

import plotly.graph_objects as go
import plotly.graph_objs as go
import plotly.io as pio
import requests
from plotly.subplots import make_subplots



def plot_time_series(df, metric_name) -> str:
    """
    Plot a time series with metric value and metric score and return the HTML representation.
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

    # Customize the layout
    fig.update_layout(
        title=f"{metric_name} Time Series",
        xaxis_title="Timestamp",
        yaxis_title="Metric Value",
        legend=dict(orientation="h", yanchor="bottom", y=-0.3, xanchor="center", x=0.5),
    )

    # Generate HTML string
    html_str = pio.to_html(fig, full_html=False)

    return html_str

def get_enabled_dagster_jobs(api_url: str) -> list:
    """
    Fetches all enabled jobs (with active schedules) from a Dagster instance using the GraphQL API.

    Args:
        api_url (str): The URL of the Dagster GraphQL API (e.g., http://localhost:3000/graphql).

    Returns:
        list: A list of enabled job names.
    """
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
        response = requests.post(api_url, json={"query": query})
        if response.status_code == 200:
            data = response.json()
            enabled_jobs = []
            for location in data["data"]["workspaceOrError"]["locationEntries"]:
                if "locationOrLoadError" in location and "repositories" in location["locationOrLoadError"]:
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
            print(f"Error: Received status code {response.status_code}")
            print(f"Response: {response.text}")
            return []
    except requests.exceptions.RequestException as e:
        print(f"Error connecting to Dagster GraphQL API: {e}")
        return []
