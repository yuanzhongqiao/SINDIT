from frontend.app import app
from dash.dependencies import Input, Output, State

from frontend.main_column.factory_graph.GraphSelectedElement import GraphSelectedElement
from typing import List
from frontend import api_client
from graph_domain.main_digital_twin.AssetNode import AssetNodeFlat
from requests.exceptions import RequestException
from dash.exceptions import PreventUpdate
from frontend import resources_manager
from frontend.left_sidebar.extensions.annotation_detection_extension.annotation_extension_callbacks import (
    CreationSteps,
)
from frontend.main_column.factory_graph.factory_graph_layout import (
    CY_GRAPH_STYLE_STATIC,
)
from graph_domain.factory_graph_types import (
    NODE_TYPE_STRINGS,
    RELATIONSHIP_TYPES_FOR_NODE_TYPE,
    NodeTypes,
)

print("Initializing visibility settings callbacks...")


@app.callback(
    Output("cytoscape-graph", "stylesheet"),
    Input("visibility-switches-input", "value"),
    Input("annotation-creation-store-step", "data"),
    Input("asset-multi-select-dropdown", "value"),
    State("annotation-creation-store-asset", "data"),
)
def change_graph_visibility_options(
    active_switches,
    annotation_creation_step,
    selected_assets,
    annotation_creation_asset_json,
):
    """
    Toggles the visibility of element types in the main graph
    :param value:
    :return:
    """
    if (
        annotation_creation_step is not None
        and annotation_creation_step == CreationSteps.ASSET_SELECTION.value
    ):
        # Only show assets:
        deactivated_switches = [
            switch for switch in NODE_TYPE_STRINGS if switch != NodeTypes.ASSET.value
        ]
        # All assets:
        selected_assets = []
    elif (
        annotation_creation_step is not None
        and annotation_creation_step == CreationSteps.DEFINITION_SELECTION.value
    ):
        # Only show annotation definitions:
        deactivated_switches = [
            switch
            for switch in NODE_TYPE_STRINGS
            if switch != NodeTypes.ANNOTATION_DEFINITION.value
        ]
        # Annotation definitions from all assets:
        selected_assets = []
    elif (
        annotation_creation_step is not None
        and annotation_creation_step == CreationSteps.TS_SELECTION.value
    ):
        # Only show annotation definitions:
        deactivated_switches = [
            switch
            for switch in NODE_TYPE_STRINGS
            if switch not in [NodeTypes.TIMESERIES_INPUT.value, NodeTypes.ASSET.value]
        ]
        # Only ts from the current asset:
        selected_asset: GraphSelectedElement = GraphSelectedElement.from_json(
            annotation_creation_asset_json
        )
        selected_assets = [selected_asset.iri]
    else:
        # Use regular user-based visibility settings:
        deactivated_switches = [
            switch for switch in NODE_TYPE_STRINGS if switch not in active_switches
        ]

    invisibility_styles = []

    for inactive_switch in deactivated_switches:
        # Hide nodes from that type:
        invisibility_styles.append(
            {"selector": f".{inactive_switch}", "style": {"display": "none"}}
        )

    # Asset-based selector:
    if selected_assets is not None and len(selected_assets) > 0:
        selectors = [f"node[associated_assets !*= '{iri}']" for iri in selected_assets]
        invisibility_styles.append(
            {"selector": "".join(selectors), "style": {"display": "none"}}
        )

    return CY_GRAPH_STYLE_STATIC + invisibility_styles


@app.callback(
    Output("visibility-settings-ignored-info", "className"),
    Input("annotation-creation-store-step", "data"),
)
def change_graph_visibility_options(annotation_creation_step):

    if annotation_creation_step is not None and annotation_creation_step in [
        CreationSteps.ASSET_SELECTION.value,
        CreationSteps.DEFINITION_SELECTION.value,
        CreationSteps.TS_SELECTION.value,
    ]:
        return ""
    else:
        return "hide-content"


@app.callback(
    Output("asset-multi-select-dropdown", "options"),
    Input("interval-component-factory-graph-initial-loading", "n_intervals"),
)
def update_asset_multi_options(n):
    if n == 3:
        try:
            assets_flat_json = api_client.get_json("/assets", deep=False)
            assets_flat: List[AssetNodeFlat] = [
                AssetNodeFlat.from_json(m) for m in assets_flat_json
            ]
        except RequestException as err:
            print("API not available when loading layout!")
            assets_flat: List[AssetNodeFlat] = []

        return [{"label": asset.caption, "value": asset.iri} for asset in assets_flat]
        return [
            {"label": "New York Citya", "value": "NYCa"},
            {"label": "Montreala", "value": "MTLa"},
            {"label": "San Franciscoa", "value": "SFa"},
        ]
    else:
        raise PreventUpdate
