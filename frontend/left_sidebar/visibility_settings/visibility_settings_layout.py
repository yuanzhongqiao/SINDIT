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
            dbc.Checklist(
                options=[
                    {"label": "Show assets", "value": NodeTypes.ASSET.value},
                    {
                        "label": "Show timeseries inputs",
                        "value": NodeTypes.TIMESERIES_INPUT.value,
                    },
                    {
                        "label": "Show supplementary files",
                        "value": NodeTypes.SUPPLEMENTARY_FILE.value,
                    },
                    {
                        "label": "Show database connections",
                        "value": NodeTypes.DATABASE_CONNECTION.value,
                    },
                    {
                        "label": "Show runtime connections",
                        "value": NodeTypes.RUNTIME_CONNECTION.value,
                    },
                    {"label": "Show units", "value": NodeTypes.UNIT.value},
                    {
                        "label": "Show timeseries clusters",
                        "value": NodeTypes.TIMESERIES_CLUSTER.value,
                    },
                    {
                        "label": "Show extracted keywords",
                        "value": NodeTypes.EXTRACTED_KEYWORD.value,
                    },
                    {
                        "label": "Show asset similarities",
                        "value": PseudoNodeTypes.ASSET_SIMILARITY_PSEUDO_NODE.value,
                    },
                    {
                        "label": "Show annotation definitions",
                        "value": NodeTypes.ANNOTATION_DEFINITION.value,
                    },
                    {
                        "label": "Show annotation instances",
                        "value": NodeTypes.ANNOTATION_INSTANCE.value,
                    },
                    {
                        "label": "Show annotation pre-indicators",
                        "value": NodeTypes.ANNOTATION_PRE_INDICATOR.value,
                    },
                    {
                        "label": "Show annotation timeseries matchers",
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
            )
        ]
    )
