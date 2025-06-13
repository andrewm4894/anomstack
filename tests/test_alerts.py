"""
Tests for anomstack.alerts module - alert sending functionality.
"""

import pytest
import pandas as pd
from unittest.mock import patch, MagicMock

from anomstack.alerts.send import send_alert, send_df


class TestSendAlert:
    """Test the send_alert function."""
    
    @patch('anomstack.alerts.send.get_dagster_logger')
    @patch('anomstack.alerts.send.make_alert_message')
    @patch('anomstack.alerts.send.send_alert_slack_with_plot')
    @patch('anomstack.alerts.send.send_email_with_plot')
    def test_send_alert_both_methods(self, mock_email, mock_slack, mock_message, mock_logger):
        """Test send_alert with both email and slack methods."""
        # Setup
        mock_logger.return_value = MagicMock()
        mock_message.return_value = "Test alert message"
        
        df = pd.DataFrame({
            'metric_timestamp': pd.to_datetime(['2023-01-01 10:00:00']),
            'metric_value': [85.5],
            'metric_score_smooth': [0.9],
            'metric_alert': [1]
        })
        
        # Call function
        result = send_alert(
            metric_name='cpu_usage',
            title='CPU Alert',
            df=df,
            alert_methods='email,slack',
            threshold=0.8,
            description='High CPU usage detected'
        )
        
        # Assertions
        mock_message.assert_called_once()
        mock_slack.assert_called_once()
        mock_email.assert_called_once()
        pd.testing.assert_frame_equal(result, df)
    
    @patch('anomstack.alerts.send.get_dagster_logger')
    @patch('anomstack.alerts.send.make_alert_message')
    @patch('anomstack.alerts.send.send_alert_slack_with_plot')
    @patch('anomstack.alerts.send.send_email_with_plot')
    def test_send_alert_slack_only(self, mock_email, mock_slack, mock_message, mock_logger):
        """Test send_alert with slack method only."""
        # Setup
        mock_logger.return_value = MagicMock()
        mock_message.return_value = "Test alert message"
        
        df = pd.DataFrame({
            'metric_timestamp': pd.to_datetime(['2023-01-01 10:00:00']),
            'metric_value': [85.5],
            'metric_score_smooth': [0.9]
        })
        
        # Call function
        result = send_alert(
            metric_name='cpu_usage',
            title='CPU Alert',
            df=df,
            alert_methods='slack',
            threshold=0.8
        )
        
        # Assertions
        mock_slack.assert_called_once()
        mock_email.assert_not_called()
        pd.testing.assert_frame_equal(result, df)
    
    @patch('anomstack.alerts.send.get_dagster_logger')
    @patch('anomstack.alerts.send.make_alert_message')
    @patch('anomstack.alerts.send.send_alert_slack_with_plot')
    @patch('anomstack.alerts.send.send_email_with_plot')
    def test_send_alert_email_only(self, mock_email, mock_slack, mock_message, mock_logger):
        """Test send_alert with email method only."""
        # Setup
        mock_logger.return_value = MagicMock()
        mock_message.return_value = "Test alert message"
        
        df = pd.DataFrame({
            'metric_timestamp': pd.to_datetime(['2023-01-01 10:00:00']),
            'metric_value': [85.5],
            'metric_score_smooth': [0.9]
        })
        
        # Call function
        result = send_alert(
            metric_name='cpu_usage',
            title='CPU Alert',
            df=df,
            alert_methods='email',
            threshold=0.8
        )
        
        # Assertions
        mock_email.assert_called_once()
        mock_slack.assert_not_called()
        pd.testing.assert_frame_equal(result, df)
    
    @patch('anomstack.alerts.send.get_dagster_logger')
    @patch('anomstack.alerts.send.make_alert_message')
    @patch('anomstack.alerts.send.send_alert_slack_with_plot')
    @patch('anomstack.alerts.send.send_email_with_plot')
    def test_send_alert_with_tags(self, mock_email, mock_slack, mock_message, mock_logger):
        """Test send_alert with tags parameter."""
        # Setup
        mock_logger.return_value = MagicMock()
        mock_message.return_value = "Test alert message"
        
        df = pd.DataFrame({
            'metric_timestamp': pd.to_datetime(['2023-01-01 10:00:00']),
            'metric_value': [85.5],
            'metric_score_smooth': [0.9]
        })
        
        tags = {'environment': 'prod', 'service': 'api'}
        
        # Call function
        result = send_alert(
            metric_name='cpu_usage',
            title='CPU Alert',
            df=df,
            alert_methods='email,slack',
            tags=tags
        )
        
        # Check that tags were passed to the alert functions
        mock_slack.assert_called_once()
        slack_call_args = mock_slack.call_args[1]
        assert slack_call_args['tags'] == tags
        
        mock_email.assert_called_once()
        email_call_args = mock_email.call_args[1]
        assert email_call_args['tags'] == tags
    
    @patch('anomstack.alerts.send.get_dagster_logger')
    @patch('anomstack.alerts.send.make_alert_message')
    @patch('anomstack.alerts.send.send_alert_slack_with_plot')
    @patch('anomstack.alerts.send.send_email_with_plot')
    def test_send_alert_custom_score_column(self, mock_email, mock_slack, mock_message, mock_logger):
        """Test send_alert with custom score column."""
        # Setup
        mock_logger.return_value = MagicMock()
        mock_message.return_value = "Test alert message"
        
        df = pd.DataFrame({
            'metric_timestamp': pd.to_datetime(['2023-01-01 10:00:00']),
            'metric_value': [85.5],
            'custom_score': [0.95]
        })
        
        # Call function
        result = send_alert(
            metric_name='cpu_usage',
            title='CPU Alert',
            df=df,
            alert_methods='slack',
            score_col='custom_score',
            score_title='Custom Score'
        )
        
        # Check that custom score column was used
        mock_slack.assert_called_once()
        slack_call_args = mock_slack.call_args[1]
        assert slack_call_args['score_col'] == 'custom_score'
        assert slack_call_args['score_title'] == 'Custom Score'


class TestSendDF:
    """Test the send_df function."""
    
    @patch('anomstack.alerts.send.get_dagster_logger')
    @patch('anomstack.alerts.send.send_alert_slack')
    @patch('anomstack.alerts.send.send_email')
    def test_send_df_both_methods(self, mock_email, mock_slack, mock_logger):
        """Test send_df with both email and slack methods."""
        # Setup
        mock_logger.return_value = MagicMock()
        
        df = pd.DataFrame({
            'metric_name': ['cpu_usage', 'memory_usage'],
            'metric_value': [85.5, 67.2],
            'status': ['alert', 'normal']
        })
        
        # Call function
        result = send_df(
            title='System Status Report',
            df=df,
            alert_methods='email,slack',
            description='Daily system metrics report'
        )
        
        # Assertions
        mock_slack.assert_called_once()
        mock_email.assert_called_once()
        
        # Check that HTML table was generated and passed
        slack_call_args = mock_slack.call_args[1]
        email_call_args = mock_email.call_args[1]
        
        # Both should receive HTML representation of the dataframe
        assert '<table' in slack_call_args['message']
        assert '<table' in email_call_args['body']
        
        pd.testing.assert_frame_equal(result, df)
    
    @patch('anomstack.alerts.send.get_dagster_logger')
    @patch('anomstack.alerts.send.send_alert_slack')
    @patch('anomstack.alerts.send.send_email')
    def test_send_df_slack_only(self, mock_email, mock_slack, mock_logger):
        """Test send_df with slack method only."""
        # Setup
        mock_logger.return_value = MagicMock()
        
        df = pd.DataFrame({
            'metric_name': ['cpu_usage'],
            'metric_value': [85.5]
        })
        
        # Call function
        result = send_df(
            title='CPU Report',
            df=df,
            alert_methods='slack'
        )
        
        # Assertions
        mock_slack.assert_called_once()
        mock_email.assert_not_called()
        pd.testing.assert_frame_equal(result, df)
    
    @patch('anomstack.alerts.send.get_dagster_logger')
    @patch('anomstack.alerts.send.send_alert_slack')
    @patch('anomstack.alerts.send.send_email')
    def test_send_df_email_only(self, mock_email, mock_slack, mock_logger):
        """Test send_df with email method only."""
        # Setup
        mock_logger.return_value = MagicMock()
        
        df = pd.DataFrame({
            'metric_name': ['memory_usage'],
            'metric_value': [67.2]
        })
        
        # Call function
        result = send_df(
            title='Memory Report',
            df=df,
            alert_methods='email'
        )
        
        # Assertions
        mock_email.assert_called_once()
        mock_slack.assert_not_called()
        pd.testing.assert_frame_equal(result, df)
    
    @patch('anomstack.alerts.send.get_dagster_logger')
    @patch('anomstack.alerts.send.send_alert_slack')
    @patch('anomstack.alerts.send.send_email')
    def test_send_df_logging(self, mock_email, mock_slack, mock_logger):
        """Test that send_df logs debug information."""
        # Setup
        logger_mock = MagicMock()
        mock_logger.return_value = logger_mock
        
        df = pd.DataFrame({
            'metric_name': ['cpu_usage'],
            'metric_value': [85.5]
        })
        
        # Call function
        send_df(
            title='Test Report',
            df=df,
            alert_methods='slack'
        )
        
        # Check that debug logging occurred
        logger_mock.debug.assert_called_once()
        debug_call = logger_mock.debug.call_args[0][0]
        assert "alerts to send:" in debug_call
    
    @patch('anomstack.alerts.send.get_dagster_logger')
    @patch('anomstack.alerts.send.send_alert_slack')
    @patch('anomstack.alerts.send.send_email')
    def test_send_df_default_parameters(self, mock_email, mock_slack, mock_logger):
        """Test send_df with default parameters."""
        # Setup
        mock_logger.return_value = MagicMock()
        
        df = pd.DataFrame({
            'metric_name': ['cpu_usage'],
            'metric_value': [85.5]
        })
        
        # Call function with minimal parameters
        result = send_df('Test Report', df)
        
        # Should use default alert_methods='email,slack'
        mock_slack.assert_called_once()
        mock_email.assert_called_once()
        
        # Should use empty description by default
        slack_call_args = mock_slack.call_args[1]
        email_call_args = mock_email.call_args[1]
        
        assert slack_call_args['title'] == 'Test Report'
        assert email_call_args['subject'] == 'Test Report'
        
        pd.testing.assert_frame_equal(result, df) 