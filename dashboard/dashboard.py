import logging

from fasthtml.common import *
from monsterui.all import *
from fasthtml.svg import *
from utils import (
    plot_time_series,
    get_data,
    get_metric_batches,
)

from anomstack.config import specs
from anomstack.jinja.render import render
from starlette.requests import Request

log = logging.getLogger("anomstack")

app, rt = fast_app(
    hdrs=(
        Theme.blue.headers(),
        Script(src="https://cdn.plot.ly/plotly-2.32.0.min.js"),
        Link(rel="icon", type="image/svg+xml", href="data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIyNCIgaGVpZ2h0PSIyNCIgdmlld0JveD0iMCAwIDI0IDI0IiBmaWxsPSJub25lIiBzdHJva2U9ImN1cnJlbnRDb2xvciIgc3Ryb2tlLXdpZHRoPSIyIiBzdHJva2UtbGluZWNhcD0icm91bmQiIHN0cm9rZS1saW5lam9pbj0icm91bmQiIGNsYXNzPSJsdWNpZGUgbHVjaWRlLWNoYXJ0LWxpbmUiPjxwYXRoIGQ9Ik0zIDN2MTZhMiAyIDAgMCAwIDIgMmgxNiIvPjxwYXRoIGQ9Im0xOSA5LTUgNS00LTQtMyAzIi8+PC9zdmc+"),
        Style("""
            /* Light mode defaults */
            body {
                background-color: #ffffff;
                color: #1a1a1a;
                transition: all 0.3s ease;
            }
            
            .loading-indicator {
                display: none;
                position: fixed;
                top: 1rem;
                right: 1rem;
                z-index: 1000;
            }
            .loading-indicator .htmx-indicator {
                padding: 0.5rem 1rem;
                background: #fff;
                border-radius: 4px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            }
            .loading-indicator .htmx-indicator.htmx-request {
                display: inline-block;
            }
            .top-nav {
                border-bottom: 1px solid #e5e7eb;
                background: #f8fafc;
            }
            .top-nav li {
                margin: 0;
            }
            .top-nav li a {
                font-weight: 500;
                color: #4b5563;
                transition: all 0.2s;
            }
            .top-nav li a:hover {
                color: #1e40af;
                background: #f1f5f9;
            }
            .top-nav li.uk-active a {
                color: #1e40af;
                border-bottom: 2px solid #1e40af;
            }
            
            /* Dark mode styles */
            body.dark-mode {
                background-color: #1a1a1a;
                color: #e5e7eb;
            }
            
            body.dark-mode .uk-card {
                background-color: #262626;
                border-color: #404040;
                color: #e5e7eb;
            }
            
            body.dark-mode .uk-card-header {
                border-color: #404040;
            }
            
            body.dark-mode .top-nav {
                background: #262626;
                border-color: #404040;
            }
            
            body.dark-mode .top-nav li a {
                color: #e5e7eb;
            }
            
            body.dark-mode .top-nav li a:hover {
                color: #60a5fa;
                background: #333333;
            }
            
            body.dark-mode .top-nav li.uk-active a {
                color: #60a5fa;
                border-color: #60a5fa;
            }
            
            body.dark-mode .uk-input,
            body.dark-mode .uk-select,
            body.dark-mode .uk-textarea,
            body.dark-mode .uk-button-secondary {
                background-color: #333333;
                border-color: #404040;
                color: #e5e7eb;
            }
            
            body.dark-mode .uk-dropdown {
                background-color: #262626;
                border-color: #404040;
                color: #e5e7eb;
            }
            
            body.dark-mode .uk-dropdown li a {
                color: #e5e7eb;
            }
            
            body.dark-mode .uk-dropdown li a:hover {
                background-color: #333333;
            }
            
            body.dark-mode .loading-indicator .htmx-indicator {
                background: #262626;
                color: #e5e7eb;
                box-shadow: 0 2px 4px rgba(255,255,255,0.1);
            }
            
            /* Ensure text colors are readable in dark mode */
            body.dark-mode h1,
            body.dark-mode h2,
            body.dark-mode h3,
            body.dark-mode h4,
            body.dark-mode h5,
            body.dark-mode h6,
            body.dark-mode p {
                color: #e5e7eb;
            }
            
            body.dark-mode .text-muted-foreground,
            body.dark-mode .uk-text-muted {
                color: #9ca3af;
            }
            
            /* Update dark mode button styles */
            body.dark-mode .uk-button-default,
            body.dark-mode .uk-button-secondary {
                background-color: #1f1f1f;  /* Darker background */
                color: #e5e7eb;
                border-color: #2d2d2d;  /* Slightly lighter border */
            }
            
            body.dark-mode .uk-button-default:hover,
            body.dark-mode .uk-button-secondary:hover {
                background-color: #2d2d2d;  /* Darker hover state */
                color: #ffffff;
                border-color: #404040;
            }
            
            body.dark-mode .uk-button-primary {
                background-color: #0f2d66;  /* Darker blue */
                color: #ffffff;
                border: none;
            }
            
            body.dark-mode .uk-button-primary:hover {
                background-color: #1a3f80;  /* Slightly lighter on hover */
            }
        """),
    ),
    debug=True, 
    log=log
)

# Set up toasts
setup_toasts(app, duration=3)

# Constants
DEFAULT_LOAD_N_CHARTS = 10
DEFAULT_ALERT_MAX_N = 30

class DashboardState:
    def __init__(self):
        self.specs = specs
        self.metric_batches = get_metric_batches()
        if not self.metric_batches:
            log.warning("No metric batches found from Dagster. Is Dagster running?")
            self.metric_batches = []
        self.specs_enabled = {batch: specs[batch] for batch in self.metric_batches}
        self.df_cache = {}
        self.chart_cache = {}
        self.stats_cache = {}
        self.small_charts = True
        self.dark_mode = False
        self.two_columns = True
        self.alert_max_n = {}
    
    def clear_batch_cache(self, batch_name):
        self.df_cache.pop(batch_name, None)
        self.chart_cache.pop(batch_name, None)
        self.stats_cache.pop(batch_name, None)
    
    def calculate_metric_stats(self, batch_name):
        df = self.df_cache[batch_name]
        metric_stats = []
        for metric_name in df["metric_name"].unique():
            df_metric = df[df["metric_name"] == metric_name]
            metric_stats.append({
                "metric_name": metric_name,
                "anomaly_rate": df_metric["metric_alert"].mean() if df_metric["metric_alert"].sum() > 0 else 0,
                "avg_score": df_metric["metric_score"].mean() if df_metric["metric_score"].sum() > 0 else 0
            })
        metric_stats.sort(key=lambda x: (-x["anomaly_rate"], -x["avg_score"]))
        self.stats_cache[batch_name] = metric_stats

class ChartManager:
    @staticmethod
    def create_chart(df_metric, metric_name, chart_index):
        return plot_time_series(
            df_metric, 
            metric_name,
            small_charts=app.state.small_charts,
            dark_mode=app.state.dark_mode
        ).to_html(
            div_id=f"plotly-chart-{chart_index}",
            include_plotlyjs=False,
            full_html=False,
            config={
                "displayModeBar": False,
                "displaylogo": False,
                "modeBarButtonsToRemove": ["zoom2d", "pan2d", "select2d", "lasso2d", "zoomIn2d", "zoomOut2d", "autoScale2d", "resetScale2d"],
                "responsive": True,
                "scrollZoom": False,
                "staticPlot": False,
            }
        )

    @staticmethod
    def create_chart_placeholder(metric_name, index, batch_name):
        return Card(
            Div(
                DivLAligned(
                    Loading((LoadingT.spinner, LoadingT.sm)),
                    P(f"Loading {metric_name}...", cls=TextPresets.muted_sm),
                    cls="space-x-2"
                ),
                cls="p-4"
            ),
            id=f"chart-{index}",
            hx_get=f"/batch/{batch_name}/chart/{index}",
            hx_trigger="load",
            hx_swap="outerHTML"
        )

app.state = DashboardState()

@rt
def index(request: Request):
    # Check if this is an HTMX request
    is_htmx = request.headers.get("HX-Request") == "true"
    
    # Add dark mode class to body if enabled
    script = Script(f"""
        if ({'true' if app.state.dark_mode else 'false'}) {{
            document.body.classList.add('dark-mode');
        }}
    """)
    
    # Get batch stats
    batch_stats = {}
    for batch_name in app.state.metric_batches:
        if batch_name not in app.state.df_cache:
            df = get_data(app.state.specs_enabled[batch_name], alert_max_n=DEFAULT_ALERT_MAX_N)
            app.state.df_cache[batch_name] = df
        else:
            df = app.state.df_cache[batch_name]
        
        latest_timestamp = df['metric_timestamp'].max() if not df.empty else 'No data'
        if latest_timestamp != 'No data':
            from datetime import datetime
            # Parse the ISO format timestamp and format it to show date and time
            dt = datetime.fromisoformat(latest_timestamp.replace('Z', '+00:00'))
            latest_timestamp_str = dt.strftime('%Y-%m-%d %H:%M:%S')
            
            # Calculate time difference
            now = datetime.now(dt.tzinfo)
            diff_seconds = (now - dt).total_seconds()
            
            # Choose appropriate time unit
            if diff_seconds < 3600:  # Less than 1 hour
                minutes_ago = round(diff_seconds / 60, 1)
                time_ago_str = f"({minutes_ago:.1f} minute{'s' if minutes_ago != 1 else ''} ago)"
            elif diff_seconds < 86400:  # Less than 24 hours
                hours_ago = round(diff_seconds / 3600, 1)
                time_ago_str = f"({hours_ago:.1f} hour{'s' if hours_ago != 1 else ''} ago)"
            else:  # Days or more
                days_ago = round(diff_seconds / 86400, 1)
                time_ago_str = f"({days_ago:.1f} day{'s' if days_ago != 1 else ''} ago)"
            
            latest_timestamp = f"{latest_timestamp_str} {time_ago_str}"
        
        batch_stats[batch_name] = {
            'unique_metrics': len(df['metric_name'].unique()),
            'latest_timestamp': latest_timestamp
        }
    
    main_content = Div(
        Card(
            DivLAligned(
                H2("Anomstack",P("Painless open source anomaly detection for your metrics 📈📉🚀", cls=TextPresets.muted_sm), cls="mb-2"),
                A(
                    DivLAligned(UkIcon("github")),
                    href="https://github.com/andrewm4894/anomstack",
                    target="_blank",
                    cls="uk-button uk-button-secondary",
                    uk_tooltip="View on GitHub"
                ),
                style="justify-content: space-between;",
                cls="mb-6"
            ),
            # Show warning if no metric batches
            Div(
                DivLAligned(
                    UkIcon("alert-triangle"),
                    P("No metric batches found. Is Dagster running?", cls=TextPresets.muted_sm),
                    cls="space-x-2 p-4 bg-yellow-50 text-yellow-700 rounded-md"
                ),
                cls="mb-6"
            ) if not app.state.metric_batches else None,
            Grid(
                *[Card(
                    DivLAligned(
                        Div(
                            H4(batch_name, cls="mb-2"),
                            DivLAligned(
                                Div(
                                    DivLAligned(
                                        UkIcon("activity", cls="text-blue-500"),
                                        P(f"{batch_stats[batch_name]['unique_metrics']} metrics", cls=TextPresets.muted_sm),
                                        cls="space-x-2"
                                    ),
                                    DivLAligned(
                                        UkIcon("clock", cls="text-green-500"),
                                        P(f"{batch_stats[batch_name]['latest_timestamp']}", cls=TextPresets.muted_sm),
                                        cls="space-x-2"
                                    ),
                                    cls="space-y-2"
                                )
                            )
                        ),
                        Button(
                            "View Metrics",
                            hx_get=f"/batch/{batch_name}",
                            hx_push_url=f"/batch/{batch_name}",
                            hx_target="#main-content",
                            hx_indicator="#loading",
                            cls=ButtonT.primary
                        ),
                        style="justify-content: space-between;",
                        cls="flex-row items-center"
                    ),
                    cls="p-6 hover:border-primary transition-colors duration-200"
                ) for batch_name in app.state.metric_batches],
                cols=3,
                gap=4
            ) if app.state.metric_batches else None,
            cls="p-6"
        ),
        id="main-content"
    )

    # For HTMX requests, return only the main content
    if is_htmx:
        return main_content

    # For full page loads, return the complete layout
    return (
        Title("Anomstack"),
        script,
        Div(
            Safe('<span class="htmx-indicator">Loading...</span>'),
            id="loading", 
            cls="loading-indicator"
        ),
        main_content
    )


@rt("/batch/{batch_name}")
def get_batch_view(batch_name: str, session, initial_load: int = DEFAULT_LOAD_N_CHARTS):
    # First, ensure we have the data and stats calculated
    if batch_name not in app.state.df_cache:
        app.state.df_cache[batch_name] = get_data(
            app.state.specs_enabled[batch_name], 
            alert_max_n=DEFAULT_ALERT_MAX_N
        )
        app.state.calculate_metric_stats(batch_name)
    elif batch_name not in app.state.stats_cache:
        app.state.calculate_metric_stats(batch_name)

    metric_stats = app.state.stats_cache[batch_name]
    total_metrics = len(metric_stats)
    remaining_metrics = total_metrics - initial_load
    
    script = Script(f"""
        document.querySelectorAll('.top-nav li').forEach(li => {{
            li.classList.remove('uk-active');
            if (li.querySelector('a').textContent.trim() === '{batch_name}') {{
                li.classList.add('uk-active');
            }}
        }});
        window.scrollTo({{ top: 0, behavior: 'smooth' }});
    """)

    # Update the load more button text
    load_next = min(DEFAULT_LOAD_N_CHARTS, remaining_metrics)
    return Div(
        _create_controls(batch_name),
        Div(
            *[ChartManager.create_chart_placeholder(
                stat['metric_name'], i, batch_name
            ) for i, stat in enumerate(metric_stats[:initial_load])],
            id="charts-container",
            cls=f"grid grid-cols-{2 if app.state.two_columns else 1} gap-4"
        ),
        # Load More button with updated text
        Div(
            Button(
                f"Load next {load_next} of {remaining_metrics}",
                hx_get=f"/batch/{batch_name}/load-more/{initial_load}",
                hx_target="#charts-container",
                hx_swap="beforeend",
                hx_indicator="#loading",
                cls=ButtonT.secondary,
                style="width: 100%; margin-top: 1rem;",
                disabled=remaining_metrics <= 0
            ),
            id="load-more-container"
        ),
        script
    )

def _create_controls(batch_name):
    settings_dropdown = DropDownNavContainer(
        NavHeaderLi("Chart Settings"),
        Li(A(
            DivLAligned(
                "Small Charts",
                P(),
                P("On" if app.state.small_charts else "Off", cls=TextPresets.muted_sm)
            ),
            hx_post=f"/batch/{batch_name}/toggle-size",
            hx_target="#main-content"
        )),
        Li(A(
            DivLAligned(
                "Two Columns",
                P(),
                P("On" if app.state.two_columns else "Off", cls=TextPresets.muted_sm)
            ),
            hx_post=f"/batch/{batch_name}/toggle-columns",
            hx_target="#main-content"
        )),
        NavDividerLi(),
        Li(A(
            DivLAligned(
                "Dark Mode",
                P(),
                P("On" if app.state.dark_mode else "Off", cls=TextPresets.muted_sm)
            ),
            hx_post=f"/batch/{batch_name}/toggle-theme",
            hx_target="#main-content"
        )),
    )

    batches_dropdown = DropDownNavContainer(
        NavHeaderLi("Metric Batches"),
        *[Li(A(
            batch_name,
            hx_get=f"/batch/{batch_name}",
            hx_push_url=f"/batch/{batch_name}",
            hx_target="#main-content",
            hx_indicator="#loading",
            cls=f"{'uk-active' if batch_name == batch_name else ''}"
        )) for batch_name in app.state.metric_batches],
    )

    return Card(
        DivFullySpaced(
            Div(
                Button(
                    DivLAligned(UkIcon("home")),
                    hx_get="/",
                    hx_push_url="/",
                    hx_target="#main-content",
                    cls=ButtonT.secondary
                ),
                Button(
                    DivLAligned(UkIcon("refresh-ccw")),
                    hx_get=f"/batch/{batch_name}/refresh", 
                    hx_target="#main-content",
                    cls=ButtonT.secondary,
                    uk_tooltip="Refresh metrics data"
                ),
                _create_search_form(batch_name),
                _create_alert_n_form(batch_name),
                style="display: flex; align-items: center; gap: 0.5rem;"
            ),
            Div(
                Button(
                    DivLAligned(UkIcon("menu")),
                    cls=ButtonT.secondary,
                    uk_tooltip="Select metric batch"
                ),
                batches_dropdown,
                Div(
                    Button(
                        DivLAligned(UkIcon("settings")),
                        cls=ButtonT.secondary,
                        uk_tooltip="Chart settings"
                    ),
                    settings_dropdown,
                ),
                A(
                    DivLAligned(UkIcon("github")),
                    href="https://github.com/andrewm4894/anomstack",
                    target="_blank",
                    cls="uk-button uk-button-secondary",
                    uk_tooltip="View on GitHub"
                ),
                style="display: flex; align-items: center; gap: 0.5rem;"
            )
        ),
        cls="mb-8 uk-padding-small"
    )

def _create_search_form(batch_name):
    return Form(
        Input(
            type="text",
            name="search",
            placeholder="Search metrics...",
            cls="uk-input uk-form-small",
            style="width: 200px;",
            uk_tooltip="Filter metrics by name"
        ),
        hx_post=f"/batch/{batch_name}/search",
        hx_target="#charts-container",
        hx_trigger="keyup changed delay:500ms, search"
    )

def _create_alert_n_form(batch_name):
    return Form(
        Input(
            type="number",
            name="alert_max_n",
            value=app.state.alert_max_n.get(batch_name, DEFAULT_ALERT_MAX_N),
            cls="uk-input uk-form-small",
            style="width: 100px;",
            uk_tooltip="Maximum number of observations",
            id=f"alert-max-n-{batch_name}"
        ),
        id=f"alert-max-n-form-{batch_name}",
        hx_post=f"/batch/{batch_name}/update-n",
        hx_target="#charts-container",
        hx_trigger="change"
    )

@rt("/batch/{batch_name}/chart/{chart_index}")
def get(batch_name: str, chart_index: int):
    df = app.state.df_cache[batch_name]
    metric_stats = app.state.stats_cache[batch_name]
    metric_name = metric_stats[chart_index]["metric_name"]
    anomaly_rate = metric_stats[chart_index]["anomaly_rate"]
    avg_score = metric_stats[chart_index]["avg_score"]
    
    if batch_name not in app.state.chart_cache:
        app.state.chart_cache[batch_name] = {}
    
    if chart_index not in app.state.chart_cache[batch_name]:
        df_metric = df[df["metric_name"] == metric_name]
        fig = ChartManager.create_chart(df_metric, metric_name, chart_index)
        app.state.chart_cache[batch_name][chart_index] = fig

    return Card(
        Style("""
            .uk-card-header {
                padding: 1rem;  /* Consistent padding */
            }
            .uk-card-body {
                padding: 1rem;  /* Consistent padding */
            }
        """),
        Safe(app.state.chart_cache[batch_name][chart_index]),
        header=Div(
            H4(metric_name, cls="mb-1"),
            DivLAligned(
                P(f"Anomaly Rate: {anomaly_rate:.1%}", cls="text-sm text-muted-foreground"),
                P(f"Avg Score: {avg_score:.1%}", cls="text-sm text-muted-foreground"),
                style="gap: 1rem;"
            )
        ),
        id=f"chart-{chart_index}",
        cls="mb-1"
    )


@rt("/batch/{batch_name}/refresh")
def get(batch_name: str, session):
    app.state.clear_batch_cache(batch_name)
    
    return get_batch_view(batch_name, session, initial_load=DEFAULT_LOAD_N_CHARTS)


@rt("/batch/{batch_name}/load-more/{start_index}")
def get(batch_name: str, start_index: int):
    metric_stats = app.state.stats_cache[batch_name]
    remaining_metrics = len(metric_stats) - (start_index + DEFAULT_LOAD_N_CHARTS)
    load_next = min(DEFAULT_LOAD_N_CHARTS, remaining_metrics)
    
    return [
        *[ChartManager.create_chart_placeholder(
            stat['metric_name'], i, batch_name
        ) for i, stat in enumerate(metric_stats[start_index:start_index + DEFAULT_LOAD_N_CHARTS], start=start_index)],
        # Update the load more button with new count and disabled state
        Div(
            Button(
                f"Load next {load_next} of {remaining_metrics}" if remaining_metrics > 0 else "No more metrics",
                hx_get=f"/batch/{batch_name}/load-more/{start_index + DEFAULT_LOAD_N_CHARTS}",
                hx_target="#charts-container",
                hx_swap="beforeend",
                hx_indicator="#loading",
                cls=ButtonT.secondary,
                style="width: 100%; margin-top: 1rem;",
                disabled=remaining_metrics <= 0
            ),
            id="load-more-container",
            hx_swap_oob="true"
        )
    ]


@rt("/batch/{batch_name}/search")
def post(batch_name: str, search: str = ""):
    import re
    metric_stats = app.state.stats_cache[batch_name]
    try:
        pattern = re.compile(search, re.IGNORECASE) if search else None
        filtered_stats = [
            stat for stat in metric_stats 
            if not pattern or pattern.search(stat["metric_name"])
        ]
        placeholders = []
        for i, stat in enumerate(filtered_stats):
            placeholders.append(
                ChartManager.create_chart_placeholder(
                    stat['metric_name'], i, batch_name
                )
            )
        return Div(*placeholders) if placeholders else Div(P("No matching metrics found"))
    except re.error:
        return Div(P("Invalid search pattern"))


@rt("/batch/{batch_name}/update-n")
def post(batch_name: str, alert_max_n: int = DEFAULT_ALERT_MAX_N, session=None):
    app.state.alert_max_n[batch_name] = alert_max_n
    app.state.clear_batch_cache(batch_name)
    
    app.state.df_cache[batch_name] = get_data(
        app.state.specs_enabled[batch_name],
        alert_max_n=alert_max_n
    )
    app.state.calculate_metric_stats(batch_name)
    
    script = Script(f"""
        document.getElementById('alert-max-n-{batch_name}').value = {alert_max_n};
    """)
    
    return Div(
        script,
        *[ChartManager.create_chart_placeholder(
            stat['metric_name'], i, batch_name
        ) for i, stat in enumerate(app.state.stats_cache[batch_name][:DEFAULT_LOAD_N_CHARTS])]
    )


@rt("/batch/{batch_name}/toggle-size")
def post(batch_name: str, session=None):
    app.state.small_charts = not app.state.small_charts
    app.state.chart_cache.clear()  # Clear cache to regenerate charts
    return get_batch_view(batch_name, session=session, initial_load=DEFAULT_LOAD_N_CHARTS)


@rt("/batch/{batch_name}/toggle-theme")
def post(batch_name: str, session=None):
    app.state.dark_mode = not app.state.dark_mode
    app.state.chart_cache.clear()  # Clear cache to regenerate charts
    
    # Add script to toggle dark mode class on body
    script = Script("""
        document.body.classList.toggle('dark-mode');
    """)
    
    response = get_batch_view(batch_name, session=session, initial_load=DEFAULT_LOAD_N_CHARTS)
    return Div(
        script,
        response
    )


@rt("/batch/{batch_name}/toggle-columns")
def post(batch_name: str, session=None):
    app.state.two_columns = not app.state.two_columns
    return get_batch_view(batch_name, session=session, initial_load=DEFAULT_LOAD_N_CHARTS)


serve(host="localhost", port=5003)
