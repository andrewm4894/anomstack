"""Seed isolated demo batches; optionally backfill public USGS observations."""

import argparse
from datetime import datetime, timedelta, timezone
import json
from pathlib import Path

import duckdb
import pandas as pd
import requests
from seed_local_db import (
    generate_alerts_data,
    generate_scores_data,
    load_ingest_function,
    wrangle_df,
)
import yaml

ROOT = Path(__file__).resolve().parents[2]
LOCAL = ROOT / "tmpdata/local-stack"


def save_batch(connection, name, frame, source):
    """Replace only this dedicated local fixture table."""
    frame = frame.copy()
    frame["metric_batch"] = name
    frame["metadata"] = json.dumps({"source": source})
    table = f"metrics_{name}"
    connection.register("seed_frame", frame)
    connection.execute(f'CREATE OR REPLACE TABLE "{table}" AS SELECT * FROM seed_frame')
    config = {
        "metric_batch": name,
        "table_key": table,
        "alert_methods": "",
        "tholdalert_methods": "",
        "disable_llmalert": True,
        "disable_ingest": True,
        "dashboard_stale_metric_max_days_ago": 90,
    }
    folder = LOCAL / "metrics/fixtures"
    folder.mkdir(parents=True, exist_ok=True)
    (folder / f"{name}.yaml").write_text(yaml.safe_dump(config))
    print(f"{name}: {frame.metric_name.nunique()} metrics, {len(frame):,} rows ({source})")


def seed_synthetic(connection):
    for source in ("netdata", "currency"):
        name = f"demo_{source}"
        ingest = load_ingest_function(source)
        frames = []
        now = datetime.now(timezone.utc).replace(tzinfo=None)
        for hour in range(7 * 24):
            frame = ingest()
            frame["metric_timestamp"] = now - timedelta(hours=hour)
            frames.append(frame)
        metrics = wrangle_df(pd.concat(frames, ignore_index=True), name)
        scores = generate_scores_data(metrics)
        save_batch(
            connection,
            name,
            pd.concat([metrics, scores, generate_alerts_data(scores)], ignore_index=True),
            "Synthetic demo data; scores and alerts are simulated",
        )


def seed_public(connection):
    # A month of real events supports seven days of rolling 24-hour aggregates.
    url = "https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/all_month.geojson"
    response = requests.get(url, timeout=30)
    response.raise_for_status()
    payload = response.json()
    events = pd.DataFrame(
        [
            {"time": feature["properties"]["time"], "mag": feature["properties"]["mag"]}
            for feature in payload["features"]
            if feature["properties"].get("mag") is not None
        ]
    )
    events["time"] = pd.to_datetime(events["time"], unit="ms", utc=True)
    end = pd.to_datetime(payload["metadata"]["generated"], unit="ms", utc=True).floor("h")
    rows = []
    for timestamp in pd.date_range(end=end, periods=7 * 24, freq="h"):
        magnitudes = events.loc[
            (events.time > timestamp - pd.Timedelta(days=1)) & (events.time <= timestamp), "mag"
        ]
        for metric, value in {
            "earthquake_count_last_day": len(magnitudes),
            "earthquake_max_magnitude_last_day": magnitudes.max() if len(magnitudes) else 0,
            "earthquake_avg_magnitude_last_day": magnitudes.mean() if len(magnitudes) else 0,
        }.items():
            rows.append(
                {
                    "metric_timestamp": timestamp.tz_localize(None),
                    "metric_name": metric,
                    "metric_value": value,
                }
            )
    frame = wrangle_df(pd.DataFrame(rows), "public_earthquake")
    save_batch(connection, "public_earthquake", frame, url)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--public", action="store_true", help="Fetch real USGS history (requires internet)"
    )
    args = parser.parse_args()
    LOCAL.mkdir(parents=True, exist_ok=True)
    with duckdb.connect(str(LOCAL / "metrics.db")) as connection:
        seed_synthetic(connection)
        if args.public:
            seed_public(connection)


if __name__ == "__main__":
    main()
