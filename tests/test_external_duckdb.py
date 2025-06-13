"""
Tests for anomstack.external.duckdb module - DuckDB functionality.
"""

import os
import pytest
import pandas as pd
from unittest.mock import patch, MagicMock
from anomstack.external.duckdb.duckdb import read_sql_duckdb, save_df_duckdb, run_sql_duckdb


class TestReadSqlDuckdb:
    """Test read_sql_duckdb function."""
    
    @patch('anomstack.external.duckdb.duckdb.get_dagster_logger')
    @patch('anomstack.external.duckdb.duckdb.connect')
    @patch('anomstack.external.duckdb.duckdb.query')
    @patch('os.makedirs')
    def test_read_sql_duckdb_local_path(self, mock_makedirs, mock_query, mock_connect, mock_logger):
        """Test read_sql_duckdb with local path."""
        # Setup
        mock_logger.return_value = MagicMock()
        mock_conn = MagicMock()
        mock_connect.return_value = mock_conn
        expected_df = pd.DataFrame({'col1': [1, 2], 'col2': ['a', 'b']})
        mock_query.return_value.df.return_value = expected_df
        
        # Call function
        result = read_sql_duckdb("SELECT * FROM test_table")
        
        # Assertions
        mock_makedirs.assert_called_once_with("tmpdata", exist_ok=True)
        mock_connect.assert_called_once_with("tmpdata/anomstack-duckdb.db")
        mock_query.assert_called_once_with(connection=mock_conn, query="SELECT * FROM test_table")
        pd.testing.assert_frame_equal(result, expected_df)
    
    @patch('anomstack.external.duckdb.duckdb.get_dagster_logger')
    @patch('anomstack.external.duckdb.duckdb.connect')
    @patch('anomstack.external.duckdb.duckdb.query')
    @patch('os.makedirs')
    def test_read_sql_duckdb_with_env_path(self, mock_makedirs, mock_query, mock_connect, mock_logger):
        """Test read_sql_duckdb with environment variable path."""
        # Setup
        mock_logger.return_value = MagicMock()
        mock_conn = MagicMock()
        mock_connect.return_value = mock_conn
        expected_df = pd.DataFrame({'col1': [1, 2], 'col2': ['a', 'b']})
        mock_query.return_value.df.return_value = expected_df
        
        with patch.dict(os.environ, {'ANOMSTACK_DUCKDB_PATH': 'custom/path/test.db'}):
            # Call function
            result = read_sql_duckdb("SELECT COUNT(*) FROM users")
            
            # Assertions
            mock_makedirs.assert_called_once_with("custom/path", exist_ok=True)
            mock_connect.assert_called_once_with("custom/path/test.db")
            pd.testing.assert_frame_equal(result, expected_df)
    
    @patch('anomstack.external.duckdb.duckdb.get_dagster_logger')
    @patch('anomstack.external.duckdb.duckdb.connect')
    @patch('anomstack.external.duckdb.duckdb.query')
    @patch('os.makedirs')
    def test_read_sql_duckdb_motherduck_with_token(self, mock_makedirs, mock_query, mock_connect, mock_logger):
        """Test read_sql_duckdb with MotherDuck and token."""
        # Setup
        mock_logger.return_value = MagicMock()
        mock_conn = MagicMock()
        mock_connect.return_value = mock_conn
        expected_df = pd.DataFrame({'result': [42]})
        mock_query.return_value.df.return_value = expected_df
        
        with patch.dict(os.environ, {
            'ANOMSTACK_DUCKDB_PATH': 'md:my_db',
            'ANOMSTACK_MOTHERDUCK_TOKEN': 'test_token_123'
        }):
            # Call function
            result = read_sql_duckdb("SELECT 42 as result")
            
            # Assertions
            mock_connect.assert_called_once_with("md:my_db?motherduck_token=test_token_123")
            pd.testing.assert_frame_equal(result, expected_df)
    
    @patch('anomstack.external.duckdb.duckdb.get_dagster_logger')
    @patch('anomstack.external.duckdb.duckdb.connect')
    @patch('anomstack.external.duckdb.duckdb.query')
    @patch('os.makedirs')
    def test_read_sql_duckdb_motherduck_no_token_fallback(self, mock_makedirs, mock_query, mock_connect, mock_logger):
        """Test read_sql_duckdb with MotherDuck but no token, should fallback to local."""
        # Setup
        mock_logger.return_value = MagicMock()
        mock_conn = MagicMock()
        mock_connect.return_value = mock_conn
        expected_df = pd.DataFrame({'result': [42]})
        mock_query.return_value.df.return_value = expected_df
        
        with patch.dict(os.environ, {'ANOMSTACK_DUCKDB_PATH': 'md:my_db'}, clear=True):
            # Call function
            result = read_sql_duckdb("SELECT 42 as result")
            
            # Assertions
            mock_logger.return_value.warning.assert_called_once()
            mock_connect.assert_called_once_with("tmpdata/anomstack-duckdb.db")
            pd.testing.assert_frame_equal(result, expected_df)


class TestSaveDfDuckdb:
    """Test save_df_duckdb function."""
    
    @patch('anomstack.external.duckdb.duckdb.get_dagster_logger')
    @patch('anomstack.external.duckdb.duckdb.connect')
    @patch('anomstack.external.duckdb.duckdb.query')
    @patch('os.makedirs')
    def test_save_df_duckdb_create_table(self, mock_makedirs, mock_query, mock_connect, mock_logger):
        """Test save_df_duckdb creating new table."""
        # Setup
        mock_logger.return_value = MagicMock()
        mock_conn = MagicMock()
        mock_connect.return_value = mock_conn
        
        # First INSERT fails, then CREATE TABLE succeeds
        mock_query.side_effect = [Exception("Table doesn't exist"), None]
        
        df = pd.DataFrame({'col1': [1, 2], 'col2': ['a', 'b']})
        
        # Call function
        result = save_df_duckdb(df, "test_table")
        
        # Assertions
        mock_makedirs.assert_called_once_with("tmpdata", exist_ok=True)
        mock_connect.assert_called_once()
        assert mock_query.call_count == 2
        mock_query.assert_any_call(connection=mock_conn, query="INSERT INTO test_table SELECT * FROM df")
        mock_query.assert_any_call(connection=mock_conn, query="CREATE TABLE test_table AS SELECT * FROM df")
        pd.testing.assert_frame_equal(result, df)


class TestRunSqlDuckdb:
    """Test run_sql_duckdb function."""
    
    @patch('anomstack.external.duckdb.duckdb.get_dagster_logger')
    @patch('anomstack.external.duckdb.duckdb.connect')
    @patch('anomstack.external.duckdb.duckdb.query')
    @patch('os.makedirs')
    def test_run_sql_duckdb_no_return(self, mock_makedirs, mock_query, mock_connect, mock_logger):
        """Test run_sql_duckdb without returning DataFrame."""
        # Setup
        mock_logger.return_value = MagicMock()
        mock_conn = MagicMock()
        mock_connect.return_value = mock_conn
        mock_query.return_value = None
        
        # Call function
        result = run_sql_duckdb("CREATE TABLE test AS SELECT 1 as col", return_df=False)
        
        # Assertions
        mock_makedirs.assert_called_once_with("tmpdata", exist_ok=True)
        mock_connect.assert_called_once()
        mock_query.assert_called_once_with(connection=mock_conn, query="CREATE TABLE test AS SELECT 1 as col")
        mock_conn.close.assert_called_once()
        assert result is None 