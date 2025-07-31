def ingest():
    """
    Ingest headline metrics from GitHub for a list of repositories.
    For each repo, the script retrieves key metrics from the GitHub API and
    returns a DataFrame with columns:
        - metric_timestamp: the time of ingestion (floored to the second)
        - metric_name: a composed name in the form github.<owner>.<repo>.<metric>
        - metric_value: the numeric value for that metric

    Headline metrics extracted include:
        - stargazers_count
        - forks_count
        - open_issues_count
        - subscribers_count
        - size
    """
    import pandas as pd
    from dagster import get_dagster_logger
    import requests

    logger = get_dagster_logger()

    # List of GitHub repositories in the format "owner/repo"
    repos = [
        "andrewm4894/anomstack",
        "netdata/netdata",
        "tensorflow/tensorflow",
        "apache/spark",
        "apache/airflow",
        "stanfordnlp/dspy",
        "scikit-learn/scikit-learn",
    ]

    # Define the headline metric keys to extract from each repository's JSON.
    metric_keys = [
        "stargazers_count",
        "forks_count",
        "open_issues_count",
        "subscribers_count",
        "size",
    ]

    all_rows = []
    for repo in repos:
        url = f"https://api.github.com/repos/{repo}"
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
        except requests.RequestException as e:
            logger.error(f"Failed to fetch data for repo {repo} from {url}: {e}")
            continue

        repo_data = response.json()
        # Use current UTC time as the ingestion timestamp, floored to the second.
        ts = pd.Timestamp.utcnow().floor("S")

        for key in metric_keys:
            value = repo_data.get(key)
            try:
                metric_value = float(value)
            except (TypeError, ValueError):
                continue  # Skip non-numeric values

            # Build a metric name in the format: github.<owner>.<repo>.<metric>
            # Replace the "/" in repo names with "."
            metric_name = f"github.{repo.replace('/', '.')}.{key}"
            all_rows.append(
                {"metric_timestamp": ts, "metric_name": metric_name, "metric_value": metric_value}
            )

    df = pd.DataFrame(all_rows)

    # Drop duplicates based on the timestamp and metric name.
    df = df.drop_duplicates(subset=["metric_timestamp", "metric_name"])
    logger.debug(f"df:\n{df}")

    # Ensure the DataFrame has the expected column order.
    df = df[["metric_timestamp", "metric_name", "metric_value"]]

    return df
