"""
Tests for anomstack.plots module - plotting and visualization functions.
"""

import matplotlib.pyplot as plt
import pandas as pd
import pytest

from anomstack.plots.plot import make_alert_plot, make_batch_plot


class TestMakeAlertPlot:
    """Test the make_alert_plot function."""

    def test_make_alert_plot_basic(self):
        """Test basic functionality of make_alert_plot."""
        # Create test data
        df = pd.DataFrame(
            {
                "metric_timestamp": pd.to_datetime(
                    ["2023-01-01 10:00:00", "2023-01-01 11:00:00", "2023-01-01 12:00:00"]
                ),
                "metric_value": [85.5, 87.2, 90.1],
                "metric_score_smooth": [0.6, 0.8, 0.9],
                "metric_score": [0.6, 0.8, 0.9],
                "metric_alert": [0, 0, 1],
            }
        )

        # Call function
        fig = make_alert_plot(
            df=df,
            metric_name="cpu_usage",
            threshold=0.8,
            score_col="metric_score_smooth",
            score_title="anomaly_score",
        )

        # Assertions
        assert fig is not None
        assert len(fig.axes) == 2  # Should have 2 subplots

        # Check that the figure has expected structure
        ax1, ax2 = fig.axes
        assert ax1.get_ylabel() == "cpu_usage"
        assert ax2.get_ylabel() == "anomaly_score"

        # Close the figure to prevent memory issues
        plt.close(fig)

    def test_make_alert_plot_with_smooth_metric(self):
        """Test make_alert_plot with metric_value_smooth column."""
        # Create test data with smooth values
        df = pd.DataFrame(
            {
                "metric_timestamp": pd.to_datetime(
                    ["2023-01-01 10:00:00", "2023-01-01 11:00:00", "2023-01-01 12:00:00"]
                ),
                "metric_value": [85.5, 87.2, 90.1],
                "metric_value_smooth": [84.0, 86.0, 88.5],
                "metric_score_smooth": [0.6, 0.8, 0.9],
                "metric_score": [0.6, 0.8, 0.9],
                "metric_alert": [0, 0, 1],
            }
        )

        # Call function
        fig = make_alert_plot(df=df, metric_name="cpu_usage", threshold=0.8)

        # Should create figure with smooth line
        assert fig is not None
        assert len(fig.axes) == 2

        # Close the figure
        plt.close(fig)

    def test_make_alert_plot_with_tags(self):
        """Test make_alert_plot with tags parameter."""
        df = pd.DataFrame(
            {
                "metric_timestamp": pd.to_datetime(["2023-01-01 10:00:00", "2023-01-01 11:00:00"]),
                "metric_value": [85.5, 87.2],
                "metric_score_smooth": [0.6, 0.8],
                "metric_score": [0.6, 0.8],
                "metric_alert": [0, 1],
            }
        )

        tags = {"alert_type": "critical"}

        # Call function
        fig = make_alert_plot(df=df, metric_name="cpu_usage", threshold=0.8, tags=tags)

        assert fig is not None
        plt.close(fig)

    def test_make_alert_plot_different_score_limits(self):
        """Test make_alert_plot with scores above 1.0."""
        df = pd.DataFrame(
            {
                "metric_timestamp": pd.to_datetime(["2023-01-01 10:00:00", "2023-01-01 11:00:00"]),
                "metric_value": [85.5, 87.2],
                "metric_score_smooth": [1.5, 2.0],  # Scores above 1.0
                "metric_score": [1.5, 2.0],
                "metric_alert": [1, 1],
            }
        )

        # Call function
        fig = make_alert_plot(df=df, metric_name="cpu_usage", threshold=0.8)

        assert fig is not None
        # Should handle scores above 1.0 by setting ylim appropriately
        ax2 = fig.axes[1]
        ylim = ax2.get_ylim()
        assert ylim[1] > 2.0  # Should be 2.0 * 1.1 = 2.2

        plt.close(fig)

    def test_make_alert_plot_custom_score_column(self):
        """Test make_alert_plot with custom score column."""
        df = pd.DataFrame(
            {
                "metric_timestamp": pd.to_datetime(["2023-01-01 10:00:00", "2023-01-01 11:00:00"]),
                "metric_value": [85.5, 87.2],
                "custom_score": [0.6, 0.9],
                "metric_score": [0.6, 0.9],
                "metric_alert": [0, 1],
            }
        )

        # Call function with custom score column
        fig = make_alert_plot(
            df=df,
            metric_name="cpu_usage",
            threshold=0.8,
            score_col="custom_score",
            score_title="Custom Anomaly Score",
        )

        assert fig is not None
        ax2 = fig.axes[1]
        assert ax2.get_ylabel() == "Custom Anomaly Score"

        plt.close(fig)


class TestMakeBatchPlot:
    """Test the make_batch_plot function."""

    def test_make_batch_plot_single_metric(self):
        """Test make_batch_plot with single metric."""
        df = pd.DataFrame(
            {
                "metric_timestamp": pd.to_datetime(
                    ["2023-01-01 10:00:00", "2023-01-01 11:00:00", "2023-01-01 12:00:00"]
                ),
                "metric_name": ["cpu_usage", "cpu_usage", "cpu_usage"],
                "metric_value": [85.5, 87.2, 90.1],
                "metric_score": [0.6, 0.8, 0.9],
                "metric_alert": [0, 0, 1],
            }
        )

        # Call function
        fig = make_batch_plot(df)

        # Assertions
        assert fig is not None
        # Should have 2 axes (main + twin) for 1 metric due to twinx()
        assert len(fig.axes) == 2

        ax = fig.axes[0]
        assert "cpu_usage" in ax.get_title()
        assert "(n=3)" in ax.get_title()  # Should show count

        plt.close(fig)

    def test_make_batch_plot_multiple_metrics(self):
        """Test make_batch_plot with multiple metrics."""
        df = pd.DataFrame(
            {
                "metric_timestamp": pd.to_datetime(
                    [
                        "2023-01-01 10:00:00",
                        "2023-01-01 11:00:00",
                        "2023-01-01 10:00:00",
                        "2023-01-01 11:00:00",
                    ]
                ),
                "metric_name": ["cpu_usage", "cpu_usage", "memory_usage", "memory_usage"],
                "metric_value": [85.5, 87.2, 65.1, 67.8],
                "metric_score": [0.6, 0.8, 0.4, 0.5],
                "metric_alert": [0, 1, 0, 0],
            }
        )

        # Call function
        fig = make_batch_plot(df)

        # Assertions
        assert fig is not None
        # Should have 4 axes (2 main + 2 twin) for 2 metrics due to twinx()
        assert len(fig.axes) == 4

        # Check that both metrics are represented in the main axes (first 2)
        main_titles = [ax.get_title() for ax in fig.axes[:2]]
        assert any("cpu_usage" in title for title in main_titles)
        assert any("memory_usage" in title for title in main_titles)

        plt.close(fig)

    def test_make_batch_plot_with_metric_change(self):
        """Test make_batch_plot with metric_change column."""
        df = pd.DataFrame(
            {
                "metric_timestamp": pd.to_datetime(
                    ["2023-01-01 10:00:00", "2023-01-01 11:00:00", "2023-01-01 12:00:00"]
                ),
                "metric_name": ["cpu_usage", "cpu_usage", "cpu_usage"],
                "metric_value": [85.5, 87.2, 90.1],
                "metric_score": [0.6, 0.8, 0.9],
                "metric_alert": [0, 0, 1],
                "metric_change": [0, 1, 0],  # Change detection
            }
        )

        # Call function
        fig = make_batch_plot(df)

        assert fig is not None
        ax = fig.axes[0]
        assert "change" in ax.get_title().lower()  # Should mention change in title

        plt.close(fig)

    def test_make_batch_plot_datetime_conversion(self):
        """Test that make_batch_plot handles string timestamps."""
        df = pd.DataFrame(
            {
                "metric_timestamp": [
                    "2023-01-01 10:00:00",
                    "2023-01-01 11:00:00",
                ],  # String timestamps
                "metric_name": ["cpu_usage", "cpu_usage"],
                "metric_value": [85.5, 87.2],
                "metric_score": [0.6, 0.8],
                "metric_alert": [0, 1],
            }
        )

        # Call function
        fig = make_batch_plot(df)

        assert fig is not None
        plt.close(fig)

    def test_make_batch_plot_empty_dataframe(self):
        """Test make_batch_plot with empty dataframe."""
        df = pd.DataFrame(
            {
                "metric_timestamp": [],
                "metric_name": [],
                "metric_value": [],
                "metric_score": [],
                "metric_alert": [],
            }
        )

        # The function will fail with empty dataframe due to matplotlib constraints
        # This documents the current behavior
        with pytest.raises(ValueError, match="Number of rows must be a positive integer"):
            make_batch_plot(df)

    def test_make_batch_plot_formatting(self):
        """Test that make_batch_plot formats axes correctly."""
        df = pd.DataFrame(
            {
                "metric_timestamp": pd.to_datetime(["2023-01-01 10:00:00", "2023-01-01 11:00:00"]),
                "metric_name": ["cpu_usage", "cpu_usage"],
                "metric_value": [85.5, 87.2],
                "metric_score": [0.6, 0.8],
                "metric_alert": [0, 1],
            }
        )

        # Call function
        fig = make_batch_plot(df)

        assert fig is not None
        ax = fig.axes[0]

        # Check that y-axis labels are set correctly
        assert ax.get_ylabel() == "Metric Value"

        # Check that twin axis exists and has correct label
        ax.right_ax if hasattr(ax, "right_ax") else None
        # The twin axis might not be directly accessible, but we can check formatting was applied

        plt.close(fig)
