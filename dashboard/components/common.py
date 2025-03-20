
def create_settings_button():
    """Create settings button for the UI."""
    return {
        "type": "button",
        "icon": "settings",
        "className": "btn btn-secondary btn-sm",
        "data-toggle": "modal",
        "data-target": "#settingsModal"
    }
