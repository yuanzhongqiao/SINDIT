from dash import html, dcc
import dash_bootstrap_components as dbc
from frontend.app import app


def get_layout():
    """
    Layout of the navbar
    :return:
    """
    return dbc.Navbar(
        children=[
            html.A(
                # Use row and col to control vertical alignment of logo / brand
                dbc.Row(
                    [
                        dbc.Col(
                            html.Img(
                                # src=app.get_asset_url("sintef_white.png"),
                                src=app.get_asset_url("sindit_logo_text.svg"),
                                height="32px",
                            )
                        ),
                    ],
                    align="center",
                ),
                href="https://www.sintef.no",
            ),
            html.Div(
                [
                    dbc.Button(
                        [
                            html.I(className="bi bi-download me-2"),
                            "Import / Export",
                        ],
                        id="import-export-button",
                        n_clicks=0,
                        color="primary",
                        size="sm",
                        style={"border": "none", "margin-right": "10px"},
                    ),
                    dbc.Button(
                        [html.I(className="bi bi-info-circle-fill me-2"), "Help"],
                        id="help-button",
                        n_clicks=0,
                        color="primary",
                        size="sm",
                        style={"border": "none"},
                    ),
                ]
            ),
            dbc.Popover(
                id="import-export-dropdown",
                is_open=False,
                children=[
                    dbc.PopoverHeader("Export"),
                    dbc.PopoverBody(
                        children=[
                            html.Div(
                                "Here, you can export the current state of either the whole system, or of specific databases."
                            ),
                            dbc.Button(
                                [
                                    html.I(className="bi bi-download me-2"),
                                    "Export all",
                                ],
                                id="export-all-button",
                                n_clicks=0,
                                color="primary",
                                size="sm",
                                style={
                                    "border": "none",
                                    "margin-top": "10px",
                                    "width": "100%",
                                    "margin-bottom": "10px",
                                },
                            ),
                            dcc.Dropdown(
                                [],
                                None,
                                id="exportable-databases-dropdown",
                            ),
                            dbc.Button(
                                [
                                    html.I(className="bi bi-download me-2"),
                                    "Export selected",
                                ],
                                id="export-single-button",
                                n_clicks=0,
                                color="primary",
                                size="sm",
                                style={
                                    "border": "none",
                                    "width": "100%",
                                    "margin-top": "10px",
                                },
                                disabled=True,
                            ),
                            dcc.Download(id="export-download"),
                            dbc.Alert(
                                children="Export started. This can take a while!",
                                id="export-started-notifier",
                                class_name="inline-alert",
                                is_open=False,
                                duration=5000,
                                style={"padding-top": "8px"},
                            ),
                        ],
                    ),
                    dbc.PopoverHeader("Import"),
                    dbc.PopoverBody(
                        [
                            html.Div(
                                "Here, you can import backups of either the whole system, or of specific databases.\n"
                                "The backups must be a valid ZIP archive as can be exported above."
                            ),
                            dcc.Upload(
                                id="upload-import",
                                children=html.Div(
                                    [
                                        "Drag and Drop or ",
                                        html.A("Click to Select a File"),
                                    ]
                                ),
                                style={
                                    "width": "100%",
                                    "height": "60px",
                                    "lineHeight": "60px",
                                    "borderWidth": "1px",
                                    "borderStyle": "dashed",
                                    "borderRadius": "5px",
                                    "textAlign": "center",
                                    "margin-top": "10px",
                                },
                                multiple=False,
                            ),
                            dbc.Collapse(
                                id="import-file-selected-info-collapse",
                                is_open=False,
                                children=[
                                    html.Div(
                                        "File selected for import:",
                                        style={
                                            "font-weight": "bold",
                                            "padding-top": "10px",
                                        },
                                    ),
                                    html.Div(id="import-file-selected-info"),
                                ],
                            ),
                            dbc.Button(
                                [
                                    html.I(className="bi bi-upload me-2"),
                                    "Import",
                                ],
                                id="import-upload-button",
                                n_clicks=0,
                                color="primary",
                                size="sm",
                                style={
                                    "border": "none",
                                    "margin-top": "10px",
                                    "width": "100%",
                                    "margin-bottom": "10px",
                                },
                                disabled=True,
                            ),
                            dbc.Alert(
                                children="Import started. This can take a while!",
                                id="import-started-notifier",
                                class_name="inline-alert",
                                is_open=False,
                                duration=5000,
                                style={"padding-top": "8px"},
                            ),
                            dcc.Store(
                                id="import-finished",
                                storage_type="memory",
                            ),
                        ]
                    ),
                ],
                target="import-export-button",
                placement="bottom",
            ),
            dbc.Offcanvas(
                [
                    html.P(
                        [
                            html.Div(
                                "Graph and Interaction:", style={"font-weight": "bold"}
                            ),
                            html.Div(
                                "Click on an element to select it. A side panel will open and display more detailed information and live data.",
                                style={"padding-bottom": "5px"},
                            ),
                            html.Div(
                                "To change the position of a node, move it around via 'drag-and-drop'. Afterwards, click on it. A button will appear below the graph, allowing to persist the new node position."
                            ),
                        ]
                    ),
                ],
                id="help-offcanvas",
                title="SINDIT – Information and Help",
                is_open=False,
            ),
        ],
    )
