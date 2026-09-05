# Local development

Use Python 3.12 and [uv](https://docs.astral.sh/uv/). From the repository root:

```sh
make setup-local
make stack
```

The dashboard runs at http://localhost:8080 and Dagster at http://localhost:3000.
Keep the command running; Ctrl-C stops both services and their child processes.
The first start seeds 72 hours of synthetic metrics, scores, and alerts. Later starts
reuse the database. Runtime files live in ignored `tmpdata/local-stack/`.

This setup uses the `python_ingest_simple` example, local DuckDB, and separate
Dagster history. It does not load the repository's `.env`; email and Slack alert
methods are empty. Schedules start stopped. Start jobs manually in Dagster as needed.
The example configuration is refreshed from the repository on each start.

Dashboard code is loaded from the working tree. Restart `make stack` after changes.
For the existing environment and full metric configuration, the older `make local`
and dashboard targets remain available.

## More dashboard data

Stop `make stack`, then seed additional isolated fixtures and restart:

```sh
.venv/bin/python scripts/development/seed_stack_data.py --public
make stack
```

This adds `demo_netdata` (51 metrics) and `demo_currency` (85 metrics), each
with seven days of hourly synthetic values, simulated scores, and alerts.
The `--public` option also adds `public_earthquake`: seven days of hourly,
rolling 24-hour earthquake counts and magnitudes reconstructed from the USGS
monthly event feed. Those are real observations with no fabricated anomaly
scores. Omit `--public` for an entirely offline seed.

Rerunning replaces only these fixture tables. The original example and Dagster
history are preserved. Fixture configs and the database stay under ignored
`tmpdata/local-stack/`; they are dashboard fixtures, not scheduled Dagster jobs.
Public data requires an internet connection but no API key. Source information
is stored in each row's metadata.

## Validation and dependency updates

```sh
make test-local
cd docs
npm ci
npm run build
```

`make test-local` uses the CI test mode, which skips live third-party API checks.
To run those as well, use `.venv/bin/python -m pytest tests/`; some require credentials.

The Python runtime and development dependency set is recorded in `constraints.txt` and used by local
setup, CI, and Docker builds. To resolve newer compatible versions:

```sh
make update-dependencies
make setup-local
make test-local
```

Review compatibility and smoke-test both services before releasing. The docs site
uses npm and `package-lock.json` as its dependency lock. Use Node.js 24 LTS.
