# Anomstack

Painless open source anomaly detection for business metrics!

## Project Structure

- [`./anomstack`](./anomstack) source code for Anomstack.
- [`./metrics`](./metrics) sample metrics data. This is where you define your metrics (check out `examples` folder). Defaults params etc live in `defaults` folder.

## Quick Start

### Docker

To get started with AnomStack, you can run it locally via docker compose.

```bash
git clone https://github.com/andrewm4894/anomstack.git
cd anomstack
cp .example.env .env
docker compose up
```

### Local Python Env

You can also run AnomStack locally via a python virtual env.

```bash
# git clone
git clone https://github.com/andrewm4894/anomstack.git
# cd into project
cd anomstack
# make virtual env
python3 -m venv .venv
# activate virtual env
source .venv/bin/activate
# install deps
pip install -r requirements.txt
# cp example env file
cp .example.env .env
# run locally
dagster dev -f anomstack/main.py
```

## Adding Your Metrics

To add metrics, you can add them to the `metrics` folder. You can see some examples in the [`metrics/examples`](./metrics/examples/) folder.

You can customize the default params for your metrics in the [`metrics/defaults`](./metrics/defaults/) folder.

Environment variables for your metrics can be set in the `.env` file (see [`.example.env`](.example.env) for examples and comments) or in the `docker-compose.yml` file.
