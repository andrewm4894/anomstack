# Anomstack

[![Open in GitHub Codespaces](https://github.com/codespaces/badge.svg)](https://codespaces.new/andrewm4894/anomstack)

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Painless open source anomaly detection for business metrics! 📈📉🚀

- [What is Anomstack?](#what-is-anomstack)
  - [How it works](#how-it-works)
- [Project structure](#project-structure)
- [Quickstart](#quickstart)
  - [GitHub Codespaces](#github-codespaces)
  - [Docker](#docker)
  - [Local Python env](#local-python-env)
- [Adding your metrics](#adding-your-metrics)
- [Concepts](#concepts)

Supported databases for your metrics to live in and be queried from:

<table>
    <thead>
        <tr>
            <th align="center">BigQuery</th>
            <th align="center">Snowflake</th>
            <th align="center">DuckDB</th>
            <th align="center">Redshift</th>
        </tr>
    </thead>
    <tbody>
        <tr>
            <td align="center">✅</td>
            <td align="center">✅</td>
            <td align="center">✅</td>
            <td align="center">🚧</td>
        </tr>
    </tbody>
</table>

Supported storage for your trained models:

<table>
    <thead>
        <tr>
            <th align="center">Local</th>
            <th align="center">GCS</th>
            <th align="center">S3</th>
            <th align="center">Azure Blob</th>
        </tr>
    </thead>
    <tbody>
        <tr>
            <td align="center">✅</td>
            <td align="center">✅</td>
            <td align="center">🚧</td>
            <td align="center">🚧</td>
        </tr>
    </tbody>
</table>

## What is Anomstack?

Anomstack is a lightweight (README buzzword bingo alert!) data app built on top of [dagster](https://dagster.io/) (for orchestration) that lets you easily get great anomaly detection (using [`pyod`](https://pyod.readthedocs.io/en/latest/) for the ML stuff) for your business metrics (whatever data platform you use) with as little pain as physically possible.

It's similar in scope and goal to this [Airflow Anomaly Detection provider](https://github.com/andrewm4894/airflow-provider-anomaly-detection) i also made, but easier to get going since does not require airflow and so easier to set up and run yourself.

### How it works

1. Define your metrics (part of a ["metric batch"](#concepts)) in a `.sql` file and corresponding config in a `.yaml` file.
1. Run Anomstack and it will automatically ingest, train, score, and alert (["jobs"](#concepts)) on your metrics and detect anomalies (alerts via email/slack etc.).
1. Get alerts when metrics look anomalous.

## Project structure

- [`./anomstack`](./anomstack) source code for Anomstack.
- [`./metrics`](./metrics) metrics `.sql` and `.yaml` configuration files. This is where you define your metrics (check out [`examples`](./metrics/examples/) folder). Defaults params etc live in [`defaults`](./metrics/defaults/) folder in [`defaults.yaml`](./metrics/defaults/defaults.yaml).

## Quickstart

Below are some quick start instructions for getting up and running with Anomstack and a local db using duckdb and some example metrics.

For proper use you would need to set up all your metrics and environment variables etc, but this should get you started.

By default Anomstack will run on port 3000, so you can go to http://localhost:3000 to see the dagster UI. You can then enable the jobs you want to run and see them run in the UI.

*Note*: you will need to wait for it to run a dozen or so ingest jobs before there is enough data for train, score and alert jobs to run successfully.

### GitHub Codespaces

[![Open in GitHub Codespaces](https://github.com/codespaces/badge.svg)](https://codespaces.new/andrewm4894/anomstack)

You can run Anomstack using docker in a [GitHub Codespace](https://docs.github.com/en/codespaces). This is a great way to get started and familiar with Anomstack without having to install or run anything locally.

You can see the [`.devcontainer`](./.devcontainer) folder for the config used to run Anomstack in a codespace and the post create script [`post_create_command.sh`](.devcontainer/post_create_command.sh) for the commands the devcontainer will run to get Anomstack up and running.

### Docker

To get started with Anomstack, you can run it via docker compose.

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

### Local Python env

You can also run Anomstack locally via a python virtual env.

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
pip3 install -r requirements.txt
# cp example env file
cp .example.env .env
# run locally
dagster dev -f anomstack/main.py
# anomstack should now be running on port 3000
```

## Adding your metrics

To add metrics, you can add them to the `metrics` folder. You can see some examples in the [`metrics/examples`](./metrics/examples/) folder.

You can customize the default params for your metrics in the [`metrics/defaults`](./metrics/defaults/) folder.

Environment variables for your metrics can be set in the `.env` file (see [`.example.env`](.example.env) for examples and comments) or in the `docker-compose.yml` file.

## Concepts

- "**Metric Batch**": You configure metric batches in Anomstack. A metric batch is a collection of metrics that you want to run together and with its own seperate set of parameters. Of course a metric batch can contain just one metric if you want but typically it makes more sense to group metrics in ways that make sense for you.
- "**Jobs**": At the core Anomstack runs a few jobs for each metric batch. These jobs are:
  - "Ingest" ([`ingest.py`](./anomstack/jobs/ingest.py)): This job runs the sql query for the metric batch and ingests the data into the database.
  - "Train" ([`train.py`](./anomstack/jobs/train.py)): This job trains a model for each metric.
  - "Score" ([`score.py`](./anomstack/jobs/score.py)): This job scores metrics using the latest trained model for each metric.
  - "Alert" ([`alert.py`](./anomstack/jobs/alert.py)): This job alerts you when the metric looks anomalous.
