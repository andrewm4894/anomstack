import sys  # ruff: noqa: E402
import types
from datetime import datetime, timedelta, timezone

import pandas as pd
import pytest

from dashboard.batch_stats import format_time_ago

# Provide a minimal dashboard.app stub to avoid circular imports when importing charts
stub_app = types.ModuleType("dashboard.app")  # noqa: E402
stub_app.app = types.SimpleNamespace()  # noqa: E402
sys.modules.setdefault("dashboard.app", stub_app)  # noqa: E402

from dashboard.charts import ChartManager, ChartStyle  # noqa: E402
from dashboard.constants import DEFAULT_LAST_N  # noqa: E402
from dashboard.data import parse_time_spec  # noqa: E402
from dashboard.state import AppState  # noqa: E402


def test_parse_time_spec_variants():
    assert parse_time_spec("30n") == {"type": "n", "value": 30}
    assert parse_time_spec(15) == {"type": "n", "value": 15}
    assert parse_time_spec("24h") == {"type": "time", "value": timedelta(hours=24)}
    assert parse_time_spec("45m") == {"type": "time", "value": timedelta(minutes=45)}
    assert parse_time_spec("7d") == {"type": "time", "value": timedelta(days=7)}
    assert parse_time_spec(None) == {"type": "n", "value": DEFAULT_LAST_N}
    with pytest.raises(ValueError):
        parse_time_spec("abc")


def test_format_time_ago_outputs():
    now = datetime.now(timezone.utc)
    assert format_time_ago((now - timedelta(days=2)).isoformat()) == "2 days ago"
    assert format_time_ago((now - timedelta(hours=5)).isoformat()) == "5 hours ago"
    thirty_min_ago = (now - timedelta(minutes=30)).isoformat()
    assert format_time_ago(thirty_min_ago) == "30 minutes ago"
    assert format_time_ago(now.isoformat()) == "just now"


def test_chart_manager_config_and_colors():
    config = ChartManager.get_chart_config()
    expected_keys = [
        "displayModeBar",
        "displaylogo",
        "modeBarButtonsToRemove",
        "responsive",
        "scrollZoom",
        "staticPlot",
    ]
    for key in expected_keys:
        assert key in config
    assert config["displaylogo"] is False

    light = ChartStyle.get_colors(False)
    dark = ChartStyle.get_colors(True)
    assert light["background"] == "white"
    assert dark["background"] == "#1a1a1a"
    assert light != dark


def test_app_state_cache_management_and_stats():
    state = AppState()
    batch = "b1"
    df = pd.DataFrame({
        "metric_name": ["m1", "m1", "m2", "m2"],
        "metric_alert": [1, 0, 0, 1],
        "metric_score": [0.5, 0.7, 0.3, 0.2],
        "thumbsup_sum": [1, 2, 3, 4],
        "thumbsdown_sum": [0, 1, 2, 3],
    })
    state.df_cache[batch] = df

    state.calculate_metric_stats(batch)

    stats = state.stats_cache[batch]
    assert len(stats) == 2
    assert stats[0]["metric_name"] == "m1"
    assert stats[0]["anomaly_rate"] == pytest.approx(0.5)
    assert stats[0]["avg_score"] == pytest.approx(0.6)

    state.clear_batch_cache(batch)
    assert batch not in state.df_cache
    assert batch not in state.chart_cache
    assert batch not in state.stats_cache
