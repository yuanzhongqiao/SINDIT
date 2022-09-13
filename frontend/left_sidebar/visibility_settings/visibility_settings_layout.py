import dash_bootstrap_components as dbc
from dash import html, dcc

from graph_domain.factory_graph_types import (
    NodeTypes,
    PseudoNodeTypes,
)


def get_layout():
    """
    Layout of the visibility settings
    :return:
    """
    return html.Div(
        [
            html.Div(
                "Creating annotation: Settings ignored!",
                className="hide-content",
                id="visibility-settings-ignored-info",
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
