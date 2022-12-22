from dash import html
import dash_bootstrap_components as dbc
from dash import html, dcc


def get_layout():
    return dbc.Card(
        [
            dbc.CardHeader(
                id="similarity-pipeline-container-card",
                class_name="tertiary-color",
                children=[
                    html.Div("Similarity Pipeline"),
                ],
            ),
            dbc.CardBody(
                html.Div(
                    id="pipeline-information-container",
                    className="annotations-extension-main-container",
                    children=[
                        html.Div(
                            className="node-information-attribute-header",
                            children="Stage 1 – Time-series Feature Extraction:",
                            style={"margin-top": "5px"},
                        ),
                        html.Div(
                            className="node-information-attribute-content",
                            id="pipeline-info-stage-1-status",
                            children="",
                        ),
                        dcc.Store(id="pipeline-feature-extraction-button-toggled"),
                        dbc.Button(
                            "Start Feature Extraction",
                            id="pipeline-feature-extraction-button",
                            color="primary",
                            size="sm",
                            style={"margin-top": "5px"},
                        ),
                        ###################
                        html.Div(
                            className="node-information-attribute-header",
                            children="Stage 2 – Time-series Dim. Reduction:",
                            style={"margin-top": "20px"},
                        ),
                        html.Div(
                            className="node-information-attribute-content",
                            id="pipeline-info-stage-2-status",
                            children="",
                        ),
                        dcc.Store(
                            id="pipeline-dimensionality-reduction-button-toggled"
                        ),
                        dbc.Button(
                            "Start Dimensionality Reduction",
                            id="pipeline-dimensionality-reduction-button",
                            color="primary",
                            size="sm",
                            style={"margin-top": "5px"},
                        ),
                        ###################
                        html.Div(
                            className="node-information-attribute-header",
                            children="Stage 3 – Time-series Clustering:",
                            style={"margin-top": "20px"},
                        ),
                        html.Div(
                            className="node-information-attribute-content",
                            id="pipeline-info-stage-3-status",
                            children="",
                        ),
                        dcc.Store(id="pipeline-ts-clustering-button-toggled"),
                        dbc.Button(
                            "Start Time-series Clustering",
                            id="pipeline-ts-clustering-button",
                            color="primary",
                            size="sm",
                            style={"margin-top": "5px"},
                        ),
                        ###################
                        html.Div(
                            className="node-information-attribute-header",
                            children="Stage 4 – Text Key-phrase Extraction:",
                            style={"margin-top": "20px"},
                        ),
                        html.Div(
                            className="node-information-attribute-content",
                            id="pipeline-info-stage-4-status",
                            children="",
                        ),
                        dcc.Store(
                            id="pipeline-text-keyphrase-extraction-button-toggled"
                        ),
                        dbc.Button(
                            "Start Key-phrase Extraction",
                            id="pipeline-text-keyphrase-extraction-button",
                            color="primary",
                            size="sm",
                            style={"margin-top": "5px"},
                        ),
                        ###################
                        html.Div(
                            className="node-information-attribute-header",
                            children="Stage 5 – CAD Analysis:",
                            style={"margin-top": "20px"},
                        ),
                        html.Div(
                            className="node-information-attribute-content",
                            id="pipeline-info-stage-5-status",
                            children="",
                        ),
                        dcc.Store(id="pipeline-cad-analysis-button-toggled"),
                        dbc.Button(
                            "Start CAD Analysis",
                            id="pipeline-cad-analysis-button",
                            color="primary",
                            size="sm",
                            style={"margin-top": "5px"},
                        ),
                        ###################
                        html.Div(
                            className="node-information-attribute-header",
                            children="Stage 6 – Image Analysis:",
                            style={"margin-top": "20px"},
                        ),
                        html.Div(
                            className="node-information-attribute-content",
                            id="pipeline-info-stage-6-status",
                            children="",
                        ),
                        dcc.Store(id="pipeline-image-analysis-button-toggled"),
                        dbc.Button(
                            "Start Image Analysis",
                            id="pipeline-image-analysis-button",
                            color="primary",
                            size="sm",
                            style={"margin-top": "5px"},
                        ),
                        ###################
                        html.Div(
                            className="node-information-attribute-header",
                            children="Stage 7 – Asset Similarity:",
                            style={"margin-top": "20px"},
                        ),
                        html.Div(
                            className="node-information-attribute-content",
                            id="pipeline-info-stage-7-status",
                            children="",
                        ),
                        dcc.Store(id="pipeline-asset-similarity-button-toggled"),
                        dbc.Button(
                            "Start Asset Similarity Calculation",
                            id="pipeline-asset-similarity-button",
                            color="primary",
                            size="sm",
                            style={"margin-top": "5px"},
                        ),
                        ###################
                    ],
                ),
            ),
        ],
        class_name="left-sidebar-full-height-card",
    )
