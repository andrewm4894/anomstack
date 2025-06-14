# Yahoo Finance Stock Anomaly Detection

This **Anomstack metric batch** demonstrates how to monitor stock market data for anomalies using the Yahoo Finance API. Perfect for detecting unusual market movements, tracking portfolio performance, or identifying trading opportunities through anomaly detection.

## Overview

This example shows how to:
- Use custom Python functions to fetch real-time stock data
- Monitor multiple stock tickers simultaneously
- Detect anomalies in stock price movements and trading volumes
- Set up alerts for unusual market activity
- Apply anomaly detection to financial time series data

## How It Works

### Anomstack Pipeline Integration
This metric batch flows through Anomstack's standard Dagster job pipeline:

1. **Ingest Job**: Runs [`yfinance.py`](yfinance.py) to fetch current stock data from Yahoo Finance
2. **Train Job**: PyOD models learn normal patterns in stock prices and volumes
3. **Score Job**: Generate anomaly scores for current market data
4. **Alert Job**: Send notifications when unusual stock activity is detected

### Financial Metrics Generated
- **Stock Prices**: Current price, price changes, percentage moves
- **Trading Volume**: Volume anomalies indicating unusual activity
- **Market Indicators**: Derived metrics like volatility, momentum
- **Portfolio Metrics**: Combined metrics across multiple holdings

## Files

- **[`yfinance.py`](yfinance.py)**: Custom Python ingest function using yfinance library
- **[`yfinance.yaml`](yfinance.yaml)**: Anomstack configuration

## Setup & Usage

### Prerequisites
- Python `yfinance` library (install with `pip install yfinance`)
- Internet connection for market data access
- No API key required (Yahoo Finance is free with rate limits)

### Configuration
The YAML file configures:
```yaml
metric_batch: 'yfinance'
ingest_fn: 'yfinance.py'  # Custom Python function
# Optional: Adjust for financial market sensitivity
alert_threshold: 0.6  # Lower threshold for more sensitive trading alerts
train_metric_timestamp_max_days_ago: 60  # Use 60 days of training data
```

### Default Stocks Monitored
The example monitors these popular tickers by default:
- **AAPL**: Apple Inc.
- **GOOGL**: Alphabet Inc. (Google)
- **MSFT**: Microsoft Corporation
- **TSLA**: Tesla Inc.
- **SPY**: SPDR S&P 500 ETF (market benchmark)

### Running the Example
1. **Install dependencies**:
   ```bash
   pip install yfinance
   ```

2. **Copy to your metrics directory**:
   ```bash
   cp -r metrics/examples/yfinance metrics/my_stocks
   ```

3. **Customize your portfolio**: Edit `yfinance.py` to track your stocks:
   ```python
   tickers = ['AAPL', 'GOOGL', 'YOUR_STOCK', 'BTC-USD', '^GSPC']
   ```

4. **Enable in Dagster**: The jobs will appear in your Dagster UI

### Customization Ideas
- **Portfolio Tracking**: Monitor your actual investment portfolio
- **Sector Analysis**: Focus on specific sectors (tech, finance, healthcare)
- **Cryptocurrency**: Add crypto tickers like 'BTC-USD', 'ETH-USD'
- **International Markets**: Include global indices and foreign stocks
- **Options & Derivatives**: Extend to monitor options chain data
- **Technical Indicators**: Add RSI, MACD, moving averages

## Example Output

The ingest function returns stock data like:
```python
[
    {
        'metric_timestamp': datetime.now(),
        'metric_name': 'AAPL_price',
        'metric_value': 185.42
    },
    {
        'metric_timestamp': datetime.now(),
        'metric_name': 'AAPL_volume',
        'metric_value': 45682300
    },
    {
        'metric_timestamp': datetime.now(),
        'metric_name': 'AAPL_change_percent',
        'metric_value': 2.45
    }
]
```

## Financial Anomaly Detection Scenarios

This example can detect:
- **Price Spikes**: Unusual stock price movements beyond normal volatility
- **Volume Anomalies**: Trading volume significantly above/below average
- **Market Crashes**: Sudden broad market declines
- **Earnings Surprises**: Post-earnings announcement price reactions
- **Breaking News Impact**: Stock reactions to company/industry news
- **Sector Rotation**: Unusual movements in sector-specific stocks
- **After-Hours Activity**: Anomalies in extended trading sessions

## Trading & Investment Use Cases

### Risk Management
- Monitor portfolio exposure and concentration risk
- Detect when positions move outside risk parameters
- Alert on correlated moves across holdings

### Opportunity Detection
- Identify stocks showing unusual positive momentum
- Detect oversold conditions in quality stocks
- Spot sector rotation opportunities

### Market Monitoring
- Track overall market health via index anomalies
- Monitor VIX and volatility indicators
- Detect flight-to-quality movements

## Integration with Anomstack Features

- **Dashboard**: Visualize stock performance and anomaly scores in real-time
- **Alerts**: Get immediate notifications for unusual market activity
- **Change Detection**: Identify structural changes in stock behavior
- **LLM Alerts**: Use AI to analyze and explain market anomalies
- **Frequency Settings**: Monitor at different intervals (1min, 5min, hourly, daily)

## Environment Variables

Configure trading-specific settings:
```bash
# Custom stock list (comma-separated)
YFINANCE_TICKERS="AAPL,GOOGL,MSFT,TSLA,SPY"

# Alert thresholds for different metrics
STOCK_PRICE_ALERT_THRESHOLD=0.6
VOLUME_ALERT_THRESHOLD=0.8

# Market hours consideration
TRADING_HOURS_ONLY=true
INCLUDE_PREMARKET=false
```

## API Details & Rate Limits

**Yahoo Finance via yfinance library**:
- **Rate Limits**: ~2000 requests/hour (generous for most use cases)
- **Data Frequency**: Real-time (15-20 minute delay for most data)
- **Historical Data**: Access to years of historical price/volume data
- **Global Markets**: Support for international exchanges

**Data Quality Considerations**:
- Yahoo Finance data is free but not guaranteed for professional trading
- For production trading systems, consider premium data providers
- Be aware of market holidays and trading hours

## Advanced Features

### Multi-Timeframe Analysis
```python
# Monitor same stock at different frequencies
tickers = {
    'AAPL_1min': {'symbol': 'AAPL', 'interval': '1m'},
    'AAPL_1hour': {'symbol': 'AAPL', 'interval': '1h'},
    'AAPL_daily': {'symbol': 'AAPL', 'interval': '1d'}
}
```

### Technical Indicators
```python
# Add technical analysis metrics
def calculate_rsi(prices, period=14):
    # RSI calculation
    return rsi_value

def calculate_macd(prices):
    # MACD calculation  
    return macd_line, signal_line
```

### Risk Metrics
```python
# Portfolio-level risk metrics
def calculate_var(returns, confidence=0.05):
    # Value at Risk calculation
    return var_value
```

This example provides a solid foundation for building sophisticated financial anomaly detection systems while leveraging Anomstack's powerful ML capabilities.
