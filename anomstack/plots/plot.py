"""
"""

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns


def make_alert_plot(df: pd.DataFrame, metric_name: str, threshold: float = 0.8) -> plt:
    """
    Creates a plot with two subplots: one for the metric values and another for the anomaly score.

    Args:
        df (pd.DataFrame): The dataframe containing the data to plot.
        metric_name (str): The name of the metric to plot.
        threshold (float, optional): The threshold value for the anomaly score. Defaults to 0.8.

    Returns:
        plt: The matplotlib figure object.
    """
    fig, axes = plt.subplots(
        nrows=2, ncols=1, figsize=(20, 10), gridspec_kw={"height_ratios": [2, 1]}
    )

    df_plot = df.set_index("metric_timestamp").sort_index()
    n = len(df_plot)

    ax1 = df_plot["metric_value"].plot(
        title=f'{metric_name} (n={n})', ax=axes[0], style="-o", color="royalblue"
    )
    if "metric_value_smooth" in df_plot.columns:
        df_plot["metric_value_smooth"].plot(
            ax=axes[0], style="--", color="darkorange", label="Value Smooth"
        )
    ax1.axes.get_xaxis().set_visible(False)
    ax1.grid(True, which="both", linestyle="--", linewidth=0.5)
    ax1.set_ylabel(metric_name)
    ax1.legend(loc="upper left")

    ax2 = df_plot["metric_score_smooth"].plot(
        title="Anomaly Score",
        ax=axes[1],
        rot=45,
        linestyle="--",
        color="seagreen",
        label="Score Smooth",
    )
    alert_points = df_plot[df_plot["metric_alert"] == 1]
    ax2.scatter(
        alert_points.index, alert_points["metric_alert"], color="red", label="Alerts"
    )
    ax2.axhline(
        threshold, color="lightgrey", linestyle="-.", label=f"Threshold ({threshold})"
    )
    ax2.xaxis.set_major_locator(plt.MaxNLocator(n))
    ax2.set_xticklabels(
        [f'{item.strftime("%Y-%m-%d %H:%M")}' for item in df_plot.index.tolist()],
        rotation=45,
    )
    ax2.set_ylabel("Score")
    ax2.set_ylim(0, 1)
    ax2.legend(loc="upper left")
    ax2.grid(False)

    for idx in alert_points.index:
        ax1.axvline(idx, color="yellow", alpha=0.3)
        ax2.axvline(idx, color="yellow", alpha=0.3)

    plt.tight_layout()

    return fig


def make_batch_plot(df: pd.DataFrame) -> plt.Figure:
    """ """

    unique_metrics = df["metric_name"].unique()
    colors = sns.color_palette("viridis", len(unique_metrics))

    fig, axs = plt.subplots(
        len(unique_metrics), 1, figsize=(10, 3 * len(unique_metrics))
    )

    if len(unique_metrics) == 1:
        axs = [axs]

    for i, metric in enumerate(unique_metrics):
        ax1 = axs[i]
        metric_data = df[df["metric_name"] == metric]
        n = len(metric_data)

        sns.lineplot(
            data=metric_data,
            x="metric_timestamp",
            y="metric_value",
            label="Metric Value",
            color=colors[i],
            ax=ax1,
            legend=True,
        )
        ax1.set_ylabel("Metric Value")
        ax1.tick_params(axis="y", labelcolor=colors[i])

        ax2 = ax1.twinx()
        sns.lineplot(
            data=metric_data,
            x="metric_timestamp",
            y="metric_score",
            label="Metric Score",
            color=colors[i],
            linestyle="dashed",
            ax=ax2,
            legend=False,
        )
        ax2.set_ylabel("Metric Score")
        ax2.set_ylim(0, 1)
        ax2.tick_params(axis="y", labelcolor=colors[i])

        ax1.set_title(f"{metric} - value vs score (n={n})")

    plt.tight_layout()

    return fig
