from frontend.app import app
from dash.dependencies import Input, Output

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
)
def change_graph_visibility_options(active_switches, annotation_creation_step):
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
    shown_asset_iris = [
        "www.sintef.no/aas_identifiers/learning_factory/machines/dps",
        "www.sintef.no/aas_identifiers/learning_factory/machines/hbw",
    ]
    selectors = [f"node[associated_assets !*= '{iri}']" for iri in shown_asset_iris]
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
