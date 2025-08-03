"""
Simple tests for anomstack.external.duckdb module.
"""

from unittest.mock import MagicMock, patch

import pandas as pd

from anomstack.external.duckdb.duckdb import (
    read_sql_duckdb,
    run_sql_duckdb,
    save_df_duckdb,
)


class TestDuckdbSimple:
    """Simple DuckDB tests."""

    @patch("anomstack.external.duckdb.duckdb.os.makedirs")
    @patch("anomstack.external.duckdb.duckdb.get_dagster_logger")
    @patch("anomstack.external.duckdb.duckdb.connect")
    @patch("anomstack.external.duckdb.duckdb.query")
    def test_read_sql_basic(self, mock_query, mock_connect, mock_logger, mock_makedirs):
        """Test basic read_sql_duckdb functionality."""
        # Setup
        mock_logger.return_value = MagicMock()
        mock_conn = MagicMock()
        mock_connect.return_value = mock_conn
        expected_df = pd.DataFrame({"col1": [1, 2], "col2": ["a", "b"]})
        mock_query.return_value.df.return_value = expected_df

        # Call function
        result = read_sql_duckdb("SELECT * FROM test_table")

        # Assertions
        mock_connect.assert_called_once()
        mock_query.assert_called_once_with(connection=mock_conn, query="SELECT * FROM test_table")
        pd.testing.assert_frame_equal(result, expected_df)

    @patch("anomstack.external.duckdb.duckdb.os.makedirs")
    @patch("anomstack.external.duckdb.duckdb.get_dagster_logger")
    @patch("anomstack.external.duckdb.duckdb.connect")
    @patch("anomstack.external.duckdb.duckdb.query")
    def test_save_df_basic(self, mock_query, mock_connect, mock_logger, mock_makedirs):
        """Test basic save_df_duckdb functionality."""
        # Setup
        mock_logger.return_value = MagicMock()
        mock_conn = MagicMock()
        mock_connect.return_value = mock_conn
        mock_query.return_value = None

        df = pd.DataFrame({"col1": [1, 2], "col2": ["a", "b"]})

        # Call function
        result = save_df_duckdb(df, "test_table")

        # Assertions
        mock_connect.assert_called_once()
        mock_query.assert_called()
        pd.testing.assert_frame_equal(result, df)

    @patch("anomstack.external.duckdb.duckdb.os.makedirs")
    @patch("anomstack.external.duckdb.duckdb.get_dagster_logger")
    @patch("anomstack.external.duckdb.duckdb.connect")
    @patch("anomstack.external.duckdb.duckdb.query")
    def test_run_sql_basic(self, mock_query, mock_connect, mock_logger, mock_makedirs):
        """Test basic run_sql_duckdb functionality."""
        # Setup
        mock_logger.return_value = MagicMock()
        mock_conn = MagicMock()
        mock_connect.return_value = mock_conn
        mock_query.return_value = None

        # Call function
        result = run_sql_duckdb("CREATE TABLE test AS SELECT 1 as col", return_df=False)

        # Assertions
        mock_connect.assert_called_once()
        mock_query.assert_called_once_with(connection=mock_conn, query="CREATE TABLE test AS SELECT 1 as col")
        assert result is None

    @patch("anomstack.external.duckdb.duckdb.os.makedirs")
    @patch("anomstack.external.duckdb.duckdb.get_dagster_logger")
    @patch("anomstack.external.duckdb.duckdb.connect")
    @patch("anomstack.external.duckdb.duckdb.query")
    def test_run_sql_with_return(self, mock_query, mock_connect, mock_logger, mock_makedirs):
        """Test run_sql_duckdb with DataFrame return."""
        # Setup
        mock_logger.return_value = MagicMock()
        mock_conn = MagicMock()
        mock_connect.return_value = mock_conn
        expected_df = pd.DataFrame({"result": [1, 2, 3]})
        mock_query.return_value.df.return_value = expected_df

        # Call function
        result = run_sql_duckdb("SELECT * FROM test", return_df=True)

        # Assertions
        mock_connect.assert_called_once()
        mock_query.assert_called_once_with(connection=mock_conn, query="SELECT * FROM test")
        pd.testing.assert_frame_equal(result, expected_df)
