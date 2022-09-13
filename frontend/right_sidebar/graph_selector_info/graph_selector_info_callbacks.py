from dash.dependencies import Input, Output

from dash.exceptions import PreventUpdate
from frontend.app import app
from frontend.main_column.factory_graph.GraphSelectedElement import GraphSelectedElement
from frontend.right_sidebar.graph_selector_info import graph_selector_info_layout
from graph_domain.factory_graph_types import NodeTypes

print("Initializing graph selector callbacks...")


@app.callback(
    Output("selected-element-id-short", "children"),
    Output("selected-element-id-short-container", "style"),
    Output("selected-element-type", "children"),
    Output("selected-element-label", "children"),
    Output("selected-element-label-container", "style"),
    Input("selected-graph-element-store", "data"),
    prevent_initial_call=True,
)
def display_selected_graph_element_info(selected_el_json):
    """
    Called whenever a element in the graph is selected.
    Refreshes the user output with id, type, ...
    :param selected_el:
    :return:
    """
    if selected_el_json is None:
        raise PreventUpdate()

    selected_el: GraphSelectedElement = GraphSelectedElement.from_json(selected_el_json)

    return (
        selected_el.id_short,
        {"display": "none"}
        if selected_el.id_short is None or selected_el.id_short == "NA"
        else {},
        f"{selected_el.type} ({'NODE' if selected_el.is_node else 'EDGE'})",
        selected_el.caption,
        {"display": "none"}
        if selected_el.caption is None
        or selected_el.caption == selected_el.id_short
        or selected_el.caption == ""
        else {},
    )
