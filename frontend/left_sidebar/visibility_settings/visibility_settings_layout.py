from lib2to3.pytree import Node
from typing import List
import dash_bootstrap_components as dbc
from dash import html, dcc
from frontend import api_client
from graph_domain.factory_graph_types import (
    NodeTypes,
    PseudoNodeTypes,
)
from graph_domain.main_digital_twin.AssetNode import AssetNodeFlat
from util.log import logger

SELECTABLE_ELEMENT_TYPES = [
    {"label": "Assets", "value": NodeTypes.ASSET.value},
    {
        "label": "Timeseries Inputs",
        "value": NodeTypes.TIMESERIES_INPUT.value,
    },
    {
        "label": "Supplementary Files",
        "value": NodeTypes.SUPPLEMENTARY_FILE.value,
    },
    {
        "label": "Database Connections",
        "value": NodeTypes.DATABASE_CONNECTION.value,
    },
    {
        "label": "Runtime Connections",
        "value": NodeTypes.RUNTIME_CONNECTION.value,
    },
    {"label": "Units", "value": NodeTypes.UNIT.value},
    {
        "label": "Timeseries Clusters",
        "value": NodeTypes.TIMESERIES_CLUSTER.value,
    },
    {
        "label": "Dimension Clusters",
        "value": NodeTypes.DIMENSION_CLUSTER.value,
    },
    {
        "label": "Extracted Keywords",
        "value": NodeTypes.EXTRACTED_KEYWORD.value,
    },
    {
        "label": "Asset Similarities",
        "value": PseudoNodeTypes.ASSET_SIMILARITY_PSEUDO_NODE.value,
    },
    {
        "label": "Annotation Definitions",
        "value": NodeTypes.ANNOTATION_DEFINITION.value,
    },
    {
        "label": "Annotation Instances",
        "value": NodeTypes.ANNOTATION_INSTANCE.value,
    },
    {
        "label": "Annotation Pre-Indicators",
        "value": NodeTypes.ANNOTATION_PRE_INDICATOR.value,
    },
    {
        "label": "Annotation Timeseries Matchers",
        "value": NodeTypes.ANNOTATION_TS_MATCHER.value,
    },
    {
        "label": "Annotation Detections",
        "value": NodeTypes.ANNOTATION_DETECTION.value,
    },
]


def get_layout():
    """
    Layout of the visibility settings
    :return:
    """
    logger.info(
        "Loading available assets to be provided as options for the graph visibility multiselect..."
    )
    assets_flat_json = api_client.get_json("/assets", deep=False, retries=2)
    if assets_flat_json is not None:
        assets_flat: List[AssetNodeFlat] = [
            AssetNodeFlat.from_json(m) for m in assets_flat_json
        ]
    else:
        # Not reachable. Selections will be lost but dropdown will fill options later
        assets_flat = []

    return html.Div(
        [
            html.Div(
                "Creating annotation: Settings ignored!",
                className="hide-content",
                id="visibility-settings-ignored-info",
            ),
            html.Div(
                "Select asset(s) to only show related nodes:",
                id="asset-multi-select-dropdown-info",
            ),
            dcc.Dropdown(
                [{"label": asset.caption, "value": asset.iri} for asset in assets_flat],
                [],
                multi=True,
                id="asset-multi-select-dropdown",
                persistence=True,
                persistence_type="session",
            ),
            html.Div(
                "Show or hide specific types of elements:",
                id="visibility-checklist-info",
            ),
            dbc.Checklist(
                options=SELECTABLE_ELEMENT_TYPES,
                value=[
                    NodeTypes.ASSET.value,
                    NodeTypes.TIMESERIES_INPUT.value,
                    NodeTypes.SUPPLEMENTARY_FILE.value,
                    PseudoNodeTypes.ASSET_SIMILARITY_PSEUDO_NODE.value,
                    NodeTypes.ANNOTATION_DEFINITION.value,
                    NodeTypes.ANNOTATION_INSTANCE.value,
                    NodeTypes.ANNOTATION_PRE_INDICATOR.value,
                    NodeTypes.ANNOTATION_TS_MATCHER.value,
                    NodeTypes.ANNOTATION_DETECTION.value,
                ],
                id="visibility-switches-input",
                switch=True,
                persistence=True,
                persistence_type="session",
            ),
        ]
    )
