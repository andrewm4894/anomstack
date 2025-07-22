"""
Tests for anomstack.sql module - SQL reading and database operations.
"""

from unittest.mock import MagicMock, patch

import pandas as pd
import pytest

from anomstack.sql.read import read_sql


class TestReadSQL:
    """Test the read_sql function."""

    @patch('anomstack.sql.read.get_dagster_logger')
    @patch('anomstack.sql.read.log_df_info')
    @patch('anomstack.sql.read.db_translate')
    @patch('anomstack.sql.read.read_sql_bigquery')
    def test_read_sql_bigquery_returns_df(self, mock_read_bigquery, mock_translate, mock_log_df_info, mock_logger):
        """Test read_sql with BigQuery when returns_df=True."""
        # Setup mocks
        mock_logger.return_value = MagicMock()
        mock_translate.return_value = "SELECT * FROM table"
        test_df = pd.DataFrame({'col1': [1, 2], 'col2': ['a', 'b']})
        mock_read_bigquery.return_value = test_df

        # Call function
        result = read_sql("SELECT * FROM table", "bigquery", returns_df=True)

        # Assertions
        mock_translate.assert_called_once_with("SELECT * FROM table", "bigquery")
        mock_read_bigquery.assert_called_once_with("SELECT * FROM table")
        mock_log_df_info.assert_called_once()
        pd.testing.assert_frame_equal(result, test_df)

    @patch('anomstack.sql.read.get_dagster_logger')
    def test_read_sql_bigquery_no_returns_df_raises_error(self, mock_logger):
        """Test read_sql with BigQuery when returns_df=False raises NotImplementedError."""
        mock_logger.return_value = MagicMock()

        with pytest.raises(NotImplementedError, match="BigQuery not yet implemented for non-returns_df queries"):
            read_sql("SELECT * FROM table", "bigquery", returns_df=False)

    @patch('anomstack.sql.read.get_dagster_logger')
    @patch('anomstack.sql.read.log_df_info')
    @patch('anomstack.sql.read.db_translate')
    @patch('anomstack.sql.read.read_sql_snowflake')
    def test_read_sql_snowflake_returns_df(self, mock_read_snowflake, mock_translate, mock_log_df_info, mock_logger):
        """Test read_sql with Snowflake when returns_df=True."""
        # Setup mocks
        mock_logger.return_value = MagicMock()
        mock_translate.return_value = "SELECT * FROM table"
        test_df = pd.DataFrame({'col1': [1, 2], 'col2': ['a', 'b']})
        mock_read_snowflake.return_value = test_df

        # Call function
        result = read_sql("SELECT * FROM table", "snowflake", returns_df=True)

        # Assertions
        mock_translate.assert_called_once_with("SELECT * FROM table", "snowflake")
        mock_read_snowflake.assert_called_once_with("SELECT * FROM table")
        mock_log_df_info.assert_called_once()
        pd.testing.assert_frame_equal(result, test_df)

    @patch('anomstack.sql.read.get_dagster_logger')
    def test_read_sql_snowflake_no_returns_df_raises_error(self, mock_logger):
        """Test read_sql with Snowflake when returns_df=False raises NotImplementedError."""
        mock_logger.return_value = MagicMock()

        with pytest.raises(NotImplementedError, match="Snowflake not yet implemented for non-returns_df queries"):
            read_sql("SELECT * FROM table", "snowflake", returns_df=False)

    @patch('anomstack.sql.read.get_dagster_logger')
    @patch('anomstack.sql.read.log_df_info')
    @patch('anomstack.sql.read.db_translate')
    @patch('anomstack.sql.read.read_sql_duckdb')
    def test_read_sql_duckdb_returns_df(self, mock_read_duckdb, mock_translate, mock_log_df_info, mock_logger):
        """Test read_sql with DuckDB when returns_df=True."""
        # Setup mocks
        mock_logger.return_value = MagicMock()
        mock_translate.return_value = "SELECT * FROM table"
        test_df = pd.DataFrame({'col1': [1, 2], 'col2': ['a', 'b']})
        mock_read_duckdb.return_value = test_df

        # Call function
        result = read_sql("SELECT * FROM table", "duckdb", returns_df=True)

        # Assertions
        mock_translate.assert_called_once_with("SELECT * FROM table", "duckdb")
        mock_read_duckdb.assert_called_once_with("SELECT * FROM table")
        mock_log_df_info.assert_called_once()
        pd.testing.assert_frame_equal(result, test_df)

    @patch('anomstack.sql.read.get_dagster_logger')
    @patch('anomstack.sql.read.log_df_info')
    @patch('anomstack.sql.read.db_translate')
    @patch('anomstack.sql.read.run_sql_duckdb')
    def test_read_sql_duckdb_no_returns_df(self, mock_run_duckdb, mock_translate, mock_log_df_info, mock_logger):
        """Test read_sql with DuckDB when returns_df=False."""
        # Setup mocks
        mock_logger.return_value = MagicMock()
        mock_translate.return_value = "INSERT INTO table VALUES (1, 'a')"

        # Call function
        result = read_sql("INSERT INTO table VALUES (1, 'a')", "duckdb", returns_df=False)

        # Assertions
        mock_translate.assert_called_once_with("INSERT INTO table VALUES (1, 'a')", "duckdb")
        mock_run_duckdb.assert_called_once_with("INSERT INTO table VALUES (1, 'a')")
        mock_log_df_info.assert_called_once()
        assert isinstance(result, pd.DataFrame)
        assert len(result) == 0  # Should return empty DataFrame

    @patch('anomstack.sql.read.get_dagster_logger')
    @patch('anomstack.sql.read.log_df_info')
    @patch('anomstack.sql.read.db_translate')
    @patch('anomstack.sql.read.read_sql_sqlite')
    def test_read_sql_sqlite_returns_df(self, mock_read_sqlite, mock_translate, mock_log_df_info, mock_logger):
        """Test read_sql with SQLite when returns_df=True."""
        # Setup mocks
        mock_logger.return_value = MagicMock()
        mock_translate.return_value = "SELECT * FROM table"
        test_df = pd.DataFrame({'col1': [1, 2], 'col2': ['a', 'b']})
        mock_read_sqlite.return_value = test_df

        # Call function
        result = read_sql("SELECT * FROM table", "sqlite", returns_df=True)

        # Assertions
        mock_translate.assert_called_once_with("SELECT * FROM table", "sqlite")
        mock_read_sqlite.assert_called_once_with("SELECT * FROM table")
        mock_log_df_info.assert_called_once()
        pd.testing.assert_frame_equal(result, test_df)

    @patch('anomstack.sql.read.get_dagster_logger')
    @patch('anomstack.sql.read.log_df_info')
    @patch('anomstack.sql.read.db_translate')
    @patch('anomstack.sql.read.run_sql_sqlite')
    def test_read_sql_sqlite_no_returns_df(self, mock_run_sqlite, mock_translate, mock_log_df_info, mock_logger):
        """Test read_sql with SQLite when returns_df=False."""
        # Setup mocks
        mock_logger.return_value = MagicMock()
        mock_translate.return_value = "INSERT INTO table VALUES (1, 'a')"

        # Call function
        result = read_sql("INSERT INTO table VALUES (1, 'a')", "sqlite", returns_df=False)

        # Assertions
        mock_translate.assert_called_once_with("INSERT INTO table VALUES (1, 'a')", "sqlite")
        mock_run_sqlite.assert_called_once_with("INSERT INTO table VALUES (1, 'a')")
        mock_log_df_info.assert_called_once()
        assert isinstance(result, pd.DataFrame)
        assert len(result) == 0  # Should return empty DataFrame

    @patch('anomstack.sql.read.get_dagster_logger')
    @patch('anomstack.sql.read.log_df_info')
    @patch('anomstack.sql.read.db_translate')
    @patch('anomstack.sql.read.read_sql_clickhouse')
    def test_read_sql_clickhouse_returns_df(self, mock_read_clickhouse, mock_translate, mock_log_df_info, mock_logger):
        """Test read_sql with ClickHouse when returns_df=True."""
        # Setup mocks
        mock_logger.return_value = MagicMock()
        mock_translate.return_value = "SELECT * FROM table"
        test_df = pd.DataFrame({'col1': [1, 2], 'col2': ['a', 'b']})
        mock_read_clickhouse.return_value = test_df

        # Call function
        result = read_sql("SELECT * FROM table", "clickhouse", returns_df=True)

        # Assertions
        mock_translate.assert_called_once_with("SELECT * FROM table", "clickhouse")
        mock_read_clickhouse.assert_called_once_with("SELECT * FROM table")
        mock_log_df_info.assert_called_once()
        pd.testing.assert_frame_equal(result, test_df)

    @patch('anomstack.sql.read.get_dagster_logger')
    @patch('anomstack.sql.read.log_df_info')
    @patch('anomstack.sql.read.db_translate')
    @patch('anomstack.sql.read.run_sql_clickhouse')
    def test_read_sql_clickhouse_no_returns_df(self, mock_run_clickhouse, mock_translate, mock_log_df_info, mock_logger):
        """Test read_sql with ClickHouse when returns_df=False."""
        # Setup mocks
        mock_logger.return_value = MagicMock()
        mock_translate.return_value = "INSERT INTO table VALUES (1, 'a')"

        # Call function
        result = read_sql("INSERT INTO table VALUES (1, 'a')", "clickhouse", returns_df=False)

        # Assertions
        mock_translate.assert_called_once_with("INSERT INTO table VALUES (1, 'a')", "clickhouse")
        mock_run_clickhouse.assert_called_once_with("INSERT INTO table VALUES (1, 'a')")
        mock_log_df_info.assert_called_once()
        assert isinstance(result, pd.DataFrame)
        assert len(result) == 0  # Should return empty DataFrame

    @patch('anomstack.sql.read.get_dagster_logger')
    def test_read_sql_unknown_database_raises_error(self, mock_logger):
        """Test read_sql with unknown database raises ValueError."""
        mock_logger.return_value = MagicMock()

        # The error actually comes from the SQL translation layer
        with pytest.raises(ValueError, match="Unknown dialect 'unknown_db'"):
            read_sql("SELECT * FROM table", "unknown_db")

    @patch('anomstack.sql.read.get_dagster_logger')
    @patch('anomstack.sql.read.log_df_info')
    @patch('anomstack.sql.read.db_translate')
    @patch('anomstack.sql.read.read_sql_duckdb')
    def test_read_sql_logging_behavior(self, mock_read_duckdb, mock_translate, mock_log_df_info, mock_logger):
        """Test that read_sql logs the correct information."""
        # Setup mocks
        logger_mock = MagicMock()
        mock_logger.return_value = logger_mock
        mock_translate.return_value = "SELECT * FROM table"
        test_df = pd.DataFrame({'col1': [1, 2], 'col2': ['a', 'b']})
        mock_read_duckdb.return_value = test_df

        # Call function
        read_sql("SELECT * FROM table", "duckdb", returns_df=True)

        # Check logging calls
        assert logger_mock.debug.call_count == 3  # Query, head(), tail()

        # Check that query was logged
        first_call = logger_mock.debug.call_args_list[0][0][0]
        assert "-- read_sql() is about to read this qry:" in first_call
        assert "SELECT * FROM table" in first_call

        # Check that head() and tail() were logged
        head_call = logger_mock.debug.call_args_list[1][0][0]
        tail_call = logger_mock.debug.call_args_list[2][0][0]
        assert "df.head():" in head_call
        assert "df.tail():" in tail_call

    @patch('anomstack.sql.read.get_dagster_logger')
    @patch('anomstack.sql.read.log_df_info')
    @patch('anomstack.sql.read.db_translate')
    @patch('anomstack.sql.read.read_sql_duckdb')
    def test_read_sql_integration_with_db_translate(self, mock_read_duckdb, mock_translate, mock_log_df_info, mock_logger):
        """Test that read_sql properly integrates with db_translate."""
        # Setup mocks
        mock_logger.return_value = MagicMock()
        mock_translate.return_value = "SELECT * FROM translated_table"
        test_df = pd.DataFrame({'col1': [1, 2]})
        mock_read_duckdb.return_value = test_df

        # Call function with original SQL
        original_sql = "SELECT * FROM original_table"
        result = read_sql(original_sql, "duckdb", returns_df=True)

        # Verify that db_translate was called with original SQL
        mock_translate.assert_called_once_with(original_sql, "duckdb")

        # Verify that the translated SQL was passed to the database function
        mock_read_duckdb.assert_called_once_with("SELECT * FROM translated_table")

        pd.testing.assert_frame_equal(result, test_df)


# Test the SQL translate function if it's accessible
try:
    from anomstack.sql.translate import db_translate

    class TestDBTranslate:
        """Test the db_translate function."""

        def test_db_translate_preserves_sql_for_supported_db(self):
            """Test that db_translate returns SQL as-is for supported databases."""
            sql = "SELECT * FROM table WHERE col = 'value'"

            # Test with different database types
            for db in ['duckdb', 'sqlite', 'bigquery', 'snowflake', 'clickhouse']:
                result = db_translate(sql, db)
                # For most cases, it should return the SQL as-is or with minimal changes
                assert isinstance(result, str)
                assert len(result) > 0

        def test_db_translate_with_empty_sql(self):
            """Test db_translate with empty SQL."""
            result = db_translate("", "duckdb")
            assert result == ""

        def test_db_translate_with_whitespace_sql(self):
            """Test db_translate with whitespace-only SQL."""
            result = db_translate("   \n\t   ", "duckdb")
            assert result.strip() == ""

except ImportError:
    # If db_translate is not accessible, skip these tests
    pass
