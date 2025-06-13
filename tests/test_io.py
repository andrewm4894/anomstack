"""
Tests for IO operations in anomstack (model saving/loading).
"""

import os
import tempfile
import pickle
from unittest.mock import Mock, patch
import pytest
from pyod.models.iforest import IForest
from pyod.models.knn import KNN
import numpy as np

from anomstack.io.save import save_models, save_models_local
from anomstack.io.load import load_model, load_model_local


class TestSaveModels:
    """Test cases for model saving functionality."""
    
    def test_save_models_local(self):
        """Test saving models locally."""
        # Create test models
        model1 = IForest(n_estimators=10, random_state=42)
        model2 = KNN(n_neighbors=3)
        
        # Fit models with dummy data
        X = np.random.randn(50, 2)
        model1.fit(X)
        model2.fit(X)
        
        models = [
            ("metric1", model1, "iforest_tag"),
            ("metric2", model2, "knn_tag")
        ]
        
        with tempfile.TemporaryDirectory() as temp_dir:
            model_path = f"local://{temp_dir}"
            metric_batch = "test_batch"
            
            result = save_models_local(models, model_path, metric_batch)
            
            # Check that models were saved
            assert len(result) == 2
            assert os.path.exists(f"{temp_dir}/test_batch")
            assert os.path.exists(f"{temp_dir}/test_batch/metric1_iforest_tag.pkl")
            assert os.path.exists(f"{temp_dir}/test_batch/metric2_knn_tag.pkl")
            
    @patch('anomstack.io.save.save_models_gcs')
    def test_save_models_gcs_path(self, mock_save_gcs):
        """Test that GCS path triggers GCS save function."""
        models = [("test_metric", Mock(), "test_tag")]
        mock_save_gcs.return_value = models
        
        result = save_models(models, "gs://test-bucket/models", "test_batch")
        
        mock_save_gcs.assert_called_once_with(models, "gs://test-bucket/models", "test_batch")
        assert result == models
        
    def test_save_models_invalid_path(self):
        """Test that invalid model path raises error."""
        models = [("test_metric", Mock(), "test_tag")]
        
        with pytest.raises(ValueError, match="model_path .* not supported"):
            save_models(models, "invalid://path", "test_batch")


class TestLoadModel:
    """Test cases for model loading functionality."""
    
    def test_load_model_local(self):
        """Test loading a single model from local storage."""
        # Create and save test model first
        model = IForest(n_estimators=10, random_state=42)
        X = np.random.randn(50, 2)
        model.fit(X)
        
        models = [("test_metric", model, "test_tag")]
        
        with tempfile.TemporaryDirectory() as temp_dir:
            model_path = f"local://{temp_dir}"
            metric_batch = "test_batch"
            
            # Save model first
            save_models_local(models, model_path, metric_batch)
            
            # Now test loading
            loaded_model = load_model_local("test_metric", model_path, metric_batch, "test_tag")
            
            assert isinstance(loaded_model, IForest)
            # Test that loaded model can score new data
            X_new = np.random.randn(10, 2)
            scores = loaded_model.decision_function(X_new)
            assert len(scores) == 10
            
    def test_load_model_local_missing_file(self):
        """Test loading model when file doesn't exist."""
        with tempfile.TemporaryDirectory() as temp_dir:
            model_path = f"local://{temp_dir}"
            
            with pytest.raises(FileNotFoundError):
                load_model_local("nonexistent_metric", model_path, "test_batch", "test_tag")
                
    @patch('anomstack.io.load.load_model_gcs')
    def test_load_model_gcs_path(self, mock_load_gcs):
        """Test that GCS path triggers GCS load function."""
        mock_model = Mock()
        mock_load_gcs.return_value = mock_model
        
        result = load_model("test_metric", "gs://test-bucket/models", "test_batch", "test_tag")
        
        mock_load_gcs.assert_called_once_with("test_metric", "gs://test-bucket/models", "test_batch", "test_tag")
        assert result == mock_model
        
    def test_load_model_invalid_path(self):
        """Test that invalid model path raises error."""
        with pytest.raises(ValueError, match="model_path .* not supported"):
            load_model("test_metric", "invalid://path", "test_batch", "test_tag")


class TestIOIntegration:
    """Integration tests for save/load operations."""
    
    def test_save_load_cycle(self):
        """Test complete save and load cycle."""
        # Create test model
        model = IForest(n_estimators=10, random_state=42)
        
        # Train model
        X = np.random.randn(100, 3)
        model.fit(X)
        
        models = [("test_metric", model, "iforest_v1")]
        
        with tempfile.TemporaryDirectory() as temp_dir:
            model_path = f"local://{temp_dir}"
            metric_batch = "integration_test"
            
            # Save model
            saved_models = save_models(models, model_path, metric_batch)
            assert len(saved_models) == 1
            
            # Load model using the single model load function
            loaded_model = load_model("test_metric", model_path, metric_batch, "iforest_v1")
            
            # Verify loaded model works correctly
            assert isinstance(loaded_model, IForest)
            
            # Test that loaded model can score new data
            X_new = np.random.randn(10, 3)
            scores = loaded_model.decision_function(X_new)
            
            assert len(scores) == 10
            assert isinstance(scores, np.ndarray) 