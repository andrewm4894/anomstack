"""
A dashboard to visualize metrics and alerts.

Run locally with:
$ streamlit run streamlit.py
"""

import pandas as pd
import streamlit as st
from dotenv import load_dotenv
from utils import plot_time_series, get_enabled_dagster_jobs

from anomstack.config import specs
from anomstack.jinja.render import render
from anomstack.sql.read import read_sql

load_dotenv()

st.set_page_config(layout="wide")


@st.cache_data(ttl=60)
def get_data(sql: str, db: str) -> pd.DataFrame:
    """
    Get data from the database.
    """
    df = read_sql(sql, db=db)

    return df


# Streamlit app
custom_css = """<style>a {text-decoration: none;}</style>"""
st.markdown(custom_css, unsafe_allow_html=True)
st.title("[Anomstack](https://github.com/andrewm4894/anomstack) Metrics Visualization")

# get metric batches of enabled jobs
enabled_jobs = get_enabled_dagster_jobs()
metric_batches = [batch for batch in list(specs.keys()) if f"{batch}_ingest" in enabled_jobs]

# inputs
last_n = st.sidebar.number_input("Last N:", min_value=1, value=5000)
batch_selection = st.sidebar.selectbox("Metric Batch:", metric_batches)

# get data
sql = render("dashboard_sql", specs[batch_selection], params={"alert_max_n": last_n})
db = specs[batch_selection]["db"]
df = get_data(sql, db)

# data based inputs
metric_names = ["ALL"]
unique_metrics = sorted(
    list(df[df["metric_batch"] == batch_selection]["metric_name"].unique())
)
metric_names.extend(unique_metrics)
metric_selection = st.sidebar.selectbox("Metric Name:", metric_names)

# filter data and plot
if metric_selection == "ALL":
    for metric in unique_metrics:
        filtered_df = df[
            (df["metric_batch"] == batch_selection) & (df["metric_name"] == metric)
        ].sort_values(by="metric_timestamp")

        # plot
        fig = plot_time_series(filtered_df, metric)
        st.plotly_chart(fig, use_container_width=True)
else:
    filtered_df = df[
        (df["metric_batch"] == batch_selection)
        & (df["metric_name"] == metric_selection)
    ].sort_values(by="metric_timestamp")

    # plot
    fig = plot_time_series(filtered_df, metric_selection)
    st.plotly_chart(fig, use_container_width=True)

with st.expander("Show SQL Query"):
    st.text(sql)
