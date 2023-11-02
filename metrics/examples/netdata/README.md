# Netdata

Ingest some metrics from some [Netdata demo servers](https://learn.netdata.cloud/docs/live-demo) using a custom Python ingest function ([`netdata.py`](./netdata/netdata.py)).

Example api call for network traffic over the last 10 minutes: [`https://london.my-netdata.io/api/v1/data?chart=system.net&after=-600&before=0&points=1`](https://london.my-netdata.io/api/v1/data?chart=system.net&after=-600&before=0&points=1)
