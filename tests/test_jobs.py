"""
Integration tests for core Dagster jobs in anomstack.
"""

import numpy as np
import pandas as pd
import pytest
from unittest.mock import Mock, patch, MagicMock
from dagster import DagsterInstance
from dagster.core.test_utils import instance_for_test

from anomstack.jobs.ingest import build_ingest_job
from anomstack.jobs.train import build_train_job
from anomstack.jobs.score import build_score_job
from anomstack.jobs.alert import build_alert_job


class TestIngestJob:
    """Test cases for the ingest job functionality."""
    
    def test_build_ingest_job_sql_based(self):
        """Test building ingest job with SQL configuration."""
        spec = {
            "metric_batch": "test_batch",
            "table_key": "test_table",
            "db": "duckdb",
            "ingest_sql": "SELECT NOW() as metric_timestamp, 'test_metric' as metric_name, 42.0 as metric_value",
            "ingest_metric_rounding": 4
        }
        
        job = build_ingest_job(spec)
        
        assert job.name == "test_batch_ingest"
        # Verify the job was created successfully
        assert job is not None
        assert hasattr(job, 'execute_in_process')
        
    def test_build_ingest_job_python_based(self):
        """Test building ingest job with Python function configuration."""
        spec = {
            "metric_batch": "test_batch",
            "table_key": "test_table", 
            "db": "duckdb",
            "ingest_fn": "def ingest_fn(): return pd.DataFrame({'metric_timestamp': [pd.Timestamp.now()], 'metric_name': ['test'], 'metric_value': [1.0]})",
            "ingest_metric_rounding": 4
        }
        
        job = build_ingest_job(spec)
        
        assert job.name == "test_batch_ingest"
        assert job is not None
        
    def test_build_ingest_job_disabled(self):
        """Test building disabled ingest job."""
        spec = {
            "metric_batch": "test_batch",
            "disable_ingest": True
        }
        
        job = build_ingest_job(spec)
        
        assert job.name == "test_batch_ingest_disabled"
    
    def test_build_ingest_job_missing_config(self):
        """Test building ingest job with missing configuration."""
        spec = {
            "metric_batch": "test_batch"
            # Missing required fields
        }
        
        # Should handle gracefully or raise appropriate error
        try:
            job = build_ingest_job(spec)
            # If no error, should create a disabled job
            assert "disabled" in job.name or job.name == "test_batch_ingest"
        except (KeyError, ValueError):
            # Acceptable to raise errors with incomplete configuration
            pass
    
    def test_build_ingest_job_with_threshold_metadata(self):
        """Test that ingest job properly adds threshold metadata when thresholds are configured."""
        spec = {
            "metric_batch": "threshold_test",
            "table_key": "test_table",
            "db": "duckdb",
            "ingest_sql": "SELECT NOW() as metric_timestamp, 'cpu_usage' as metric_name, 85.0 as metric_value",
            "disable_tholdalert": False,
            "tholdalert_thresholds": {
                "cpu_usage": {"upper": 90, "lower": 10},
                "memory_usage": {"upper": 80, "lower": 5}
            }
        }
        
        job = build_ingest_job(spec)
        
        # Verify the job was created with threshold configuration
        assert job.name == "threshold_test_ingest"
        assert job is not None
        
        # Job should be created successfully with threshold metadata functionality
        # The actual metadata addition is tested in test_df.py::TestAddThresholdMetadata
        assert hasattr(job, 'execute_in_process')


class TestTrainJob:
    """Test cases for the train job functionality."""
    
    def test_build_train_job_basic(self):
        """Test building basic train job."""
        spec = {
            "metric_batch": "test_batch",
            "table_key": "test_table",
            "db": "duckdb",
            "model_path": "local://./models",
            "model_configs": [
                {"model_name": "IForest", "model_tag": "iforest_test", "model_params": {"n_estimators": 50}},
                {"model_name": "KNN", "model_tag": "knn_test", "model_params": {"n_neighbors": 5}}
            ],
            "train_sql": "SELECT * FROM test_table",
            "preprocess_fn": "def preprocess_fn(df): return df",
            "preprocess_params": {
                "diff_n": 1,
                "smooth_n": 3,
                "lags_n": 5
            }
        }
        
        job = build_train_job(spec)
        
        assert job.name == "test_batch_train"
        
    def test_build_train_job_disabled(self):
        """Test building disabled train job."""
        spec = {
            "metric_batch": "test_batch",
            "disable_train": True
        }
        
        job = build_train_job(spec)
        
        assert job.name == "test_batch_train_disabled"
        
    def test_train_job_with_multiple_models(self):
        """Test building train job with multiple model configurations."""
        spec = {
            "metric_batch": "multi_model_test",
            "table_key": "test_table",
            "db": "duckdb",
            "model_path": "local://./models",
            "model_configs": [
                {"model_name": "IForest", "model_tag": "iforest_test", "model_params": {"n_estimators": 50}},
                {"model_name": "KNN", "model_tag": "knn_test", "model_params": {"n_neighbors": 5}},
                {"model_name": "PCA", "model_tag": "pca_test", "model_params": {"contamination": 0.01}}
            ],
            "train_sql": "SELECT * FROM test_table",
            "preprocess_fn": "def preprocess_fn(df): return df",
            "preprocess_params": {
                "diff_n": 1,
                "smooth_n": 3,
                "lags_n": 5
            }
        }
        
        job = build_train_job(spec)
        
        assert job.name == "multi_model_test_train"
        # Verify job was created successfully
        assert callable(job)


class TestScoreJob:
    """Test cases for the score job functionality."""
    
    def test_build_score_job_basic(self):
        """Test building basic score job."""
        spec = {
            "metric_batch": "test_batch",
            "table_key": "test_table",
            "db": "duckdb",
            "model_path": "local://./models",
            "model_configs": [
                {"model_name": "IForest", "model_tag": "iforest_test", "model_params": {}}
            ],
            "score_sql": "SELECT * FROM test_table",
            "preprocess_fn": "def preprocess_fn(df): return df",
            "preprocess_params": {
                "diff_n": 1,
                "smooth_n": 3,
                "lags_n": 5
            }
        }
        
        job = build_score_job(spec)
        
        assert job.name == "test_batch_score"
        
    def test_build_score_job_disabled(self):
        """Test building disabled score job."""
        spec = {
            "metric_batch": "test_batch",
            "disable_score": True
        }
        
        job = build_score_job(spec)
        
        assert job.name == "test_batch_score_disabled"
        
    def test_score_job_with_model_combination_methods(self):
        """Test building score job with different model combination methods."""
        for method in ["mean", "max", "min"]:
            spec = {
                "metric_batch": f"combo_{method}_test",
                "table_key": "test_table",
                "db": "duckdb",
                "model_path": "local://./models",
                "model_configs": [
                    {"model_name": "IForest", "model_tag": "iforest_test", "model_params": {}},
                    {"model_name": "KNN", "model_tag": "knn_test", "model_params": {}}
                ],
                "score_sql": "SELECT * FROM test_table",
                "preprocess_fn": "def preprocess_fn(df): return df",
                "model_combination_method": method,
                "preprocess_params": {
                    "diff_n": 1,
                    "smooth_n": 3,
                    "lags_n": 5
                }
            }
            
            job = build_score_job(spec)
            
            assert job.name == f"combo_{method}_test_score"
            # Verify job was created successfully
            assert callable(job)


class TestAlertJob:
    """Test cases for the alert job functionality."""
    
    def test_build_alert_job_basic(self):
        """Test building basic alert job."""
        spec = {
            "metric_batch": "test_batch",
            "table_key": "test_table",
            "db": "duckdb",
            "alert_methods": "email,slack",
            "alert_sql": "SELECT * FROM test_table",
            "alert_threshold": 0.8
        }
        
        job = build_alert_job(spec)
        
        assert job.name == "test_batch_alerts"
        
    def test_build_alert_job_disabled(self):
        """Test building disabled alert job."""
        spec = {
            "metric_batch": "test_batch",
            "disable_alerts": True
        }
        
        job = build_alert_job(spec)
        
        assert job.name == "test_batch_alerts_disabled"
        
    def test_alert_job_with_different_methods(self):
        """Test building alert job with different alert methods."""
        methods = ["email", "slack", "email,slack"]
        
        for method in methods:
            spec = {
                "metric_batch": f"alert_{method.replace(',', '_')}_test",
                "table_key": "test_table",
                "db": "duckdb",
                "alert_methods": method,
                "alert_sql": "SELECT * FROM test_table",
                "alert_threshold": 0.8
            }
            
            job = build_alert_job(spec)
            
            assert job.name == f"alert_{method.replace(',', '_')}_test_alerts"
            # Verify job was created successfully
            assert callable(job)
            
    def test_alert_job_with_different_thresholds(self):
        """Test building alert job with different alert thresholds."""
        thresholds = [0.5, 0.8, 0.9, 0.95]
        
        for threshold in thresholds:
            spec = {
                "metric_batch": f"threshold_{str(threshold).replace('.', '_')}_test",
                "table_key": "test_table",
                "db": "duckdb",
                "alert_methods": "email",
                "alert_sql": "SELECT * FROM test_table",
                "alert_threshold": threshold
            }
            
            job = build_alert_job(spec)
            
            assert job.name == f"threshold_{str(threshold).replace('.', '_')}_test_alerts"
            # Verify job was created successfully
            assert callable(job)


class TestJobIntegration:
    """Integration tests for job workflow."""
    
    def test_job_workflow_integration(self):
        """Test that jobs can be created with realistic configurations."""
        spec = {
            "metric_batch": "integration_test",
            "table_key": "metrics",
            "db": "duckdb",
            "model_path": "local://./models",
            "model_configs": [
                {"model_name": "PCA", "model_tag": "pca_default", "model_params": {"contamination": 0.01}},
                {"model_name": "KNN", "model_tag": "knn_default", "model_params": {"contamination": 0.01}}
            ],
            "model_combination_method": "mean",
            "alert_methods": "email,slack",
            "alert_threshold": 0.8,
            "ingest_sql": "SELECT NOW() as metric_timestamp, 'test' as metric_name, 1.0 as metric_value",
            "train_sql": "SELECT * FROM metrics WHERE metric_batch = 'integration_test'",
            "score_sql": "SELECT * FROM metrics WHERE metric_batch = 'integration_test'",
            "alert_sql": "SELECT * FROM metrics WHERE metric_batch = 'integration_test'",
            "preprocess_fn": "def preprocess_fn(df): return df",
            "preprocess_params": {
                "diff_n": 1,
                "smooth_n": 3,
                "lags_n": 5
            }
        }
        
        # Test that all core jobs can be built successfully
        ingest_job = build_ingest_job(spec)
        train_job = build_train_job(spec)
        score_job = build_score_job(spec)
        alert_job = build_alert_job(spec)
        
        assert ingest_job.name == "integration_test_ingest"
        assert train_job.name == "integration_test_train"
        assert score_job.name == "integration_test_score"
        assert alert_job.name == "integration_test_alerts"
        
        # Verify jobs are created successfully (they have names and are callable)
        assert callable(ingest_job)
        assert callable(train_job)
        assert callable(score_job)
        assert callable(alert_job)
        
    def test_disabled_jobs_workflow(self):
        """Test that disabled jobs are handled properly."""
        spec = {
            "metric_batch": "disabled_test",
            "disable_ingest": True,
            "disable_train": True,
            "disable_score": True,
            "disable_alerts": True
        }
        
        # Test that disabled jobs are created with appropriate names
        ingest_job = build_ingest_job(spec)
        train_job = build_train_job(spec)
        score_job = build_score_job(spec)
        alert_job = build_alert_job(spec)
        
        assert ingest_job.name == "disabled_test_ingest_disabled"
        assert train_job.name == "disabled_test_train_disabled"
        assert score_job.name == "disabled_test_score_disabled"
        assert alert_job.name == "disabled_test_alerts_disabled"
        
    def test_job_error_handling(self):
        """Test error handling in job creation."""
        # Test with missing required fields
        incomplete_spec = {
            "metric_batch": "error_test"
            # Missing required fields like table_key, db, etc.
        }
        
        # Jobs should handle missing fields gracefully or raise appropriate errors
        try:
            ingest_job = build_ingest_job(incomplete_spec)
            # If no error, the job should still be created (possibly disabled)
            assert ingest_job.name == "error_test_ingest_disabled"
        except (KeyError, ValueError):
            # Acceptable to raise errors with incomplete configuration
            pass 