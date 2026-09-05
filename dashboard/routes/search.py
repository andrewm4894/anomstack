"""Search, pagination and time-window updates for metric charts."""

from fasthtml.common import Div, P

from dashboard.app import app, rt
from dashboard.data import get_data, parse_time_spec
from dashboard.metric_results import metric_results


@rt("/batch/{batch_name}/search")
def search_metrics(batch_name: str, search: str = ""):
    app.state.search_term[batch_name] = search
    if batch_name not in app.state.stats_cache:
        app.state.calculate_metric_stats(batch_name)
    return metric_results(app.state, batch_name)


@rt("/batch/{batch_name}/load-more/{start_index}")
def load_more(batch_name: str, start_index: int):
    return metric_results(app.state, batch_name, start=start_index, append=True)


@rt("/batch/{batch_name}/update-n")
def update_window(batch_name: str, last_n: str = "90n"):
    try:
        # Validate and fetch before changing the selected window or clearing caches.
        parse_time_spec(last_n)
        df = get_data(app.state.specs_enabled[batch_name], last_n=last_n, ensure_timestamp=True)
    except ValueError as exc:
        return [
            *metric_results(app.state, batch_name),
            Div(
                P(str(exc), role="alert", cls="text-red-500 p-4"),
                id="window-error",
                hx_swap_oob="true",
            ),
        ]

    app.state.last_n[batch_name] = last_n
    app.state.clear_batch_cache(batch_name)
    app.state.df_cache[batch_name] = df
    app.state.calculate_metric_stats(batch_name)
    return [*metric_results(app.state, batch_name), Div(id="window-error", hx_swap_oob="true")]
