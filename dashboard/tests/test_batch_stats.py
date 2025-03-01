import pandas as pd
from datetime import datetime, timedelta, timezone
import pytest
from batch_stats import calculate_batch_stats, _format_time_ago

@pytest.fixture
def sample_df():
    """Create a sample DataFrame for testing."""
    now = datetime.now(timezone.utc)
    return pd.DataFrame({
        'metric_name': ['test_metric1', 'test_metric1', 'test_metric2'],
        'metric_timestamp': [
            now.isoformat(),
            (now - timedelta(minutes=30)).isoformat(),
            (now - timedelta(hours=2)).isoformat()
        ],
        'metric_value': [1.0, 2.0, 3.0],
        'metric_score': [0.5, 0.7, 0.3],
        'metric_alert': [1, 0, 1]
    })

def test_calculate_batch_stats_empty_df():
    """Test stats calculation with empty DataFrame."""
    empty_df = pd.DataFrame()
    stats = calculate_batch_stats(empty_df, "test_batch")
    
    assert stats["unique_metrics"] == 0
    assert stats["latest_timestamp"] == "No data"
    assert stats["avg_score"] == 0
    assert stats["alert_count"] == 0

def test_calculate_batch_stats(sample_df):
    """Test stats calculation with sample data."""
    stats = calculate_batch_stats(sample_df, "test_batch")
    
    assert stats["unique_metrics"] == 2  # test_metric1 and test_metric2
    assert "ago" in stats["latest_timestamp"]  # Should contain time ago string
    assert stats["avg_score"] == 0.5  # Average of [0.5, 0.7, 0.3]
    assert stats["alert_count"] == 2  # Count of 1s in metric_alert

def test_format_time_ago():
    """Test time ago formatting."""
    now = datetime.now(timezone.utc)
    
    # Test minutes
    timestamp = (now - timedelta(minutes=5)).isoformat()
    assert "minute" in _format_time_ago(timestamp)
    
    # Test hours
    timestamp = (now - timedelta(hours=3)).isoformat()
    assert "hour" in _format_time_ago(timestamp)
    
    # Test days
    timestamp = (now - timedelta(days=2)).isoformat()
    assert "day" in _format_time_ago(timestamp)

def test_format_time_ago_no_data():
    """Test handling of 'No data' timestamp."""
    assert _format_time_ago("No data") == "No data" 