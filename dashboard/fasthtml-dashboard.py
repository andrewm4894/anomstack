import logging

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


@rt
def index():

    print(f"{specs.keys()=}")

    enabled_jobs = get_enabled_dagster_jobs(host="http://localhost", port="3000")
    print(f"{enabled_jobs=}")

    ingest_jobs = [job for job in enabled_jobs if job.endswith("_ingest")]
    print(f"{ingest_jobs=}")

    metric_batches = [job[:-7] for job in ingest_jobs if job.endswith("_ingest")]
    print(f"{metric_batches=}")

    top_nav = TabContainer(
        *map(lambda x: Li(A(x)), metric_batches),
        alt=True,
        cls="top-nav",
    )

    specs_enabled = {}
    for metric_batch in metric_batches:
        specs_enabled[metric_batch] = specs[metric_batch]
    # print(f"{specs_enabled=}")
    
    return (Title("Anomstack"), top_nav)


serve(host="localhost", port=5003)
