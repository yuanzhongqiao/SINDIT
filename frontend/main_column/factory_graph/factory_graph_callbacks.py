from datetime import datetime
from dash import ctx, Input, Output, State
from dash.exceptions import PreventUpdate
import pytz
from util.environment_and_configuration import (
    ConfigGroups,
    get_configuration_int,
)
from frontend import api_client
from frontend.app import app
from frontend.main_column.factory_graph import factory_graph_cytoscape_converter
from frontend.main_column.factory_graph.GraphSelectedElement import GraphSelectedElement
from graph_domain.main_digital_twin.AssetNode import AssetNodeDeep


print("Initializing factory graph callbacks...")


def _get_graph_age_seconds(timestamp):
    if timestamp is not None:
        return (
            datetime.now() - datetime.fromtimestamp(timestamp / 1000.0)
        ).total_seconds()
    else:
        return (
            get_configuration_int(group=ConfigGroups.FRONTEND, key="max_graph_age") + 1
        )


@app.callback(
    Output("cytoscape-graph", "elements"),
    Output("cytoscape-graph-store", "data"),
    Output("cytoscape-graph-store-age", "data"),
    Output("factory-graph-loading-state", "data"),
    Input("graph-reload-button", "n_clicks"),
    State("cytoscape-graph-store", "data"),
    State("cytoscape-graph-store-age", "modified_timestamp"),
    State("graph-force-full-reload-store", "modified_timestamp"),
    prevent_initial_call=True,
)
def update_factory_graph(
    n_clicks, stored_graph, local_timestamp, force_reload_timestamp
):
    """
    Updates the main graph: Loads the nodes and edges from Neo4J or local storage
    :param n:
    :return:
    """

    # Reload from backend when button manually clicked (n > 1), no graph is stored locally,
    # or the stored one is older than the configured max age
    if (
        n_clicks > 1
        or stored_graph is None
        or _get_graph_age_seconds(local_timestamp)
        > get_configuration_int(group=ConfigGroups.FRONTEND, key="max_graph_age")
        or (
            force_reload_timestamp is not None
            and force_reload_timestamp > local_timestamp
        )
    ):
        print("Loading graph from backend")
        assets_deep_json = api_client.get_json("/assets")
        # pylint: disable=no-member
        assets_deep = [AssetNodeDeep.from_json(m) for m in assets_deep_json]
        asset_similarities = api_client.get_json("/assets/similarities")

        cygraph_elements = factory_graph_cytoscape_converter.get_cytoscape_elements(
            assets_deep=assets_deep, asset_similarities=asset_similarities
        )
    else:
        cygraph_elements = stored_graph
        print("Using cached graph")

    return cygraph_elements, cygraph_elements, datetime.now().isoformat(), True


# pylint: disable=W0613
@app.callback(
    Output("graph-reload-button", "n_clicks"),
    Input("interval-component-factory-graph", "n_intervals"),
    Input("graph-reload-button", "n_clicks"),
    Input("interval-component-factory-graph-initial-loading", "n_intervals"),
    State("cytoscape-graph-store-age", "modified_timestamp"),
    State("factory-graph-loading-state", "data"),
    State("graph-force-full-reload-store", "modified_timestamp"),
    Input("annotation-creation-saved", "modified_timestamp"),
    Input("annotation-deleted", "modified_timestamp"),
    Input("import-finished", "modified_timestamp"),
    prevent_initial_call=True,
)
def factory_graph_update_trigger(
    n,
    n_clicks,
    n_init_intervall,
    local_timestamp,
    graph_loaded,
    force_reload_timestamp,
    annotation_created_full_reload,
    annotation_deleted_full_reload,
    import_finished,
):
    if ctx.triggered_id in [
        "annotation-creation-saved",
        "annotation-deleted",
        "import-finished",
    ]:
        print("Reloading graph from backend after creating a new annotation...")
        return 2
    elif graph_loaded is None and n_init_intervall == 1:
        # First loading after opening / reloading whole page
        print("Initial graph loading...")
        return 1
    elif graph_loaded is None and n_init_intervall < 4:
        print("Waiting for graph to load...")
        raise PreventUpdate()
    elif graph_loaded is None and n_init_intervall == 4:
        print(
            "Graph not loaded after first intervall. "
            "Checking if reloading from backend or local storage..."
        )
        if _get_graph_age_seconds(local_timestamp) > get_configuration_int(
            group=ConfigGroups.FRONTEND, key="max_graph_age"
        ) or (
            force_reload_timestamp is not None
            and force_reload_timestamp > local_timestamp
        ):
            print("Loading from backend. Giving it more time...")
            raise PreventUpdate()
        else:
            print(
                "Loading from local storage. Should be already finished. Reloading as fallback..."
            )
            return 1
    elif _get_graph_age_seconds(local_timestamp) > get_configuration_int(
        group=ConfigGroups.FRONTEND, key="max_graph_age"
    ):
        print("Graph to old! Reloading graph from backend...")
        return 2
    else:
        print("Graph okay")
        raise PreventUpdate()


@app.callback(
    [
        Output("selected-graph-element-store", "data"),
        Output("selected-graph-element-timestamp", "data"),
    ],
    [
        Input("kg-container", "n_clicks"),
        State("selected-graph-element-timestamp", "data"),
        State("cytoscape-graph", "tapNode"),
        State("cytoscape-graph", "tapEdge"),
    ],
    prevent_initial_call=True,
)
def store_selected_element_info(n_clicks, last_click_time_str, tap_node, tap_edge):
    """
    Called whenever an element in the graph is selected (or de-selected).
    Stores the selected element to be available for other callbacks
    :param n_clicks:
    :param last_click_time_str:
    :param tap_edge:
    :param tap_node:
    :return:
    """
    if last_click_time_str is not None:
        last_click_time = datetime.fromisoformat(last_click_time_str)
    else:
        # Min available timestamp, so that the current one will be considered newer
        last_click_time = datetime.fromtimestamp(0, tz=pytz.UTC)

    if (
        tap_node is not None
        and datetime.fromtimestamp(tap_node["timeStamp"] / 1000.0, tz=pytz.UTC)
        > last_click_time
    ):
        # Currently selected a node:
        selected_el = GraphSelectedElement.from_tap_node(tap_node)
        # pylint: disable=no-member
        new_selected_el_json = selected_el.to_json()
        new_click_time = datetime.fromtimestamp(
            tap_node["timeStamp"] / 1000.0, tz=pytz.UTC
        )
    elif (
        tap_edge is not None
        and datetime.fromtimestamp(tap_edge["timeStamp"] / 1000.0, tz=pytz.UTC)
        > last_click_time
    ):
        # Currently selected an edge:
        selected_el = GraphSelectedElement.from_tap_edge(tap_edge)
        # pylint: disable=no-member
        new_selected_el_json = selected_el.to_json()
        new_click_time = datetime.fromtimestamp(
            tap_edge["timeStamp"] / 1000.0, tz=pytz.UTC
        )
    else:
        # Deselected the element (click into the white space)
        new_selected_el_json = None
        new_click_time = last_click_time

    return new_selected_el_json, new_click_time.isoformat()


@app.callback(
    Output("graph-positioning-saved-notifier", "children"),
    Output("graph-positioning-saved-notifier", "is_open"),
    Output("graph-force-full-reload-store", "data"),
    Input("graph-positioning-save-button", "n_clicks"),
    State("selected-graph-element-store", "data"),
    prevent_initial_call=True,
)
def update_node_position(n_clicks, selected_el_json):
    """
    Called when the user selects to store the altered position of a node
    :param n_clicks:
    :param selected_el_json:
    :return:
    """
    # pylint: disable=no-member
    selected_el: GraphSelectedElement = GraphSelectedElement.from_json(selected_el_json)

    api_client.patch(
        "/node_position",
        iri=selected_el.iri,
        pos_x=selected_el.position_x,
        pos_y=selected_el.position_y,
    )

    # Notify the user with an auto-dismissing alert:
    return "New node position saved!", True, datetime.now()


@app.callback(
    Output("graph-positioning-container", "style"),
    Input("selected-graph-element-store", "data"),
    Input("cytoscape-graph", "elements"),
    prevent_initial_call=True,
)
def toggle_layout_saver_visibility(selected_el_json, elements):
    """
    Called whenever a element is selected (or de-selected) in the graph, or when the graph changes.
    Provides the user with a visible save-functionality for the altered node position,
    if a node is selected, that
    the user moved via drag and drop.
    :param selected_el_json:
    :param elements:
    :return:
    """
    if selected_el_json is not None and elements is not None:
        # pylint: disable=no-member
        selected_el: GraphSelectedElement = GraphSelectedElement.from_json(
            selected_el_json
        )
        if selected_el.is_node:
            # Get the last persisted position for comparison
            stored_el_pos = next(
                (
                    element["data"].get("persisted_pos")
                    for element in elements
                    if element["data"].get("iri") == selected_el.iri
                ),
                # Default:
                {"x": 0, "y": 0},
            )
            if selected_el.position_x != stored_el_pos.get(
                "x"
            ) or selected_el.position_y != stored_el_pos.get("y"):
                # Show save position button:
                return {}

    # Do not show in any other case
    return {"display": "None"}
