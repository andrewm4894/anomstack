"""
dashboard/state.py

State manager for the dashboard.

This module contains the AppState class, which is responsible for managing the state of the dashboard.

"""

import logging

from anomstack.config import get_specs
from dashboard.utils import get_metric_batches


log = logging.getLogger("anomstack")


class AppState:
    """
    State manager for the dashboard.
    """

    def __init__(self):
        """
        Initialize the app state.
        """
        self.specs = get_specs()
        self.metric_batches = get_metric_batches(source="all")
        if not self.metric_batches:
            log.warning("No metric batches found.")
        self.specs_enabled = {batch: self.specs[batch] for batch in self.metric_batches}
        self.df_cache = {}
        self.chart_cache = {}
        self.stats_cache = {}
        self.small_charts = True
        self.dark_mode = False
        self.two_columns = True
        self.show_markers = True
        self.last_n = {}
        self.line_width = 2
        self.show_legend = False
        self.search_term = {}
        self.anomaly_feedback = {}  # Store feedback for anomalies
        
        # Initialize all batch data and stats
        for batch_name in self.metric_batches:
            try:
                from dashboard.data import get_data
                from dashboard.constants import DEFAULT_LAST_N
                self.df_cache[batch_name] = get_data(
                    self.specs_enabled[batch_name],
                    last_n=DEFAULT_LAST_N,
                    ensure_timestamp=True
                )
                self.calculate_metric_stats(batch_name)
            except Exception as e:
                log.error(f"Error initializing batch {batch_name}: {e}")

    def clear_batch_cache(self, batch_name):
        """
        Clear the cache for a given batch name.
        """
        self.df_cache.pop(batch_name, None)
        self.chart_cache.pop(batch_name, None)
        self.stats_cache.pop(batch_name, None)

    def calculate_metric_stats(self, batch_name):
        """
        Calculate the metric stats for a given batch name.
        """
        df = self.df_cache[batch_name]
        metric_stats = []
        for metric_name in df["metric_name"].unique():
            df_metric = df[df["metric_name"] == metric_name]
            metric_stats.append(
                {
                    "metric_name": metric_name,
                    "anomaly_rate": (
                        df_metric["metric_alert"].fillna(0).mean()
                        if df_metric["metric_alert"].sum() > 0
                        else 0
                    ),
                    "avg_score": (
                        df_metric["metric_score"].mean()
                        if df_metric["metric_score"].sum() > 0
                        else 0
                    ),
                }
            )
        metric_stats.sort(key=lambda x: (-x["anomaly_rate"], -x["avg_score"]))
        self.stats_cache[batch_name] = metric_stats
