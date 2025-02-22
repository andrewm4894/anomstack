# Prometheus

Ingest some metrics from [CoinDesk](https://www.coindesk.com) using a custom Python ingest function ([`coindesk.py`](./coindesk/coindesk.py)).

Example api call [`https://data-api.coindesk.com/index/cc/v1/latest/tick?market=cadli&instruments=BTC-USD,ETH-USD&apply_mapping=true`](https://data-api.coindesk.com/index/cc/v1/latest/tick?market=cadli&instruments=BTC-USD,ETH-USD&apply_mapping=true)