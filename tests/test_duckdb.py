"""
Tests for anomstack.external.duckdb module - DuckDB functionality.
"""

import os
from unittest.mock import MagicMock, patch

import pandas as pd
import pytest

from anomstack.external.duckdb.duckdb import (
    read_sql_duckdb,
    run_sql_duckdb,
    save_df_duckdb,
)


class TestReadSqlDuckdb:
    """Test the read_sql_duckdb function."""

    @patch("anomstack.external.duckdb.duckdb.get_dagster_logger")
    @patch("anomstack.external.duckdb.duckdb.connect")
    @patch("anomstack.external.duckdb.duckdb.query")
    @patch("anomstack.external.duckdb.duckdb.os.makedirs")
    def test_read_sql_duckdb_local_path(self, mock_makedirs, mock_query, mock_connect, mock_logger):
        """Test read_sql_duckdb with local path."""
        # Setup
        mock_logger.return_value = MagicMock()
        mock_conn = MagicMock()
        mock_connect.return_value = mock_conn
        expected_df = pd.DataFrame({"col1": [1, 2], "col2": ["a", "b"]})
        mock_query.return_value.df.return_value = expected_df

        # CRITICAL: Isolate environment variables to prevent token exposure
        with patch.dict(os.environ, {}, clear=True):
            # Call function
            result = read_sql_duckdb("SELECT * FROM test_table")

            # Assertions
            mock_connect.assert_called_once_with("tmpdata/anomstack-duckdb.db")
            mock_query.assert_called_once_with(
                connection=mock_conn, query="SELECT * FROM test_table"
            )
            pd.testing.assert_frame_equal(result, expected_df)

    @patch("anomstack.external.duckdb.duckdb.get_dagster_logger")
    @patch("anomstack.external.duckdb.duckdb.connect")
    @patch("anomstack.external.duckdb.duckdb.query")
    @patch("anomstack.external.duckdb.duckdb.os.makedirs")
    def test_read_sql_duckdb_with_env_path(
        self, mock_makedirs, mock_query, mock_connect, mock_logger
    ):
        """Test read_sql_duckdb with environment variable path."""
        # Setup
        mock_logger.return_value = MagicMock()
        mock_conn = MagicMock()
        mock_connect.return_value = mock_conn
        expected_df = pd.DataFrame({"col1": [1, 2], "col2": ["a", "b"]})
        mock_query.return_value.df.return_value = expected_df

        with patch.dict(os.environ, {"ANOMSTACK_DUCKDB_PATH": "custom/path/test.db"}, clear=True):
            # Call function
            result = read_sql_duckdb("SELECT COUNT(*) FROM users")

            # Assertions
            mock_connect.assert_called_once_with("custom/path/test.db")
            pd.testing.assert_frame_equal(result, expected_df)

    @patch("anomstack.external.duckdb.duckdb.get_dagster_logger")
    @patch("anomstack.external.duckdb.duckdb.connect")
    @patch("anomstack.external.duckdb.duckdb.query")
    @patch("anomstack.external.duckdb.duckdb.os.makedirs")
    def test_read_sql_duckdb_motherduck_with_token(
        self, mock_makedirs, mock_query, mock_connect, mock_logger
    ):
        """Test read_sql_duckdb with MotherDuck and token."""
        # Setup
        mock_logger.return_value = MagicMock()
        mock_conn = MagicMock()
        mock_connect.return_value = mock_conn
        expected_df = pd.DataFrame({"result": [42]})
        mock_query.return_value.df.return_value = expected_df

        with patch.dict(
            os.environ,
            {"ANOMSTACK_DUCKDB_PATH": "md:my_db", "ANOMSTACK_MOTHERDUCK_TOKEN": "test_token_123"},
            clear=True,
        ):
            # Call function
            result = read_sql_duckdb("SELECT 42 as result")

            # Assertions
            mock_connect.assert_called_once_with("md:my_db?motherduck_token=test_token_123")
            pd.testing.assert_frame_equal(result, expected_df)

    @patch("anomstack.external.duckdb.duckdb.get_dagster_logger")
    @patch("anomstack.external.duckdb.duckdb.connect")
    @patch("anomstack.external.duckdb.duckdb.query")
    @patch("anomstack.external.duckdb.duckdb.os.makedirs")
    def test_read_sql_duckdb_motherduck_no_token_fallback(
        self, mock_makedirs, mock_query, mock_connect, mock_logger
    ):
        """Test read_sql_duckdb with MotherDuck but no token, should fallback to local."""
        # Setup
        mock_logger_instance = MagicMock()
        mock_logger.return_value = mock_logger_instance
        mock_conn = MagicMock()
        mock_connect.return_value = mock_conn
        expected_df = pd.DataFrame({"result": [42]})
        mock_query.return_value.df.return_value = expected_df

        with patch.dict(os.environ, {"ANOMSTACK_DUCKDB_PATH": "md:my_db"}, clear=True):
            # Call function
            result = read_sql_duckdb("SELECT 42 as result")

            # Assertions
            mock_logger_instance.warning.assert_called_once()
            mock_connect.assert_called_once_with("tmpdata/anomstack-duckdb.db")
            pd.testing.assert_frame_equal(result, expected_df)

    @patch("anomstack.external.duckdb.duckdb.get_dagster_logger")
    @patch("anomstack.external.duckdb.duckdb.connect")
    @patch("anomstack.external.duckdb.duckdb.query")
    @patch("anomstack.external.duckdb.duckdb.os.makedirs")
    def test_read_sql_duckdb_motherduck_error_fallback(
        self, mock_makedirs, mock_query, mock_connect, mock_logger
    ):
        """Test read_sql_duckdb with MotherDuck error and fallback to local."""
        # Setup
        mock_logger.return_value = MagicMock()
        expected_df = pd.DataFrame({"result": [42]})

        # First call fails with motherduck error, second call succeeds
        mock_connect.side_effect = [Exception("MotherDuck connection failed"), MagicMock()]
        mock_query.return_value.df.return_value = expected_df

        with patch.dict(
            os.environ,
            {"ANOMSTACK_DUCKDB_PATH": "md:my_db", "ANOMSTACK_MOTHERDUCK_TOKEN": "test_token"},
            clear=True,
        ):
            # Call function
            result = read_sql_duckdb("SELECT 42 as result")

            # Assertions
            mock_logger.return_value.warning.assert_called_once()
            assert mock_connect.call_count == 2
            mock_connect.assert_any_call("md:my_db?motherduck_token=test_token")
            mock_connect.assert_any_call("tmpdata/anomstack-duckdb.db")
            pd.testing.assert_frame_equal(result, expected_df)

    @patch("anomstack.external.duckdb.duckdb.get_dagster_logger")
    @patch("anomstack.external.duckdb.duckdb.connect")
    @patch("anomstack.external.duckdb.duckdb.query")
    @patch("anomstack.external.duckdb.duckdb.os.makedirs")
    def test_read_sql_duckdb_non_motherduck_error(
        self, mock_makedirs, mock_query, mock_connect, mock_logger
    ):
        """Test read_sql_duckdb with non-MotherDuck error, should raise."""
        # Setup
        mock_logger.return_value = MagicMock()
        mock_conn = MagicMock()
        mock_connect.return_value = mock_conn
        mock_query.side_effect = Exception("SQL syntax error")

        with patch.dict(os.environ, {}, clear=True):
            # Call function and expect exception
            with pytest.raises(Exception, match="SQL syntax error"):
                read_sql_duckdb("SELECT invalid syntax")


class TestSaveDfDuckdb:
    """Test the save_df_duckdb function."""

    @patch("anomstack.external.duckdb.duckdb.get_dagster_logger")
    @patch("anomstack.external.duckdb.duckdb.connect")
    @patch("anomstack.external.duckdb.duckdb.query")
    @patch("anomstack.external.duckdb.duckdb.os.makedirs")
    def test_save_df_duckdb_create_table(
        self, mock_makedirs, mock_query, mock_connect, mock_logger
    ):
        """Test save_df_duckdb creating new table."""
        # Setup
        mock_logger.return_value = MagicMock()
        mock_conn = MagicMock()
        mock_connect.return_value = mock_conn

        # First INSERT fails, then CREATE TABLE succeeds
        mock_query.side_effect = [Exception("Table doesn't exist"), None]

        df = pd.DataFrame({"col1": [1, 2], "col2": ["a", "b"]})

        with patch.dict(os.environ, {}, clear=True):
            # Call function
            result = save_df_duckdb(df, "test_table")

            # Assertions
            mock_connect.assert_called_once()
            assert mock_query.call_count == 2
            mock_query.assert_any_call(
                connection=mock_conn, query="INSERT INTO test_table (col1, col2) SELECT col1, col2 FROM df"
            )
            mock_query.assert_any_call(
                connection=mock_conn, query="CREATE TABLE test_table AS SELECT * FROM df"
            )
            pd.testing.assert_frame_equal(result, df)

    @patch("anomstack.external.duckdb.duckdb.get_dagster_logger")
    @patch("anomstack.external.duckdb.duckdb.connect")
    @patch("anomstack.external.duckdb.duckdb.query")
    @patch("anomstack.external.duckdb.duckdb.os.makedirs")
    def test_save_df_duckdb_insert_existing_table(
        self, mock_makedirs, mock_query, mock_connect, mock_logger
    ):
        """Test save_df_duckdb inserting into existing table."""
        # Setup
        mock_logger.return_value = MagicMock()
        mock_conn = MagicMock()
        mock_connect.return_value = mock_conn
        mock_query.return_value = None

        df = pd.DataFrame({"col1": [1, 2], "col2": ["a", "b"]})

        with patch.dict(os.environ, {}, clear=True):
            # Call function
            result = save_df_duckdb(df, "existing_table")

            # Assertions
            mock_connect.assert_called_once()
            mock_query.assert_called_once_with(
                connection=mock_conn, query="INSERT INTO existing_table (col1, col2) SELECT col1, col2 FROM df"
            )
            pd.testing.assert_frame_equal(result, df)

    @patch("anomstack.external.duckdb.duckdb.get_dagster_logger")
    @patch("anomstack.external.duckdb.duckdb.connect")
    @patch("anomstack.external.duckdb.duckdb.query")
    @patch("anomstack.external.duckdb.duckdb.os.makedirs")
    def test_save_df_duckdb_with_schema(self, mock_makedirs, mock_query, mock_connect, mock_logger):
        """Test save_df_duckdb with schema in table name."""
        # Setup
        mock_logger.return_value = MagicMock()
        mock_conn = MagicMock()
        mock_connect.return_value = mock_conn

        # First CREATE SCHEMA succeeds, then INSERT fails, then CREATE TABLE succeeds
        mock_query.side_effect = [None, Exception("Table doesn't exist"), None]

        df = pd.DataFrame({"col1": [1, 2], "col2": ["a", "b"]})

        with patch.dict(os.environ, {}, clear=True):
            # Call function
            save_df_duckdb(df, "my_schema.test_table")

            # Assertions
            assert mock_query.call_count == 3
            mock_query.assert_any_call(
                connection=mock_conn, query="CREATE SCHEMA IF NOT EXISTS my_schema"
            )
            mock_query.assert_any_call(
                connection=mock_conn, query="INSERT INTO my_schema.test_table (col1, col2) SELECT col1, col2 FROM df"
            )
            mock_query.assert_any_call(
                connection=mock_conn, query="CREATE TABLE my_schema.test_table AS SELECT * FROM df"
            )


class TestRunSqlDuckdb:
    """Test the run_sql_duckdb function."""

    @patch("anomstack.external.duckdb.duckdb.get_dagster_logger")
    @patch("anomstack.external.duckdb.duckdb.connect")
    @patch("anomstack.external.duckdb.duckdb.query")
    @patch("anomstack.external.duckdb.duckdb.os.makedirs")
    def test_run_sql_duckdb_no_return(self, mock_makedirs, mock_query, mock_connect, mock_logger):
        """Test run_sql_duckdb without returning DataFrame."""
        # Setup
        mock_logger.return_value = MagicMock()
        mock_conn = MagicMock()
        mock_connect.return_value = mock_conn
        mock_query.return_value = None

        with patch.dict(os.environ, {}, clear=True):
            # Call function
            result = run_sql_duckdb("CREATE TABLE test AS SELECT 1 as col", return_df=False)

            # Assertions
            mock_connect.assert_called_once()
            mock_query.assert_called_once_with(
                connection=mock_conn, query="CREATE TABLE test AS SELECT 1 as col"
            )
            mock_conn.close.assert_called_once()
            assert result is None

    @patch("anomstack.external.duckdb.duckdb.get_dagster_logger")
    @patch("anomstack.external.duckdb.duckdb.connect")
    @patch("anomstack.external.duckdb.duckdb.query")
    @patch("anomstack.external.duckdb.duckdb.os.makedirs")
    def test_run_sql_duckdb_with_return(self, mock_makedirs, mock_query, mock_connect, mock_logger):
        """Test run_sql_duckdb with returning DataFrame."""
        # Setup
        mock_logger.return_value = MagicMock()
        mock_conn = MagicMock()
        mock_connect.return_value = mock_conn
        expected_df = pd.DataFrame({"result": [1, 2, 3]})
        mock_query.return_value.df.return_value = expected_df

        with patch.dict(os.environ, {}, clear=True):
            # Call function
            result = run_sql_duckdb("SELECT * FROM test", return_df=True)

            # Assertions
            mock_connect.assert_called_once()
            mock_query.assert_called_once_with(connection=mock_conn, query="SELECT * FROM test")
            mock_conn.close.assert_called_once()
            pd.testing.assert_frame_equal(result, expected_df)

    @patch("anomstack.external.duckdb.duckdb.get_dagster_logger")
    @patch("anomstack.external.duckdb.duckdb.connect")
    @patch("anomstack.external.duckdb.duckdb.query")
    @patch("anomstack.external.duckdb.duckdb.os.makedirs")
    def test_run_sql_duckdb_error_handling(
        self, mock_makedirs, mock_query, mock_connect, mock_logger
    ):
        """Test run_sql_duckdb error handling and connection cleanup."""
        # Setup
        mock_logger.return_value = MagicMock()
        mock_conn = MagicMock()
        mock_connect.return_value = mock_conn
        mock_query.side_effect = Exception("Database error")

        with patch.dict(os.environ, {}, clear=True):
            # Call function and expect exception
            with pytest.raises(Exception, match="Database error"):
                run_sql_duckdb("INVALID SQL", return_df=False)

            # Assertions
            mock_conn.close.assert_called_once()
            mock_logger.return_value.error.assert_called_once()
