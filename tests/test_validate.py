"""
Tests for anomstack.validate module - data validation functions.
"""

import pytest
import pandas as pd
import numpy as np
from unittest.mock import patch, MagicMock
from io import StringIO

from anomstack.validate.validate import validate_df


class TestValidateDF:
    """Test the validate_df function."""
    
    def test_validate_df_valid_data(self):
        """Test validate_df with valid data."""
        df = pd.DataFrame({
            'metric_timestamp': pd.to_datetime(['2023-01-01 10:00:00', '2023-01-01 11:00:00']),
            'metric_batch': ['batch1', 'batch2'],
            'metric_name': ['cpu_usage', 'memory_usage'],
            'metric_type': ['gauge', 'gauge'],
            'metric_value': [85.5, 67.2],
            'metadata': ['{}', '{}']
        })
        
        with patch('anomstack.validate.validate.get_dagster_logger') as mock_logger:
            mock_logger.return_value = MagicMock()
            result = validate_df(df)
            
            # Should return the same dataframe if valid
            pd.testing.assert_frame_equal(result, df)
            
            # Should have logged debug info
            mock_logger.return_value.debug.assert_called_once()
    
    def test_validate_df_missing_columns(self):
        """Test validate_df with missing required columns."""
        test_cases = [
            # Missing metric_type
            {
                'metric_timestamp': pd.to_datetime(['2023-01-01 10:00:00']),
                'metric_batch': ['batch1'],
                'metric_name': ['cpu_usage'],
                'metric_value': [85.5],
                'metadata': ['{}']
            },
            # Missing metric_batch
            {
                'metric_timestamp': pd.to_datetime(['2023-01-01 10:00:00']),
                'metric_type': ['gauge'],
                'metric_name': ['cpu_usage'],
                'metric_value': [85.5],
                'metadata': ['{}']
            },
            # Missing metric_name
            {
                'metric_timestamp': pd.to_datetime(['2023-01-01 10:00:00']),
                'metric_batch': ['batch1'],
                'metric_type': ['gauge'],
                'metric_value': [85.5],
                'metadata': ['{}']
            },
            # Missing metric_value
            {
                'metric_timestamp': pd.to_datetime(['2023-01-01 10:00:00']),
                'metric_batch': ['batch1'],
                'metric_name': ['cpu_usage'],
                'metric_type': ['gauge'],
                'metadata': ['{}']
            },
            # Missing metadata
            {
                'metric_timestamp': pd.to_datetime(['2023-01-01 10:00:00']),
                'metric_batch': ['batch1'],
                'metric_name': ['cpu_usage'],
                'metric_type': ['gauge'],
                'metric_value': [85.5]
            },
            # Missing metric_timestamp
            {
                'metric_batch': ['batch1'],
                'metric_name': ['cpu_usage'],
                'metric_type': ['gauge'],
                'metric_value': [85.5],
                'metadata': ['{}']
            }
        ]
        
        for test_df_dict in test_cases:
            df = pd.DataFrame(test_df_dict)
            with pytest.raises(AssertionError):
                validate_df(df)
    
    def test_validate_df_wrong_column_count(self):
        """Test validate_df with wrong number of columns."""
        # Too many columns
        df_too_many = pd.DataFrame({
            'metric_timestamp': pd.to_datetime(['2023-01-01 10:00:00']),
            'metric_batch': ['batch1'],
            'metric_name': ['cpu_usage'],
            'metric_type': ['gauge'],
            'metric_value': [85.5],
            'metadata': ['{}'],
            'extra_column': ['extra']
        })
        
        with pytest.raises(AssertionError, match="expected 6 columns, got 7"):
            validate_df(df_too_many)
        
        # Too few columns (missing metadata)
        df_too_few = pd.DataFrame({
            'metric_timestamp': pd.to_datetime(['2023-01-01 10:00:00']),
            'metric_batch': ['batch1'],
            'metric_name': ['cpu_usage'],
            'metric_type': ['gauge'],
            'metric_value': [85.5]
        })
        
        with pytest.raises(AssertionError, match="metadata column missing"):
            validate_df(df_too_few)
    
    def test_validate_df_empty_dataframe(self):
        """Test validate_df with empty dataframe."""
        df = pd.DataFrame({
            'metric_timestamp': pd.to_datetime([]),
            'metric_batch': [],
            'metric_name': [],
            'metric_type': [],
            'metric_value': [],
            'metadata': []
        })
        
        with pytest.raises(AssertionError, match="no data returned"):
            validate_df(df)
    
    def test_validate_df_wrong_data_types(self):
        """Test validate_df with wrong data types."""
        # Wrong metric_name type (should be string/object)
        df_wrong_name_type = pd.DataFrame({
            'metric_timestamp': pd.to_datetime(['2023-01-01 10:00:00']),
            'metric_batch': ['batch1'],
            'metric_name': [123],  # Should be string
            'metric_type': ['gauge'],
            'metric_value': [85.5],
            'metadata': ['{}']
        })
        
        with pytest.raises(AssertionError, match="metric_name is not string"):
            validate_df(df_wrong_name_type)
        
        # Wrong metric_value type (should be numeric)
        df_wrong_value_type = pd.DataFrame({
            'metric_timestamp': pd.to_datetime(['2023-01-01 10:00:00']),
            'metric_batch': ['batch1'],
            'metric_name': ['cpu_usage'],
            'metric_type': ['gauge'],
            'metric_value': ['not_numeric'],  # Should be numeric
            'metadata': ['{}']
        })
        
        with pytest.raises(AssertionError, match="metric_value is not numeric"):
            validate_df(df_wrong_value_type)
        
        # Wrong metric_timestamp type (should be datetime)
        df_wrong_timestamp_type = pd.DataFrame({
            'metric_timestamp': ['not_datetime'],  # Should be datetime
            'metric_batch': ['batch1'],
            'metric_name': ['cpu_usage'],
            'metric_type': ['gauge'],
            'metric_value': [85.5],
            'metadata': ['{}']
        })
        
        with pytest.raises(AssertionError, match="metric_timestamp is not timestamp"):
            validate_df(df_wrong_timestamp_type)
    
    def test_validate_df_case_insensitive_columns(self):
        """Test validate_df works with different case column names."""
        # The validation function only checks for presence case-insensitively
        # but then tries to access columns with exact names, so this will fail
        # This test documents the current behavior
        df = pd.DataFrame({
            'METRIC_TIMESTAMP': pd.to_datetime(['2023-01-01 10:00:00']),
            'Metric_Batch': ['batch1'],
            'metric_name': ['cpu_usage'],
            'METRIC_TYPE': ['gauge'],
            'metric_value': [85.5],
            'MetaData': ['{}']
        })
        
        # This should raise a KeyError because validate_df expects exact column names
        # after the case-insensitive check
        with pytest.raises(KeyError, match="metric_timestamp"):
            validate_df(df)
    
    def test_validate_df_debug_logging(self):
        """Test that validate_df logs debug information."""
        df = pd.DataFrame({
            'metric_timestamp': pd.to_datetime(['2023-01-01 10:00:00']),
            'metric_batch': ['batch1'],
            'metric_name': ['cpu_usage'],
            'metric_type': ['gauge'],
            'metric_value': [85.5],
            'metadata': ['{}']
        })
        
        with patch('anomstack.validate.validate.get_dagster_logger') as mock_logger:
            mock_logger.return_value = MagicMock()
            
            validate_df(df)
            
            # Should have called debug with df.info() output
            mock_logger.return_value.debug.assert_called_once()
            call_args = mock_logger.return_value.debug.call_args[0][0]
            assert "df.info()" in call_args
    
    def test_validate_df_with_various_numeric_types(self):
        """Test validate_df accepts various numeric types for metric_value."""
        numeric_types = [
            [85.5],  # float
            [85],    # int
            [np.float64(85.5)],  # numpy float
            [np.int64(85)],      # numpy int
        ]
        
        for values in numeric_types:
            df = pd.DataFrame({
                'metric_timestamp': pd.to_datetime(['2023-01-01 10:00:00']),
                'metric_batch': ['batch1'],
                'metric_name': ['cpu_usage'],
                'metric_type': ['gauge'],
                'metric_value': values,
                'metadata': ['{}']
            })
            
            with patch('anomstack.validate.validate.get_dagster_logger') as mock_logger:
                mock_logger.return_value = MagicMock()
                result = validate_df(df)
                pd.testing.assert_frame_equal(result, df)
    
    def test_validate_df_with_various_datetime_types(self):
        """Test validate_df accepts various datetime types for metric_timestamp."""
        datetime_types = [
            pd.to_datetime(['2023-01-01 10:00:00']),
            pd.to_datetime(['2023-01-01 10:00:00']).astype('datetime64[ns]'),
            pd.to_datetime(['2023-01-01 10:00:00']).astype('datetime64[ms]'),
        ]
        
        for timestamps in datetime_types:
            df = pd.DataFrame({
                'metric_timestamp': timestamps,
                'metric_batch': ['batch1'],
                'metric_name': ['cpu_usage'],
                'metric_type': ['gauge'],
                'metric_value': [85.5],
                'metadata': ['{}']
            })
            
            with patch('anomstack.validate.validate.get_dagster_logger') as mock_logger:
                mock_logger.return_value = MagicMock()
                result = validate_df(df)
                pd.testing.assert_frame_equal(result, df) 