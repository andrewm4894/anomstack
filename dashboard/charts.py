"""
dashboard/charts.py

Chart manager for the dashboard.

This module contains the ChartManager class, which is responsible for creating charts for the dashboard.

"""

from fasthtml.common import Div, P
from monsterui.all import Card, DivLAligned, Loading, LoadingT, TextPresets, ApexChart
import pandas as pd
import json
from datetime import datetime


class ChartManager:
    """
    Chart manager for the dashboard.
    """

    @staticmethod
    def get_chart_config(small_charts=False, dark_mode=False):
        """Return the common ApexChart configuration."""
        return {
            "chart": {
                "type": "line",
                "height": 250 if small_charts else 400,
                "zoom": {
                    "enabled": True
                },
                "toolbar": {
                    "show": False
                },
                "animations": {
                    "enabled": False
                }
            },
            "theme": {
                "mode": "dark" if dark_mode else "light"
            },
            "responsive": [{
                "breakpoint": 480,
                "options": {
                    "chart": {
                        "height": 200
                    }
                }
            }]
        }

    @staticmethod
    def create_chart(df_metric, chart_index, small_charts=False, dark_mode=False, show_markers=True, line_width=2, show_legend=False):
        """
        Create a chart for a given metric using ApexChart.
        """
        chart_opts = ChartManager._build_time_series_chart(
            df_metric,
            small_charts=small_charts,
            dark_mode=dark_mode,
            show_markers=show_markers,
            line_width=line_width,
            show_legend=show_legend,
        )
        
        return ApexChart(
            opts=chart_opts,
            id=f"apex-chart-{chart_index}"
        )

    @staticmethod
    def _build_time_series_chart(df_metric, small_charts=False, dark_mode=False, show_markers=True, line_width=2, show_legend=False):
        """Build ApexChart configuration for time series data."""
        colors = ChartStyle.get_colors(dark_mode)
        
        # Convert timestamps to milliseconds for ApexCharts
        timestamps = [int(pd.to_datetime(ts).timestamp() * 1000) for ts in df_metric["metric_timestamp"]]
        
        # Prepare main metric data (ensure native Python types for JSON serialization)
        value_data = [[int(ts), float(val)] for ts, val in zip(timestamps, df_metric["metric_value"])]
        score_data = [[int(ts), float(val)] for ts, val in zip(timestamps, df_metric["metric_score"])]
        
        # Build series array
        series = [
            {
                "name": "Value",
                "type": "line",
                "data": value_data,
                "yAxisIndex": 0,
                "color": colors["primary"],
                "marker": {
                    "size": 4 if show_markers else 0
                }
            },
            {
                "name": "Score", 
                "type": "line",
                "data": score_data,
                "yAxisIndex": 1,
                "color": colors["secondary"],
                "marker": {
                    "size": 0  # Never show markers on score line
                }
            }
        ]
        
        # Add alert markers if they exist (on score axis at y=1)
        alert_data = df_metric[df_metric["metric_alert"] == 1]
        if not alert_data.empty:
            alert_timestamps = [int(pd.to_datetime(ts).timestamp() * 1000) for ts in alert_data["metric_timestamp"]]
            # Put all alert markers at y=1 on the score axis
            alert_values = [[int(ts), 1.0] for ts in alert_timestamps]
            series.append({
                "name": "Alert",
                "type": "line",
                "data": alert_values,
                "yAxisIndex": 1,  # Score axis
                "color": colors["alert"],
                "fill": {
                    "opacity": 1
                },
                "stroke": {
                    "width": 0,  # No line, just markers
                    "lineCap": "round"
                }
            })
        
        # Add LLM alert markers if they exist (on score axis at y=1)
        llm_alert_data = df_metric[df_metric["metric_llmalert"] == 1]
        if not llm_alert_data.empty:
            llm_timestamps = [int(pd.to_datetime(ts).timestamp() * 1000) for ts in llm_alert_data["metric_timestamp"]]
            # Put all LLM alert markers at y=1 on the score axis
            llm_values = [[int(ts), 1.0] for ts in llm_timestamps]
            series.append({
                "name": "LLM Alert",
                "type": "line", 
                "data": llm_values,
                "yAxisIndex": 1,  # Score axis
                "color": colors["llmalert"],
                "fill": {
                    "opacity": 1
                },
                "stroke": {
                    "width": 0,  # No line, just markers
                    "lineCap": "round"
                }
            })
        
        # Build chart configuration
        config = ChartManager.get_chart_config(small_charts, dark_mode)
        config.update({
            "series": series,
            "xaxis": {
                "type": "datetime",
                "labels": {
                    "format": "HH:mm",
                    "style": {
                        "colors": colors["text"]
                    }
                }
            },
            "yaxis": [
                {
                    "title": {
                        "text": "Value",
                        "style": {
                            "color": colors["text"]
                        }
                    },
                    "labels": {
                        "style": {
                            "colors": colors["text"]
                        }
                    }
                },
                {
                    "opposite": True,
                    "title": {
                        "text": "Score", 
                        "style": {
                            "color": colors["text"]
                        }
                    },
                    "labels": {
                        "style": {
                            "colors": colors["text"]
                        }
                    },
                    "min": 0,
                    "max": 1
                }
            ],
            "stroke": {
                "width": [line_width, line_width, 0, 0],  # Line widths for each series
                "dashArray": [0, 5, 0, 0]  # Dash patterns (score line dashed)
            },
            "markers": {
                "size": [4 if show_markers else 0, 0, 4, 4],  # Much smaller alert markers
                "colors": [colors["primary"], "undefined", colors["alert"], colors["llmalert"]],  # Value markers same as blue line
                "strokeWidth": [1, 0, 1, 1],
                "strokeColors": ["#ffffff", "#ffffff", "#ffffff", "#ffffff"],
                "hover": {
                    "size": [6 if show_markers else 0, 0, 6, 6]  # Smaller hover too
                }
            },
            "legend": {
                "show": show_legend,
                "position": "top",
                "horizontalAlign": "left",
                "labels": {
                    "colors": colors["text"]
                }
            },
            "grid": {
                "borderColor": colors["grid"]
            },
            "tooltip": {
                "theme": "dark" if dark_mode else "light",
                "x": {
                    "format": "dd MMM yyyy HH:mm"
                }
            }
        })
        
        return config

    @staticmethod
    def create_expanded_chart(df_metric, chart_index, dark_mode=False, show_markers=True, line_width=2):
        """
        Create an expanded chart for modal display with enhanced interactivity.
        """
        chart_opts = ChartManager._build_time_series_chart(
            df_metric,
            small_charts=False,  # Always use large size for expanded view
            dark_mode=dark_mode,
            show_markers=show_markers,
            line_width=line_width,
            show_legend=True,  # Always show legend in expanded view
        )
        
        # Override chart height for expanded view
        chart_opts["chart"]["height"] = 600
        chart_opts["chart"]["toolbar"]["show"] = True  # Show toolbar in expanded view
        chart_opts["chart"]["zoom"]["enabled"] = True
        
        return ApexChart(
            opts=chart_opts,
            id=f"apex-chart-expanded-{chart_index}"
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
    def create_sparkline(df_metric: pd.DataFrame, anomaly_timestamp: pd.Timestamp = None, dark_mode=False):
        """Create a sparkline chart for a metric.

        Args:
            df_metric (pd.DataFrame): The metric data.
            anomaly_timestamp (pd.Timestamp): The specific timestamp of the anomaly to mark.
            dark_mode (bool): Whether to use dark mode styling.

        Returns:
            ApexChart: The sparkline chart component.
        """
        colors = ChartStyle.get_colors(dark_mode)
        
        # Convert timestamps to milliseconds
        timestamps = [int(pd.to_datetime(ts).timestamp() * 1000) for ts in df_metric["metric_timestamp"]]
        
        # Prepare data (ensure native Python types for JSON serialization)
        value_data = [[int(ts), float(val)] for ts, val in zip(timestamps, df_metric["metric_value"])]
        score_data = [[int(ts), float(val)] for ts, val in zip(timestamps, df_metric["metric_score"])]
        
        series = [
            {
                "name": "Value",
                "type": "line",
                "data": value_data,
                "yAxisIndex": 0,
                "color": colors["primary"]
            },
            {
                "name": "Score",
                "type": "line", 
                "data": score_data,
                "yAxisIndex": 1,
                "color": colors["secondary"]
            }
        ]
        
        # Add specific anomaly marker if provided
        if anomaly_timestamp is not None:
            anomaly_point = df_metric[df_metric["metric_timestamp"] == anomaly_timestamp]
            if not anomaly_point.empty:
                alert_color = (
                    colors["llmalert"]
                    if anomaly_point["metric_llmalert"].iloc[0] == 1
                    else colors["alert"]
                )
                anomaly_ts = int(pd.to_datetime(anomaly_timestamp).timestamp() * 1000)
                series.append({
                    "name": "Alert",
                    "type": "scatter",
                    "data": [[int(anomaly_ts), float(anomaly_point["metric_value"].iloc[0])]],
                    "yAxisIndex": 0,
                    "color": alert_color
                })
        
        chart_opts = {
            "chart": {
                "type": "line",
                "height": 50,
                "width": 200,
                "sparkline": {
                    "enabled": True
                },
                "toolbar": {
                    "show": False
                },
                "animations": {
                    "enabled": False
                }
            },
            "series": series,
            "stroke": {
                "width": [1, 1, 0],
                "dashArray": [0, 3, 0]
            },
            "markers": {
                "size": [0, 0, 6]
            },
            "yaxis": [
                {
                    "show": False
                },
                {
                    "show": False,
                    "min": 0,
                    "max": 1.05
                }
            ],
            "xaxis": {
                "type": "datetime",
                "labels": {
                    "show": False
                },
                "axisBorder": {
                    "show": False
                },
                "axisTicks": {
                    "show": False
                }
            },
            "grid": {
                "show": False
            },
            "tooltip": {
                "enabled": False
            },
            "legend": {
                "show": False
            }
        }
        
        return ApexChart(opts=chart_opts)

    @staticmethod
    def create_expanded_sparkline(df_metric: pd.DataFrame, anomaly_timestamp: pd.Timestamp = None, dark_mode=False):
        """Create an expanded sparkline chart for a specific anomaly.

        Args:
            df_metric (pd.DataFrame): The metric data.
            anomaly_timestamp (pd.Timestamp): The specific timestamp of the anomaly to highlight.
            dark_mode (bool): Whether to use dark mode styling.

        Returns:
            ApexChart: The expanded sparkline chart.
        """
        chart_opts = ChartManager._build_time_series_chart(
            df_metric,
            small_charts=False,
            dark_mode=dark_mode,
            show_markers=True,
            line_width=3,
            show_legend=True,
        )
        
        # Override settings for expanded view
        chart_opts["chart"]["height"] = 500
        chart_opts["chart"]["toolbar"]["show"] = True
        chart_opts["title"] = {
            "text": "Anomaly Detail View",
            "align": "center"
        }
        
        # Add specific anomaly marker if provided
        if anomaly_timestamp is not None:
            anomaly_row = df_metric[df_metric["metric_timestamp"] == anomaly_timestamp]
            if not anomaly_row.empty:
                anomaly_ts = int(pd.to_datetime(anomaly_timestamp).timestamp() * 1000)
                chart_opts["series"].append({
                    "name": "Selected Anomaly",
                    "type": "scatter",
                    "data": [[int(anomaly_ts), float(anomaly_row["metric_value"].iloc[0])]],
                    "yAxisIndex": 0,
                    "color": "#ff0000"
                })
                # Update marker sizes to include the new series
                chart_opts["markers"]["size"].append(12)
        
        return ApexChart(opts=chart_opts)

    @staticmethod
    def create_single_anomaly_expanded_chart(df_metric: pd.DataFrame, anomaly_timestamp: pd.Timestamp = None, dark_mode=False):
        """Create an expanded chart showing full time series but highlighting only one specific anomaly.

        Args:
            df_metric (pd.DataFrame): The metric data.
            anomaly_timestamp (pd.Timestamp): The specific timestamp of the anomaly to highlight.
            dark_mode (bool): Whether to use dark mode styling.

        Returns:
            ApexChart: The expanded chart component.
        """
        colors = ChartStyle.get_colors(dark_mode)
        
        chart_opts = ChartManager._build_time_series_chart(
            df_metric,
            small_charts=False,
            dark_mode=dark_mode,
            show_markers=True,
            line_width=3,
            show_legend=True,
        )
        
        # Override settings for single anomaly view
        chart_opts["chart"]["height"] = 500
        chart_opts["chart"]["toolbar"]["show"] = True
        chart_opts["title"] = {
            "text": "Single Anomaly Detail View",
            "align": "center"
        }
        
        # Add ONLY the specific anomaly marker if provided
        if anomaly_timestamp is not None:
            anomaly_row = df_metric[df_metric["metric_timestamp"] == anomaly_timestamp]
            if not anomaly_row.empty:
                # Use same color logic as sparkline
                alert_color = (
                    colors["llmalert"]
                    if anomaly_row["metric_llmalert"].iloc[0] == 1
                    else colors["alert"]
                )
                
                anomaly_ts = int(pd.to_datetime(anomaly_timestamp).timestamp() * 1000)
                chart_opts["series"].append({
                    "name": "Selected Alert",
                    "type": "scatter",
                    "data": [[int(anomaly_ts), float(anomaly_row["metric_value"].iloc[0])]],
                    "yAxisIndex": 0,
                    "color": alert_color
                })
                # Update marker sizes to include the new series
                chart_opts["markers"]["size"].append(15)
        
        return ApexChart(opts=chart_opts)


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

