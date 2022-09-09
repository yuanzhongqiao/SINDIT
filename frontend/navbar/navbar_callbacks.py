from dash.dependencies import Input, Output, State

from dash.exceptions import PreventUpdate
from frontend.app import app
from frontend.main_column.factory_graph.GraphSelectedElement import GraphSelectedElement
from frontend.right_sidebar.graph_selector_info import graph_selector_info_layout

print("Initializing navbar callbacks...")


@app.callback(
    Output("help-offcanvas", "is_open"),
    Input("help-button", "n_clicks"),
    [State("help-offcanvas", "is_open")],
)
def toggle_offcanvas(n1, is_open):
    if n1:
        return not is_open
    return is_open
