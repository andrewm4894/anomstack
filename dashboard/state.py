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

    def get_connection(self):
        """Get database connection with MotherDuck fallback"""
        import os
        duckdb_path = os.getenv('ANOMSTACK_DUCKDB_PATH', 'tmpdata/anomstack-duckdb.db')
        
        if duckdb_path.startswith('md:'):
            motherduck_token = os.getenv('ANOMSTACK_MOTHERDUCK_TOKEN')
            if motherduck_token:
                try:
                    import duckdb
                    connection_string = f"{duckdb_path}?motherduck_token={motherduck_token}"
                    return duckdb.connect(connection_string)
                except Exception as e:
                    print(f"MotherDuck connection failed: {e}, falling back to local DuckDB")
                    # Fall back to local DuckDB
                    fallback_path = 'tmpdata/anomstack-duckdb.db'
                    os.makedirs(os.path.dirname(fallback_path), exist_ok=True)
                    import duckdb
                    return duckdb.connect(fallback_path)
            else:
                print("No MotherDuck token provided, using local DuckDB")
                fallback_path = 'tmpdata/anomstack-duckdb.db'
                os.makedirs(os.path.dirname(fallback_path), exist_ok=True)
                import duckdb
                return duckdb.connect(fallback_path)
        else:
            try:
                os.makedirs(os.path.dirname(duckdb_path), exist_ok=True)
                import duckdb
                return duckdb.connect(duckdb_path)
            except Exception as e:
                print(f"Failed to connect to DuckDB: {e}")
                return None

    def __init__(self):
        """
        Initialize the app state with lazy loading.
        """
        # Initialize basic state immediately
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
        
        # Lazy initialization flags
        self._specs_loaded = False
        self._metric_batches_loaded = False
        self._specs = None
        self._metric_batches = None
        self._specs_enabled = None
        
        print("AppState initialized with lazy loading")

    @property
    def specs(self):
        """Lazy-loaded specs property"""
        if not self._specs_loaded:
            self._ensure_specs_loaded()
        return self._specs

    @specs.setter
    def specs(self, value):
        """Setter for specs"""
        self._specs = value
        self._specs_loaded = True

    @property
    def metric_batches(self):
        """Lazy-loaded metric batches property"""
        if not self._metric_batches_loaded:
            self._ensure_metric_batches_loaded()
        return self._metric_batches

    @metric_batches.setter 
    def metric_batches(self, value):
        """Setter for metric_batches"""
        self._metric_batches = value

    @property
    def specs_enabled(self):
        """Lazy-loaded specs_enabled property"""
        if not self._metric_batches_loaded:
            self._ensure_metric_batches_loaded()
        return self._specs_enabled

    @specs_enabled.setter
    def specs_enabled(self, value):
        """Setter for specs_enabled"""
        self._specs_enabled = value
    
    def _ensure_specs_loaded(self):
        """Lazy load specs and metric batches"""
        if not self._specs_loaded:
            try:
                self._specs = get_specs()
                self._specs_loaded = True
                print("Specs loaded successfully")
            except Exception as e:
                log.error(f"Error loading specs: {e}")
                self._specs = {}
                
    def _ensure_metric_batches_loaded(self):
        """Lazy load metric batches"""
        if not self._metric_batches_loaded:
            try:
                # Ensure specs are loaded first
                if not self._specs_loaded:
                    self._ensure_specs_loaded()
                    
                self._metric_batches = get_metric_batches(source="all")
                if not self._metric_batches:
                    log.warning("No metric batches found.")
                    self._metric_batches = []
                
                if self._specs and self._metric_batches:
                    self._specs_enabled = {batch: self._specs[batch] for batch in self._metric_batches if batch in self._specs}
                else:
                    self._specs_enabled = {}
                
                self._metric_batches_loaded = True
                print("Metric batches loaded successfully")
            except Exception as e:
                log.error(f"Error loading metric batches: {e}")
                self._metric_batches = []
                self._specs_enabled = {}

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
                    "thumbsup_sum": df_metric["thumbsup_sum"].fillna(0).sum(),
                    "thumbsdown_sum": df_metric["thumbsdown_sum"].fillna(0).sum(),
                }
            )
        metric_stats.sort(key=lambda x: (-x["anomaly_rate"], -x["avg_score"]))
        self.stats_cache[batch_name] = metric_stats