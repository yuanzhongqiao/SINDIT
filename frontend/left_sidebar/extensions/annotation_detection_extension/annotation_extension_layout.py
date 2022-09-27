import dash_bootstrap_components as dbc
from dash import html, dcc
from frontend.left_sidebar.extensions.annotation_detection_extension.annotation_creation import (
    annotation_creation_layout,
)
from frontend.left_sidebar.extensions.annotation_detection_extension.annotation_detection_confirmation import (
    annotation_confirmation_layout,
)

import dash_mantine_components as dmc


def get_layout():
    return dbc.Card(
        [
            dbc.CardHeader(
                id="annotations-container-card",
                class_name="quaternary-color",
                children=[
                    html.Div("Annotation Detection"),
                ],
            ),
            dbc.CardBody(
                children=[
                    annotation_confirmation_layout.get_layout(),
                    dbc.Collapse(
                        id="annotation-information-collapse",
                        class_name="annotations-extension-vertical-collapse",
                        is_open=True,
                        children=[
                            html.Div(
                                id="annotations-information-container",
                                className="annotations-extension-main-container",
                                children=[
                                    html.Div(
                                        className="node-information-attribute-header",
                                        children="Count of Annotations:",
                                        style={"margin-top": "10px"},
                                    ),
                                    html.Div(
                                        className="node-information-attribute-content",
                                        id="annotations-info-total-count",
                                        children="",
                                    ),
                                    html.Div(
                                        className="node-information-attribute-header",
                                        children="Total Amount of Active Detectors:",
                                        style={"margin-top": "10px"},
                                    ),
                                    html.Div(
                                        className="node-information-attribute-content",
                                        id="annotations-info-scan-sum",
                                        children="",
                                    ),
                                    html.Div(
                                        className="node-information-attribute-header",
                                        children="Currently Unconfirmed Detections:",
                                        style={"margin-top": "10px"},
                                    ),
                                    html.Div(
                                        className="node-information-attribute-content",
                                        id="annotations-info-unconfirmed-detections",
                                        children="",
                                    ),
                                    html.Div(
                                        className="node-information-attribute-header",
                                        children="Total Amount of Confirmed Detections:",
                                        style={"margin-top": "10px"},
                                    ),
                                    html.Div(
                                        className="node-information-attribute-content",
                                        id="annotations-info-confirmed-detections",
                                        children="",
                                    ),
                                ],
                            ),
                            html.Div(
                                id="annotations-buttons-container",
                                className="annotations-bottom-buttons",
                                children=[
                                    dcc.ConfirmDialogProvider(
                                        children=dbc.Button(
                                            "Delete Annotation",
                                            id="delete-annotation-button",
                                            color="dark",
                                            size="sm",
                                            disabled=True,
                                            style={"margin-right": "5px"},
                                        ),
                                        id="delete-annotation-button-confirm",
                                        message="Are you sure you want to delete the selected annotation instance / definition?\n\n"
                                        "Definitions can only be deleted, if every related instance has been deleted before.",
                                    ),
                                    dbc.Button(
                                        "Create Annotation",
                                        id="create-annotation-button",
                                        color="primary",
                                        size="sm",
                                    ),
                                ],
                            ),
                        ],
                    ),
                    annotation_creation_layout.get_layout(),
                ],
            ),
        ],
        class_name="left-sidebar-full-height-card",
    )
