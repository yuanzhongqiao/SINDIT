from dash import html
import dash_bootstrap_components as dbc
from dash import html, dcc


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
                    dbc.Collapse(
                        id="annotation-information-collapse",
                        class_name="annotations-extension-vertical-collapse",
                        is_open=True,
                        children=[
                            html.Div(
                                id="annotations-information-container",
                                className="annotations-extension-main-container",
                                children=[
                                    "Domain expert annotations information coming soon...",
                                ],
                            ),
                            html.Div(
                                id="annotations-buttons-container",
                                className="annotations-bottom-buttons",
                                children=[
                                    dbc.Button(
                                        "Delete Annotation",
                                        id="delete-annotation-button",
                                        color="dark",
                                        size="sm",
                                        disabled=True,
                                        style={"margin-right": "5px"},
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
                    dbc.Collapse(
                        id="annotation-create-collapse",
                        class_name="annotations-extension-vertical-collapse",
                        is_open=False,
                        children=[
                            html.Div(
                                id="annotations-create-container",
                                className="annotations-extension-main-container",
                                children=[
                                    "Create annotation...",
                                ],
                            ),
                            html.Div(
                                id="annotations-create_buttons-container",
                                className="annotations-bottom-buttons",
                                children=[
                                    dbc.Button(
                                        "Cancel",
                                        id="cancel-create-annotation-button",
                                        color="secondary",
                                        size="sm",
                                        style={"margin-right": "5px"},
                                    ),
                                    dbc.Button(
                                        "Save Annotation",
                                        id="save-create-annotation-button",
                                        color="primary",
                                        size="sm",
                                        disabled=True,
                                    ),
                                ],
                            ),
                        ],
                    ),
                ],
            ),
        ],
        class_name="left-sidebar-full-height-card",
    )
