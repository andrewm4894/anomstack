# Anomstack

Painless open source anomaly detection for business metrics! 📈📉🚀

![image](https://github.com/andrewm4894/anomstack/assets/2178292/30b05941-a53b-4e1f-9ac9-ed082cf6be40)

## What is Anomstack?

Anomstack is a little ("lightweight" - README buzzword bingo alert!) data app built on top of [dagster](https://dagster.io/) that lets you easily get great anomaly detection (using [`pyod`](https://pyod.readthedocs.io/en/latest/)) for your business metrics.

1. Define your metrics in a `.sql` file and corresponding config in a `.yaml` file.
1. Run Anomstack and it will automatically ingest, train, score, and alert on your metrics and detect anomalies (alerts via email/slack etc.).

## Project Structure

- [`./anomstack`](./anomstack) source code for Anomstack.
- [`./metrics`](./metrics) metrics `.sql` and `.yaml` configuration files. This is where you define your metrics (check out [`examples`](./metrics/examples/) folder). Defaults params etc live in [`defaults`](./metrics/defaults/) folder in [`defaults.yaml`](./metrics/defaults/defaults.yaml).

## Quick Start

Below are some quick start instructions for getting up and running with AnomStack and a local db using duckdb.

For proper use you would need to set up all your metrics and environment variables etc, but this should get you started.

### Docker

To get started with AnomStack, you can run it locally via docker compose.

```bash
# clone repo
git clone https://github.com/andrewm4894/anomstack.git
# cd into project
cd anomstack
# generate your .env file based on example
cp .example.env .env
# run docker compose up to start anomstack
docker compose up
# anomstack should now be running on port 3000
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
# anomstack should now be running on port 3000
```

## Adding Your Metrics

To add metrics, you can add them to the `metrics` folder. You can see some examples in the [`metrics/examples`](./metrics/examples/) folder.

You can customize the default params for your metrics in the [`metrics/defaults`](./metrics/defaults/) folder.

Environment variables for your metrics can be set in the `.env` file (see [`.example.env`](.example.env) for examples and comments) or in the `docker-compose.yml` file.
