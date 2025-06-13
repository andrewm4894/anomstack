"""
Tests for anomstack.alerts.email module - Email functionality.
"""

import os
import pytest
import pandas as pd
from unittest.mock import patch, MagicMock, mock_open, call
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from anomstack.alerts.email import send_email_with_plot, send_email


class TestSendEmailWithPlot:
    """Test the send_email_with_plot function."""
    
    @patch('anomstack.alerts.email.get_dagster_logger')
    @patch('anomstack.alerts.email.make_alert_plot')
    @patch('anomstack.alerts.email.tempfile.NamedTemporaryFile')
    @patch('anomstack.alerts.email.smtplib.SMTP')
    @patch('anomstack.alerts.email.ssl.create_default_context')
    @patch('builtins.open', new_callable=mock_open, read_data=b'fake_image_data')
    def test_send_email_with_plot_success(self, mock_file, mock_ssl, mock_smtp, mock_temp, mock_plot, mock_logger):
        """Test successful email sending with plot."""
        # Setup
        mock_logger.return_value = MagicMock()
        mock_fig = MagicMock()
        mock_plot.return_value = mock_fig
        mock_temp_file = MagicMock()
        mock_temp_file.name = '/tmp/test_plot.png'
        mock_temp.__enter__.return_value = mock_temp_file
        mock_server = MagicMock()
        mock_smtp.return_value.__enter__.return_value = mock_server
        mock_context = MagicMock()
        mock_ssl.return_value = mock_context
        
        # Mock environment variables
        env_vars = {
            'ANOMSTACK_ALERT_EMAIL_FROM': 'sender@example.com',
            'ANOMSTACK_ALERT_EMAIL_PASSWORD': 'password123',
            'ANOMSTACK_ALERT_EMAIL_TO': 'recipient@example.com',
            'ANOMSTACK_ALERT_EMAIL_SMTP_HOST': 'smtp.example.com',
            'ANOMSTACK_ALERT_EMAIL_SMTP_PORT': '587'
        }
        
        # Test data
        df = pd.DataFrame({
            'metric_timestamp': pd.date_range('2023-01-01', periods=3, freq='h'),
            'metric_value': [10, 20, 30],
            'metric_score_smooth': [0.1, 0.5, 0.9]
        })
        
        with patch.dict(os.environ, env_vars):
            # Call function
            send_email_with_plot(
                df=df,
                metric_name='test_metric',
                subject='Test Alert',
                body='Test email body',
                attachment_name='test_alert',
                threshold=0.8
            )
        
        # Assertions
        mock_plot.assert_called_once()
        mock_fig.savefig.assert_called_once()
        mock_smtp.assert_called_once_with('smtp.example.com', '587', timeout=30)
        mock_server.connect.assert_called_once_with('smtp.example.com', '587')
        mock_server.starttls.assert_called_once_with(context=mock_context)
        mock_server.login.assert_called_once_with('sender@example.com', 'password123')
        mock_server.sendmail.assert_called_once()
        mock_server.quit.assert_called_once()
    
    @patch('anomstack.alerts.email.get_dagster_logger')
    @patch('anomstack.alerts.email.make_alert_plot')
    @patch('anomstack.alerts.email.tempfile.NamedTemporaryFile')
    @patch('anomstack.alerts.email.smtplib.SMTP')
    @patch('anomstack.alerts.email.ssl.create_default_context')
    @patch('builtins.open', new_callable=mock_open, read_data=b'fake_image_data')
    def test_send_email_with_plot_custom_params(self, mock_file, mock_ssl, mock_smtp, mock_temp, mock_plot, mock_logger):
        """Test email sending with custom parameters."""
        # Setup
        mock_logger.return_value = MagicMock()
        mock_fig = MagicMock()
        mock_plot.return_value = mock_fig
        mock_temp_file = MagicMock()
        mock_temp_file.name = '/tmp/custom_plot.png'
        mock_temp.__enter__.return_value = mock_temp_file
        mock_server = MagicMock()
        mock_smtp.return_value.__enter__.return_value = mock_server
        
        # Mock environment variables
        env_vars = {
            'ANOMSTACK_ALERT_EMAIL_FROM': 'sender@example.com',
            'ANOMSTACK_ALERT_EMAIL_PASSWORD': 'password123',
            'ANOMSTACK_ALERT_EMAIL_TO': 'recipient@example.com',
            'ANOMSTACK_ALERT_EMAIL_SMTP_HOST': 'smtp.example.com',
            'ANOMSTACK_ALERT_EMAIL_SMTP_PORT': '587'
        }
        
        # Test data
        df = pd.DataFrame({
            'metric_timestamp': pd.date_range('2023-01-01', periods=3, freq='h'),
            'metric_value': [10, 20, 30],
            'custom_score': [0.2, 0.6, 0.8]
        })
        
        tags = {'environment': 'prod', 'service': 'api'}
        
        with patch.dict(os.environ, env_vars):
            # Call function with custom parameters
            send_email_with_plot(
                df=df,
                metric_name='custom_metric',
                subject='Custom Alert',
                body='Custom email body',
                attachment_name='custom_alert',
                threshold=0.7,
                score_col='custom_score',
                score_title='Custom Score',
                tags=tags
            )
        
        # Assertions
        mock_plot.assert_called_once_with(
            df, 'custom_metric', 0.7, 'custom_score', 'Custom Score', tags=tags
        )


class TestSendEmail:
    """Test the send_email function."""
    
    @patch('anomstack.alerts.email.get_dagster_logger')
    @patch('anomstack.alerts.email.smtplib.SMTP')
    @patch('anomstack.alerts.email.ssl.create_default_context')
    def test_send_email_success(self, mock_ssl, mock_smtp, mock_logger):
        """Test successful email sending."""
        # Setup
        mock_logger.return_value = MagicMock()
        mock_server = MagicMock()
        mock_smtp.return_value.__enter__.return_value = mock_server
        mock_context = MagicMock()
        mock_ssl.return_value = mock_context
        
        # Mock environment variables
        env_vars = {
            'ANOMSTACK_ALERT_EMAIL_FROM': 'sender@example.com',
            'ANOMSTACK_ALERT_EMAIL_PASSWORD': 'password123',
            'ANOMSTACK_ALERT_EMAIL_TO': 'recipient@example.com',
            'ANOMSTACK_ALERT_EMAIL_SMTP_HOST': 'smtp.example.com',
            'ANOMSTACK_ALERT_EMAIL_SMTP_PORT': '587'
        }
        
        with patch.dict(os.environ, env_vars):
            # Call function
            send_email(
                subject='Test Subject',
                body='Test body content'
            )
        
        # Assertions
        mock_smtp.assert_called_once_with('smtp.example.com', '587')
        mock_server.connect.assert_called_once_with('smtp.example.com', '587')
        mock_server.starttls.assert_called_once_with(context=mock_context)
        mock_server.login.assert_called_once_with('sender@example.com', 'password123')
        mock_server.sendmail.assert_called_once()
        mock_server.quit.assert_called_once()
        mock_logger.return_value.info.assert_called_once_with("email 'Test Subject' sent to recipient@example.com")
    
    @patch('anomstack.alerts.email.get_dagster_logger')
    @patch('anomstack.alerts.email.smtplib.SMTP')
    @patch('anomstack.alerts.email.ssl.create_default_context')
    def test_send_email_html_body(self, mock_ssl, mock_smtp, mock_logger):
        """Test email sending with HTML body."""
        # Setup
        mock_logger.return_value = MagicMock()
        mock_server = MagicMock()
        mock_smtp.return_value.__enter__.return_value = mock_server
        
        # Mock environment variables
        env_vars = {
            'ANOMSTACK_ALERT_EMAIL_FROM': 'sender@example.com',
            'ANOMSTACK_ALERT_EMAIL_PASSWORD': 'password123',
            'ANOMSTACK_ALERT_EMAIL_TO': 'recipient@example.com',
            'ANOMSTACK_ALERT_EMAIL_SMTP_HOST': 'smtp.example.com',
            'ANOMSTACK_ALERT_EMAIL_SMTP_PORT': '587'
        }
        
        html_body = '<html><body><h1>Alert</h1><p>Test HTML content</p></body></html>'
        
        with patch.dict(os.environ, env_vars):
            # Call function
            send_email(
                subject='HTML Alert',
                body=html_body
            )
        
        # Assertions
        mock_server.sendmail.assert_called_once()
        mock_logger.return_value.info.assert_called_once_with("email 'HTML Alert' sent to recipient@example.com") 