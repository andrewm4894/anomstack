"""
dashboard/charts.py

Chart manager for the dashboard.

This module contains the ChartManager class, which is responsible for creating charts for the dashboard.

"""

import pandas as pd
import plotly.graph_objects as go
from fasthtml.common import Div, P
from monsterui.all import Card, DivLAligned, Loading, LoadingT, TextPresets
from plotly.subplots import make_subplots

from dashboard.app import app


class ChartManager:
    """
    Chart manager for the dashboard.
    """

    @staticmethod
    def get_chart_config():
        """Return the common chart configuration."""
        return {
            "displayModeBar": False,
            "displaylogo": False,
            "modeBarButtonsToRemove": [
                "zoom2d",
                "pan2d",
                "select2d",
                "lasso2d",
                "zoomIn2d",
                "zoomOut2d",
                "autoScale2d",
                "resetScale2d",
            ],
            "responsive": True,
            "scrollZoom": False,
            "staticPlot": False,
        }

    @staticmethod
    def create_chart(df_metric, chart_index):
        """
        Create a chart for a given metric.
        """
        return plot_time_series(
            df_metric,
            small_charts=app.state.small_charts,
            dark_mode=app.state.dark_mode,
            show_markers=app.state.show_markers,
            line_width=app.state.line_width,
            show_legend=app.state.show_legend,
        ).to_html(
            div_id=f"plotly-chart-{chart_index}",
            include_plotlyjs=False,
            full_html=False,
            config=ChartManager.get_chart_config(),
        )

    @staticmethod
    def create_chart_placeholder(metric_name, index, batch_name) -> Card:
        """
        Create a placeholder for a chart.

        Args:
            metric_name (str): The name of the metric.
            index (int): The index of the chart.
            batch_name (str): The name of the batch.

        Returns:
            Card: The placeholder for the chart.
        """
        return Card(
            Div(
                DivLAligned(
                    Loading((LoadingT.spinner, LoadingT.sm)),
                    P(f"Loading {metric_name}...", cls=TextPresets.muted_sm),
                    cls="space-x-2",
                ),
                cls="px-2 py-2",
            ),
            id=f"chart-{index}",
            hx_get=f"/batch/{batch_name}/chart/{index}",
            hx_trigger="load",
            hx_swap="outerHTML",
        )

    @staticmethod
    def create_sparkline(df_metric: pd.DataFrame, anomaly_timestamp: pd.Timestamp = None) -> str:
        """Create a sparkline chart for a metric.

        Args:
            df_metric (pd.DataFrame): The metric data.
            anomaly_timestamp (pd.Timestamp): The specific timestamp of the anomaly to mark.

        Returns:
            str: The HTML for the sparkline.
        """
        colors = ChartStyle.get_colors(app.state.dark_mode)
        fig = make_subplots(specs=[[{"secondary_y": True}]])

        # Add the main line
        fig.add_trace(
            go.Scatter(
                x=df_metric["metric_timestamp"],
                y=df_metric["metric_value"],
                name="Value",
                mode="lines",
                line=dict(
                    color=colors["primary"],
                    width=1,
                ),
                showlegend=False,
                connectgaps=True,
            ),
            secondary_y=False,
        )

        # Add the score line
        fig.add_trace(
            go.Scatter(
                x=df_metric["metric_timestamp"],
                y=df_metric["metric_score"],
                name="Score",
                mode="lines",
                line=dict(
                    color=colors["secondary"],
                    width=1,
                    dash="dot",
                ),
                showlegend=False,
                connectgaps=True,
            ),
            secondary_y=True,
        )

        # Add marker for the specific anomaly point if provided
        if anomaly_timestamp is not None:
            anomaly_point = df_metric[df_metric['metric_timestamp'] == anomaly_timestamp]
            if not anomaly_point.empty:
                alert_color = colors["llmalert"] if df_metric["metric_llmalert"].iloc[-1] == 1 else colors["alert"]
                fig.add_trace(
                    go.Scatter(
                        x=[anomaly_point["metric_timestamp"].iloc[0]],
                        y=[anomaly_point["metric_value"].iloc[0]],
                        name="Alert",
                        mode="markers",
                        marker=dict(
                            color=alert_color,
                            size=8,
                            symbol="diamond",
                        ),
                        showlegend=False,
                    ),
                    secondary_y=False,
                )

        fig.update_layout(
            height=50,
            width=200,
            margin=dict(l=0, r=0, t=0, b=0),
            xaxis=dict(
                showgrid=False,
                showticklabels=False,
                zeroline=False,
            ),
            yaxis=dict(
                showgrid=False,
                showticklabels=False,
                zeroline=False,
            ),
            yaxis2=dict(
                showgrid=False,
                showticklabels=False,
                zeroline=False,
                range=[0, 1.05],
            ),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            modebar=dict(remove=["zoom", "pan", "select", "lasso", "zoomIn", "zoomOut", "autoScale", "resetScale"]),
        )

        return fig.to_html(
            full_html=False,
            include_plotlyjs=False,
            config=dict(displayModeBar=False),
        )


class ChartStyle:
    """Handle chart styling and theme-related configurations."""

    @staticmethod
    def get_colors(dark_mode: bool) -> dict:
        """Return theme-based colors."""
        return {
            "background": "#1a1a1a" if dark_mode else "white",
            "text": "#e5e7eb" if dark_mode else "#64748b",
            "grid": "rgba(255,255,255,0.1)" if dark_mode else "rgba(0,0,0,0.1)",
            "primary": "#3b82f6" if dark_mode else "#2563eb",
            "secondary": "#9ca3af" if dark_mode else "#64748b",
            "alert": "#ef4444" if dark_mode else "#dc2626",
            "llmalert": "#f97316" if dark_mode else "#fb923c",
            "change": "#fb923c" if dark_mode else "#f97316",
        }

    @staticmethod
    def get_common_styling(colors: dict) -> tuple:
        """Return common styling configurations."""
        common_font = dict(size=10, color=colors["text"])
        common_title_font = dict(size=12, color=colors["text"])
        common_grid = dict(
            showgrid=True,
            gridwidth=1,
            gridcolor=colors["grid"],
            zeroline=False,
            tickfont=common_font,
            title_font=common_title_font,
        )
        return common_font, common_title_font, common_grid


def plot_time_series(
    df,
    small_charts=False,
    dark_mode=False,
    show_markers=True,
    line_width=2,
    show_legend=False,
) -> go.Figure:
    """
    Plot a time series with metric value and metric score.

    Args:
        df: DataFrame with metric data
        small_charts: Whether to use small chart size
        dark_mode: Whether to use dark mode styling
        show_markers: Whether to show line markers
        line_width: Width of the lines (1-10)
        show_legend: Whether to show the legend

    Returns:
        go.Figure: The plotly figure
    """
    df["metric_llmalert"] = df["metric_llmalert"].clip(upper=1)
    colors = ChartStyle.get_colors(dark_mode)
    _, _, common_grid = ChartStyle.get_common_styling(colors)

    # Define height based on size toggle
    height = 250 if small_charts else 400

    # Create figure with secondary y-axis
    fig = make_subplots(specs=[[{"secondary_y": True}]])

    # Add main metric value trace
    _add_main_metric_trace(fig, df, colors, show_markers, line_width, show_legend)

    # Add metric score trace
    _add_score_trace(fig, df, colors, line_width, show_legend)

    # Add alert and change markers if they exist
    _add_condition_traces(fig, df, colors, line_width, show_legend)

    # Update axes
    _update_axes_and_layout(fig, common_grid, colors, show_legend, height)

    return fig


def _add_main_metric_trace(fig, df, colors, show_markers, line_width, show_legend):
    """Add the main metric value trace to the figure."""
    fig.add_trace(
        go.Scatter(
            x=df["metric_timestamp"],
            y=df["metric_value"],
            name="Value",
            mode="lines" + ("+markers" if show_markers else ""),
            line=dict(color=colors["primary"], width=line_width),
            marker=(
                dict(size=line_width + 4, color=colors["primary"], symbol="circle")
                if show_markers
                else None
            ),
            showlegend=show_legend,
            connectgaps=True,
            hovertemplate=(
                f'<span style="color: {colors["primary"]}"><b>Value</b>: %{{y:.2f}}<br>'
                f"Time: %{{x}}</span><extra></extra>"
            ),
        ),
        secondary_y=False,
    )


def _add_score_trace(fig, df, colors, line_width, show_legend):
    """Add the metric score trace to the figure."""
    fig.add_trace(
        go.Scatter(
            x=df["metric_timestamp"],
            y=df["metric_score"],
            name="Score",
            line=dict(color=colors["secondary"], width=line_width, dash="dot"),
            showlegend=show_legend,
            connectgaps=True,
            hovertemplate=(
                f'<span style="color: {colors["secondary"]}"><b>Score</b>: %{{y:.1%}}<br>'
                f"Time: %{{x}}</span><extra></extra>"
            ),
        ),
        secondary_y=True,
    )


def _add_condition_traces(fig, df, colors, line_width, show_legend):
    """Add alert and change markers to the figure."""
    for condition, props in {
        "metric_alert": dict(
            name="Alert",
            color=colors["alert"],
            hovertemplate=(
                f'<span style="color: {colors["alert"]}">'
                f"<b>Alert</b><br>"
                "Time: %{x}"
                "</span><extra></extra>"
            ),
        ),
        "metric_llmalert": dict(
            name="LLM Alert",
            color=colors["llmalert"],
            hovertemplate=(
                f'<span style="color: {colors["llmalert"]}">'
                f"<b>LLM Alert</b><br>"
                "Time: %{x}<br>"
                "<b>Details</b>: %{customdata}"
                "</span><extra></extra>"
            ),
        ),
        "metric_change": dict(
            name="Change",
            color=colors["change"],
            hovertemplate=(
                f'<span style="color: {colors["change"]}">'
                f"<b>Change</b><br>"
                "Time: %{x}"
                "</span><extra></extra>"
            ),
        ),
    }.items():
        condition_df = df[df[condition] == 1]
        if not condition_df.empty:
            fig.add_trace(
                go.Scatter(
                    x=condition_df["metric_timestamp"],
                    y=condition_df[condition],
                    mode="markers",
                    name=props["name"],
                    marker=dict(
                        color=props["color"], size=line_width + 4, symbol="circle"
                    ),
                    showlegend=show_legend,
                    customdata=condition_df["anomaly_explanation"],
                    hovertemplate=props["hovertemplate"],
                ),
                secondary_y=True,
            )


def _update_axes_and_layout(fig, common_grid, colors, show_legend, height):
    """Update axes and layout of the figure."""
    # Update axes
    fig.update_xaxes(**common_grid)
    fig.update_yaxes(title_text="Value", secondary_y=False, **common_grid)
    fig.update_yaxes(
        title_text="Score",
        secondary_y=True,
        showgrid=False,
        range=[0, 1.05],
        tickformat=".0%",
        **{k: v for k, v in common_grid.items() if k != "showgrid"},
    )

    # Update layout
    fig.update_layout(
        plot_bgcolor=colors["background"],
        paper_bgcolor=colors["background"],
        hovermode="closest",
        hoverdistance=100,
        showlegend=show_legend,
        legend=(
            dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="left",
                x=0,
                bgcolor=colors["background"],
                font=dict(color=colors["text"]),
            )
            if show_legend
            else None
        ),
        margin=dict(t=5, b=5, l=5, r=5),
        height=height,
        hoverlabel=dict(
            bgcolor="white",
            bordercolor="white",
            font=dict(size=12),
        ),
    )
