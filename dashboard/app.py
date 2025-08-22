"""
dashboard/app.py

Anomstack Dashboard

This is a dashboard for the Anomstack project. It is a web application
that allows you to view and analyze metrics from the Anomstack project.

It is built with FastHTML and MonsterUI.

"""

import logging
import os

from dotenv import load_dotenv
from fasthtml.common import Link, Script, Style, fast_app, serve
from monsterui.all import *

from dashboard.constants import POSTHOG_SCRIPT
from dashboard.state import AppState

# load the environment variables with custom env file support
def load_env_with_custom_path():
    """Load environment variables from custom path or default .env file."""
    from pathlib import Path
    
    env_file_path = os.getenv("ANOMSTACK_ENV_FILE_PATH")
    
    if env_file_path:
        env_path = Path(env_file_path)
        if env_path.exists():
            print(f"🎯 Using custom environment file: {env_file_path}")
            load_dotenv(env_path, override=True)
            print("✅ Custom environment file loaded")
        else:
            print(f"❌ Custom environment file not found: {env_file_path}")
            print("📄 Falling back to default .env file")
            load_dotenv(override=True)
    else:
        # Standard .env loading
        load_dotenv(override=True)

load_env_with_custom_path()

log = logging.getLogger("anomstack_dashboard")

# Get PostHog API key from environment
posthog_api_key = os.getenv("POSTHOG_API_KEY")
if posthog_api_key:
    from dashboard.constants import POSTHOG_SCRIPT

    POSTHOG_SCRIPT = POSTHOG_SCRIPT.replace("window.POSTHOG_API_KEY || ''", f"'{posthog_api_key}'")

# Define the app
app, rt = fast_app(
    hdrs=(
        Theme.blue.headers(),
        Script(src="https://cdn.jsdelivr.net/npm/apexcharts@latest"),
        Style("""
uk-chart {
    display: block !important;
    width: 100% !important;
    min-height: 300px !important;
    height: auto !important;
}
uk-chart .apexcharts-canvas {
    width: 100% !important;
    height: 100% !important;
}
/* Sparklines should fill their grid cell for consistent alignment */
/* We now size sparkline charts via JS by detecting chart.sparkline.enabled */
.sparkline-cell uk-chart[id^="sparkline-"] {
    min-height: 32px !important;
    height: 32px !important;
    width: 260px !important;
}
.sparkline-cell uk-chart[id^="sparkline-"] .apexcharts-canvas {
    width: 100% !important;
    height: 100% !important;
}
.sparkline-container {
    display: flex;
    justify-content: center;
    align-items: center;
    width: 100%;
    height: 100%;
}
        """),
        Script("""
const __chartInitState = {
    observer: null,
    seen: new WeakSet(),
};

function renderChartElement(el) {
    const script = el.querySelector('script[type="application/json"]');
    if (!script) return false;
    if (el.hasAttribute('data-chart-initialized')) return true;
    try {
        const config = JSON.parse(script.textContent);
        if (config.yaxis && config.yaxis[1]) {
            config.yaxis[1].labels = config.yaxis[1].labels || {};
            config.yaxis[1].labels.formatter = function(val) { return Math.round(val * 100) + '%'; };
        }
        const isSpark = !!(config.chart && config.chart.sparkline && config.chart.sparkline.enabled);
        el.style.display = 'block';
        el.style.width = '100%';
        el.style.minHeight = isSpark ? '32px' : '300px';
        el.style.height = isSpark ? '32px' : 'auto';
        // Ensure ApexCharts receives an explicit width to avoid 0-width renders
        const width = Math.max(220, Math.floor(el.getBoundingClientRect().width || el.clientWidth || 0));
        config.chart = config.chart || {};
        config.chart.width = width;
        config.chart.height = isSpark ? 32 : (config.chart.height || 300);
        if (typeof ApexCharts === 'undefined') return false;
        const chart = new ApexCharts(el, config);
        chart.render().then(() => el.setAttribute('data-chart-initialized', 'true'));
        return true;
    } catch (e) {
        console.error('renderChartElement error', e, el);
        return false;
    }
}

function ensureChartObserver() {
    if (__chartInitState.observer) return __chartInitState.observer;
    __chartInitState.observer = new IntersectionObserver((entries) => {
        entries.forEach((entry) => {
            const el = entry.target;
            if (!entry.isIntersecting) return;
            if (__chartInitState.seen.has(el) || el.hasAttribute('data-chart-initialized')) {
                __chartInitState.observer.unobserve(el);
                return;
            }
            const script = el.querySelector('script[type="application/json"]');
            if (!script) return;
            try {
                const config = JSON.parse(script.textContent);
                if (config.yaxis && config.yaxis[1]) {
                    config.yaxis[1].labels = config.yaxis[1].labels || {};
                    config.yaxis[1].labels.formatter = function(val) { return Math.round(val * 100) + '%'; };
                }
                const isSpark = !!(config.chart && config.chart.sparkline && config.chart.sparkline.enabled);
                el.style.display = 'block';
                el.style.width = '100%';
                el.style.minHeight = isSpark ? '32px' : '300px';
                el.style.height = isSpark ? '32px' : 'auto';
                // Explicit width
                const width = Math.max(220, Math.floor(el.getBoundingClientRect().width || el.clientWidth || 0));
                config.chart = config.chart || {};
                config.chart.width = width;
                config.chart.height = isSpark ? 32 : (config.chart.height || 300);
                requestAnimationFrame(() => {
                    const chart = new ApexCharts(el, config);
                    chart.render().then(() => {
                        el.setAttribute('data-chart-initialized', 'true');
                        __chartInitState.seen.add(el);
                        __chartInitState.observer.unobserve(el);
                    });
                });
            } catch (e) {
                console.error('Error initializing chart:', e, el);
            }
        });
    }, { root: null, rootMargin: '200px 0px', threshold: 0.01 });
    return __chartInitState.observer;
}

function initializeCharts() {
    // Prefer immediate render inside anomaly list to avoid races
    const anomalyContainer = document.getElementById('anomaly-list');
    if (anomalyContainer) {
        const charts = Array.from(anomalyContainer.querySelectorAll('uk-chart:not([data-chart-initialized])'));
        let rendered = 0;
        charts.forEach((el) => { if (renderChartElement(el)) rendered++; });
        if (rendered < charts.length) {
            // Retry after a short delay (e.g. if ApexCharts not ready yet)
            setTimeout(() => {
                charts.forEach((el) => { if (!el.hasAttribute('data-chart-initialized')) renderChartElement(el); });
            }, 300);
        }
        return; // Skip observer path for anomalies page
    }

    // Fallback: use lazy observer for other pages
    const observer = ensureChartObserver();
    document.querySelectorAll('uk-chart:not([data-chart-initialized])').forEach((el) => observer.observe(el));
}

// Wait for both DOM and ApexCharts to be ready
document.addEventListener('DOMContentLoaded', function() {
    // Check if ApexCharts is loaded
    if (typeof ApexCharts !== 'undefined') {
        initializeCharts();
    } else {
        // Wait a bit more for ApexCharts to load
        setTimeout(() => {
            if (typeof ApexCharts !== 'undefined') {
                initializeCharts();
            } else {
                console.error('ApexCharts library not loaded');
            }
        }, 1000);
    }
});

// Re-initialize charts after HTMX requests
document.addEventListener('htmx:afterSwap', initializeCharts);
document.addEventListener('htmx:afterSettle', initializeCharts);
// Debug: log counts and row metadata after HTMX updates
document.addEventListener('htmx:afterSettle', function() {
    try {
        const container = document.getElementById('anomaly-list');
        if (!container) return;
        const rows = Array.from(container.querySelectorAll('[data-row]'));
        const charts = Array.from(container.querySelectorAll('uk-chart'));
        const visibleCharts = charts.filter(c => c.offsetParent !== null);
        console.log('[anomstack] rows:', rows.length, 'charts:', charts.length, 'visibleCharts:', visibleCharts.length);
        rows.slice(0, 5).forEach(r => {
            const ds = r.dataset || {};
            console.log('[row]', ds.row, ds.metric, ds.ts);
        });
        const initialized = container.querySelectorAll('uk-chart[data-chart-initialized]');
        console.log('[anomstack] initialized charts:', initialized.length);
        // Force initialize any visible charts not initialized yet (safety net)
        if (visibleCharts.length && initialized.length < visibleCharts.length) {
            visibleCharts.forEach((el) => { if (!el.hasAttribute('data-chart-initialized')) renderChartElement(el); });
        }
    } catch (e) { console.warn('debug error', e); }
});
        """),
        Script(POSTHOG_SCRIPT) if posthog_api_key else None,
        Link(
            rel="icon",
            type="image/svg+xml",
            href="data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIyNCIgaGVpZ2h0PSIyNCIgdmlld0JveD0iMCAwIDI0IDI0IiBmaWxsPSJub25lIiBzdHJva2U9ImN1cnJlbnRDb2xvciIgc3Ryb2tlLXdpZHRoPSIyIiBzdHJva2UtbGluZWNhcD0icm91bmQiIHN0cm9rZS1saW5lam9pbj0icm91bmQiIGNsYXNzPSJsdWNpZGUgbHVjaWRlLWNoYXJ0LWxpbmUiPjxwYXRoIGQ9Ik0zIDN2MTZhMiAyIDAgMCAwIDIgMmgxNiIvPjxwYXRoIGQ9Im0xOSA5LTUgNS00LTQtMyAzIi8+PC9zdmc+",
        ),
        Link(rel="stylesheet", href="dashboard/static/styles.css"),
    ),
    debug=os.getenv("ANOMSTACK_DASHBOARD_DEBUG", "false").lower() == "true",
    log=log,
)

# Set the app state
app.state = AppState()


# Add health check endpoint for Cloud Run
@rt("/health")
def health_check():
    """Quick health check endpoint for deployment."""
    return {"status": "ok", "service": "anomstack-dashboard"}


# Add version information endpoint
@rt("/version")
def version_info():
    """Version information endpoint."""
    try:
        from anomstack.version import get_version_info
        return get_version_info()
    except Exception as e:
        return {"error": str(e), "service": "anomstack-dashboard"}


# Add lightweight root handler for deployment health checks
@rt("/")
def root_health_check(request):
    """Handle root path health checks from Cloud Run."""
    user_agent = request.headers.get("User-Agent", "")
    # Check if this is a health check request
    if (
        user_agent.startswith("GoogleHC")
        or user_agent.startswith("kube-probe")
        or user_agent.startswith("Google-Cloud-Tasks")
    ):
        return {"status": "healthy", "service": "anomstack-dashboard"}
    # Otherwise, let the regular index route handle it
    from dashboard.routes.index import index

    return index(request)


# Import routes after app is defined
from dashboard.routes import *

if __name__ == "__main__":
    try:
        print("Starting Anomstack dashboard on port 8080")
        serve(app, host="0.0.0.0", port=8080)
    except Exception as e:
        print(f"Failed to start dashboard: {e}")
        raise
