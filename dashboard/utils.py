import logging
import os
import requests
from dotenv import load_dotenv


log = logging.getLogger("fasthtml")


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


def get_metric_batches():
    enabled_jobs = get_enabled_dagster_jobs(host="http://localhost", port="3000")
    ingest_jobs = [job for job in enabled_jobs if job.endswith("_ingest")]
    metric_batches = [job[:-7] for job in ingest_jobs if job.endswith("_ingest")]
    return metric_batches
