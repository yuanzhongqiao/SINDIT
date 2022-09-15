from datetime import datetime
from dash import html
import dash_bootstrap_components as dbc
from dash import html, dcc

import dash_mantine_components as dmc
import dash_daq as daq


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
                                        storage_type="session",
                                    ),
                                    dcc.Store(
                                        id="annotation-creation-store-asset",
                                        storage_type="session",
                                    ),
                                    dcc.Store(
                                        id="annotation-creation-store-definition",
                                        storage_type="session",
                                    ),
                                    dcc.Store(
                                        id="annotation-creation-store-new-definition-description",
                                        storage_type="session",
                                    ),
                                    dcc.Store(
                                        id="annotation-creation-store-new-definition-id-short",
                                        storage_type="session",
                                    ),
                                    dcc.Store(
                                        id="annotation-creation-store-new-definition-caption",
                                        storage_type="session",
                                    ),
                                    dcc.Store(
                                        id="annotation-creation-store-caption",
                                        storage_type="session",
                                    ),
                                    dcc.Store(
                                        id="annotation-creation-store-description",
                                        storage_type="session",
                                    ),
                                    dcc.Store(
                                        id="annotation-creation-store-selected-ts",
                                        storage_type="session",
                                    ),
                                    dcc.Store(
                                        id="annotation-creation-store-ts-list",
                                        storage_type="session",
                                    ),
                                    dcc.Store(
                                        id="annotation-creation-store-range-start",
                                        storage_type="session",
                                    ),
                                    dcc.Store(
                                        id="annotation-creation-store-range-end",
                                        storage_type="session",
                                    ),
                                    dcc.Store(
                                        id="annotation-creation-saved",
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
                                                    "5. Give the annotation a caption and description",
                                                    html.Div(
                                                        id="annotation-creation-step-list-5-caption-description-result",
                                                        className="annotation-creation-step-list-result",
                                                    ),
                                                ],
                                                id="annotation-creation-step-list-5-caption-description",
                                            ),
                                            # dbc.ListGroupItem(
                                            #     [
                                            #         "6. Describe the situation",
                                            #         html.Div(
                                            #             id="annotation-creation-step-list-6-description-result",
                                            #             className="annotation-creation-step-list-result",
                                            #         ),
                                            #     ],
                                            #     id="annotation-creation-step-list-6-description",
                                            # ),
                                        ],
                                        flush=True,
                                    ),
                                    html.Div(
                                        id="annotation-creation-step-2-definition-form",
                                        className="hide-content",
                                        children=[
                                            dbc.Checklist(
                                                id="new-annotation-definition-switch-input",
                                                options=[
                                                    {
                                                        "label": "Create a new annotation type definition instead",
                                                        "value": True,
                                                    }
                                                ],
                                                value=[],
                                                persistence=True,
                                                switch=True,
                                                persistence_type="session",
                                            ),
                                            html.Div(
                                                "ID_Short:",
                                                style={
                                                    "font-weight": "bold",
                                                    "margin-bottom": "5px",
                                                },
                                            ),
                                            dbc.Input(
                                                id="annotation-definition-id-short-input",
                                                placeholder="Define a short identifier...",
                                                size="sm",
                                                style={
                                                    "margin-right": "5px",
                                                    "width": "300px",
                                                },
                                                persistence=True,
                                                persistence_type="session",
                                                disabled=True,
                                            ),
                                            html.Div(
                                                "Caption:",
                                                style={
                                                    "font-weight": "bold",
                                                    "margin-bottom": "5px",
                                                },
                                            ),
                                            dbc.Input(
                                                id="annotation-definition-caption-input",
                                                placeholder="Define a short caption...",
                                                size="sm",
                                                style={
                                                    "margin-right": "5px",
                                                    "width": "300px",
                                                },
                                                persistence=True,
                                                persistence_type="session",
                                                disabled=True,
                                            ),
                                            html.Div(
                                                "Solution Proposal:",
                                                style={
                                                    "font-weight": "bold",
                                                    "margin-bottom": "5px",
                                                    "margin-top": "10px",
                                                },
                                            ),
                                            dbc.Textarea(
                                                id="annotation-definition-proposal-input",
                                                placeholder="What should be done when this situation occurs...",
                                                size="sm",
                                                style={
                                                    "width": "300px",
                                                    "height": "100px",
                                                },
                                                persistence=True,
                                                persistence_type="session",
                                                disabled=True,
                                            ),
                                            html.Div(
                                                "Description (optional):",
                                                style={
                                                    "font-weight": "bold",
                                                    "margin-bottom": "5px",
                                                    "margin-top": "10px",
                                                },
                                            ),
                                            dbc.Textarea(
                                                id="annotation-definition-description-input",
                                                placeholder="Describe the situation...",
                                                size="sm",
                                                style={
                                                    "width": "300px",
                                                    "height": "100px",
                                                },
                                                persistence=True,
                                                persistence_type="session",
                                                disabled=True,
                                            ),
                                        ],
                                    ),
                                    html.Div(
                                        id="annotation-creation-step-3-ts-form",
                                        className="hide-content",
                                        children=[
                                            html.Div(
                                                "You can collapse the annotations-card and continue to use the time-series range selection.",
                                                style={
                                                    "width": "300px",
                                                    "margin-bottom": "10px",
                                                    "text-align": "center",
                                                },
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
                                    html.Div(
                                        id="annotation-creation-step-4-range-form",
                                        className="hide-content",
                                        children=[
                                            html.Div(
                                                "Select a range by opening the data-tab of a time-series input and drawing an area in the graph with the mouse.",
                                                style={
                                                    "width": "300px",
                                                    "font-weight": "bold",
                                                    "text-align": "center",
                                                },
                                            ),
                                            html.Div(
                                                "Begin of the visible range:",
                                                style={
                                                    "font-weight": "bold",
                                                    "margin-bottom": "5px",
                                                    "margin-top": "20px",
                                                },
                                            ),
                                            html.Div(
                                                [
                                                    dmc.DatePicker(
                                                        id="annotation-creation-date-selector-start",
                                                        persistence=True,
                                                        persistence_type="session",
                                                        style={"margin-right": "5px"},
                                                    ),
                                                    dmc.TimeInput(
                                                        id="annotation-creation-time-selector-start",
                                                        withSeconds=True,
                                                        persistence=True,
                                                        persistence_type="session",
                                                    ),
                                                ],
                                                className="annotation-creation-datetime-pair",
                                            ),
                                            html.Div(
                                                "End of the visible range:",
                                                style={
                                                    "font-weight": "bold",
                                                    "margin-bottom": "5px",
                                                    "margin-top": "10px",
                                                },
                                            ),
                                            html.Div(
                                                [
                                                    dmc.DatePicker(
                                                        id="annotation-creation-date-selector-end",
                                                        persistence=True,
                                                        persistence_type="session",
                                                        style={"margin-right": "5px"},
                                                    ),
                                                    dmc.TimeInput(
                                                        id="annotation-creation-time-selector-end",
                                                        withSeconds=True,
                                                        persistence=True,
                                                        persistence_type="session",
                                                    ),
                                                ],
                                                className="annotation-creation-datetime-pair",
                                            ),
                                        ],
                                    ),
                                    html.Div(
                                        id="annotation-creation-step-5-caption-description-form",
                                        className="hide-content",
                                        children=[
                                            html.Div(
                                                "Caption:",
                                                style={
                                                    "font-weight": "bold",
                                                    "margin-bottom": "5px",
                                                },
                                            ),
                                            dbc.Input(
                                                id="annotation-caption-input",
                                                placeholder="Provide a short caption...",
                                                size="sm",
                                                style={
                                                    "margin-right": "5px",
                                                    "width": "300px",
                                                },
                                                persistence=True,
                                                persistence_type="session",
                                            ),
                                            html.Div(
                                                "Description (optional):",
                                                style={
                                                    "font-weight": "bold",
                                                    "margin-bottom": "5px",
                                                    "margin-top": "10px",
                                                },
                                            ),
                                            dbc.Textarea(
                                                id="annotation-description-input",
                                                placeholder="Describe the situation...",
                                                size="sm",
                                                style={
                                                    "width": "300px",
                                                    "height": "120px",
                                                },
                                                persistence=True,
                                                persistence_type="session",
                                            ),
                                        ],
                                    ),
                                ],
                            ),
                            html.Div(
                                id="annotations-create_buttons-container",
                                className="annotations-bottom-buttons",
                                children=[
                                    dcc.ConfirmDialog(
                                        id="confirm-cancel-annotation-creation",
                                        message="Are you sure you want to discard the annotation?",
                                    ),
                                    dbc.Button(
                                        "Cancel",
                                        id="cancel-create-annotation-button",
                                        color="secondary",
                                        size="sm",
                                        style={"margin-right": "5px"},
                                    ),
                                    dbc.Button(
                                        "Previous Step",
                                        id="back-create-annotation-button",
                                        color="primary",
                                        size="sm",
                                        disabled=True,
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
