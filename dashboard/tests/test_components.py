import pytest
from components import create_batch_card, create_header

def test_create_batch_card():
    """Test batch card creation."""
    stats = {
        "unique_metrics": 10,
        "latest_timestamp": "5 minutes ago",
        "avg_score": 0.75,
        "alert_count": 3
    }
    
    card = create_batch_card("test_batch", stats)
    
    # Test that the card contains key information
    card_str = str(card)
    assert "test_batch" in card_str
    assert "10 metrics" in card_str
    assert "5 minutes ago" in card_str
    assert "75.0%" in card_str  # 0.75 formatted as percentage
    assert "3 alerts" in card_str

def test_create_header():
    """Test header creation."""
    header = create_header()
    header_str = str(header)
    
    # Test that header contains key elements
    assert "Anomstack" in header_str
    assert "Painless open source anomaly detection" in header_str
    assert "github.com/andrewm4894/anomstack" in header_str 