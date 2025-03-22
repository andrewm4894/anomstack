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
