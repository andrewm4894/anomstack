"""
Test threshold alert functionality.
"""

import pandas as pd
import pytest

from anomstack.ml.threshold import detect_threshold_alerts


class TestThresholdAlerts:
    """Test threshold alert detection."""

    def test_detect_threshold_alerts_basic(self):
        """Test basic threshold alert detection."""
        # Create test data
        df = pd.DataFrame({
            'metric_timestamp': pd.to_datetime(['2023-01-01 10:00:00', '2023-01-01 11:00:00', '2023-01-01 12:00:00']),
            'metric_name': ['cpu_usage', 'cpu_usage', 'cpu_usage'],
            'metric_value': [50, 95, 30]  # Middle value should trigger upper threshold
        })
        
        thresholds = {
            'cpu_usage': {'upper': 90, 'lower': 10}
        }
        
        result = detect_threshold_alerts(df, thresholds, recent_n=3, snooze_n=1)
        
        # Check that threshold alert columns were added
        assert 'threshold_alert' in result.columns
        assert 'threshold_type' in result.columns
        assert 'threshold_value' in result.columns
        
        # Check that the high value triggered an alert
        alerts = result[result['threshold_alert'] == 1]
        assert len(alerts) == 1
        assert alerts.iloc[0]['metric_value'] == 95
        assert alerts.iloc[0]['threshold_type'] == 'upper'
        assert alerts.iloc[0]['threshold_value'] == 90

    def test_detect_threshold_alerts_lower_bound(self):
        """Test lower threshold detection."""
        df = pd.DataFrame({
            'metric_timestamp': pd.to_datetime(['2023-01-01 10:00:00', '2023-01-01 11:00:00']),
            'metric_name': ['memory_usage', 'memory_usage'],
            'metric_value': [50, 5]  # Second value should trigger lower threshold
        })
        
        thresholds = {
            'memory_usage': {'lower': 10}
        }
        
        result = detect_threshold_alerts(df, thresholds)
        
        alerts = result[result['threshold_alert'] == 1]
        assert len(alerts) == 1
        assert alerts.iloc[0]['threshold_type'] == 'lower'
        assert alerts.iloc[0]['threshold_value'] == 10

    def test_detect_threshold_alerts_no_thresholds(self):
        """Test when no thresholds are configured."""
        df = pd.DataFrame({
            'metric_timestamp': pd.to_datetime(['2023-01-01 10:00:00']),
            'metric_name': ['test_metric'],
            'metric_value': [100]
        })
        
        result = detect_threshold_alerts(df, {})
        
        # Should return original df with threshold columns but no alerts
        assert 'threshold_alert' in result.columns
        assert result['threshold_alert'].sum() == 0

    def test_detect_threshold_alerts_snoozing(self):
        """Test alert snoozing functionality."""
        df = pd.DataFrame({
            'metric_timestamp': pd.to_datetime([
                '2023-01-01 10:00:00', 
                '2023-01-01 11:00:00', 
                '2023-01-01 12:00:00',
                '2023-01-01 13:00:00'
            ]),
            'metric_name': ['disk_usage', 'disk_usage', 'disk_usage', 'disk_usage'],
            'metric_value': [95, 96, 97, 98]  # All should exceed threshold but snoozing should prevent some alerts
        })
        
        thresholds = {
            'disk_usage': {'upper': 90}
        }
        
        result = detect_threshold_alerts(df, thresholds, recent_n=4, snooze_n=3)
        
        # With snooze_n=3, should only have one alert (first one blocks the next 2)
        alerts = result[result['threshold_alert'] == 1]
        assert len(alerts) == 1
        # First observation should trigger the alert
        assert alerts.iloc[0]['metric_value'] == 95

    def test_detect_threshold_alerts_multiple_metrics(self):
        """Test threshold detection across multiple metrics."""
        df = pd.DataFrame({
            'metric_timestamp': pd.to_datetime(['2023-01-01 10:00:00'] * 4),
            'metric_name': ['cpu', 'memory', 'disk', 'network'],
            'metric_value': [95, 5, 50, 200]  # cpu and memory should alert
        })
        
        thresholds = {
            'cpu': {'upper': 90},
            'memory': {'lower': 10},
            'disk': {'upper': 80, 'lower': 20},  # Should not alert
            'network': {'upper': 300}  # Should not alert
        }
        
        result = detect_threshold_alerts(df, thresholds)
        
        alerts = result[result['threshold_alert'] == 1]
        assert len(alerts) == 2
        
        alert_metrics = alerts['metric_name'].tolist()
        assert 'cpu' in alert_metrics
        assert 'memory' in alert_metrics

    def test_detect_threshold_alerts_empty_df(self):
        """Test with empty DataFrame."""
        df = pd.DataFrame(columns=['metric_timestamp', 'metric_name', 'metric_value'])
        
        thresholds = {'test': {'upper': 100}}
        
        result = detect_threshold_alerts(df, thresholds)
        
        assert result.empty 