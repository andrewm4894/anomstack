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


def InfoCard(title, value, change):
    return Card(H3(value), P(change, cls=TextPresets.muted_sm), header=H4(title))


@rt
def index():

    # get enabled jobs from Dagster
    enabled_jobs = get_enabled_dagster_jobs()

    print(f"{enabled_jobs=}")

    figs = []

    rev = InfoCard("Total Revenue", "$45,231.89", "+20.1% from last month")
    sub = InfoCard("Subscriptions", "+2350", "+180.1% from last month")
    sal = InfoCard("Sales", "+12,234", "+19% from last month")
    act = InfoCard("Active Now", "+573", "+201 since last hour")

    info_card_data = [
        ("Total Revenue", "$45,231.89", "+20.1% from last month"),
        ("Subscriptions", "+2350", "+180.1% from last month"),
        ("Sales", "+12,234", "+19% from last month"),
        ("Active Now", "+573", "+201 since last hour"),
    ]

    top_info_row = Grid(*[InfoCard(*row) for row in info_card_data])

    # loop through metric batches
    for i, metric_batch in enumerate(specs, start=1):

        # check if the job is enabled
        if f"{metric_batch}_ingest" in enabled_jobs:

            print(f"job {metric_batch}_ingest is enabled.")

            spec = specs[metric_batch]
            sql = render("dashboard_sql", spec, params={"alert_max_n": 90})
            db = spec["db"]
            df = read_sql(sql, db=db)

            for metric_name in df["metric_name"].unique():

                print(f"metric_name: {metric_name}")

                metric_df = df[df["metric_name"] == metric_name]
                fig = Safe(
                        plot_time_series(metric_df, metric_name).to_html(
                            include_plotlyjs=True,
                            full_html=False,
                            config={"displayModeBar": False},
                        )
                    )
                figs.append(fig)

        else:
            print(f"job {metric_batch}_ingest is not enabled.")

    return (Title("Anomstack"), top_info_row, figs)


serve(host="localhost", port=5003)
