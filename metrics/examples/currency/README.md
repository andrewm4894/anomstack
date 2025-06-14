# Currency Exchange Rate Monitoring

This **Anomstack metric batch** demonstrates how to monitor currency exchange rates for anomaly detection using free currency APIs. Perfect for forex traders, international businesses, financial analysts, and anyone needing to track unusual movements in foreign exchange markets.

## Overview

This example shows how to:
- Monitor real-time currency exchange rates from free APIs
- Detect anomalies in forex price movements and volatility
- Track multiple currency pairs simultaneously
- Set up alerts for unusual exchange rate fluctuations
- Apply machine learning to foreign exchange market data

## How It Works

### Anomstack Pipeline Integration
This metric batch flows through Anomstack's standard Dagster job pipeline:

1. **Ingest Job**: Runs [`currency.py`](currency.py) to fetch current exchange rates
2. **Train Job**: PyOD models learn normal patterns in currency movements
3. **Score Job**: Generate anomaly scores for current exchange rate data
4. **Alert Job**: Send notifications when unusual currency movements are detected

### Currency Metrics Monitored
- **Exchange Rates**: Current rates for major currency pairs (EUR/USD, GBP/USD, etc.)
- **Rate Changes**: Percentage moves and absolute rate differences
- **Cross-Currency Analysis**: Relative performance between different currencies
- **Volatility Tracking**: Exchange rate volatility and trend indicators

## Files

- **[`currency.py`](currency.py)**: Custom Python ingest function using currency API
- **[`currency.yaml`](currency.yaml)**: Anomstack configuration with daily scheduling

## Setup & Usage

### Prerequisites
- Internet connection for currency API access
- Python `requests` library (included with Anomstack)
- No API key required (uses free currency API)

### Configuration
The YAML file configures:
```yaml
metric_batch: 'currency'
ingest_fn: 'currency.py'  # Custom Python function
# Scheduled once daily (forex markets close on weekends)
ingest_cron_schedule: "30 8 * * *"  # 8:30 AM daily
# Recommended: Adjust for forex market sensitivity
alert_threshold: 0.7  # Higher threshold for less noisy forex alerts
train_metric_timestamp_max_days_ago: 60  # Use 60 days of forex data
```

### Default Currency Pairs Monitored
The example monitors these major currency pairs by default:
- **EUR**: Euro against multiple currencies
- **USD**: US Dollar cross-rates
- **GBP**: British Pound exchange rates
- **JPY**: Japanese Yen rates
- **Additional major currencies**: CHF, CAD, AUD, etc.

### Running the Example
1. **Copy to your metrics directory**:
   ```bash
   cp -r metrics/examples/currency metrics/my_currency
   ```

2. **Customize currency pairs**: Edit `currency.py`:
   ```python
   # Monitor your preferred base currencies
   BASE_CURRENCIES = [
       'eur',  # Euro
       'usd',  # US Dollar
       'gbp',  # British Pound
       'jpy',  # Japanese Yen
       'chf'   # Swiss Franc
   ]
   
   # Target currencies to convert to
   TARGET_CURRENCIES = ['usd', 'eur', 'gbp', 'jpy', 'cad', 'aud']
   ```

3. **Adjust scheduling**: Modify the cron schedule for your timezone:
   ```yaml
   # Run during your business hours
   ingest_cron_schedule: "0 9 * * 1-5"  # 9 AM weekdays only
   ```

4. **Enable in Dagster**: The jobs will appear in your Dagster UI

### Customization Ideas
- **Business Focus**: Monitor currencies relevant to your business operations
- **Regional Pairs**: Focus on specific geographic regions (Asian currencies, European pairs)
- **Emerging Markets**: Add emerging market currencies for broader coverage
- **Commodity Currencies**: Include currencies tied to commodities (AUD, CAD, NOK)
- **Cross-Rate Analysis**: Monitor currency triangulation opportunities
- **Central Bank Rates**: Correlate with interest rate differentials

## Example Output

The ingest function returns currency data like:
```python
[
    {
        'metric_timestamp': datetime.now(),
        'metric_name': 'EUR_USD_rate',
        'metric_value': 1.0925
    },
    {
        'metric_timestamp': datetime.now(),
        'metric_name': 'GBP_USD_rate',
        'metric_value': 1.2675
    },
    {
        'metric_timestamp': datetime.now(),
        'metric_name': 'USD_JPY_rate',
        'metric_value': 149.85
    }
]
```

## Currency Anomaly Detection Scenarios

This example can detect:
- **Central Bank Interventions**: Sudden rate moves from monetary policy changes
- **Economic Data Releases**: Currency reactions to GDP, inflation, employment data
- **Geopolitical Events**: Currency movements from political or economic shocks
- **Interest Rate Changes**: Reactions to central bank rate decisions
- **Market Crisis Events**: Flight-to-safety movements during market stress
- **Technical Breakouts**: Rate movements beyond key technical levels
- **Carry Trade Unwinding**: Sudden reversals in currency carry trades
- **Seasonal Patterns**: Unusual movements outside normal seasonal trends

## Forex Trading & Business Use Cases

### International Business
- Monitor exchange rates affecting import/export costs
- Detect when rates move outside budget assumptions
- Alert on currency exposure that impacts profit margins
- Track rates for international payment timing

### Forex Trading
- Identify currency pairs showing unusual momentum
- Detect mean reversion opportunities in overextended moves
- Monitor for central bank intervention patterns
- Spot arbitrage opportunities in cross-currency rates

### Risk Management
- Track currency exposure across international portfolios
- Monitor hedging effectiveness for FX risk
- Detect when currency volatility spikes require action
- Alert on correlation breakdowns between currency pairs

### Economic Analysis
- Monitor currency strength as economic indicator
- Track real effective exchange rate changes
- Analyze currency impacts on inflation and trade
- Detect changes in international capital flows

## Integration with Anomstack Features

- **Dashboard**: Visualize exchange rates and anomaly scores in real-time
- **Alerts**: Get notifications for unusual currency movements
- **Change Detection**: Identify structural changes in currency behavior
- **LLM Alerts**: Use AI to analyze and explain forex market anomalies
- **Frequency Settings**: Adjust for forex market hours and your needs

## Environment Variables

Configure currency-specific settings:
```bash
# Custom currency pairs (comma-separated)
CURRENCY_BASE_CURRENCIES="eur,usd,gbp,jpy"
CURRENCY_TARGET_CURRENCIES="usd,eur,gbp,jpy,cad,aud,chf"

# API configuration
CURRENCY_API_BASE_URL="https://cdn.jsdelivr.net/npm/@fawazahmed0/currency-api"
CURRENCY_API_DATE="latest"  # or specific date like "2024-03-06"

# Alert thresholds for different scenarios
FOREX_RATE_ALERT_THRESHOLD=0.7
FOREX_VOLATILITY_ALERT_THRESHOLD=0.8

# Market hours consideration
FOREX_WEEKDAYS_ONLY=true
FOREX_MARKET_TIMEZONE="UTC"
```

## API Integration Details

**Currency API Endpoints Used**:
- **Single Currency**: `https://cdn.jsdelivr.net/npm/@fawazahmed0/currency-api@latest/v1/currencies/{base}.json`
- **Specific Pair**: `https://cdn.jsdelivr.net/npm/@fawazahmed0/currency-api@latest/v1/currencies/{base}/{target}.json`
- **Historical Data**: `https://cdn.jsdelivr.net/npm/@fawazahmed0/currency-api@{date}/v1/currencies/{base}.json`

**Example API Call**:
```
https://cdn.jsdelivr.net/npm/@fawazahmed0/currency-api@latest/v1/currencies/eur.json
```

**Response Format**:
```json
{
  "date": "2024-01-15",
  "eur": {
    "usd": 1.0925,
    "gbp": 0.8650,
    "jpy": 163.75,
    "cad": 1.4720,
    "aud": 1.6350
  }
}
```

**API Features**:
- **Free to Use**: No API key required
- **Historical Data**: Access to past exchange rates
- **Wide Coverage**: 150+ currencies supported
- **Daily Updates**: New rates published daily
- **Reliable**: Hosted on CDN for high availability

## Advanced Features

### Cross-Currency Arbitrage Detection
```python
# Detect triangular arbitrage opportunities
def detect_arbitrage(eur_usd, gbp_usd, eur_gbp):
    # Calculate implied EUR/GBP from USD cross rates
    implied_eur_gbp = eur_usd / gbp_usd
    actual_eur_gbp = eur_gbp
    
    # Calculate arbitrage spread
    spread = abs(implied_eur_gbp - actual_eur_gbp) / actual_eur_gbp * 100
    
    return {
        'metric_timestamp': datetime.now(),
        'metric_name': 'EUR_GBP_arbitrage_spread',
        'metric_value': spread
    }
```

### Currency Strength Index
```python
# Calculate currency strength across multiple pairs
def calculate_currency_strength(currency_rates):
    base_currencies = ['usd', 'eur', 'gbp', 'jpy']
    strength_index = {}
    
    for base in base_currencies:
        total_change = 0
        pair_count = 0
        
        for pair, rate in currency_rates.items():
            if pair.startswith(base + '_'):
                # Calculate percentage change from previous day
                change = calculate_daily_change(pair, rate)
                total_change += change
                pair_count += 1
        
        strength_index[base] = total_change / pair_count if pair_count > 0 else 0
    
    return [
        {
            'metric_timestamp': datetime.now(),
            'metric_name': f'{currency.upper()}_strength_index',
            'metric_value': strength
        }
        for currency, strength in strength_index.items()
    ]
```

### Volatility and Risk Metrics
```python
# Calculate currency volatility metrics
def calculate_forex_volatility(rate_history, window=30):
    import numpy as np
    
    # Calculate daily returns
    returns = np.diff(rate_history) / rate_history[:-1] * 100
    
    # Calculate volatility metrics
    volatility = np.std(returns[-window:]) if len(returns) >= window else 0
    var_95 = np.percentile(returns[-window:], 5) if len(returns) >= window else 0
    
    return [
        {
            'metric_timestamp': datetime.now(),
            'metric_name': 'EUR_USD_volatility_30d',
            'metric_value': volatility
        },
        {
            'metric_timestamp': datetime.now(),
            'metric_name': 'EUR_USD_var_95',
            'metric_value': abs(var_95)
        }
    ]
```

### Error Handling for Currency Data
```python
# Robust error handling for currency API calls
def safe_currency_request(base_currency, retries=3):
    for attempt in range(retries):
        try:
            url = f"https://cdn.jsdelivr.net/npm/@fawazahmed0/currency-api@latest/v1/currencies/{base_currency}.json"
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            if attempt == retries - 1:
                logger.error(f"Failed to get currency data for {base_currency}: {e}")
                return None
            time.sleep(2 ** attempt)  # Exponential backoff
```

## Forex Market Considerations

### Market Hours
- **24/5 Trading**: Forex markets trade 24 hours, 5 days a week
- **Weekend Gaps**: Markets close Friday evening, reopen Sunday evening
- **Holiday Impact**: Reduced liquidity during major holidays
- **Session Overlap**: Highest volatility during session overlaps

### Economic Factors
- **Interest Rates**: Primary driver of currency movements
- **Economic Data**: GDP, inflation, employment data impact rates
- **Central Bank Policy**: Monetary policy decisions and communication
- **Political Events**: Elections, policy changes, geopolitical risks

### Technical Factors
- **Carry Trades**: Interest rate differentials drive flows
- **Risk Sentiment**: Safe haven flows during market stress
- **Intervention**: Central bank intervention in currency markets
- **Correlation**: Currencies often move in correlated patterns

## Risk Considerations

- **Leverage Risk**: Forex markets often involve high leverage
- **Liquidity Risk**: Some currency pairs may have limited liquidity
- **Political Risk**: Government policies can significantly impact currencies
- **Economic Risk**: Economic data and central bank policies drive major moves
- **Correlation Risk**: Currency movements can be highly correlated during stress

This example provides a comprehensive foundation for currency exchange rate monitoring and anomaly detection, enabling sophisticated analysis of forex markets within the Anomstack ecosystem.

