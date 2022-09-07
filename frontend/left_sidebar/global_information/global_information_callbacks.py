from datetime import datetime
from frontend.app import app
from dash.dependencies import Input, Output

from frontend.left_sidebar.global_information import global_information_layout

print("Initializing global information callbacks...")


@app.callback(
    Output("status-system-time", "children"),
    Output("status-db-connections", "children"),
    Output("status-ts-connections", "children"),
    Output("status-ts-inputs", "children"),
    Output("status-assets-count", "children"),
    Input("interval-component", "n_intervals"),
)
def update_connectivity_information(n):
    """
    Periodically refreshes the global information
    :param n:
    :return:
    """
    return datetime.now().ctime(), "3 / 3", "2 / 2", "28", "5"
