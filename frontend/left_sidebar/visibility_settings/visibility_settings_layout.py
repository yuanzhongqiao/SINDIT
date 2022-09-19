from typing import List
import dash_bootstrap_components as dbc
from dash import html, dcc

from requests.exceptions import RequestException
from frontend import api_client
from graph_domain.factory_graph_types import (
    NodeTypes,
    PseudoNodeTypes,
)
from graph_domain.main_digital_twin.AssetNode import AssetNodeFlat


def get_layout():
    """
    Layout of the visibility settings
    :return:
    """
    print(
        "Loading available assets to be provided as options for the graph visibility multiselect..."
    )
    assets_flat_json = api_client.get_json("/assets", deep=False)
    assets_flat: List[AssetNodeFlat] = [
        AssetNodeFlat.from_json(m) for m in assets_flat_json
    ]
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
                "Show or hide types of nodes:",
                id="visibility-checklist-info",
            ),
            dbc.Checklist(
                options=[
                    {"label": "Assets", "value": NodeTypes.ASSET.value},
                    {
                        "label": "Timeseries inputs",
                        "value": NodeTypes.TIMESERIES_INPUT.value,
                    },
                    {
                        "label": "Supplementary files",
                        "value": NodeTypes.SUPPLEMENTARY_FILE.value,
                    },
                    {
                        "label": "Database connections",
                        "value": NodeTypes.DATABASE_CONNECTION.value,
                    },
                    {
                        "label": "Runtime connections",
                        "value": NodeTypes.RUNTIME_CONNECTION.value,
                    },
                    {"label": "Units", "value": NodeTypes.UNIT.value},
                    {
                        "label": "Timeseries clusters",
                        "value": NodeTypes.TIMESERIES_CLUSTER.value,
                    },
                    {
                        "label": "Extracted keywords",
                        "value": NodeTypes.EXTRACTED_KEYWORD.value,
                    },
                    {
                        "label": "Asset similarities",
                        "value": PseudoNodeTypes.ASSET_SIMILARITY_PSEUDO_NODE.value,
                    },
                    {
                        "label": "Annotation definitions",
                        "value": NodeTypes.ANNOTATION_DEFINITION.value,
                    },
                    {
                        "label": "Annotation instances",
                        "value": NodeTypes.ANNOTATION_INSTANCE.value,
                    },
                    {
                        "label": "Annotation pre-indicators",
                        "value": NodeTypes.ANNOTATION_PRE_INDICATOR.value,
                    },
                    {
                        "label": "Annotation timeseries matchers",
                        "value": NodeTypes.ANNOTATION_TS_MATCHER.value,
                    },
                ],
                value=[
                    NodeTypes.ASSET.value,
                    NodeTypes.TIMESERIES_INPUT.value,
                    NodeTypes.SUPPLEMENTARY_FILE.value,
                ],
                id="visibility-switches-input",
                switch=True,
                persistence=True,
                persistence_type="session",
            ),
        ]
    )
