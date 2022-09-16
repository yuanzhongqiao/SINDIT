from dash import html, ctx
from dash.dependencies import Input, Output, State

from frontend.app import app
from frontend.left_sidebar.extensions.annotation_detection_extension.annotation_extension_callbacks import (
    CreationSteps,
)
from frontend.main_column.factory_graph.GraphSelectedElement import GraphSelectedElement
from frontend.right_sidebar.node_data_tab import node_data_layout
from frontend.right_sidebar.node_information_tab import node_information_layout

print("Initializing navigation callbacks...")


@app.callback(
    # Output("right-sidebar-collapse", "is_open"),
    Output("right-sidebar-collapse", "className"),
    Input("selected-graph-element-store", "data"),
    Input("annotation-deleted", "modified_timestamp"),
)
def show_selected_element_sidebar(selected_el_json, annotation_deleted_force_close):
    """
    Toggles the visibility of the right sidebar
    :param selected_el:
    :return:
    """
    if ctx.triggered_id == "annotation-deleted":
        return "sidebar-collapsed"

    return "" if selected_el_json is not None else "sidebar-collapsed"


@app.callback(
    Output("tabs-content", "children"),
    [
        Input("tabs-infos", "active_tab"),
        Input("selected-graph-element-store", "data"),
    ],
)
def change_navigation_tab(tab, selected_el_json):
    """
    Navigation through the tabs of the right sidebar
    :param selected_el_json:
    :param tab:
    :return:
    """
    if selected_el_json is None:
        selected_el = None
    else:
        selected_el = GraphSelectedElement.from_json(selected_el_json)

    if tab == "tab-node-data":
        return html.Div(
            children=[node_data_layout.get_layout(selected_el)],
            className="tab-content-container",
        )
    elif tab == "tab-node-information":
        return html.Div(
            children=[node_information_layout.get_layout(selected_el)],
            className="tab-content-container",
        )
