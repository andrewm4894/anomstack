"""
Chart manager for the dashboard.
"""

from fasthtml.common import *
from monsterui.all import *
from fasthtml.svg import *
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from dashboard.app import app


class ChartManager:
    """
    Chart manager for the dashboard.
    """

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
            config={
                "displayModeBar":
                False,
                "displaylogo":
                False,
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
                "responsive":
                True,
                "scrollZoom":
                False,
                "staticPlot":
                False,
            },
        )

    @staticmethod
    def create_chart_placeholder(metric_name, index, batch_name):
        """
        Create a placeholder for a chart.
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
    """
    # Define height based on size toggle
    height = 250 if small_charts else 400

    # Theme-based colors
    colors = {
        "background": "#1a1a1a" if dark_mode else "white",
        "text": "#e5e7eb" if dark_mode else "#64748b",
        "grid": "rgba(255,255,255,0.1)" if dark_mode else "rgba(0,0,0,0.1)",
        "primary": "#3b82f6" if dark_mode else "#2563eb",
        "secondary": "#9ca3af" if dark_mode else "#64748b",
        "alert": "#ef4444" if dark_mode else "#dc2626",
        "change": "#fb923c" if dark_mode else "#f97316",
    }

    # Common styling configurations
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

    # Create figure with secondary y-axis
    fig = make_subplots(specs=[[{"secondary_y": True}]])

    # Add main metric value trace
    fig.add_trace(
        go.Scatter(
            x=df["metric_timestamp"],
            y=df["metric_value"],
            name="Metric Value",
            mode="lines" + ("+markers" if show_markers else ""),
            line=dict(color=colors["primary"], width=line_width),
            marker=(dict(size=6, color=colors["primary"], symbol="circle")
                    if show_markers else None),
            showlegend=show_legend,
        ),
        secondary_y=False,
    )

    # Add metric score trace
    fig.add_trace(
        go.Scatter(
            x=df["metric_timestamp"],
            y=df["metric_score"],
            name="Metric Score",
            line=dict(color=colors["secondary"], width=line_width, dash="dot"),
            showlegend=show_legend,
        ),
        secondary_y=True,
    )

    # Add alert and change markers if they exist
    for condition, props in {
            "metric_alert": dict(name="Metric Alert", color=colors["alert"]),
            "metric_change": dict(name="Metric Change",
                                  color=colors["change"]),
    }.items():
        condition_df = df[df[condition] == 1]
        if not condition_df.empty:
            fig.add_trace(
                go.Scatter(
                    x=condition_df["metric_timestamp"],
                    y=condition_df[condition],
                    mode="markers",
                    name=props["name"],
                    marker=dict(color=props["color"], size=8, symbol="circle"),
                    showlegend=show_legend,
                ),
                secondary_y=True,
            )

    # Update axes
    fig.update_xaxes(**common_grid)
    fig.update_yaxes(title_text="Metric Value",
                     secondary_y=False,
                     **common_grid)
    fig.update_yaxes(
        title_text="Metric Score",
        secondary_y=True,
        showgrid=False,
        range=[0, 1.1],
        tickformat=".0%",
        **{
            k: v
            for k, v in common_grid.items() if k != "showgrid"
        },
    )

    # Update layout
    fig.update_layout(
        plot_bgcolor=colors["background"],
        paper_bgcolor=colors["background"],
        hovermode="x unified",
        hoverdistance=100,
        showlegend=show_legend,
        legend=(dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="left",
            x=0,
            bgcolor=colors["background"],
            font=dict(color=colors["text"]),
        ) if show_legend else None),
        margin=dict(t=5, b=5, l=5, r=5),
        height=height,
    )

    return fig
