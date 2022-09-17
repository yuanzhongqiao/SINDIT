from multiprocessing.dummy import active_children
from dash import html, ctx
from dash.dependencies import Input, Output, State

from dash.exceptions import PreventUpdate
import dash_bootstrap_components as dbc
from frontend.app import app
from frontend.left_sidebar.extensions.annotation_detection_extension.annotation_extension_callbacks import (
    CreationSteps,
)
from frontend.main_column.factory_graph.GraphSelectedElement import GraphSelectedElement
from frontend.right_sidebar.node_data_tab import node_data_layout
from frontend.right_sidebar.node_information_tab import node_information_layout
from graph_domain.factory_graph_types import NodeTypes

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


def change_navigation_tab_content(tab, selected_el):
    """
    Navigation through the tabs of the right sidebar
    :param selected_el:
    :param tab:
    :return:
    """
    if tab == "tab-node-data":
        return html.Div(
            children=node_data_layout.get_layout(selected_el),
            className="tab-content-container",
        )
    elif tab == "tab-node-information":
        return html.Div(
            children=[node_information_layout.get_layout(selected_el)],
            className="tab-content-container",
        )


@app.callback(
    Output("tabs-infos", "children"),
    Output("tabs-infos", "active_tab"),
    Output("last-manually-selected-tab", "data"),
    Output("tabs-content", "children"),
    Input("selected-graph-element-store", "data"),
    Input("tabs-infos", "active_tab"),
    Input("annotation-creation-store-step", "data"),
    State("last-manually-selected-tab", "data"),
    prevent_initial_update=False,
)
def add_remove_navigation_tabs(
    selected_el_json, active_tab, annotation_creation_step, last_manually_opened_tab
):
    if ctx.triggered_id == "tabs-infos":
        last_manually_opened_tab = active_tab

    if selected_el_json is None:
        # Cancel, if nothing selected
        raise PreventUpdate
    else:
        selected_el: GraphSelectedElement = GraphSelectedElement.from_json(
            selected_el_json
        )

    available_tabs = []
    available_tab_ids = []
    selected_tab = active_tab

    # Available Tabs:
    if selected_el.is_node:
        # Node information tab available only for all node-types
        available_tabs.append(
            dbc.Tab(
                id="tab-node-information",
                label="Node Details",
                tab_id="tab-node-information",
            )
        )
        available_tab_ids.append("tab-node-information")

    if selected_el.type in [
        NodeTypes.TIMESERIES_INPUT.value,
        NodeTypes.SUPPLEMENTARY_FILE.value,
        NodeTypes.ANNOTATION_TS_MATCHER.value,
    ]:
        available_tabs.append(
            dbc.Tab(
                id="tab-node-data",
                label="Context Data",
                tab_id="tab-node-data",
            ),
        )
        available_tab_ids.append("tab-node-data")

    # Reopen last manually selected tab, if available again:
    if (
        last_manually_opened_tab != active_tab
        and last_manually_opened_tab in available_tab_ids
    ):
        selected_tab = last_manually_opened_tab

    # Override selected tab in specific situation(s):
    if (
        annotation_creation_step is not None
        and annotation_creation_step == CreationSteps.RANGE_SELECTION.value
    ):
        # Auto jump to data tab for time range selection
        return "tab-node-data"

    # Override selected tab, if not available for selected element
    if selected_tab not in available_tab_ids:
        selected_tab = available_tab_ids[0] if len(available_tab_ids) > 0 else None

    return (
        available_tabs,
        selected_tab,
        last_manually_opened_tab,
        change_navigation_tab_content(tab=selected_tab, selected_el=selected_el),
    )


#     if n == 5:
#         return (), "tab-node-information"
#     elif n == 10:
#         return (
#             dbc.Tab(
#                 id="tab-node-information",
#                 label="Node details",
#                 tab_id="tab-node-information",
#             ),
#             dbc.Tab(
#                 id="tab-node-data",
#                 label="Contextualized Data",
#                 tab_id="tab-node-data",
#             ),
#         ), active_tab
#     else:
#         raise PreventUpdate


# @app.callback(
#     Output("tabs-infos", "active_tab"),
#     Input("annotation-creation-store-step", "data"),
# )
# def change_navigation_tab(annotation_creation_step):
#     if (
#         annotation_creation_step is not None
#         and annotation_creation_step == CreationSteps.RANGE_SELECTION.value
#     ):
#         return "tab-node-data"
#     else:
#         raise PreventUpdate
