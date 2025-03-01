import pytest
from fasthtml.common import Div
from app import app
from routes import index, get_batch_view

@pytest.fixture
def mock_app_state(monkeypatch):
    """Mock application state for testing."""
    class MockState:
        dark_mode = False
        metric_batches = ["test_batch"]
        df_cache = {}
        specs_enabled = {"test_batch": {}}
        alert_max_n = {"test_batch": 100}
        stats_cache = {"test_batch": []}
        
    monkeypatch.setattr(app, "state", MockState())
    return app.state

@pytest.fixture
def mock_request():
    """Mock HTTP request."""
    class MockRequest:
        def __init__(self, htmx=False):
            self.headers = {"HX-Request": "true"} if htmx else {}
    return MockRequest

def test_index_route_no_htmx(mock_app_state, mock_request):
    """Test index route with regular request."""
    response = index(mock_request())
    
    # Should return multiple elements for full page load
    assert len(response) > 1
    assert any("Anomstack" in str(elem) for elem in response)

def test_index_route_htmx(mock_app_state, mock_request):
    """Test index route with HTMX request."""
    response = index(mock_request(htmx=True))
    
    # Should return only main content
    assert isinstance(response, Div)
    assert response.attrs.get("id") == "main-content"

def test_batch_view(mock_app_state):
    """Test batch view."""
    response = get_batch_view("test_batch", None)
    
    # Should return a div containing charts container
    assert isinstance(response, Div)
    assert any("charts-container" in str(elem) for elem in response.children) 