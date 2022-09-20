from dash.dependencies import Input, Output, State
from dash import html
import dash_bootstrap_components as dbc
import dash_core_components as dcc
from frontend.app import app

print("Initializing navbar callbacks...")


@app.callback(
    Output("help-offcanvas", "is_open"),
    Input("help-button", "n_clicks"),
    [State("help-offcanvas", "is_open")],
    prevent_initial_call=True,
)
def toggle_offcanvas(n1, is_open):
    if n1:
        return not is_open
    return is_open


@app.callback(
    Output("import-export-dropdown", "is_open"),
    Output("exportable-databases-dropdown", "options"),
    Input("import-export-button", "n_clicks"),
    State("import-export-dropdown", "is_open"),
    prevent_initial_call=True,
)
def toggle_popover(n, is_open):
    exportable_dbs = []
    if not is_open:
        # Load content
        exportable_dbs = ["A", "B"]

    return not is_open, exportable_dbs


@app.callback(
    Output("export-single-button", "disabled"),
    Input("exportable-databases-dropdown", "value"),
    prevent_initial_call=True,
)
def download_single_button_active(selected):
    if selected is not None:
        return False
    return True


@app.callback(
    Output("export-started-notifier", "is_open"),
    Input("export-single-button", "n_clicks"),
    State("exportable-databases-dropdown", "value"),
    prevent_initial_call=True,
)
def download_single_notifier(n, selected_db):
    print(f"Startet export for single database: {selected_db}")
    return True
