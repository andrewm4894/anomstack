"""
Tests for anomstack.df module - data wrangling and manipulation functions.
"""

import json
from unittest.mock import MagicMock, patch

import pandas as pd

from anomstack.df.wrangle import (
    add_threshold_metadata_to_row,
    extract_metadata,
    wrangle_df,
)


class TestWrangleDF:
    """Test the wrangle_df function."""

    def test_wrangle_df_basic(self):
        """Test basic functionality of wrangle_df."""
        # Create test data
        df = pd.DataFrame({
            'metric_timestamp': ['2023-01-01 10:00:00', '2023-01-01 11:00:00'],
            'metric_batch': ['batch1', 'batch2'],
            'metric_name': ['cpu_usage', 'memory_usage'],
            'metric_type': ['gauge', 'gauge'],
            'metric_value': ['85.5', '67.2'],  # String values to test conversion
            'metadata': ['{}', '{}']
        })

        result = wrangle_df(df)

        # Check data types
        assert pd.api.types.is_numeric_dtype(result['metric_value'])
        assert pd.api.types.is_datetime64_any_dtype(result['metric_timestamp'])

        # Check values
        assert result['metric_value'].iloc[0] == 85.5
        assert result['metric_value'].iloc[1] == 67.2

        # Check column order
        expected_columns = [
            'metric_timestamp', 'metric_batch', 'metric_name',
            'metric_type', 'metric_value', 'metadata'
        ]
        assert list(result.columns) == expected_columns

    def test_wrangle_df_with_nan_values(self):
        """Test wrangle_df handles NaN values correctly."""
        df = pd.DataFrame({
            'metric_timestamp': ['2023-01-01 10:00:00', '2023-01-01 11:00:00', '2023-01-01 12:00:00'],
            'metric_batch': ['batch1', 'batch2', 'batch3'],
            'metric_name': ['cpu_usage', 'memory_usage', 'disk_usage'],
            'metric_type': ['gauge', 'gauge', 'gauge'],
            'metric_value': ['85.5', 'invalid', '67.2'],  # 'invalid' will become NaN
            'metadata': ['{}', '{}', '{}']
        })

        with patch('anomstack.df.wrangle.get_dagster_logger') as mock_logger:
            mock_logger.return_value = MagicMock()
            result = wrangle_df(df)

            # Should have dropped the NaN row
            assert len(result) == 2
            assert result['metric_value'].notna().all()

            # Check that warning was logged
            mock_logger.return_value.warning.assert_called_once()

    def test_wrangle_df_missing_metadata_column(self):
        """Test wrangle_df adds metadata column if missing."""
        df = pd.DataFrame({
            'metric_timestamp': ['2023-01-01 10:00:00'],
            'metric_batch': ['batch1'],
            'metric_name': ['cpu_usage'],
            'metric_type': ['gauge'],
            'metric_value': [85.5]
        })

        result = wrangle_df(df)

        assert 'metadata' in result.columns
        assert result['metadata'].iloc[0] == ""

    def test_wrangle_df_rounding(self):
        """Test wrangle_df rounds values correctly."""
        df = pd.DataFrame({
            'metric_timestamp': ['2023-01-01 10:00:00'],
            'metric_batch': ['batch1'],
            'metric_name': ['cpu_usage'],
            'metric_type': ['gauge'],
            'metric_value': [85.123456789],
            'metadata': ['{}']
        })

        result = wrangle_df(df, rounding=2)

        assert result['metric_value'].iloc[0] == 85.12

    def test_wrangle_df_invalid_timestamps(self):
        """Test wrangle_df handles invalid timestamps."""
        df = pd.DataFrame({
            'metric_timestamp': ['invalid_date', '2023-01-01 11:00:00'],
            'metric_batch': ['batch1', 'batch2'],
            'metric_name': ['cpu_usage', 'memory_usage'],
            'metric_type': ['gauge', 'gauge'],
            'metric_value': [85.5, 67.2],
            'metadata': ['{}', '{}']
        })

        result = wrangle_df(df)

        # Invalid timestamps should become NaT
        assert pd.isna(result['metric_timestamp'].iloc[0])
        assert not pd.isna(result['metric_timestamp'].iloc[1])


class TestExtractMetadata:
    """Test the extract_metadata function."""

    def test_extract_metadata_basic(self):
        """Test basic metadata extraction."""
        df = pd.DataFrame({
            'metric_name': ['test_metric'],
            'metadata': ['{"host": "server1", "env": "prod"}']
        })

        result = extract_metadata(df, 'host')

        assert 'host' in result.columns
        assert result['host'].iloc[0] == 'server1'

    def test_extract_metadata_no_metadata_column(self):
        """Test extract_metadata when metadata column is missing."""
        df = pd.DataFrame({
            'metric_name': ['test_metric']
        })

        result = extract_metadata(df, 'host')

        # Should return original df unchanged
        assert 'host' not in result.columns
        assert list(result.columns) == ['metric_name']

    def test_extract_metadata_invalid_json(self):
        """Test extract_metadata with invalid JSON."""
        df = pd.DataFrame({
            'metric_name': ['test_metric1', 'test_metric2'],
            'metadata': ['invalid_json', '{"host": "server1"}']
        })

        result = extract_metadata(df, 'host')

        assert 'host' in result.columns
        assert pd.isna(result['host'].iloc[0])  # Invalid JSON should return None
        assert result['host'].iloc[1] == 'server1'

    def test_extract_metadata_empty_values(self):
        """Test extract_metadata with empty/null values."""
        df = pd.DataFrame({
            'metric_name': ['test1', 'test2', 'test3', 'test4'],
            'metadata': [None, '', '   ', '{"host": "server1"}']
        })

        result = extract_metadata(df, 'host')

        assert 'host' in result.columns
        assert pd.isna(result['host'].iloc[0])  # None
        assert pd.isna(result['host'].iloc[1])  # Empty string
        assert pd.isna(result['host'].iloc[2])  # Whitespace
        assert result['host'].iloc[3] == 'server1'

    def test_extract_metadata_with_array_input(self):
        """Test extract_metadata with array/list input."""
        df = pd.DataFrame({
            'metric_name': ['test_metric'],
            'metadata': [['{"host": "server1"}', None, '{"host": "server2"}']]
        })

        result = extract_metadata(df, 'host')

        assert 'host' in result.columns
        assert result['host'].iloc[0] == 'server1'  # Should take first non-None element

    def test_extract_metadata_missing_key(self):
        """Test extract_metadata when key doesn't exist in JSON."""
        df = pd.DataFrame({
            'metric_name': ['test_metric'],
            'metadata': ['{"env": "prod", "region": "us-east-1"}']
        })

        result = extract_metadata(df, 'host')

        assert 'host' in result.columns
        assert pd.isna(result['host'].iloc[0])

    def test_extract_metadata_none_string_conversion(self):
        """Test extract_metadata converts 'None' strings to None."""
        df = pd.DataFrame({
            'metric_name': ['test1', 'test2'],
            'metadata': ['{"host": "None"}', '{"host": "server1"}']
        })

        result = extract_metadata(df, 'host')

        assert 'host' in result.columns
        assert pd.isna(result['host'].iloc[0])  # 'None' string should become None
        assert result['host'].iloc[1] == 'server1'

    def test_extract_metadata_preserves_original_df(self):
        """Test that extract_metadata doesn't modify the original DataFrame."""
        original_df = pd.DataFrame({
            'metric_name': ['test_metric'],
            'metadata': ['{"host": "server1"}']
        })

        # Make a copy to compare
        original_copy = original_df.copy()

        result = extract_metadata(original_df, 'host')

        # Original df should be unchanged
        pd.testing.assert_frame_equal(original_df, original_copy)

        # Result should have the new column
        assert 'host' in result.columns
        assert 'host' not in original_df.columns


class TestAddThresholdMetadata:
    """Test the add_threshold_metadata_to_row function."""

    def test_add_threshold_metadata_basic(self):
        """Test basic threshold metadata addition."""
        row = pd.Series({
            'metric_name': 'cpu_usage',
            'metadata': '{}'
        })

        thresholds = {
            'cpu_usage': {'upper': 90, 'lower': 10}
        }

        result = add_threshold_metadata_to_row(row, thresholds)

        expected_metadata = {
            'thresholds': {'upper': 90, 'lower': 10}
        }

        assert result == json.dumps(expected_metadata)

    def test_add_threshold_metadata_no_thresholds_for_metric(self):
        """Test when no thresholds exist for the specific metric."""
        row = pd.Series({
            'metric_name': 'memory_usage',
            'metadata': '{}'
        })

        thresholds = {
            'cpu_usage': {'upper': 90, 'lower': 10}
        }

        result = add_threshold_metadata_to_row(row, thresholds)

        assert result == ""  # Should return empty string when no metadata to add

    def test_add_threshold_metadata_preserves_existing_metadata(self):
        """Test that existing metadata is preserved when adding thresholds."""
        row = pd.Series({
            'metric_name': 'cpu_usage',
            'metadata': '{"host": "server1", "env": "prod"}'
        })

        thresholds = {
            'cpu_usage': {'upper': 90, 'lower': 10}
        }

        result = add_threshold_metadata_to_row(row, thresholds)
        parsed_result = json.loads(result)

        # Should preserve existing metadata
        assert parsed_result['host'] == 'server1'
        assert parsed_result['env'] == 'prod'

        # Should add threshold metadata
        assert parsed_result['thresholds'] == {'upper': 90, 'lower': 10}

    def test_add_threshold_metadata_with_breach_details(self):
        """Test adding breach details for threshold alerts."""
        row = pd.Series({
            'metric_name': 'cpu_usage',
            'metric_value': 95.2,
            'threshold_type': 'upper',
            'threshold_value': 90,
            'metadata': '{}'
        })

        thresholds = {
            'cpu_usage': {'upper': 90, 'lower': 10}
        }

        result = add_threshold_metadata_to_row(row, thresholds, include_breach_details=True)
        parsed_result = json.loads(result)

        # Should include threshold configuration
        assert parsed_result['thresholds'] == {'upper': 90, 'lower': 10}

        # Should include breach details
        assert parsed_result['breached_threshold_type'] == 'upper'
        assert parsed_result['breached_threshold_value'] == 90
        assert parsed_result['metric_value_at_breach'] == 95.2

    def test_add_threshold_metadata_invalid_existing_metadata(self):
        """Test handling of invalid existing metadata JSON."""
        row = pd.Series({
            'metric_name': 'cpu_usage',
            'metadata': 'invalid_json'
        })

        thresholds = {
            'cpu_usage': {'upper': 90, 'lower': 10}
        }

        result = add_threshold_metadata_to_row(row, thresholds)

        # Should create new metadata despite invalid existing metadata
        expected_metadata = {
            'thresholds': {'upper': 90, 'lower': 10}
        }

        assert result == json.dumps(expected_metadata)

    def test_add_threshold_metadata_empty_thresholds_dict(self):
        """Test with empty thresholds dictionary."""
        row = pd.Series({
            'metric_name': 'cpu_usage',
            'metadata': '{}'
        })

        thresholds = {}

        result = add_threshold_metadata_to_row(row, thresholds)

        assert result == ""  # Should return empty string

    def test_add_threshold_metadata_missing_metric_name(self):
        """Test with missing metric_name in row."""
        row = pd.Series({
            'metadata': '{}'
        })

        thresholds = {
            'cpu_usage': {'upper': 90, 'lower': 10}
        }

        result = add_threshold_metadata_to_row(row, thresholds)

        assert result == ""  # Should return empty string

    def test_add_threshold_metadata_none_values_in_breach_details(self):
        """Test breach details with None/NaN values."""
        row = pd.Series({
            'metric_name': 'cpu_usage',
            'metric_value': 95.2,
            'threshold_type': None,  # None value
            'threshold_value': 90,
            'metadata': '{}'
        })

        thresholds = {
            'cpu_usage': {'upper': 90, 'lower': 10}
        }

        result = add_threshold_metadata_to_row(row, thresholds, include_breach_details=True)
        parsed_result = json.loads(result)

        # Should include threshold configuration
        assert parsed_result['thresholds'] == {'upper': 90, 'lower': 10}

        # Should include non-None breach details only
        assert 'breached_threshold_type' not in parsed_result  # None value should be skipped
        assert parsed_result['breached_threshold_value'] == 90
        assert parsed_result['metric_value_at_breach'] == 95.2

    def test_add_threshold_metadata_no_existing_metadata_column(self):
        """Test when metadata column doesn't exist in row."""
        row = pd.Series({
            'metric_name': 'cpu_usage'
        })

        thresholds = {
            'cpu_usage': {'upper': 90, 'lower': 10}
        }

        result = add_threshold_metadata_to_row(row, thresholds)

        expected_metadata = {
            'thresholds': {'upper': 90, 'lower': 10}
        }

        assert result == json.dumps(expected_metadata)
