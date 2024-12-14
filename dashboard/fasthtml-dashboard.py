import logging

from fasthtml.common import Title, fast_app, serve
from fh_plotly import plotly2fasthtml, plotly_headers
from utils import get_enabled_dagster_jobs, plot_time_series

from anomstack.config import specs
from anomstack.jinja.render import render
from anomstack.sql.read import read_sql

log = logging.getLogger("fasthtml")

app, rt = fast_app(hdrs=(plotly_headers,))


@app.get('/')
def home():

    # get enabled jobs from Dagster
    enabled_jobs = get_enabled_dagster_jobs()

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
                fig = plotly2fasthtml(plot_time_series(metric_df, metric_name))
                figs.append(fig)

        else:
            log.debug(f"job {metric_batch}_ingest is not enabled.")

    return (
        Title("Anomstack"),
        figs
        )



serve()
