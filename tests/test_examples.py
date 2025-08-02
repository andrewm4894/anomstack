"""
Tests for example ingest functions.

These tests verify that all example ingest functions work correctly and return
properly formatted DataFrames with the expected columns and data types.
"""

import importlib.util
import os
import sys
from unittest.mock import MagicMock, patch

import pandas as pd
import pytest


class TestExampleIngests:
    """Test all example ingest functions."""

    def load_ingest_function(self, example_path: str, module_name: str = "ingest"):
        """Load an ingest function from a Python file."""
        spec = importlib.util.spec_from_file_location(module_name, example_path)
        if spec is None or spec.loader is None:
            raise ImportError(f"Could not load module from {example_path}")

        module = importlib.util.module_from_spec(spec)
        sys.modules[module_name] = module
        spec.loader.exec_module(module)

        return getattr(module, "ingest")

    def validate_dataframe(self, df: pd.DataFrame, example_name: str):
        """Validate that a DataFrame has the expected structure."""
        assert isinstance(df, pd.DataFrame), f"{example_name}: Expected DataFrame, got {type(df)}"
        assert not df.empty, f"{example_name}: DataFrame should not be empty"

        # Check required columns
        required_columns = {"metric_timestamp", "metric_name", "metric_value"}
        actual_columns = set(df.columns)
        missing_columns = required_columns - actual_columns
        assert not missing_columns, f"{example_name}: Missing columns: {missing_columns}"

        # Check data types - be flexible with timestamp types as examples might return strings
        timestamp_col = df["metric_timestamp"]
        is_datetime = pd.api.types.is_datetime64_any_dtype(timestamp_col)
        is_string = timestamp_col.dtype == "object"
        assert (
            is_datetime or is_string
        ), f"{example_name}: metric_timestamp should be datetime or string (got {timestamp_col.dtype})"

        assert (
            df["metric_name"].dtype == "object"
        ), f"{example_name}: metric_name should be string/object"
        assert pd.api.types.is_numeric_dtype(
            df["metric_value"]
        ), f"{example_name}: metric_value should be numeric"

        # Check no null values in required columns
        for col in required_columns:
            null_count = df[col].isnull().sum()
            assert null_count == 0, f"{example_name}: Column '{col}' has {null_count} null values"

    @patch("requests.get")
    def test_bitcoin_price_ingest_mocked(self, mock_get):
        """Test bitcoin_price with mocked API call."""
        # Mock the API response
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "bpi": {"USD": {"rate_float": 45000.0}},
            "time": {"updatedISO": "2024-01-01T12:00:00+00:00"},
        }
        mock_get.return_value = mock_response

        ingest_fn = self.load_ingest_function("metrics/examples/bitcoin_price/bitcoin_price.py")
        df = ingest_fn()
        self.validate_dataframe(df, "bitcoin_price_mocked")

    @pytest.mark.skipif("CI" in os.environ, reason="Requires internet access")
    def test_hackernews_ingest(self):
        """Test hackernews example ingest function."""
        ingest_fn = self.load_ingest_function("metrics/examples/hackernews/hackernews.py")
        df = ingest_fn(top_n=5)  # Use smaller number for faster testing
        self.validate_dataframe(df, "hackernews")

        # Check that we get expected metrics
        expected_metrics = {
            "hn_top_5_min_score",
            "hn_top_5_max_score",
            "hn_top_5_avg_score",
            "hn_top_5_total_score",
        }
        actual_metrics = set(df["metric_name"])
        assert (
            expected_metrics == actual_metrics
        ), f"Expected {expected_metrics}, got {actual_metrics}"

    @patch("requests.get")
    def test_hackernews_ingest_mocked(self, mock_get):
        """Test hackernews with mocked API calls."""

        # Mock the top stories response
        def mock_requests_get(url):
            mock_response = MagicMock()
            mock_response.status_code = 200

            if "topstories.json" in url:
                mock_response.json.return_value = [1, 2, 3]
            else:  # individual story
                mock_response.json.return_value = {"score": 100}

            return mock_response

        mock_get.side_effect = mock_requests_get

        ingest_fn = self.load_ingest_function("metrics/examples/hackernews/hackernews.py")
        df = ingest_fn(top_n=3)
        self.validate_dataframe(df, "hackernews_mocked")

    @pytest.mark.skipif("CI" in os.environ, reason="Requires internet access")
    def test_weather_ingest(self):
        """Test weather example ingest function."""
        ingest_fn = self.load_ingest_function("metrics/examples/weather/ingest_weather.py")
        df = ingest_fn()
        self.validate_dataframe(df, "weather")

        # Should have metrics for multiple cities and weather parameters
        assert len(df) > 10, "Weather should return metrics for multiple cities and parameters"

        # Check that metric names start with city names
        city_prefixes = [
            "dublin",
            "athens",
            "london",
            "berlin",
            "paris",
            "madrid",
            "new_york",
            "los_angeles",
            "sydney",
            "tokyo",
            "beijing",
            "cape_town",
        ]
        metric_names = df["metric_name"].tolist()
        has_expected_cities = any(
            any(name.startswith(f"temp_{city}") for city in city_prefixes) for name in metric_names
        )
        assert has_expected_cities, "Should have metrics for expected cities"

    @pytest.mark.skipif("CI" in os.environ, reason="Requires internet access")
    def test_coindesk_ingest(self):
        """Test coindesk example ingest function."""
        ingest_fn = self.load_ingest_function("metrics/examples/coindesk/coindesk.py")
        df = ingest_fn()
        self.validate_dataframe(df, "coindesk")

        # Check that all metric names contain CURRENT_HOUR (as per the filtering logic)
        assert all(
            "CURRENT_HOUR" in name for name in df["metric_name"]
        ), "All metrics should contain CURRENT_HOUR"

    @pytest.mark.skipif("CI" in os.environ, reason="Requires internet access")
    def test_iss_location_ingest(self):
        """Test ISS location example ingest function."""
        ingest_fn = self.load_ingest_function("metrics/examples/iss_location/iss_location.py")
        df = ingest_fn()
        self.validate_dataframe(df, "iss_location")

        # Should have latitude and longitude metrics
        metric_names = set(df["metric_name"])
        assert "iss_latitude" in metric_names
        assert "iss_longitude" in metric_names

    @pytest.mark.skipif("CI" in os.environ, reason="Requires internet access")
    def test_earthquake_ingest(self):
        """Test earthquake example ingest function."""
        ingest_fn = self.load_ingest_function("metrics/examples/earthquake/earthquake.py")
        df = ingest_fn()
        self.validate_dataframe(df, "earthquake")

    @pytest.mark.skipif("CI" in os.environ, reason="Requires internet access")
    def test_currency_ingest(self):
        """Test currency example ingest function."""
        ingest_fn = self.load_ingest_function("metrics/examples/currency/currency.py")
        df = ingest_fn()
        self.validate_dataframe(df, "currency")

    def test_python_simple_ingest(self):
        """Test the simple Python example ingest function."""
        ingest_fn = self.load_ingest_function(
            "metrics/examples/python/python_ingest_simple/ingest.py"
        )
        df = ingest_fn()
        self.validate_dataframe(df, "python_simple")

        # This should be a simple example that doesn't require external APIs
        # Check for expected simple metrics
        assert len(df) >= 1, "Simple Python example should return at least 1 metric"

    @pytest.mark.skipif("CI" in os.environ, reason="May require API keys or external services")
    def test_github_ingest(self):
        """Test GitHub example ingest function."""
        ingest_fn = self.load_ingest_function("metrics/examples/github/github.py")
        df = ingest_fn()
        self.validate_dataframe(df, "github")

    @pytest.mark.skipif("CI" in os.environ, reason="May require API keys or external services")
    def test_yfinance_ingest(self):
        """Test yfinance example ingest function."""
        ingest_fn = self.load_ingest_function("metrics/examples/yfinance/yfinance.py")
        df = ingest_fn()
        self.validate_dataframe(df, "yfinance")

    @pytest.mark.skipif("CI" in os.environ, reason="May require API keys or external services")
    def test_prometheus_ingest(self):
        """Test Prometheus example ingest function."""
        ingest_fn = self.load_ingest_function("metrics/examples/prometheus/prometheus.py")
        df = ingest_fn()
        self.validate_dataframe(df, "prometheus")

    @pytest.mark.skipif("CI" in os.environ, reason="May require external services")
    def test_netdata_ingest(self):
        """Test Netdata example ingest function."""
        ingest_fn = self.load_ingest_function("metrics/examples/netdata/netdata.py")
        df = ingest_fn()
        self.validate_dataframe(df, "netdata")

    @pytest.mark.skipif("CI" in os.environ, reason="May require external services")
    def test_netdata_httpcheck_ingest(self):
        """Test Netdata HTTP check example ingest function."""
        ingest_fn = self.load_ingest_function(
            "metrics/examples/netdata_httpcheck/netdata_httpcheck.py"
        )
        df = ingest_fn()
        self.validate_dataframe(df, "netdata_httpcheck")

    @pytest.mark.skipif("CI" in os.environ, reason="May require API keys")
    def test_eirgrid_ingest(self):
        """Test EirGrid example ingest function."""
        ingest_fn = self.load_ingest_function("metrics/examples/eirgrid/eirgrid.py")
        df = ingest_fn()
        self.validate_dataframe(df, "eirgrid")


class TestExampleIntegration:
    """Integration tests using the run_example.py script."""

    def test_run_example_script_exists(self):
        """Test that the run_example.py script exists and can be imported."""
        script_path = "scripts/examples/run_example.py"
        assert os.path.exists(script_path), f"run_example.py script should exist at {script_path}"

        # Test that we can import the main functions
        spec = importlib.util.spec_from_file_location("run_example", script_path)
        assert spec is not None and spec.loader is not None

        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        # Check that required functions exist
        assert hasattr(module, "run_example"), "Should have run_example function"
        assert hasattr(module, "list_examples"), "Should have list_examples function"
        assert hasattr(module, "main"), "Should have main function"

    @patch("anomstack.config.get_specs")
    def test_list_examples_function(self, mock_get_specs):
        """Test the list_examples function with mocked specs."""
        # Mock some example specs
        mock_specs = {
            "bitcoin_price": {"ingest_fn": "def ingest(): pass"},
            "hackernews": {"ingest_fn": "def ingest(): pass"},
            "example_sql": {"ingest_sql": "SELECT 1 as value"},
        }
        mock_get_specs.return_value = mock_specs

        # Import and test the function
        script_path = "scripts/examples/run_example.py"
        spec = importlib.util.spec_from_file_location("run_example", script_path)
        assert spec is not None and spec.loader is not None

        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        # Should return 0 for success
        result = module.list_examples()
        assert result == 0, "list_examples should return 0 for success"
