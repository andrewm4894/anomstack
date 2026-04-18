"""
dashboard/presentation.py

Presentation helpers for the dashboard UI.
"""

from dashboard.app import app


def format_batch_name(batch_name: str) -> str:
    """Convert internal batch ids into friendlier display labels."""
    return batch_name.replace("_", " ").replace("-", " ").strip().title()


def format_metric_count(count: int) -> str:
    """Return a metric count label with simple pluralization."""
    return f"{count} metric" if count == 1 else f"{count} metrics"


def get_filtered_metric_stats(batch_name: str) -> list[tuple[int, dict]]:
    """Return metric stats together with their original indices after filtering."""
    stats = app.state.stats_cache.get(batch_name, [])
    indexed_stats = list(enumerate(stats))

    search_term = app.state.search_term.get(batch_name, "").strip().lower()
    if not search_term:
        return indexed_stats

    return [
        (index, stat)
        for index, stat in indexed_stats
        if search_term in stat["metric_name"].lower()
    ]


def summarize_batches(batch_stats: dict, active_batch_names: list[str]) -> dict:
    """Create summary stats for the homepage overview cards."""
    active_stats = [batch_stats[name] for name in active_batch_names]
    return {
        "active_batches": len(active_batch_names),
        "configured_batches": len(batch_stats),
        "tracked_metrics": sum(stat["unique_metrics"] for stat in active_stats),
        "alerts": int(sum(stat["alert_count"] for stat in active_stats)),
    }
