# Dashboard

- [`app.py`](app.py): [FastHTML](https://fastht.ml/) dashboard for the project (WIP).
- [`charts.py`](charts.py): Chart manager for the dashboard.
- [`components/`](components/): Components for the dashboard.
- [`constants.py`](constants.py): Constants for the dashboard.
- [`data.py`](data.py): Data manager for the dashboard.
- [`routes/`](routes/): Routes for the dashboard.
- [`batch_stats.py`](batch_stats.py): Batch stats for the dashboard.
- [`static/`](static/): Static files for the dashboard.
- [`state.py`](state.py): State manager for the dashboard.
- [`utils.py`](utils.py): Utility functions for the dashboard.

## Running the dashboard

```bash
make dashboard
```

## Running the dashboard in the background

```bash
make dashboardd
```

To stop:

```bash
make kill-dashboardd
```

### Demo observability

The Fly demo sends browser analytics and server telemetry to Deepwell's PostHog
`dev` project (148051). `profiles/demo.env` holds the deployment configuration.

- `POSTHOG_FRONTEND_API_KEY`: browser analytics, exceptions, and session replay.
- `POSTHOG_API_KEY` / `POSTHOG_HOST`: existing LLM telemetry and server errors/logs.
- `POSTHOG_OBSERVABILITY_ENABLED=true`: opt in to dashboard request logs and server
  exception capture. Other installations remain opted out by default.

Application logs use OpenTelemetry HTTP export to `/i/v1/logs`, with service name
`anomstack-dashboard`. HTTP logs include method, route template, status, and duration;
request bodies, query strings, and headers are not included. This covers dashboard
application logs, not nginx, Dagster daemon, or machine-wide stdout.

Replay uses the project's recording settings and masks input values. The existing
Replay Vision scanners process eligible recordings and emit Signals. Those scanners
are shared with other apps using the dev project. Filter analytics/replays to
`anomstack-live-demo.fly.dev` when inspecting this demo.

Useful project links:
- https://us.posthog.com/project/148051/error_tracking
- https://us.posthog.com/project/148051/replay
- https://us.posthog.com/project/148051/replay-vision
- https://us.posthog.com/project/148051/logs

Setup references: https://posthog.com/docs/logs/installation/python and
https://posthog.com/docs/error-tracking/installation/python.
