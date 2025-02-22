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
        """),
    ),
    debug=True, 
    log=log
)

# Set up toasts
setup_toasts(app, duration=3)

# Constants
DEFAULT_INITIAL_LOAD = 5
DEFAULT_ALERT_MAX_N = 30

class DashboardState:
    def __init__(self):
        self.specs = specs
        self.metric_batches = get_metric_batches()
        self.specs_enabled = {batch: specs[batch] for batch in self.metric_batches}
        self.df_cache = {}
        self.chart_cache = {}
        self.stats_cache = {}
        self.small_charts = True  # Changed to True to default to small charts
        self.dark_mode = False
    
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
    # Add dark mode class to body if enabled
    script = Script(f"""
        if ({'true' if app.state.dark_mode else 'false'}) {{
            document.body.classList.add('dark-mode');
        }}
    """)
    
    current_path = request.url.path
    current_batch = current_path.split("/batch/")[-1] if "/batch/" in current_path else None

    top_nav = TabContainer(
        *map(
            lambda x: Li(
                A(x, 
                  hx_get=f"/batch/{x}", 
                  hx_push_url=f"/batch/{x}",
                  hx_target="#main-content",
                  hx_indicator="#loading",
                  hx_swap="innerHTML",
                  cls="uk-padding-small"
                ),
                cls="uk-active" if x == current_batch else ""
            ),
            app.state.metric_batches,
        ),
        alt=True,
        cls="top-nav uk-margin-bottom"
    )

    main_content = Card(
        _create_controls(current_batch) if current_batch else None,
        Div(
            DivLAligned(
                P("Please select a metric batch above to view metrics.", cls=TextPresets.muted_lg),
                cls="p-8 text-center"
            ) if not current_batch else None,
            id="charts-container"
        ),
        id="main-content", 
        cls="col-span-4"
    ) if not current_batch else None

    return (
        Title("Anomstack"),
        script,
        Div(
            Safe('<span class="htmx-indicator">Loading...</span>'),
            id="loading", 
            cls="loading-indicator"
        ),
        Card(
            top_nav,
            Grid(main_content) if main_content else None,
            cls="uk-margin-top"
        )
    )


@rt("/batch/{batch_name}")
def get_batch_view(batch_name: str, session, initial_load: int = DEFAULT_INITIAL_LOAD):
    if batch_name not in app.state.df_cache:
        app.state.df_cache[batch_name] = get_data(
            app.state.specs_enabled[batch_name], 
            alert_max_n=DEFAULT_ALERT_MAX_N
        )
        app.state.calculate_metric_stats(batch_name)

    metric_stats = app.state.stats_cache[batch_name]
    total_metrics = len(metric_stats)
    
    script = Script(f"""
        document.querySelectorAll('.top-nav li').forEach(li => {{
            li.classList.remove('uk-active');
            if (li.querySelector('a').textContent.trim() === '{batch_name}') {{
                li.classList.add('uk-active');
            }}
        }});
        window.scrollTo({{ top: 0, behavior: 'smooth' }});
    """)

    return Div(
        _create_controls(batch_name),
        Div(
            *[ChartManager.create_chart_placeholder(
                stat['metric_name'], i, batch_name
            ) for i, stat in enumerate(metric_stats[:initial_load])],
            # Add Load All button if there are more metrics
            Div(
                Button(
                    "Load All",
                    hx_get=f"/batch/{batch_name}/load-more/{initial_load}",
                    hx_target="#load-all-container",
                    hx_swap="outerHTML",
                    cls=ButtonT.secondary,
                    style="width: 100%; margin-top: 1rem;"
                ),
                id="load-all-container"
            ) if total_metrics > initial_load else None,
            id="charts-container"
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

    return Card(
        Div(
            Button(
                DivLAligned(UkIcon("refresh"), "Refresh"),
                hx_get=f"/batch/{batch_name}/refresh", 
                hx_target="#main-content",
                cls=ButtonT.secondary,
                uk_tooltip="Refresh metrics data"
            ),
            _create_search_form(batch_name),
            _create_alert_n_form(batch_name),
            Button(
                DivLAligned(UkIcon("settings"), "Settings"),
                cls=ButtonT.secondary,
                uk_tooltip="Chart settings"
            ),
            settings_dropdown,
            style="display: flex; align-items: center; gap: 0.5rem;"
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
            value=DEFAULT_ALERT_MAX_N,
            cls="uk-input uk-form-small",
            style="width: 100px;",
            uk_tooltip="Maximum number of observations"
        ),
        hx_post=f"/batch/{batch_name}/update-n",
        hx_target="#main-content",
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
    
    return get_batch_view(batch_name, session, initial_load=DEFAULT_INITIAL_LOAD)


@rt("/batch/{batch_name}/load-more/{start_index}")
def get(batch_name: str, start_index: int):
    metric_stats = app.state.stats_cache[batch_name]
    remaining_metrics = metric_stats[start_index:]
    
    return Div(
        *[ChartManager.create_chart_placeholder(
            stat['metric_name'], i, batch_name
        ) for i, stat in enumerate(remaining_metrics, start=start_index)],
        id="load-all-container"  # Same ID as container above
    )


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
    app.state.clear_batch_cache(batch_name)
    
    app.state.df_cache[batch_name] = get_data(
        app.state.specs_enabled[batch_name],
        alert_max_n=alert_max_n
    )
    app.state.calculate_metric_stats(batch_name)
    return get_batch_view(batch_name, session, initial_load=DEFAULT_INITIAL_LOAD)


@rt("/batch/{batch_name}/toggle-size")
def post(batch_name: str):
    app.state.small_charts = not app.state.small_charts
    app.state.chart_cache.clear()  # Clear cache to regenerate charts
    return get_batch_view(batch_name, session=None)


@rt("/batch/{batch_name}/toggle-theme")
def post(batch_name: str):
    app.state.dark_mode = not app.state.dark_mode
    app.state.chart_cache.clear()  # Clear cache to regenerate charts
    
    # Add script to toggle dark mode class on body
    script = Script("""
        document.body.classList.toggle('dark-mode');
    """)
    
    return Div(
        script,
        get_batch_view(batch_name, session=None)
    )


serve(host="localhost", port=5003)
