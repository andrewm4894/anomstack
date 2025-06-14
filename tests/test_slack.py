"""
Tests for anomstack.alerts.slack module - Slack integration functionality.
"""

import os
import tempfile
import pytest
import pandas as pd
from unittest.mock import patch, MagicMock, mock_open, call
from slack_sdk.errors import SlackApiError

from anomstack.alerts.slack import send_alert_slack, send_alert_slack_with_plot


class TestSendAlertSlack:
    """Test the send_alert_slack function."""
    
    @patch.dict(os.environ, {
        'ANOMSTACK_SLACK_BOT_TOKEN': 'xoxb-test-token',
        'ANOMSTACK_SLACK_CHANNEL': 'test-channel'
    })
    @patch('anomstack.alerts.slack.get_dagster_logger')
    @patch('anomstack.alerts.slack.WebClient')
    def test_send_alert_slack_text_only_success(self, mock_webclient, mock_logger):
        """Test successful text-only Slack alert with environment variables."""
        # Setup
        mock_logger.return_value = MagicMock()
        mock_client = MagicMock()
        mock_webclient.return_value = mock_client
        
        # Mock channel lookup response
        mock_client.conversations_list.return_value = {
            'channels': [
                {'name': 'test-channel', 'id': 'C1234567890'},
                {'name': 'other-channel', 'id': 'C0987654321'}
            ]
        }
        
        # Mock successful message post
        mock_client.chat_postMessage.return_value = {'ok': True}
        
        # Call function
        send_alert_slack(
            title="Test Alert",
            message="This is a test alert message"
        )
        
        # Assertions
        mock_webclient.assert_called_once_with(token='xoxb-test-token')
        mock_client.conversations_list.assert_called_once_with(types="public_channel,private_channel")
        mock_client.chat_postMessage.assert_called_once_with(
            channel='C1234567890',
            text='*Test Alert*\nThis is a test alert message'
        )
    
    @patch.dict(os.environ, {
        'ANOMSTACK_SLACK_BOT_TOKEN': 'xoxb-test-token'
    })
    @patch('anomstack.alerts.slack.get_dagster_logger')
    @patch('anomstack.alerts.slack.WebClient')
    def test_send_alert_slack_with_explicit_channel(self, mock_webclient, mock_logger):
        """Test Slack alert with explicitly provided channel name."""
        # Setup
        mock_logger.return_value = MagicMock()
        mock_client = MagicMock()
        mock_webclient.return_value = mock_client
        
        # Mock channel lookup response
        mock_client.conversations_list.return_value = {
            'channels': [
                {'name': 'alerts', 'id': 'C1111111111'},
                {'name': 'general', 'id': 'C2222222222'}
            ]
        }
        
        # Call function with explicit channel
        send_alert_slack(
            title="Explicit Channel Test",
            message="Testing explicit channel",
            channel_name="alerts"
        )
        
        # Assertions
        mock_client.chat_postMessage.assert_called_once_with(
            channel='C1111111111',
            text='*Explicit Channel Test*\nTesting explicit channel'
        )
    
    @patch.dict(os.environ, {
        'ANOMSTACK_SLACK_BOT_TOKEN': 'xoxb-test-token'
    })
    @patch('anomstack.alerts.slack.get_dagster_logger')
    @patch('anomstack.alerts.slack.WebClient')
    def test_send_alert_slack_with_hash_prefix(self, mock_webclient, mock_logger):
        """Test Slack alert with channel name that has # prefix."""
        # Setup
        mock_logger.return_value = MagicMock()
        mock_client = MagicMock()
        mock_webclient.return_value = mock_client
        
        # Mock channel lookup response
        mock_client.conversations_list.return_value = {
            'channels': [
                {'name': 'alerts', 'id': 'C1111111111'}
            ]
        }
        
        # Call function with # prefixed channel
        send_alert_slack(
            title="Hash Prefix Test",
            message="Testing hash prefix removal",
            channel_name="#alerts"
        )
        
        # Assertions - should look for 'alerts' not '#alerts'
        mock_client.chat_postMessage.assert_called_once_with(
            channel='C1111111111',
            text='*Hash Prefix Test*\nTesting hash prefix removal'
        )
    
    @patch.dict(os.environ, {
        'ANOMSTACK_SLACK_BOT_TOKEN': 'xoxb-test-token'
    })
    @patch('anomstack.alerts.slack.get_dagster_logger')
    @patch('anomstack.alerts.slack.WebClient')
    @patch('builtins.open', new_callable=mock_open, read_data=b'fake_image_data')
    def test_send_alert_slack_with_image(self, mock_file, mock_webclient, mock_logger):
        """Test Slack alert with image attachment."""
        # Setup
        mock_logger.return_value = MagicMock()
        mock_client = MagicMock()
        mock_webclient.return_value = mock_client
        
        # Mock channel lookup response
        mock_client.conversations_list.return_value = {
            'channels': [
                {'name': 'alerts', 'id': 'C1111111111'}
            ]
        }
        
        # Mock successful file upload
        mock_client.files_upload_v2.return_value = {'ok': True}
        
        # Call function with image
        send_alert_slack(
            title="Image Alert",
            message="Alert with image",
            image_file_path="/tmp/test_image.png",
            channel_name="alerts"
        )
        
        # Assertions
        mock_client.files_upload_v2.assert_called_once()
        upload_call = mock_client.files_upload_v2.call_args
        
        assert upload_call[1]['channels'] == ['C1111111111']
        assert upload_call[1]['initial_comment'] == '*Image Alert*\nAlert with image'
        assert upload_call[1]['filename'] == 'test_image.png'
        
        # Should not call chat_postMessage when uploading file
        mock_client.chat_postMessage.assert_not_called()
    
    def test_send_alert_slack_missing_token(self):
        """Test Slack alert fails when bot token is missing."""
        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(ValueError, match="Slack bot token not found"):
                send_alert_slack(title="Test", message="Test")
    
    @patch.dict(os.environ, {
        'ANOMSTACK_SLACK_BOT_TOKEN': 'xoxb-test-token'
    })
    def test_send_alert_slack_missing_channel(self):
        """Test Slack alert fails when channel is not specified."""
        with pytest.raises(ValueError, match="Slack channel not specified"):
            send_alert_slack(title="Test", message="Test")
    
    @patch.dict(os.environ, {
        'ANOMSTACK_SLACK_BOT_TOKEN': 'xoxb-test-token',
        'ANOMSTACK_SLACK_CHANNEL': 'test-channel'
    })
    @patch('anomstack.alerts.slack.get_dagster_logger')
    @patch('anomstack.alerts.slack.WebClient')
    def test_send_alert_slack_channel_not_found(self, mock_webclient, mock_logger):
        """Test Slack alert when channel is not found."""
        # Setup
        mock_logger_instance = MagicMock()
        mock_logger.return_value = mock_logger_instance
        mock_client = MagicMock()
        mock_webclient.return_value = mock_client
        
        # Mock channel lookup response without target channel
        mock_client.conversations_list.return_value = {
            'channels': [
                {'name': 'other-channel', 'id': 'C0987654321'}
            ]
        }
        
        # Call function
        send_alert_slack(title="Test", message="Test")
        
        # Assertions
        mock_logger_instance.error.assert_called_with("Channel test-channel not found.")
        mock_client.chat_postMessage.assert_not_called()
        mock_client.files_upload_v2.assert_not_called()
    
    @patch.dict(os.environ, {
        'ANOMSTACK_SLACK_BOT_TOKEN': 'xoxb-test-token',
        'ANOMSTACK_SLACK_CHANNEL': 'test-channel'
    })
    @patch('anomstack.alerts.slack.get_dagster_logger')
    @patch('anomstack.alerts.slack.WebClient')
    def test_send_alert_slack_api_error_channel_lookup(self, mock_webclient, mock_logger):
        """Test Slack alert when API error occurs during channel lookup."""
        # Setup
        mock_logger_instance = MagicMock()
        mock_logger.return_value = mock_logger_instance
        mock_client = MagicMock()
        mock_webclient.return_value = mock_client
        
        # Mock API error during channel lookup
        mock_client.conversations_list.side_effect = SlackApiError(
            message="API Error", response={'error': 'invalid_auth'}
        )
        
        # Call function
        send_alert_slack(title="Test", message="Test")
        
        # Assertions
        mock_logger_instance.error.assert_called()
        error_call = mock_logger_instance.error.call_args[0][0]
        assert "Error fetching channel ID" in error_call
        mock_client.chat_postMessage.assert_not_called()
    
    @patch.dict(os.environ, {
        'ANOMSTACK_SLACK_BOT_TOKEN': 'xoxb-test-token',
        'ANOMSTACK_SLACK_CHANNEL': 'test-channel'
    })
    @patch('anomstack.alerts.slack.get_dagster_logger')
    @patch('anomstack.alerts.slack.WebClient')
    def test_send_alert_slack_api_error_sending_message(self, mock_webclient, mock_logger):
        """Test Slack alert when API error occurs during message sending."""
        # Setup
        mock_logger_instance = MagicMock()
        mock_logger.return_value = mock_logger_instance
        mock_client = MagicMock()
        mock_webclient.return_value = mock_client
        
        # Mock successful channel lookup
        mock_client.conversations_list.return_value = {
            'channels': [
                {'name': 'test-channel', 'id': 'C1234567890'}
            ]
        }
        
        # Mock API error during message sending
        mock_client.chat_postMessage.side_effect = SlackApiError(
            message="API Error", response={'error': 'channel_not_found'}
        )
        
        # Call function
        send_alert_slack(title="Test", message="Test")
        
        # Assertions
        mock_logger_instance.error.assert_called()
        error_call = mock_logger_instance.error.call_args[0][0]
        assert "Error sending message to Slack channel" in error_call
    
    @patch.dict(os.environ, {
        'ANOMSTACK_SLACK_BOT_TOKEN': 'xoxb-test-token',
        'ANOMSTACK_SLACK_CHANNEL': 'test-channel'
    })
    @patch('anomstack.alerts.slack.get_dagster_logger')
    @patch('anomstack.alerts.slack.WebClient')
    @patch('builtins.open', new_callable=mock_open, read_data=b'fake_image_data')
    def test_send_alert_slack_api_error_file_upload(self, mock_file, mock_webclient, mock_logger):
        """Test Slack alert when API error occurs during file upload."""
        # Setup
        mock_logger_instance = MagicMock()
        mock_logger.return_value = mock_logger_instance
        mock_client = MagicMock()
        mock_webclient.return_value = mock_client
        
        # Mock successful channel lookup
        mock_client.conversations_list.return_value = {
            'channels': [
                {'name': 'test-channel', 'id': 'C1234567890'}
            ]
        }
        
        # Mock API error during file upload
        mock_client.files_upload_v2.side_effect = SlackApiError(
            message="API Error", response={'error': 'file_uploads_disabled'}
        )
        
        # Call function with image
        send_alert_slack(
            title="Test",
            message="Test",
            image_file_path="/tmp/test.png"
        )
        
        # Assertions
        mock_logger_instance.error.assert_called()
        error_call = mock_logger_instance.error.call_args[0][0]
        assert "Error sending message to Slack channel" in error_call


class TestSendAlertSlackWithPlot:
    """Test the send_alert_slack_with_plot function."""
    
    @patch.dict(os.environ, {
        'ANOMSTACK_SLACK_BOT_TOKEN': 'xoxb-test-token',
        'ANOMSTACK_SLACK_CHANNEL': 'alerts'
    })
    @patch('anomstack.alerts.slack.send_alert_slack')
    @patch('anomstack.alerts.slack.make_alert_plot')
    @patch('anomstack.alerts.slack.plt')
    @patch('anomstack.alerts.slack.tempfile.NamedTemporaryFile')
    @patch('anomstack.alerts.slack.os.unlink')
    def test_send_alert_slack_with_plot_success(self, mock_unlink, mock_tempfile, 
                                               mock_plt, mock_make_plot, mock_send_slack):
        """Test successful Slack alert with plot generation."""
        # Setup
        mock_temp = MagicMock()
        mock_temp.name = '/tmp/test_metric_2023-01-01_plot.png'
        mock_tempfile.return_value.__enter__.return_value = mock_temp
        mock_tempfile.return_value.__exit__.return_value = None
        
        mock_fig = MagicMock()
        mock_make_plot.return_value = mock_fig
        
        df = pd.DataFrame({
            'metric_timestamp': pd.to_datetime(['2023-01-01 10:00:00', '2023-01-01 11:00:00']),
            'metric_value': [85.5, 92.1],
            'metric_score_smooth': [0.7, 0.9]
        })
        
        # Call function
        send_alert_slack_with_plot(
            df=df,
            metric_name='cpu_usage',
            title='CPU Alert',
            message='High CPU usage detected',
            threshold=0.8,
            metric_timestamp='2023-01-01'
        )
        
        # Assertions
        mock_make_plot.assert_called_once_with(
            df, 'cpu_usage', 0.8, 'metric_score_smooth', 'anomaly_score', tags=None
        )
        mock_fig.savefig.assert_called_once_with('/tmp/test_metric_2023-01-01_plot.png')
        mock_plt.close.assert_called_once_with(mock_fig)
        mock_send_slack.assert_called_once_with(
            title='CPU Alert',
            message='High CPU usage detected',
            image_file_path='/tmp/test_metric_2023-01-01_plot.png',
            channel_name='alerts'
        )
        mock_unlink.assert_called_once_with('/tmp/test_metric_2023-01-01_plot.png')
    
    @patch.dict(os.environ, {
        'ANOMSTACK_SLACK_BOT_TOKEN': 'xoxb-test-token'
    })
    @patch('anomstack.alerts.slack.send_alert_slack')
    @patch('anomstack.alerts.slack.make_alert_plot')
    @patch('anomstack.alerts.slack.plt')
    @patch('anomstack.alerts.slack.tempfile.NamedTemporaryFile')
    @patch('anomstack.alerts.slack.os.unlink')
    def test_send_alert_slack_with_plot_explicit_channel(self, mock_unlink, mock_tempfile,
                                                        mock_plt, mock_make_plot, mock_send_slack):
        """Test Slack alert with plot using explicit channel name."""
        # Setup
        mock_temp = MagicMock()
        mock_temp.name = '/tmp/memory_usage_None_plot.png'
        mock_tempfile.return_value.__enter__.return_value = mock_temp
        mock_tempfile.return_value.__exit__.return_value = None
        
        mock_fig = MagicMock()
        mock_make_plot.return_value = mock_fig
        
        df = pd.DataFrame({
            'metric_timestamp': pd.to_datetime(['2023-01-01 10:00:00']),
            'metric_value': [67.2],
            'custom_score': [0.85]
        })
        
        # Call function with explicit channel and custom parameters
        send_alert_slack_with_plot(
            df=df,
            metric_name='memory_usage',
            title='Memory Alert',
            message='High memory usage detected',
            threshold=0.75,
            score_col='custom_score',
            channel_name='system-alerts',
            score_title='Memory Score',
            tags={'env': 'prod', 'service': 'api'}
        )
        
        # Assertions
        mock_make_plot.assert_called_once_with(
            df, 'memory_usage', 0.75, 'custom_score', 'Memory Score', 
            tags={'env': 'prod', 'service': 'api'}
        )
        mock_send_slack.assert_called_once_with(
            title='Memory Alert',
            message='High memory usage detected',
            image_file_path='/tmp/memory_usage_None_plot.png',
            channel_name='system-alerts'
        )
    
    @patch.dict(os.environ, {
        'ANOMSTACK_SLACK_BOT_TOKEN': 'xoxb-test-token',
        'ANOMSTACK_SLACK_CHANNEL': 'alerts'
    })
    @patch('anomstack.alerts.slack.send_alert_slack')
    @patch('anomstack.alerts.slack.make_alert_plot')
    @patch('anomstack.alerts.slack.plt')
    @patch('anomstack.alerts.slack.tempfile.NamedTemporaryFile')
    @patch('anomstack.alerts.slack.os.unlink')
    def test_send_alert_slack_with_plot_cleanup_on_error(self, mock_unlink, mock_tempfile,
                                                        mock_plt, mock_make_plot, mock_send_slack):
        """Test that temp file is cleaned up even when send_alert_slack fails."""
        # Setup
        mock_temp = MagicMock()
        mock_temp.name = '/tmp/error_test_plot.png'
        mock_tempfile.return_value.__enter__.return_value = mock_temp
        mock_tempfile.return_value.__exit__.return_value = None
        
        mock_fig = MagicMock()
        mock_make_plot.return_value = mock_fig
        
        # Mock send_alert_slack to raise an exception
        mock_send_slack.side_effect = Exception("Slack API Error")
        
        df = pd.DataFrame({
            'metric_timestamp': pd.to_datetime(['2023-01-01 10:00:00']),
            'metric_value': [85.5],
            'metric_score_smooth': [0.9]
        })
        
        # Call function - should raise exception but still clean up
        with pytest.raises(Exception, match="Slack API Error"):
            send_alert_slack_with_plot(
                df=df,
                metric_name='error_test',
                title='Error Test',
                message='This will fail'
            )
        
        # Assertions - temp file should still be cleaned up
        mock_unlink.assert_called_once_with('/tmp/error_test_plot.png')
        mock_plt.close.assert_called_once_with(mock_fig)
    
    @patch.dict(os.environ, {
        'ANOMSTACK_SLACK_BOT_TOKEN': 'xoxb-test-token',
        'ANOMSTACK_SLACK_CHANNEL': 'alerts'
    })
    @patch('anomstack.alerts.slack.send_alert_slack')
    @patch('anomstack.alerts.slack.make_alert_plot')
    @patch('anomstack.alerts.slack.plt')
    @patch('anomstack.alerts.slack.tempfile.NamedTemporaryFile')
    @patch('anomstack.alerts.slack.os.unlink')
    def test_send_alert_slack_with_plot_default_parameters(self, mock_unlink, mock_tempfile,
                                                          mock_plt, mock_make_plot, mock_send_slack):
        """Test Slack alert with plot using all default parameters."""
        # Setup
        mock_temp = MagicMock()
        mock_temp.name = '/tmp/default_test_None_plot.png'
        mock_tempfile.return_value.__enter__.return_value = mock_temp
        mock_tempfile.return_value.__exit__.return_value = None
        
        mock_fig = MagicMock()
        mock_make_plot.return_value = mock_fig
        
        df = pd.DataFrame({
            'metric_timestamp': pd.to_datetime(['2023-01-01 10:00:00']),
            'metric_value': [85.5],
            'metric_score_smooth': [0.9]
        })
        
        # Call function with minimal parameters
        send_alert_slack_with_plot(
            df=df,
            metric_name='default_test',
            title='Default Test',
            message='Testing defaults'
        )
        
        # Assertions - should use default values
        mock_make_plot.assert_called_once_with(
            df, 'default_test', 0.8, 'metric_score_smooth', 'anomaly_score', tags=None
        )
        mock_send_slack.assert_called_once_with(
            title='Default Test',
            message='Testing defaults',
            image_file_path='/tmp/default_test_None_plot.png',
            channel_name='alerts'
        ) 