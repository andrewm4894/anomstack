"""
Tests for anomstack.alerts.asciiart module - ASCII art functionality.
"""


import pandas as pd

from anomstack.alerts.asciiart import Pyasciigraph, make_alert_message


class TestMakeAlertMessage:
    """Test the make_alert_message function."""

    def test_make_alert_message_basic(self):
        """Test basic make_alert_message functionality."""
        # Create test data
        df = pd.DataFrame({
            'metric_name': ['cpu_usage'] * 5,
            'metric_timestamp': pd.date_range('2023-01-01 10:00:00', periods=5, freq='h'),
            'metric_value': [75.5, 82.3, 89.1, 76.2, 78.8],
            'metric_score_smooth': [0.2, 0.5, 0.9, 0.3, 0.4],
            'metric_alert': [0, 0, 1, 0, 0]
        })

        # Call function
        result = make_alert_message(df, description="Test alert")

        # Assertions
        assert isinstance(result, str)
        assert "Test alert" in result
        assert "<pre><code>" in result

    def test_make_alert_message_with_ascii_graph(self):
        """Test make_alert_message with ASCII graph enabled."""
        # Create test data
        df = pd.DataFrame({
            'metric_name': ['memory_usage'] * 3,
            'metric_timestamp': pd.date_range('2023-01-01 12:00:00', periods=3, freq='30min'),
            'metric_value': [65.2, 78.9, 85.1],
            'metric_score_smooth': [0.1, 0.6, 0.8],
            'metric_alert': [0, 1, 1]
        })

        # Call function
        result = make_alert_message(
            df,
            description="Memory alert",
            ascii_graph=True,
            graph_symbol="=",
            anomaly_symbol="! ",
            normal_symbol="  ",
            alert_float_format="{:.1f}"
        )

        # Assertions
        assert isinstance(result, str)
        assert "Memory alert" in result
        assert "memory_usage" in result
        assert "2023-01-01 12:00" in result
        assert "2023-01-01 13:00" in result

    def test_make_alert_message_with_tags(self):
        """Test make_alert_message with tags."""
        # Create test data
        df = pd.DataFrame({
            'metric_name': ['disk_usage'] * 2,
            'metric_timestamp': pd.date_range('2023-01-01 15:00:00', periods=2, freq='h'),
            'metric_value': [88.5, 92.3],
            'metric_score_smooth': [0.7, 0.9],
            'metric_alert': [1, 1]
        })

        tags = {'environment': 'production', 'service': 'web-server'}

        # Call function
        result = make_alert_message(
            df,
            description="Disk space alert",
            tags=tags
        )

        # Assertions
        assert isinstance(result, str)
        assert "Disk space alert" in result
        assert str(tags) in result

    def test_make_alert_message_custom_score_col(self):
        """Test make_alert_message with custom score column."""
        # Create test data
        df = pd.DataFrame({
            'metric_name': ['network_latency'] * 3,
            'metric_timestamp': pd.date_range('2023-01-01 09:00:00', periods=3, freq='15min'),
            'metric_value': [45.2, 78.9, 123.5],
            'custom_score': [0.2, 0.5, 0.9],
            'metric_alert': [0, 0, 1]
        })

        # Call function
        result = make_alert_message(
            df,
            score_col='custom_score',
            ascii_graph=True
        )

        # Assertions
        assert isinstance(result, str)
        assert "network_latency" in result

    def test_make_alert_message_empty_description(self):
        """Test make_alert_message with empty description."""
        # Create test data
        df = pd.DataFrame({
            'metric_name': ['test_metric'] * 2,
            'metric_timestamp': pd.date_range('2023-01-01', periods=2, freq='D'),
            'metric_value': [100.0, 200.0],
            'metric_score_smooth': [0.3, 0.7],
            'metric_alert': [0, 1]
        })

        # Call function
        result = make_alert_message(df, description="", ascii_graph=True)

        # Assertions
        assert isinstance(result, str)
        assert "test_metric" in result


class TestPyasciigraph:
    """Test the Pyasciigraph class basic functionality."""

    def test_pyasciigraph_init_defaults(self):
        """Test Pyasciigraph initialization with defaults."""
        graph = Pyasciigraph()

        # Check default values
        assert graph.line_length == 79
        assert graph.min_graph_length == 50
        assert graph.separator_length == 2
        assert graph.multivalue is True
        assert graph.float_format == "{0:.0f}"
        assert graph.titlebar == "#"

    def test_pyasciigraph_init_custom(self):
        """Test Pyasciigraph initialization with custom values."""
        graph = Pyasciigraph(
            line_length=100,
            min_graph_length=30,
            separator_length=3,
            graphsymbol="*",
            multivalue=False,
            float_format="{:.2f}",
            titlebar="="
        )

        # Check custom values
        assert graph.line_length == 100
        assert graph.min_graph_length == 30
        assert graph.separator_length == 3
        assert graph.graphsymbol == "*"
        assert graph.multivalue is False
        assert graph.float_format == "{:.2f}"
        assert graph.titlebar == "="

    def test_pyasciigraph_simple_graph(self):
        """Test creating a simple ASCII graph."""
        graph = Pyasciigraph()
        data = [('Item A', 10), ('Item B', 20), ('Item C', 15)]

        result = graph.graph('Test Graph', data)

        # Assertions
        assert isinstance(result, list)
        assert len(result) > 0
        assert 'Test Graph' in result[0]
        assert result[1] == '#' * 79  # Title bar

    def test_pyasciigraph_len_noansi(self):
        """Test the _len_noansi static method."""
        # Test normal string
        assert Pyasciigraph._len_noansi("hello") == 5

        # Test string with ANSI codes
        ansi_string = "\x1b[31mred text\x1b[0m"
        assert Pyasciigraph._len_noansi(ansi_string) == 8  # "red text"

    def test_pyasciigraph_u_helper(self):
        """Test the _u unicode helper method."""
        # Test basic string
        result = Pyasciigraph._u("test")
        assert result == "test"

        # Test with unicode character
        result = Pyasciigraph._u("█")
        assert result == "█"

    def test_pyasciigraph_color_string(self):
        """Test the _color_string static method."""
        # Test with no color
        result = Pyasciigraph._color_string("test", None)
        assert result == "test"

        # Test with color
        result = Pyasciigraph._color_string("test", "\033[31m")
        assert result == "\033[31mtest\033[0m"
