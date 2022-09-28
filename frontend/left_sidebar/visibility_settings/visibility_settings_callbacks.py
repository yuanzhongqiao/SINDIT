import json
from frontend.app import app
from dash.dependencies import Input, Output, State
from dash import ctx
from frontend.main_column.factory_graph.GraphSelectedElement import GraphSelectedElement
from typing import List
from frontend import api_client
from graph_domain.main_digital_twin.AssetNode import AssetNodeFlat
from requests.exceptions import RequestException
from dash.exceptions import PreventUpdate
from frontend.left_sidebar.extensions.annotation_detection_extension.annotation_creation.annotation_creation_callbacks import (
    CreationSteps,
)
from frontend.main_column.factory_graph.factory_graph_layout import (
    CY_GRAPH_STYLE_STATIC,
)
from graph_domain.factory_graph_types import (
    NODE_TYPE_STRINGS,
    PSEUDO_NODE_TYPE_STRINGS,
    NodeTypes,
    PseudoNodeTypes,
)
from util.log import logger

logger.info("Initializing visibility settings callbacks...")


@app.callback(
    Output("cytoscape-graph", "stylesheet"),
    Input("visibility-switches-input", "value"),
    Input("annotation-creation-store-step", "data"),
    Input("asset-multi-select-dropdown", "value"),
    State("annotation-creation-store-asset", "data"),
    State("annotation-creation-store-ts-list", "data"),
    Input("annotation-detection-details-store", "data"),
)
def change_graph_visibility_options(
    active_switches,
    annotation_creation_step,
    selected_assets,
    annotation_creation_asset_json,
    annotation_creation_ts_list_json,
    detection_details,
):
    """
    Toggles the visibility of element types in the main graph
    :param value:
    :return:
    """
    invisibility_styles = []
    iri_filter_list = []

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
        # Only show ts and the asset:
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
    elif (
        annotation_creation_step is not None
        and annotation_creation_step >= CreationSteps.RANGE_SELECTION.value
    ):
        # Block all. Unblock specified with rule below:
        deactivated_switches = NODE_TYPE_STRINGS
        # Only show selected time-series and asset:
        ts_list = json.loads(annotation_creation_ts_list_json)
        for ts_json in ts_list:
            ts = GraphSelectedElement.from_json(ts_json)
            iri_filter_list.append(ts.iri)
        selected_asset: GraphSelectedElement = GraphSelectedElement.from_json(
            annotation_creation_asset_json
        )
        iri_filter_list.append(selected_asset.iri)

    else:
        # Use regular user-based visibility settings:
        deactivated_switches = [
            switch for switch in NODE_TYPE_STRINGS if switch not in active_switches
        ]

    # Filter, if new detection:
    if detection_details is not None and ctx.triggered_id not in [
        "asset-multi-select-dropdown",
        "visibility-switches-input",
    ]:
        # Only showdetected asset and original annotated one
        selected_assets = [
            detection_details.get("asset_iri"),
            detection_details.get("original_annotated_asset_iri"),
        ]
        # Show ts, the asset and annotation types:
        deactivated_switches = [
            switch
            for switch in NODE_TYPE_STRINGS
            if switch
            not in [
                NodeTypes.TIMESERIES_INPUT.value,
                NodeTypes.ASSET.value,
                NodeTypes.ANNOTATION_DEFINITION.value,
                NodeTypes.ANNOTATION_INSTANCE.value,
                NodeTypes.ANNOTATION_TS_MATCHER.value,
                NodeTypes.ANNOTATION_DETECTION.value,
                NodeTypes.ANNOTATION_PRE_INDICATOR.value,
            ]
        ]

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

    # IRI-based selector (making visible, not invisible):
    for iri in iri_filter_list:
        invisibility_styles.append(
            {"selector": f"node[iri = '{iri}']", "style": {"display": "element"}}
        )

    return CY_GRAPH_STYLE_STATIC + invisibility_styles


@app.callback(
    Output("visibility-settings-ignored-info", "className"),
    Input("annotation-creation-store-step", "data"),
)
def inform_graph_visibility_ignored(annotation_creation_step):

    if annotation_creation_step is not None:
        return ""
    else:
        return "hide-content"


@app.callback(
    Output("asset-multi-select-dropdown", "options"),
    Input("interval-component-factory-graph-initial-loading", "n_intervals"),
    prevent_initial_call=True,
)
def update_asset_multi_options(n):
    if n == 3:  # Do not load everything at once
        try:
            assets_flat_json = api_client.get_json("/assets", deep=False)
            assets_flat: List[AssetNodeFlat] = [
                AssetNodeFlat.from_json(m) for m in assets_flat_json
            ]
        except RequestException as err:
            logger.info("API not available when loading layout!")
            assets_flat: List[AssetNodeFlat] = []

        return [{"label": asset.caption, "value": asset.iri} for asset in assets_flat]
    else:
        raise PreventUpdate
