import logging
import os

from dotenv import load_dotenv
from fasthtml.common import Div, P, Table, fast_app, serve
from utils import get_enabled_dagster_jobs

from anomstack.config import specs
from anomstack.jinja.render import render
from anomstack.sql.read import read_sql

load_dotenv('./.env')


# Resolve DAGSTER_HOME to an absolute path
dagster_home = os.getenv("DAGSTER_HOME", "./")
dagster_home_absolute = os.path.abspath(dagster_home)
os.environ["DAGSTER_HOME"] = dagster_home_absolute

# Infer Dagster GraphQL API URL from environment variable or default to localhost
dagster_host = os.getenv("DAGSTER_HOST", "http://localhost")
dagster_port = os.getenv("DAGSTER_PORT", "3000")
dagster_graphql_url = f"{dagster_host}:{dagster_port}/graphql"

print(f"DAGSTER_HOME resolved to: {os.environ['DAGSTER_HOME']}")
print(f"Dagster GraphQL API URL: {dagster_graphql_url}")


# Configure logging
logging.basicConfig(level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s")
log = logging.getLogger("fasthtml")

app,rt = fast_app(debug=False)


@rt('/')
def get():

    # get enabled jobs from Dagster
    enabled_jobs = get_enabled_dagster_jobs(dagster_graphql_url)

    figs = []

    # loop through metric batches
    for i, metric_batch in enumerate(specs, start=1):

        if i > 3:
            break

        # check if the job is enabled
        if f'{metric_batch}_ingest' in enabled_jobs:

            spec = specs[metric_batch]
            sql = render("dashboard_sql", spec, params={"alert_max_n": 90})
            db = spec["db"]
            df = read_sql(sql, db=db)

            for metric_name in df["metric_name"].unique():

                metric_df = df[df["metric_name"] == metric_name]
                # fig = plot_time_series(metric_df, metric_name)

                div = Div(
                    P(f"Metric Batch: {metric_batch}"),
                    P(f"Metric Name: {metric_name}"),
                    Table(metric_df.head().to_html()),
                )
                figs.append(div)

        else:
            log.debug(f"job {metric_batch}_ingest is not enabled.")

    return figs



serve(host="0.0.0.0", port=5002)
