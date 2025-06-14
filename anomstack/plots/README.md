# Plotting Utilities

This directory contains utilities for generating visualizations and plots within Anomstack's anomaly detection pipeline.

## Overview

The `plots` module provides standardized plotting functionality for visualizing metrics, anomaly scores, and model performance. These visualizations are used in the dashboard, Dagster UI, and alert notifications.

## Components

### `plot.py`
- **Purpose**: Core plotting and visualization functions
- **Functions**:
  - Generate time series plots of metrics and anomaly scores
  - Create diagnostic plots for model evaluation
  - Render plots for dashboard and web interface
  - Generate static plots for email alerts and reports
  - Create interactive plots for data exploration

## Visualization Types

### Time Series Plots
- **Metric Values**: Line plots showing metric values over time
- **Anomaly Scores**: Overlay anomaly scores on metric plots
- **Anomaly Highlights**: Visual indicators for detected anomalies
- **Confidence Intervals**: Show model uncertainty bands
- **Multi-metric**: Compare multiple metrics on the same plot

### Diagnostic Plots
- **Model Performance**: ROC curves, precision-recall curves
- **Residual Analysis**: Plots for model validation
- **Feature Importance**: Show which features drive anomaly detection
- **Training Progress**: Monitor model training convergence

### Dashboard Visualizations
- **Interactive Charts**: Plotly-based interactive visualizations
- **Real-time Updates**: Live updating charts for monitoring
- **Drill-down Views**: Detailed views of specific time periods
- **Comparative Analysis**: Side-by-side metric comparisons

## Plot Generation Flow

1. **Data Preparation**: Clean and format data for plotting
2. **Plot Configuration**: Apply styling and layout settings
3. **Rendering**: Generate plot using appropriate library
4. **Export**: Save or display plot in target format
5. **Integration**: Embed plots in dashboard or alerts

## Supported Output Formats

- **PNG/JPG**: Static images for emails and reports
- **SVG**: Vector graphics for web interfaces
- **HTML**: Interactive plots with Plotly
- **PDF**: High-quality prints and documents
- **ASCII Art**: Text-based plots for terminal/email alerts

## Configuration

Plot settings can be configured through the configuration system:

```yaml
plotting:
  # Style settings
  theme: "anomstack"
  color_palette: ["#1f77b4", "#ff7f0e", "#2ca02c"]
  figure_size: [12, 6]
  
  # Content settings
  show_anomalies: true
  show_confidence_bands: true
  anomaly_threshold_line: true
  
  # Output settings
  dpi: 150
  format: "png"
  interactive: false
```

## Common Usage Patterns

### Basic Time Series Plot
```python
from anomstack.plots.plot import plot_metric_timeseries

# Create a basic time series plot
fig = plot_metric_timeseries(
    df=metric_data,
    title="Daily Revenue Metrics",
    anomaly_scores=scores_df,
    show_anomalies=True
)
```

### Dashboard Integration
```python
from anomstack.plots.plot import create_dashboard_plot

# Create interactive plot for dashboard
plotly_fig = create_dashboard_plot(
    df=metric_data,
    plot_type="timeseries",
    interactive=True,
    height=400
)
```

### Alert Visualization
```python
from anomstack.plots.plot import generate_alert_plot

# Generate plot for email alerts
alert_plot = generate_alert_plot(
    df=recent_data,
    anomaly_detected=True,
    format="ascii"  # For email compatibility
)
```

## Styling and Theming

Anomstack uses consistent visual styling across all plots:

- **Color Scheme**: Blue for normal values, red for anomalies
- **Typography**: Clear, readable fonts optimized for different displays
- **Layout**: Consistent spacing and alignment
- **Branding**: Subtle Anomstack branding elements

### Custom Themes
```python
# Define custom plot theme
custom_theme = {
    "background_color": "#ffffff",
    "grid_color": "#f0f0f0",
    "normal_color": "#1f77b4",
    "anomaly_color": "#d62728",
    "threshold_color": "#ff7f0e"
}
```

## Performance Considerations

- **Data Sampling**: Automatically downsample large datasets for performance
- **Lazy Rendering**: Generate plots only when needed
- **Caching**: Cache generated plots to avoid regeneration
- **Efficient Libraries**: Use optimized plotting libraries (matplotlib, plotly)

## Integration Points

The plotting utilities are used throughout Anomstack:

- **Dashboard**: Interactive visualizations for the web interface
- **Dagster UI**: Plots embedded in job logs and asset views
- **Email Alerts**: Static plots included in alert notifications
- **Reports**: Automated report generation with visualizations
- **API**: Plot generation endpoints for external integrations

## Accessibility

Plots are designed with accessibility in mind:

- **Color Blind Friendly**: Use distinct colors and patterns
- **High Contrast**: Ensure sufficient contrast ratios
- **Alternative Text**: Provide descriptive alt text for images
- **Scalable**: Vector formats that scale without quality loss

## Export and Sharing

- **Web Sharing**: Generate shareable HTML plots
- **Print Ready**: High-resolution plots for documentation
- **Social Media**: Optimized formats for sharing insights
- **API Access**: Programmatic access to generated plots

## Troubleshooting

### Common Issues

1. **Memory Issues**: Large datasets causing memory problems
2. **Rendering Errors**: Font or display driver issues
3. **Format Compatibility**: Output format not supported by target system
4. **Performance**: Slow plot generation for large time series

### Debugging

Enable plot debugging:
```python
import logging
logging.getLogger('anomstack.plots').setLevel(logging.DEBUG)
```

### Performance Optimization

- Use data sampling for large datasets
- Enable plot caching for repeated views
- Choose appropriate output formats for use case
- Monitor memory usage during plot generation 