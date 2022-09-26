import dash_bootstrap_components as dbc
from dash import html, dcc

import dash_mantine_components as dmc


def get_layout():
    return dbc.Collapse(
        id="annotation-confirmation-collapse",
        class_name="annotations-extension-vertical-collapse",
        is_open=False,
        children=[
            html.Div(
                id="annotations-confirm-container",
                className="annotations-extension-main-container",
                children=[
                    html.Div(
                        "An occurance of an annotation has been detected!",
                        style={"font-weight": "bold"},
                    ),
                    "Please check the affected asset and solution proposals and confirm or decline, whether the detected situation actually matches.",
                    dbc.Checklist(
                        id="annotation-detection-show-situation-input",
                        options=[
                            {
                                "label": "Show the detected situation when selecting the matched timeseries",
                                "value": True,
                            }
                        ],
                        value=[True],
                        switch=True,
                        style={"margin-top": "10px"},
                    ),
                    html.Div(
                        className="node-information-attribute-header",
                        children="Affected Asset:",
                        style={"margin-top": "10px"},
                    ),
                    html.Div(
                        className="node-information-attribute-content",
                        id="detection-info-asset",
                        children="",
                    ),
                    html.Div(
                        className="node-information-attribute-header",
                        children="Start of the detected occurance:",
                    ),
                    html.Div(
                        className="node-information-attribute-content",
                        id="detection-info-occurance-start",
                        children="",
                    ),
                    html.Div(
                        className="node-information-attribute-header",
                        children="End of the detected occurance:",
                    ),
                    html.Div(
                        className="node-information-attribute-content",
                        id="detection-info-occurance-end",
                        children="",
                    ),
                    html.Div(
                        className="node-information-attribute-header",
                        children="Type of the detected Annotation:",
                    ),
                    html.Div(
                        className="node-information-attribute-content",
                        id="detection-info-definition",
                        children="",
                    ),
                    html.Div(
                        className="node-information-attribute-header",
                        children="Matching annotation instance:",
                    ),
                    html.Div(
                        className="node-information-attribute-content",
                        id="detection-info-instance",
                        children="",
                    ),
                    html.Div(
                        className="node-information-attribute-header",
                        children="Solution Proposal:",
                    ),
                    html.Div(
                        className="node-information-attribute-content",
                        id="detection-info-solution-proposal",
                        children="",
                    ),
                    html.Div(
                        className="node-information-attribute-header",
                        children="Definition Description:",
                    ),
                    html.Div(
                        className="node-information-attribute-content",
                        id="detection-info-definition-description",
                        children="",
                    ),
                    html.Div(
                        className="node-information-attribute-header",
                        children="Instance Description:",
                    ),
                    html.Div(
                        className="node-information-attribute-content",
                        id="detection-info-instance-description",
                        children="",
                    ),
                ],
            ),
            html.Div(
                id="annotations-confirmation-buttons-container",
                className="annotations-bottom-buttons",
                children=[
                    dcc.ConfirmDialogProvider(
                        dbc.Button(
                            "Decline Detection",
                            id="decline-detection-button",
                            color="secondary",
                            size="sm",
                            style={"margin-right": "5px"},
                        ),
                        message="Are you sure this detection was wrong?",
                        id="decline-detection-confirm",
                    ),
                    dcc.ConfirmDialogProvider(
                        dbc.Button(
                            "Confirm Detection",
                            className="",
                            id="confirm-detection-button",
                            color="primary",
                            size="sm",
                        ),
                        message="Are you sure you want to confirm this detection?",
                        id="confirm-detection-confirm",
                    ),
                ],
            ),
        ],
    )
