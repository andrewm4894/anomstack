"""
A dashboard to visualize metrics and alerts.

Run locally with:
$ streamlit run dashboard.py
"""

import pandas as pd
import plotly.graph_objs as go
import streamlit as st
from dotenv import load_dotenv
from plotly.subplots import make_subplots

from anomstack.config import specs
from anomstack.jinja.render import render
from anomstack.sql.read import read_sql

load_dotenv()

st.set_page_config(layout="wide")


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

    # Update x-axis and y-axes to remove gridlines, set the y-axis range for metric score, and format as percentage
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

# get metric batches
metric_batches = list(specs.keys())

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
