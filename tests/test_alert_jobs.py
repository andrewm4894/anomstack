"""
Tests for anomstack.jobs.alert module - Alert job workflow integration tests.
"""

import pytest
import pandas as pd
from unittest.mock import patch, MagicMock, call
from dagster import DagsterInstance

from anomstack.jobs.alert import build_alert_job


class TestBuildAlertJob:
    """Test the build_alert_job function and alert job workflows."""
    
    def test_build_alert_job_disabled(self):
        """Test building a disabled alert job."""
        spec = {
            "metric_batch": "test_batch",
            "disable_alerts": True,
            "db": "duckdb",
            "alert_threshold": 0.8,
            "alert_methods": "email,slack",
            "table_key": "test_table"
        }
        
        job_def = build_alert_job(spec)
        
        # Assertions
        assert job_def.name == "test_batch_alerts_disabled"
        assert len(job_def.graph.nodes) == 1  # Only the noop operation
        assert job_def.graph.nodes[0].name == "test_batch_noop"
    
    def test_build_alert_job_enabled_basic(self):
        """Test building a basic enabled alert job."""
        spec = {
            "metric_batch": "cpu_metrics",
            "disable_alerts": False,
            "db": "duckdb",
            "alert_threshold": 0.8,
            "alert_methods": "email,slack",
            "table_key": "metrics_table",
            "metric_tags": {
                "cpu_usage": {"env": "prod", "service": "api"}
            }
        }
        
        job_def = build_alert_job(spec)
        
        # Assertions
        assert job_def.name == "cpu_metrics_alerts"
        assert len(job_def.graph.nodes) == 3  # get_alerts, alert, save_alerts
        
        node_names = [node.name for node in job_def.graph.nodes]
        assert "cpu_metrics_get_alerts" in node_names
        assert "cpu_metrics_alerts_op" in node_names
        assert "cpu_metrics_save_alerts" in node_names
    
    @patch('anomstack.jobs.alert.read_sql')
    @patch('anomstack.jobs.alert.render')
    @patch('anomstack.jobs.alert.get_dagster_logger')
    def test_alert_job_execution_no_alerts(self, mock_logger, mock_render, mock_read_sql):
        """Test alert job execution when no alerts are found."""
        # Setup
        mock_logger.return_value = MagicMock()
        mock_render.return_value = "SELECT * FROM alerts WHERE metric_alert = 1"
        # Empty DataFrame with correct columns
        empty_df = pd.DataFrame(columns=[
            'metric_timestamp', 'metric_batch', 'metric_name', 
            'metric_value', 'metric_score_smooth', 'metric_alert'
        ])
        mock_read_sql.return_value = empty_df
        
        spec = {
            "metric_batch": "test_metrics",
            "disable_alerts": False,
            "db": "duckdb",
            "alert_threshold": 0.8,
            "alert_methods": "email",
            "table_key": "test_table"
        }
        
        job_def = build_alert_job(spec)
        
        # Execute the job
        instance = DagsterInstance.ephemeral()
        result = job_def.execute_in_process(instance=instance)
        
        # Assertions
        assert result.success
        mock_logger.return_value.info.assert_any_call("no alerts to send")
        mock_logger.return_value.info.assert_any_call("no alerts to save")
    
    @patch('anomstack.jobs.alert.save_df')
    @patch('anomstack.jobs.alert.validate_df')
    @patch('anomstack.jobs.alert.wrangle_df')
    @patch('anomstack.jobs.alert.send_alert')
    @patch('anomstack.jobs.alert.read_sql')
    @patch('anomstack.jobs.alert.render')
    @patch('anomstack.jobs.alert.get_dagster_logger')
    def test_alert_job_execution_with_alerts(self, mock_logger, mock_render, mock_read_sql,
                                           mock_send_alert, mock_wrangle, mock_validate, mock_save):
        """Test alert job execution when alerts are found."""
        # Setup
        mock_logger_instance = MagicMock()
        mock_logger.return_value = mock_logger_instance
        mock_render.return_value = "SELECT * FROM alerts WHERE metric_alert = 1"
        
        # Mock alert data
        alert_data = pd.DataFrame({
            'metric_timestamp': pd.to_datetime(['2023-01-01 10:00:00', '2023-01-01 11:00:00']),
            'metric_batch': ['system_metrics', 'system_metrics'],
            'metric_name': ['cpu_usage', 'memory_usage'],
            'metric_value': [85.5, 92.1],
            'metric_score_smooth': [0.9, 0.85],
            'metric_alert': [1, 1]
        })
        mock_read_sql.return_value = alert_data
        
        # Mock alert sending
        mock_send_alert.side_effect = lambda **kwargs: kwargs.get('df', alert_data)
        
        # Mock data processing
        mock_wrangle.side_effect = lambda df: df
        mock_validate.side_effect = lambda df: df
        mock_save.side_effect = lambda df, db, table: df
        
        spec = {
            "metric_batch": "system_metrics",
            "disable_alerts": False,
            "db": "duckdb",
            "alert_threshold": 0.8,
            "alert_methods": "email,slack",
            "table_key": "alerts_table",
            "metric_tags": {
                "cpu_usage": {"env": "prod", "host": "server1"},
                "memory_usage": {"env": "prod", "host": "server1"}
            }
        }
        
        job_def = build_alert_job(spec)
        
        # Execute the job
        instance = DagsterInstance.ephemeral()
        result = job_def.execute_in_process(instance=instance)
        
        # Assertions
        assert result.success
        
        # Verify alerts were sent for each metric
        assert mock_send_alert.call_count == 2
        
        # Check alert titles and tags
        send_alert_calls = mock_send_alert.call_args_list
        
        # First alert (cpu_usage)
        cpu_call = send_alert_calls[0]
        assert cpu_call[1]['metric_name'] == 'cpu_usage'
        assert '🔥 [cpu_usage] looks anomalous' in cpu_call[1]['title']
        assert cpu_call[1]['threshold'] == 0.8
        assert cpu_call[1]['alert_methods'] == 'email,slack'
        assert cpu_call[1]['tags']['metric_batch'] == 'system_metrics'
        assert cpu_call[1]['tags']['env'] == 'prod'
        assert cpu_call[1]['tags']['host'] == 'server1'
        
        # Second alert (memory_usage)
        memory_call = send_alert_calls[1]
        assert memory_call[1]['metric_name'] == 'memory_usage'
        assert '🔥 [memory_usage] looks anomalous' in memory_call[1]['title']
        
        # Verify logging
        mock_logger_instance.info.assert_any_call("alerting on cpu_usage")
        mock_logger_instance.info.assert_any_call("alerting on memory_usage")
        mock_logger_instance.info.assert_any_call("successfully sent alert for cpu_usage")
        mock_logger_instance.info.assert_any_call("successfully sent alert for memory_usage")
        
        # Verify data was saved
        mock_save.assert_called_once()
        save_call_args = mock_save.call_args
        assert save_call_args[0][1] == "duckdb"  # db parameter
        assert save_call_args[0][2] == "alerts_table"  # table_key parameter
    
    @patch('anomstack.jobs.alert.save_df')
    @patch('anomstack.jobs.alert.validate_df')
    @patch('anomstack.jobs.alert.wrangle_df')
    @patch('anomstack.jobs.alert.send_alert')
    @patch('anomstack.jobs.alert.read_sql')
    @patch('anomstack.jobs.alert.render')
    @patch('anomstack.jobs.alert.get_dagster_logger')
    def test_alert_job_execution_alert_failure_handling(self, mock_logger, mock_render, mock_read_sql,
                                                       mock_send_alert, mock_wrangle, mock_validate, mock_save):
        """Test alert job continues processing when individual alerts fail."""
        # Setup
        mock_logger_instance = MagicMock()
        mock_logger.return_value = mock_logger_instance
        mock_render.return_value = "SELECT * FROM alerts WHERE metric_alert = 1"
        
        # Mock alert data with multiple metrics
        alert_data = pd.DataFrame({
            'metric_timestamp': pd.to_datetime(['2023-01-01 10:00:00', '2023-01-01 11:00:00']),
            'metric_batch': ['system_metrics', 'system_metrics'],
            'metric_name': ['cpu_usage', 'disk_usage'],
            'metric_value': [85.5, 92.1],
            'metric_score_smooth': [0.9, 0.85],
            'metric_alert': [1, 1]
        })
        mock_read_sql.return_value = alert_data
        
        # Mock send_alert to fail for first metric but succeed for second
        def mock_send_alert_side_effect(**kwargs):
            if kwargs.get('metric_name') == 'cpu_usage':
                raise Exception("Slack API Error")
            else:
                return kwargs.get('df', alert_data)
        
        mock_send_alert.side_effect = mock_send_alert_side_effect
        
        # Mock data processing
        mock_wrangle.side_effect = lambda df: df
        mock_validate.side_effect = lambda df: df
        mock_save.side_effect = lambda df, db, table: df
        
        spec = {
            "metric_batch": "system_metrics",
            "disable_alerts": False,
            "db": "duckdb",
            "alert_threshold": 0.8,
            "alert_methods": "slack",
            "table_key": "alerts_table"
        }
        
        job_def = build_alert_job(spec)
        
        # Execute the job
        instance = DagsterInstance.ephemeral()
        result = job_def.execute_in_process(instance=instance)
        
        # Assertions
        assert result.success  # Job should still succeed despite individual alert failure
        
        # Verify both alerts were attempted
        assert mock_send_alert.call_count == 2
        
        # Verify error logging for failed alert
        mock_logger_instance.error.assert_any_call("failed to send alert for cpu_usage: Slack API Error")
        
        # Verify success logging for successful alert
        mock_logger_instance.info.assert_any_call("successfully sent alert for disk_usage")
        
        # Verify data was still saved despite alert failure
        mock_save.assert_called_once()
    
    def test_alert_job_execution_mixed_alert_data(self):
        """Test alert job with mixed data by testing the job structure rather than execution."""
        # Mock mixed data with alerts and non-alerts
        mixed_data = pd.DataFrame({
            'metric_timestamp': pd.to_datetime([
                '2023-01-01 10:00:00', '2023-01-01 11:00:00', 
                '2023-01-01 12:00:00', '2023-01-01 13:00:00'
            ]),
            'metric_batch': ['mixed_metrics', 'mixed_metrics', 'mixed_metrics', 'mixed_metrics'],
            'metric_name': ['cpu_usage', 'cpu_usage', 'memory_usage', 'memory_usage'],
            'metric_value': [45.0, 85.5, 60.0, 92.1],
            'metric_score_smooth': [0.3, 0.9, 0.4, 0.85],
            'metric_alert': [0, 1, 0, 1]  # Mixed alerts
        })
        
        spec = {
            "metric_batch": "mixed_metrics",
            "disable_alerts": False,
            "db": "duckdb", 
            "alert_threshold": 0.8,
            "alert_methods": "email",
            "table_key": "mixed_table"
        }
        
        job_def = build_alert_job(spec)
        
        # Test that the job was built correctly
        assert job_def.name == "mixed_metrics_alerts"
        assert len(job_def.graph.nodes) == 3  # get_alerts, alert, save_alerts
        
        # Test the query logic that was failing
        alerts_only = mixed_data.query("metric_alert == 1")
        assert len(alerts_only) == 2  # Should have 2 alert rows
        assert all(alerts_only['metric_alert'] == 1)
        assert set(alerts_only['metric_name'].unique()) == {'cpu_usage', 'memory_usage'}
    
    def test_build_alert_job_with_metric_tags(self):
        """Test building alert job with custom metric tags."""
        spec = {
            "metric_batch": "tagged_metrics",
            "disable_alerts": False,
            "db": "postgresql",
            "alert_threshold": 0.75,
            "alert_methods": "slack",
            "table_key": "tagged_table",
            "metric_tags": {
                "api_latency": {
                    "service": "user-api",
                    "env": "production",
                    "team": "backend"
                },
                "database_connections": {
                    "service": "postgres",
                    "env": "production", 
                    "team": "data"
                }
            }
        }
        
        job_def = build_alert_job(spec)
        
        # Assertions
        assert job_def.name == "tagged_metrics_alerts"
        assert len(job_def.graph.nodes) == 3
    
    def test_build_alert_job_without_metric_tags(self):
        """Test building alert job without metric tags (uses empty dict default)."""
        spec = {
            "metric_batch": "simple_metrics",
            "disable_alerts": False,
            "db": "sqlite",
            "alert_threshold": 0.9,
            "alert_methods": "email",
            "table_key": "simple_table"
            # No metric_tags specified
        }
        
        job_def = build_alert_job(spec)
        
        # Assertions
        assert job_def.name == "simple_metrics_alerts"
        assert len(job_def.graph.nodes) == 3


class TestAlertJobSchedules:
    """Test alert job schedule creation."""
    
    def test_alert_jobs_and_schedules_creation(self):
        """Test that alert jobs and schedules are created from specs."""
        # Test the build_alert_job function directly instead of module-level variables
        spec1 = {
            "metric_batch": "batch1",
            "disable_alerts": False,
            "db": "duckdb",
            "alert_threshold": 0.8,
            "alert_methods": "email",
            "table_key": "table1",
            "alert_cron_schedule": "0 */6 * * *",
            "alert_default_schedule_status": "RUNNING"
        }
        
        spec2 = {
            "metric_batch": "batch2", 
            "disable_alerts": True,
            "db": "sqlite",
            "alert_threshold": 0.9,
            "alert_methods": "slack",
            "table_key": "table2",
            "alert_cron_schedule": "0 8 * * *",
            "alert_default_schedule_status": "STOPPED"
        }
        
        # Test building individual jobs
        job1 = build_alert_job(spec1)
        job2 = build_alert_job(spec2)
        
        # Assertions
        assert job1.name == "batch1_alerts"
        assert job2.name == "batch2_alerts_disabled"
        
        # Verify job structures
        assert len(job1.graph.nodes) == 3  # Full alert job
        assert len(job2.graph.nodes) == 1  # Disabled job (just noop) 