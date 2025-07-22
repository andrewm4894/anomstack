# Alerts System

This directory contains the alerting system for Anomstack, responsible for notifying you when anomalies are detected in your metrics.

## Overview

When Anomstack detects anomalies in your metrics, it can send notifications through various channels. The alerts include detailed information about the anomaly, visualizations, and context to help you understand what happened.

## Components

### `send.py`
- **Purpose**: Main alert orchestration and dispatch
- **Functions**:
  - Coordinates sending alerts across different channels
  - Handles alert throttling and deduplication
  - Manages alert formatting and content preparation

### `email.py`
- **Purpose**: Email notification system
- **Functions**:
  - Sends HTML email alerts with metric visualizations
  - Includes ASCII art plots in email body
  - Supports rich formatting with metric details and context
  - Configurable SMTP settings

### `slack.py`
- **Purpose**: Slack integration for team notifications
- **Functions**:
  - Sends structured Slack messages to configured channels
  - Includes metric information and anomaly details
  - Supports Slack's rich message formatting
  - Can mention specific users or teams

### `asciiart.py`
- **Purpose**: ASCII art plot generation for alerts
- **Functions**:
  - Generates text-based visualizations of metrics
  - Creates ASCII plots showing anomaly scores over time
  - Provides visual context in text-only environments
  - Optimized for email and terminal display

## Alert Content

Alerts typically include:

- **Metric Information**: Name, batch, and current value
- **Anomaly Score**: How anomalous the current value is
- **Visual Context**: ASCII plots showing recent metric behavior
- **Timestamp**: When the anomaly was detected
- **Historical Context**: Recent values and trends

## Configuration

Alert settings are configured in your metric batch YAML files:

```yaml
# Email alerts
email_enabled: true
email_to: ["team@company.com"]
email_from: "anomstack@company.com"

# Slack alerts  
slack_enabled: true
slack_webhook_url: "https://hooks.slack.com/..."
slack_channel: "#anomalies"

# Alert thresholds
anomaly_threshold: 0.8
alert_frequency: "once_per_day"
```

## Environment Variables

Required environment variables for alerts:

```bash
# Email (if using SMTP)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password

# Slack (if using Slack)
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/...
```

## Custom Alert Channels

You can extend the alert system by:

1. Creating a new alert module (e.g., `teams.py`, `discord.py`)
2. Implementing the alert interface
3. Adding configuration support
4. Registering the new channel in `send.py`

See existing implementations as reference for creating custom alert channels.
