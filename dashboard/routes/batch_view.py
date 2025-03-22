import pandas as pd
from fasthtml.common import *
from monsterui.all import *
from dashboard.app import app, rt, log
from dashboard.components import create_controls
from dashboard.charts import ChartManager
from dashboard.data import get_data
from dashboard.constants import DEFAULT_LAST_N, DEFAULT_LOAD_N_CHARTS


def _get_batch_data(batch_name: str):
    """Get batch data, either from cache or by fetching."""
    try:
        return get_data(app.state.specs_enabled[batch_name],
                        last_n=app.state.last_n.get(batch_name,
                                                    DEFAULT_LAST_N),
                        ensure_timestamp=True)
    except Exception as e:
        log.error(f"Error getting data for batch {batch_name}: {e}")
        return pd.DataFrame(
            data=[],
            columns=["metric_name", "metric_timestamp", "metric_value"])


@rt("/batch/{batch_name}")
def get_batch_view(batch_name: str,
                   initial_load: int = DEFAULT_LOAD_N_CHARTS):
    """Get the batch view."""
    if batch_name not in app.state.df_cache or batch_name not in app.state.stats_cache:
        app.state.df_cache[batch_name] = _get_batch_data(batch_name)
        app.state.calculate_metric_stats(batch_name)

    metric_stats = app.state.stats_cache[batch_name]
    remaining_metrics = len(metric_stats) - initial_load

    script = Script(f"""
        document.querySelectorAll('.top-nav li').forEach(li => {{
            li.classList.remove('uk-active');
            if (li.querySelector('a').textContent.trim() === '{batch_name}') {{
                li.classList.add('uk-active');
            }}
        }});
        window.scrollTo({{ top: 0, behavior: 'smooth' }});
    """)

    load_next = min(DEFAULT_LOAD_N_CHARTS, remaining_metrics)
    return Div(
        create_controls(batch_name),
        Div(
            *[
                ChartManager.create_chart_placeholder(stat["metric_name"], i,
                                                      batch_name)
                for i, stat in enumerate(metric_stats[:initial_load])
            ],
            id="charts-container",
            cls=f"grid grid-cols-{2 if app.state.two_columns else 1} gap-4",
        ),
        Div(
            Button(
                f"Load next {load_next} of {remaining_metrics}",
                hx_get=f"/batch/{batch_name}/load-more/{initial_load}",
                hx_target="#charts-container",
                hx_swap="beforeend",
                hx_indicator="#loading",
                cls=ButtonT.secondary,
                style="width: 100%; margin-top: 1rem;",
                disabled=remaining_metrics <= 0,
            ),
            id="load-more-container",
        ),
        script,
    )


@rt("/batch/{batch_name}/chart/{chart_index}")
def get(batch_name: str, chart_index: int):
    """Get chart for a batch and index."""
    df = app.state.df_cache[batch_name]
    metric_stats = app.state.stats_cache[batch_name]
    metric_name = metric_stats[chart_index]["metric_name"]
    anomaly_rate = metric_stats[chart_index]["anomaly_rate"]
    avg_score = metric_stats[chart_index]["avg_score"]

    if batch_name not in app.state.chart_cache:
        app.state.chart_cache[batch_name] = {}

    if chart_index not in app.state.chart_cache[batch_name]:
        df_metric = df[df["metric_name"] == metric_name]
        fig = ChartManager.create_chart(df_metric, chart_index)
        app.state.chart_cache[batch_name][chart_index] = fig

    return Card(
        Style("""
            .uk-card-header { padding: 1rem; }
            .uk-card-body { padding: 1rem; }
        """),
        Safe(app.state.chart_cache[batch_name][chart_index]),
        header=Div(
            H4(metric_name, cls="mb-1"),
            DivLAligned(
                P(f"Anomaly Rate: {anomaly_rate:.1%}",
                  cls="text-sm text-muted-foreground"),
                P(f"Avg Score: {avg_score:.1%}",
                  cls="text-sm text-muted-foreground"),
                style="gap: 1rem;",
            ),
        ),
        id=f"chart-{chart_index}",
        cls="mb-1",
    )
