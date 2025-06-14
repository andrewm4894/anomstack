# GitHub Repository Metrics

This example demonstrates how to monitor GitHub repository metrics using Anomstack's custom Python ingest function pattern. The system tracks key repository statistics like stars, forks, issues, and repository size across multiple projects to detect unusual activity patterns, sudden popularity spikes, or development velocity changes.

## Overview

The GitHub metric batch uses the GitHub API to collect repository statistics and identifies anomalies in:
- **Repository Growth**: Unusual spikes in stars, forks, or watchers
- **Development Activity**: Changes in issue patterns or repository size
- **Community Engagement**: Subscriber count fluctuations
- **Project Health**: Open issues trending up or down

This example is particularly valuable for:
- **Open Source Maintainers**: Monitor project popularity and community engagement
- **Developer Relations**: Track adoption of company repositories
- **Competitive Analysis**: Monitor competitor projects and industry trends
- **Portfolio Management**: Track the health of multiple projects

## Files

- `github.yaml` - Configuration defining the metric batch, schedules, and ingest function
- `github.py` - Custom Python function that fetches repository metrics from GitHub API
- `README.md` - This documentation

## Configuration Details

### Metric Batch Setup
```yaml
metric_batch: "github"
table_key: "metrics_github"
```

### Scheduling
- **Ingest**: Every 15 minutes (`*/15 * * * *`) - Regular data collection
- **Training**: Every 3 hours (`*/180 * * * *`) - Model updates for trend analysis
- **Scoring**: Every 30 minutes (`*/30 * * * *`) - Anomaly detection
- **Alerts**: Every 30 minutes (`*/30 * * * *`) - Notification delivery

### Python Ingest Function

The `github.py` file contains the core data collection logic:

```python
def ingest() -> pd.DataFrame:
    """
    Fetches repository metrics from GitHub API and returns standardized DataFrame
    """
```

#### Key Features:
- **Multi-Repository Support**: Monitors multiple repos simultaneously
- **Comprehensive Metrics**: Tracks stars, forks, issues, subscribers, and size
- **Error Handling**: Graceful handling of API failures and rate limits
- **Standardized Output**: Consistent metric naming and timestamp handling

#### Default Repositories Monitored:
- `andrewm4894/anomstack` - The Anomstack project itself
- `netdata/netdata` - Real-time monitoring system
- `tensorflow/tensorflow` - Machine learning framework
- `apache/spark` - Big data processing
- `apache/airflow` - Workflow orchestration
- `stanfordnlp/dspy` - Language model programming
- `scikit-learn/scikit-learn` - Machine learning library

## How It Works

### 1. Data Collection (Ingest Job)
- Fetches repository data from GitHub API
- Extracts key metrics: `stargazers_count`, `forks_count`, `open_issues_count`, `subscribers_count`, `size`
- Creates standardized metric names: `github.{owner}.{repo}.{metric}`
- Handles API rate limits and errors gracefully

### 2. Anomaly Detection (Train & Score Jobs)
- Analyzes historical patterns for each repository metric
- Identifies unusual growth patterns, sudden drops, or activity spikes
- Considers normal variations in open source project lifecycles

### 3. Alerting (Alert Job)
- Sends notifications when anomalies are detected
- Provides context about which repository and metric triggered the alert
- Includes trend information and significance scoring

### 4. LLM-Enhanced Alerts (LLMAlert Job)
- Generates intelligent summaries of repository activity
- Provides context about potential causes of anomalies
- Suggests actionable insights for repository maintainers

## Example Metrics Generated

```
metric_name: github.andrewm4894.anomstack.stargazers_count
metric_value: 1250
metric_timestamp: 2024-01-15 10:30:00

metric_name: github.tensorflow.tensorflow.forks_count
metric_value: 88234
metric_timestamp: 2024-01-15 10:30:00

metric_name: github.netdata.netdata.open_issues_count
metric_value: 245
metric_timestamp: 2024-01-15 10:30:00
```

## Use Cases and Scenarios

### 1. Open Source Project Management
- **Star Growth Monitoring**: Detect viral moments or marketing campaign effects
- **Community Health**: Track subscriber engagement and issue resolution patterns
- **Fork Analysis**: Identify when projects are being heavily forked (potential concerns or opportunities)

### 2. Competitive Intelligence
- **Market Trends**: Monitor adoption of competing technologies
- **Activity Patterns**: Track development velocity and community engagement
- **Technology Shifts**: Identify emerging or declining technologies

### 3. Developer Relations
- **Adoption Tracking**: Monitor uptake of company open source projects
- **Community Engagement**: Track how documentation and outreach efforts affect metrics
- **Release Impact**: Correlate repository activity with product releases

### 4. Investment and Business Analysis
- **Due Diligence**: Assess the health and adoption of technology investments
- **Portfolio Monitoring**: Track multiple projects across a portfolio
- **Trend Analysis**: Identify long-term patterns in technology adoption

## Customization Options

### Adding New Repositories
Edit the `repos` list in `github.py`:
```python
repos = [
    "your-org/your-repo",
    "another-org/another-repo",
    # Add more repositories here
]
```

### Adding New Metrics
Extend the `metric_keys` list to include additional GitHub API fields:
```python
metric_keys = [
    "stargazers_count",
    "forks_count",
    "open_issues_count",
    "subscribers_count",
    "size",
    "watchers_count",  # Add new metrics
    "network_count",
]
```

### Adjusting Collection Frequency
Modify schedules in `github.yaml` based on your monitoring needs:
- **High-frequency monitoring**: Every 5-10 minutes for critical projects
- **Standard monitoring**: Every 15-30 minutes for regular tracking
- **Low-frequency monitoring**: Hourly or daily for stable projects

## API Considerations

### Rate Limits
- GitHub API allows 60 requests/hour for unauthenticated requests
- Consider using GitHub tokens for higher limits (5000 requests/hour)
- Current implementation processes 7 repositories every 15 minutes = 28 requests/hour

### Authentication (Optional Enhancement)
To add GitHub token authentication:
```python
headers = {"Authorization": f"token {your_github_token}"}
response = requests.get(url, headers=headers, timeout=10)
```

### Error Handling
The implementation includes robust error handling:
- Request timeouts (10 seconds)
- HTTP status code validation
- Graceful handling of missing or invalid data
- Detailed logging for troubleshooting

## Integration with Anomstack Pipeline

This example integrates seamlessly with Anomstack's core pipeline:

1. **Ingest Job**: Collects GitHub metrics using the custom Python function
2. **Train Job**: Builds anomaly detection models specific to repository patterns
3. **Score Job**: Applies models to detect unusual repository activity
4. **Alert Job**: Sends notifications via configured channels (email, Slack)
5. **Change Job**: Tracks change detection for repository metrics
6. **LLMAlert Job**: Generates intelligent summaries and insights
7. **Plot Job**: Creates visualizations of repository trends and anomalies

## Advanced Features

### Multi-Tenant Support
Configure different repository sets for different teams or purposes:
- Development team repositories
- Competitive analysis repositories
- Portfolio company repositories

### Metric Enrichment
Enhance basic metrics with calculated fields:
- Growth rates and velocity
- Issue resolution ratios
- Fork-to-star ratios

### Historical Analysis
Leverage Anomstack's historical data capabilities:
- Long-term trend analysis
- Seasonal pattern detection
- Comparative analysis across repositories

This GitHub monitoring example provides a foundation for comprehensive repository analytics, helping teams stay informed about project health, community engagement, and competitive positioning through intelligent anomaly detection.
