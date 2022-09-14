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
                                    dcc.Store(
                                        id="annotation-creation-store-step",
                                        storage_type="memory",
                                    ),
                                    dcc.Store(
                                        id="annotation-creation-store-asset",
                                        storage_type="memory",
                                    ),
                                    dcc.Store(
                                        id="annotation-creation-store-definition",
                                        storage_type="memory",
                                    ),
                                    dcc.Store(
                                        id="annotation-creation-store-new-definition-description",
                                        storage_type="memory",
                                    ),
                                    dcc.Store(
                                        id="annotation-creation-store-new-definition-id-short",
                                        storage_type="memory",
                                    ),
                                    dcc.Store(
                                        id="annotation-creation-store-new-definition-caption",
                                        storage_type="memory",
                                    ),
                                    dcc.Store(
                                        id="annotation-creation-store-caption",
                                        storage_type="memory",
                                    ),
                                    dcc.Store(
                                        id="annotation-creation-store-description",
                                        storage_type="memory",
                                    ),
                                    dcc.Store(
                                        id="annotation-creation-store-selected-ts",
                                        storage_type="memory",
                                    ),
                                    dcc.Store(
                                        id="annotation-creation-store-ts-list",
                                        storage_type="memory",
                                    ),
                                    dbc.ListGroup(
                                        [
                                            dbc.ListGroupItem(
                                                [
                                                    "1. Select an asset",
                                                    html.Div(
                                                        id="annotation-creation-step-list-1-asset-result",
                                                        className="annotation-creation-step-list-result",
                                                    ),
                                                ],
                                                id="annotation-creation-step-list-1-asset",
                                            ),
                                            dbc.ListGroupItem(
                                                [
                                                    "2. Select an annotation type (definition)",
                                                    html.Div(
                                                        id="annotation-creation-step-list-2-definition-result",
                                                        className="annotation-creation-step-list-result",
                                                    ),
                                                ],
                                                id="annotation-creation-step-list-2-definition",
                                            ),
                                            dbc.ListGroupItem(
                                                [
                                                    "3. Select the timeseries nodes used for detecting the annotation",
                                                    html.Div(
                                                        id="annotation-creation-step-list-3-ts-result",
                                                        className="annotation-creation-step-list-result",
                                                    ),
                                                ],
                                                id="annotation-creation-step-list-3-ts",
                                            ),
                                            dbc.ListGroupItem(
                                                [
                                                    "4. Select the time-range, when the situation was detectable",
                                                    html.Div(
                                                        id="annotation-creation-step-list-4-range-result",
                                                        className="annotation-creation-step-list-result",
                                                    ),
                                                ],
                                                id="annotation-creation-step-list-4-range",
                                            ),
                                            dbc.ListGroupItem(
                                                [
                                                    "5. Give the annotation a caption",
                                                    html.Div(
                                                        id="annotation-creation-step-list-5-caption-result",
                                                        className="annotation-creation-step-list-result",
                                                    ),
                                                ],
                                                id="annotation-creation-step-list-5-caption",
                                            ),
                                            dbc.ListGroupItem(
                                                [
                                                    "6. Describe the situation",
                                                    html.Div(
                                                        id="annotation-creation-step-list-6-description-result",
                                                        className="annotation-creation-step-list-result",
                                                    ),
                                                ],
                                                id="annotation-creation-step-list-6-description",
                                            ),
                                        ],
                                        flush=True,
                                    ),
                                    html.Div(
                                        id="annotation-creation-step-3-ts-form",
                                        className="hide-content",
                                        children=[
                                            html.Div(
                                                "Select in the graph and add here.",
                                                style={"width": "fit-content"},
                                            ),
                                            html.Div(
                                                id="annotations-creation-ts-form-buttons-container",
                                                children=[
                                                    dbc.Button(
                                                        "Remove Timeseries",
                                                        id="annotation-remove-ts-button",
                                                        color="secondary",
                                                        size="sm",
                                                        style={
                                                            "margin-right": "5px",
                                                            "width": "145px",
                                                        },
                                                    ),
                                                    dbc.Button(
                                                        "Add Timeseries",
                                                        id="annotation-add-ts-button",
                                                        color="primary",
                                                        size="sm",
                                                        style={"width": "145px"},
                                                    ),
                                                ],
                                            ),
                                        ],
                                    ),
                                ],
                            ),
                            html.Div(
                                id="annotations-create_buttons-container",
                                className="annotations-bottom-buttons",
                                children=[
                                    dbc.Button(
                                        "Abort",
                                        id="cancel-create-annotation-button",
                                        color="secondary",
                                        size="sm",
                                        style={"margin-right": "5px"},
                                    ),
                                    dbc.Button(
                                        "Next Step",
                                        id="continue-create-annotation-button",
                                        color="primary",
                                        size="sm",
                                        disabled=True,
                                    ),
                                    dbc.Button(
                                        "Save Annotation",
                                        className="hide-content",
                                        id="save-create-annotation-button",
                                        color="primary",
                                        size="sm",
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
