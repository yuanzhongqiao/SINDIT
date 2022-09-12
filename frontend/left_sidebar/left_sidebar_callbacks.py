from dash import html
from dash.dependencies import Input, Output, State

from frontend.app import app
from frontend.main_column.factory_graph.GraphSelectedElement import GraphSelectedElement
from frontend.right_sidebar.node_data_tab import node_data_layout
from frontend.right_sidebar.node_information_tab import node_information_layout

print("Initializing extension collapsable callbacks...")


def show_horizontal_collapsable(n_clicks):
    if n_clicks % 2 == 0:
        return "collapsable-horizontal"
    else:
        return "collapsable-horizontal collapsed-horizontal"


def show_left_collaps_button(n_clicks):
    if n_clicks % 2 == 0:
        return "vertical-button-left-collapse-icon"
    else:
        return "vertical-button-left-collapse-icon vertical-button-left-collapse-icon-expanded"


@app.callback(
    Output("left-sidebar-collapse-similarity-pipeline", "className"),
    Output("left-sidebar-collapse-main", "className"),
    Output("similarity-pipeline-button-icon", "className"),
    Input("similarity-pipeline-collapse-button", "n_clicks"),
    prevent_initial_call=True,
)
def show_similarity_pipeline_sidebar(n_clicks):
    """
    Toggles the visibility of a left collapsable sidebar
    :param selected_el:
    :return:
    """

    return (
        show_horizontal_collapsable(n_clicks + 1),
        show_horizontal_collapsable(n_clicks),
        show_left_collaps_button(n_clicks),
    )


@app.callback(
    Output("annotation-detection-button-icon", "className"),
    Input("annotation-detection-collapse-button", "n_clicks"),
    prevent_initial_call=True,
)
def show_annotation_detection_sidebar(n_clicks):
    """
    Toggles the visibility of a left collapsable sidebar
    :param selected_el:
    :return:
    """

    return show_left_collaps_button(n_clicks)
