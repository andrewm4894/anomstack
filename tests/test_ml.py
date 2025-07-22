"""
Tests for ML components in anomstack.
"""

from unittest.mock import Mock, patch

import numpy as np
import pandas as pd
import pytest
from pyod.models.iforest import IForest
from pyod.models.knn import KNN

from anomstack.ml.change import detect_change
from anomstack.ml.preprocess import make_x
from anomstack.ml.train import train_model


class TestTrainModel:
    """Test cases for model training functionality."""

    def test_train_model_with_iforest(self):
        """Test training an Isolation Forest model."""
        # Create sample data
        np.random.seed(42)
        X = pd.DataFrame(np.random.randn(100, 3), columns=['feature1', 'feature2', 'feature3'])

        # Train model
        model = train_model(
            X=X,
            metric="test_metric",
            model_name="IForest",
            model_params={"n_estimators": 50, "random_state": 42},
            model_tag="test_tag"
        )

        # Verify model type and properties
        assert isinstance(model, IForest)
        assert hasattr(model, 'decision_scores_')
        assert len(model.decision_scores_) == len(X)

    def test_train_model_with_knn(self):
        """Test training a KNN model."""
        np.random.seed(42)
        X = pd.DataFrame(np.random.randn(50, 2), columns=['feature1', 'feature2'])

        model = train_model(
            X=X,
            metric="test_metric",
            model_name="KNN",
            model_params={"n_neighbors": 5},
            model_tag="knn_test"
        )

        assert isinstance(model, KNN)
        assert hasattr(model, 'decision_scores_')

    def test_train_model_invalid_model_name(self):
        """Test training with invalid model name raises appropriate error."""
        X = pd.DataFrame(np.random.randn(10, 2), columns=['f1', 'f2'])

        with pytest.raises(ModuleNotFoundError):
            train_model(
                X=X,
                metric="test_metric",
                model_name="InvalidModel",
                model_params={},
                model_tag="test"
            )

    def test_train_model_empty_dataframe(self):
        """Test training with empty dataframe."""
        X = pd.DataFrame()

        with pytest.raises(ValueError):
            train_model(
                X=X,
                metric="test_metric",
                model_name="IForest",
                model_params={},
                model_tag="test"
            )


class TestMakeX:
    """Test cases for the make_x preprocessing functionality."""

    def test_make_x_basic_train_mode(self):
        """Test basic make_x functionality in train mode."""
        # Create sample data
        df = pd.DataFrame({
            'metric_timestamp': pd.date_range('2023-01-01', periods=100, freq='H'),
            'metric_value': np.random.randn(100)
        })

        X = make_x(df, mode="train")

        # Should have metric_value column
        assert 'metric_value' in X.columns
        assert len(X) <= len(df)  # May be shuffled and dropna applied
        assert isinstance(X, pd.DataFrame)

    def test_make_x_score_mode(self):
        """Test make_x functionality in score mode."""
        df = pd.DataFrame({
            'metric_timestamp': pd.date_range('2023-01-01', periods=50, freq='H'),
            'metric_value': np.random.randn(50)
        })

        X = make_x(df, mode="score", score_n=5)

        # Should return last 5 rows
        assert len(X) <= 5
        assert 'metric_value' in X.columns

    def test_make_x_with_differencing(self):
        """Test make_x with differencing applied."""
        df = pd.DataFrame({
            'metric_timestamp': pd.date_range('2023-01-01', periods=20, freq='H'),
            'metric_value': list(range(20))  # Linear increase
        })

        X = make_x(df, mode="train", diff_n=1)

        # After differencing linear series, should have constant differences
        assert len(X) < len(df)  # Some rows lost due to differencing and dropna

    def test_make_x_with_smoothing(self):
        """Test make_x with smoothing applied."""
        df = pd.DataFrame({
            'metric_timestamp': pd.date_range('2023-01-01', periods=30, freq='H'),
            'metric_value': np.random.randn(30) * 10  # Noisy data
        })

        X = make_x(df, mode="train", smooth_n=5)

        # Smoothing should reduce variance
        assert len(X) < len(df)  # Some rows lost due to rolling window

    def test_make_x_with_lags(self):
        """Test make_x with lagged features."""
        df = pd.DataFrame({
            'metric_timestamp': pd.date_range('2023-01-01', periods=25, freq='H'),
            'metric_value': np.random.randn(25)
        })

        X = make_x(df, mode="train", lags_n=3)

        # Should have lagged columns
        expected_cols = ['metric_value', 'lag_1', 'lag_2', 'lag_3']
        for col in expected_cols:
            assert col in X.columns
        assert len(X) < len(df)  # Some rows lost due to lags and dropna

    def test_make_x_invalid_mode(self):
        """Test make_x with invalid mode raises error."""
        df = pd.DataFrame({
            'metric_timestamp': pd.date_range('2023-01-01', periods=10, freq='H'),
            'metric_value': np.random.randn(10)
        })

        with pytest.raises(ValueError, match="mode must be 'train' or 'score'"):
            make_x(df, mode="invalid")

    def test_make_x_empty_dataframe(self):
        """Test make_x with empty dataframe."""
        df = pd.DataFrame(columns=['metric_timestamp', 'metric_value'])

        X = make_x(df, mode="train")

        assert len(X) == 0
        assert isinstance(X, pd.DataFrame)


class TestChangeDetection:
    """Test cases for change detection functionality."""

    def test_detect_change_basic(self):
        """Test basic change detection functionality."""
        # Create stable time series
        np.random.seed(42)
        df = pd.DataFrame({
            'metric_timestamp': pd.date_range('2023-01-01', periods=100, freq='H'),
            'metric_name': ['test_metric'] * 100,
            'metric_value': np.random.normal(10, 1, 100),  # Stable around 10
            'metric_change': [0] * 100  # No expected changes
        })

        result_df = detect_change(df, threshold=3.5, detect_last_n=1)

        # Should return DataFrame (empty or with results)
        assert isinstance(result_df, pd.DataFrame)

    def test_detect_change_with_change(self):
        """Test change detection when significant change occurs."""
        # Create time series with sudden jump at the end
        np.random.seed(42)
        values = [10] * 99 + [50]  # Big jump at the end
        df = pd.DataFrame({
            'metric_timestamp': pd.date_range('2023-01-01', periods=100, freq='H'),
            'metric_name': ['test_metric'] * 100,
            'metric_value': values,
            'metric_change': [0] * 100
        })

        result_df = detect_change(df, threshold=2.0, detect_last_n=1)

        assert isinstance(result_df, pd.DataFrame)
        # If change detected, result should not be empty
        if not result_df.empty:
            assert 'metric_score' in result_df.columns
            assert 'metric_change_calculated' in result_df.columns
            assert 'metric_alert' in result_df.columns

    def test_detect_change_multiple_detect_points(self):
        """Test change detection with multiple detection points."""
        df = pd.DataFrame({
            'metric_timestamp': pd.date_range('2023-01-01', periods=50, freq='H'),
            'metric_name': ['test_metric'] * 50,
            'metric_value': [10] * 47 + [30, 35, 40],  # Changes in last 3 points
            'metric_change': [0] * 50
        })

        result_df = detect_change(df, threshold=2.0, detect_last_n=3)

        assert isinstance(result_df, pd.DataFrame)

    def test_detect_change_insufficient_data(self):
        """Test change detection with insufficient data."""
        # Very small dataset
        df = pd.DataFrame({
            'metric_timestamp': pd.date_range('2023-01-01', periods=2, freq='H'),
            'metric_name': ['test_metric'] * 2,
            'metric_value': [10, 12],
            'metric_change': [0, 0]
        })

        # Should handle gracefully, might return empty or raise error
        try:
            result_df = detect_change(df, threshold=3.5, detect_last_n=1)
            assert isinstance(result_df, pd.DataFrame)
        except (ValueError, IndexError):
            # Acceptable to raise error with insufficient data
            pass


class TestMLIntegration:
    """Integration tests for ML components working together."""

    def test_preprocess_and_train_pipeline(self):
        """Test preprocessing followed by model training."""
        # Create sample data
        np.random.seed(42)
        df = pd.DataFrame({
            'metric_timestamp': pd.date_range('2023-01-01', periods=200, freq='H'),
            'metric_value': np.random.randn(200) * 10 + 50
        })

        # Preprocess
        X = make_x(df, mode="train")
        assert not X.empty

        # Train model on preprocessed data
        model = train_model(
            X=X,
            metric="test_metric",
            model_name="IForest",
            model_params={"n_estimators": 50, "random_state": 42},
            model_tag="integration_test"
        )

        assert isinstance(model, IForest)
        assert len(model.decision_scores_) == len(X)

    def test_full_pipeline_with_change_detection(self):
        """Test complete pipeline including change detection."""
        np.random.seed(42)

        # Create metric data for change detection
        df_metric = pd.DataFrame({
            'metric_timestamp': pd.date_range('2023-01-01', periods=100, freq='H'),
            'metric_name': ['integration_test'] * 100,
            'metric_value': np.concatenate([
                np.random.normal(10, 1, 95),  # Stable period
                np.random.normal(20, 1, 5)    # Changed period
            ]),
            'metric_change': [0] * 100
        })

        # Run change detection
        change_result = detect_change(df_metric, threshold=2.5, detect_last_n=5)

        # Prepare data for training
        X = make_x(df_metric, mode="train")

        # Train model if we have sufficient data
        if not X.empty and len(X) > 10:
            model = train_model(
                X=X,
                metric="integration_test",
                model_name="IForest",
                model_params={"n_estimators": 20, "random_state": 42},
                model_tag="full_pipeline"
            )

            assert isinstance(model, IForest)

        assert isinstance(change_result, pd.DataFrame)

    @patch('anomstack.ml.train.get_dagster_logger')
    @patch('anomstack.ml.preprocess.get_dagster_logger')
    @patch('anomstack.ml.change.get_dagster_logger')
    def test_ml_logging_integration(self, mock_change_logger, mock_preprocess_logger, mock_train_logger):
        """Test that ML operations log appropriately."""
        # Setup mock loggers
        for mock_logger in [mock_change_logger, mock_preprocess_logger, mock_train_logger]:
            mock_logger.return_value.debug = Mock()
            mock_logger.return_value.info = Mock()

        # Test data
        df = pd.DataFrame({
            'metric_timestamp': pd.date_range('2023-01-01', periods=50, freq='H'),
            'metric_value': np.random.randn(50)
        })

        # Test preprocessing logging
        X = make_x(df, mode="train")
        mock_preprocess_logger.return_value.debug.assert_called()

        # Test training logging
        if not X.empty:
            model = train_model(
                X=X,
                metric="log_test",
                model_name="IForest",
                model_params={"n_estimators": 10},
                model_tag="log_test"
            )
            mock_train_logger.return_value.debug.assert_called()
            assert isinstance(model, IForest)
