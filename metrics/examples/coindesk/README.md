# CoinDesk Cryptocurrency Monitoring

This **Anomstack metric batch** demonstrates how to monitor cryptocurrency prices and market data using CoinDesk's API for anomaly detection. Perfect for crypto traders, portfolio managers, and anyone wanting to detect unusual market movements in digital assets.

## Overview

This example shows how to:
- Monitor real-time cryptocurrency prices from CoinDesk API
- Detect anomalies in crypto price movements and volatility
- Track multiple cryptocurrency pairs simultaneously
- Set up alerts for unusual market activity and price movements
- Apply machine learning to cryptocurrency market data

## How It Works

### Anomstack Pipeline Integration
This metric batch flows through Anomstack's standard Dagster job pipeline:

1. **Ingest Job**: Runs [`coindesk.py`](coindesk.py) to fetch current crypto prices from CoinDesk
2. **Train Job**: PyOD models learn normal patterns in cryptocurrency price movements
3. **Score Job**: Generate anomaly scores for current crypto market data
4. **Alert Job**: Send notifications when unusual crypto activity is detected

### Cryptocurrency Metrics Monitored
- **Price Data**: Current prices for major cryptocurrencies (BTC, ETH, etc.)
- **Price Changes**: Percentage moves and absolute price differences
- **Market Volatility**: Price volatility measures and trend indicators
- **Cross-Pair Analysis**: Relative performance between different crypto assets

## Files

- **[`coindesk.py`](coindesk.py)**: Custom Python ingest function using CoinDesk API
- **[`coindesk.yaml`](coindesk.yaml)**: Anomstack configuration

## Setup & Usage

### Prerequisites
- Internet connection for CoinDesk API access
- Python `requests` library (included with Anomstack)
- No API key required (CoinDesk API is free with rate limits)

### Configuration
The YAML file configures:
```yaml
metric_batch: 'coindesk'
ingest_fn: 'coindesk.py'  # Custom Python function
# Recommended: Adjust for crypto market sensitivity
alert_threshold: 0.6  # Lower threshold for more sensitive crypto alerts
train_metric_timestamp_max_days_ago: 30  # Use 30 days of crypto data
score_metric_timestamp_max_days_ago: 7   # Score recent week for patterns
```

### Default Cryptocurrencies Monitored
The example monitors these major cryptocurrency pairs by default:
- **BTC-USD**: Bitcoin to US Dollar
- **ETH-USD**: Ethereum to US Dollar
- **Additional pairs can be easily added**

### Running the Example
1. **Copy to your metrics directory**:
   ```bash
   cp -r metrics/examples/coindesk metrics/my_crypto
   ```

2. **Customize cryptocurrency pairs**: Edit `coindesk.py`:
   ```python
   # Monitor your preferred cryptocurrency pairs
   CRYPTO_INSTRUMENTS = [
       'BTC-USD',   # Bitcoin
       'ETH-USD',   # Ethereum
       'ADA-USD',   # Cardano
       'SOL-USD',   # Solana
       'MATIC-USD'  # Polygon
   ]
   ```

3. **Configure markets**: Adjust the market parameter:
   ```python
   # Different markets available
   MARKET = 'cadli'  # Default market
   # Other options: 'coinbase', 'kraken', 'binance'
   ```

4. **Enable in Dagster**: The jobs will appear in your Dagster UI

### Customization Ideas
- **Portfolio Tracking**: Monitor your actual crypto holdings
- **DeFi Tokens**: Add popular DeFi tokens and altcoins
- **Stablecoin Monitoring**: Track USDC, USDT, DAI for peg anomalies
- **Cross-Market Analysis**: Compare prices across different exchanges
- **Market Cap Tracking**: Monitor market capitalization changes
- **Volume Analysis**: Include trading volume anomaly detection

## Example Output

The ingest function returns cryptocurrency data like:
```python
[
    {
        'metric_timestamp': datetime.now(),
        'metric_name': 'BTC_USD_price',
        'metric_value': 43250.50
    },
    {
        'metric_timestamp': datetime.now(),
        'metric_name': 'ETH_USD_price',
        'metric_value': 2650.75
    },
    {
        'metric_timestamp': datetime.now(),
        'metric_name': 'BTC_USD_change_24h',
        'metric_value': 3.45  # Percentage change
    }
]
```

## Cryptocurrency Anomaly Detection Scenarios

This example can detect:
- **Price Spikes**: Sudden price movements beyond normal volatility
- **Flash Crashes**: Rapid price drops indicating market stress
- **Pump and Dump**: Unusual price patterns suggesting manipulation
- **Market Correlation Breaks**: When crypto assets decouple from normal patterns
- **News Impact**: Price reactions to major cryptocurrency news or events
- **Regulatory Events**: Market responses to regulatory announcements
- **Technical Breakouts**: Price movements beyond technical resistance/support levels
- **Whale Activity**: Large trades causing unusual price movements

## Crypto Trading & Investment Use Cases

### Risk Management
- Monitor portfolio exposure and concentration risk
- Detect when positions move outside risk parameters
- Alert on correlated moves across crypto holdings
- Track volatility spikes that could impact portfolios

### Trading Opportunities
- Identify cryptocurrencies showing unusual momentum
- Detect oversold/overbought conditions in quality assets
- Spot arbitrage opportunities between exchanges
- Monitor for technical breakout patterns

### Market Analysis
- Track overall crypto market health and sentiment
- Monitor Bitcoin dominance and altcoin seasons
- Detect sector rotation within cryptocurrency markets
- Analyze correlation patterns between crypto and traditional assets

### DeFi & Web3 Monitoring
- Track governance token price movements
- Monitor stablecoin peg stability
- Detect unusual activity in DeFi protocol tokens
- Alert on bridge token price discrepancies

## Integration with Anomstack Features

- **Dashboard**: Visualize crypto prices and anomaly scores in real-time
- **Alerts**: Get immediate notifications for unusual crypto market activity
- **Change Detection**: Identify structural changes in crypto market behavior
- **LLM Alerts**: Use AI to analyze and explain crypto market anomalies
- **Frequency Settings**: Monitor at different intervals (1min, 5min, hourly)

## Environment Variables

Configure crypto-specific settings:
```bash
# Custom cryptocurrency list (comma-separated)
COINDESK_INSTRUMENTS="BTC-USD,ETH-USD,ADA-USD,SOL-USD"

# Market selection
COINDESK_MARKET="cadli"

# Alert thresholds for different scenarios
CRYPTO_PRICE_ALERT_THRESHOLD=0.6
CRYPTO_VOLATILITY_ALERT_THRESHOLD=0.8

# Trading hours consideration (24/7 for crypto)
CRYPTO_24_7_MONITORING=true
```

## API Integration Details

**CoinDesk API Endpoints Used**:
- **Current Prices**: `/index/cc/v1/latest/tick?market={market}&instruments={instruments}&apply_mapping=true`
- **Historical Data**: `/index/cc/v1/history/tick?market={market}&instruments={instruments}`

**Example API Call**:
```
https://data-api.coindesk.com/index/cc/v1/latest/tick?market=cadli&instruments=BTC-USD,ETH-USD&apply_mapping=true
```

**Response Format**:
```json
{
  "data": [
    {
      "instrument": "BTC-USD",
      "price": "43250.50",
      "change_24h": "3.45",
      "timestamp": "2024-01-15T10:30:00Z"
    },
    {
      "instrument": "ETH-USD",
      "price": "2650.75",
      "change_24h": "-1.23",
      "timestamp": "2024-01-15T10:30:00Z"
    }
  ]
}
```

**Rate Limits**:
- Free tier: 100 requests per hour
- Generally sufficient for regular monitoring
- Consider upgrading for high-frequency trading applications

## Advanced Features

### Multi-Exchange Price Comparison
```python
# Compare prices across different markets
def get_cross_exchange_data():
    markets = ['cadli', 'coinbase', 'kraken']
    prices = {}

    for market in markets:
        data = get_coindesk_data(market, 'BTC-USD')
        prices[market] = data['price']

    # Calculate price spreads and arbitrage opportunities
    max_price = max(prices.values())
    min_price = min(prices.values())
    spread = (max_price - min_price) / min_price * 100

    return {
        'metric_timestamp': datetime.now(),
        'metric_name': 'BTC_USD_cross_exchange_spread',
        'metric_value': spread
    }
```

### Volatility Calculation
```python
# Calculate rolling volatility metrics
def calculate_crypto_volatility(price_history, window=24):
    import numpy as np

    # Calculate percentage returns
    returns = np.diff(price_history) / price_history[:-1] * 100

    # Rolling volatility (standard deviation of returns)
    volatility = np.std(returns[-window:]) if len(returns) >= window else 0

    return {
        'metric_timestamp': datetime.now(),
        'metric_name': 'BTC_USD_volatility_24h',
        'metric_value': volatility
    }
```

### Market Cap and Dominance Metrics
```python
# Calculate market dominance and relative performance
def calculate_market_metrics(btc_price, eth_price, total_market_cap):
    btc_dominance = (btc_price * btc_supply) / total_market_cap * 100
    eth_btc_ratio = eth_price / btc_price

    return [
        {
            'metric_timestamp': datetime.now(),
            'metric_name': 'BTC_market_dominance',
            'metric_value': btc_dominance
        },
        {
            'metric_timestamp': datetime.now(),
            'metric_name': 'ETH_BTC_ratio',
            'metric_value': eth_btc_ratio
        }
    ]
```

### Error Handling for Market Data
```python
# Robust error handling for crypto API calls
def safe_crypto_request(instruments, retries=3):
    for attempt in range(retries):
        try:
            response = requests.get(
                f"{COINDESK_BASE_URL}/latest/tick",
                params={
                    'market': 'cadli',
                    'instruments': ','.join(instruments),
                    'apply_mapping': 'true'
                },
                timeout=10
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            if attempt == retries - 1:
                logger.error(f"Failed to get crypto data: {e}")
                return None
            time.sleep(2 ** attempt)  # Exponential backoff
```

## Crypto Market Considerations

### Market Hours
- **24/7 Trading**: Cryptocurrency markets never close
- **Weekend Activity**: Unlike traditional markets, crypto trades weekends
- **Global Nature**: Price movements happen across all time zones

### Volatility Characteristics
- **High Volatility**: Crypto markets are more volatile than traditional assets
- **Correlation Patterns**: Crypto assets often move together during major events
- **News Sensitivity**: Prices react quickly to regulatory and adoption news

### Technical Factors
- **Blockchain Events**: Halvings, upgrades, and forks affect prices
- **Mining Dynamics**: Hash rate and difficulty adjustments
- **Exchange Flows**: On-chain metrics and exchange reserves

## Risk Warnings

- **High Volatility**: Cryptocurrency markets are extremely volatile
- **Regulatory Risk**: Regulatory changes can significantly impact prices
- **Market Manipulation**: Smaller crypto markets may be subject to manipulation
- **Technology Risk**: Smart contract bugs and blockchain issues can affect prices
- **Liquidity Risk**: Some cryptocurrencies may have limited liquidity

This example provides a solid foundation for cryptocurrency monitoring and anomaly detection, enabling sophisticated analysis of digital asset markets within the Anomstack ecosystem.
