# AnomStack

Painless open source anomaly detection for business metrics!

## Quick Start

```bash
# run locally
dagster dev -f anomstack/main.py
```

```bash
# run via docker
docker compose up
```

## Project Structure

- [`./anomstack`](./anomstack) source code for AnomStack.
- [`./metrics`](./metrics) sample metrics data. This is where you define your metrics (check out `examples` folder). Defaults params etc live in `defaults` folder.
