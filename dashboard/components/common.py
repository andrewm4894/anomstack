"""
dashboard/components/common.py

Common components shared across the dashboard.

This module contains the common components for the dashboard.

"""

from fasthtml.common import Div
from monsterui.all import Card, DivFullySpaced
from .search import create_search_form, create_last_n_form
from .toolbar import create_toolbar_buttons


def create_controls(batch_name: str) -> Card:
    """Create the main controls for the dashboard.

    Args:
        batch_name (str): The name of the batch.

    Returns:
        Card: The card.
    """
    return Card(
        DivFullySpaced(
            Div(
                Div(
                    Div(
                        create_toolbar_buttons(batch_name),
                        Div(
                            create_search_form(batch_name),
                            create_last_n_form(batch_name),
                            cls="flex flex-col space-y-2 md:flex-row md:space-y-0 md:space-x-4 mt-4",
                        ),
                        cls="flex flex-col w-full",
                    ), ),
                cls="w-full",
            ), ),
        cls="mb-4 uk-padding-small py-2 shadow-sm",
    )
