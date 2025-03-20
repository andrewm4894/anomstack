
"""Controls components for the dashboard."""
from fasthtml.common import *
from monsterui.all import *

from .forms import create_search_form, create_last_n_form

def create_controls(batch_name: str) -> Div:
    """Create the control components."""
    return Div(
        create_search_form(batch_name),
        create_last_n_form(batch_name),
        cls="flex items-center space-x-2 flex-wrap mb-4",
    )
