from dash import html, dcc
import dash_bootstrap_components as dbc
import dash_cytoscape as cyto

from frontend import resources_manager

CY_GRAPH_STYLE_STATIC = resources_manager.load_json("cytoscape-graph-style.json")


def get_layout():
    return html.Div(
        id="factory-graph-container",
        children=[
            # Storage for accessing the selected element
            dcc.Store(id="selected-graph-element-store", storage_type="session"),
            # Storage for the graph content
            dcc.Store(id="cytoscape-graph-store", storage_type="local"),
            # Timestamp for the selected element storage
            dcc.Store(id="selected-graph-element-timestamp", storage_type="session"),
            dbc.Card(
                id="factory-graph-card",
                children=[
                    dbc.CardHeader(
                        id="graph-header-container",
                        children=[
                            dbc.Row(
                                id="graph-header-row",
                                children=[
                                    dbc.Col(
                                        html.Div("Factory graph"),
                                        align="center",
                                    ),
                                    dbc.Col(
                                        dbc.Button(
                                            html.Div(
                                                [
                                                    "Reload graph",
                                                    html.Img(
                                                        src="https://fonts.gstatic.com/s/i/short-term/release/materialsymbolsrounded/refresh/wght500/48px.svg",
                                                        height=20,
                                                        width=20,
                                                        style={
                                                            # Color applied to svg as filter. Converter: (https://isotropic.co/tool/hex-color-to-css-filter/)
                                                            "filter": "invert(40%) sepia(60%) saturate(0%) hue-rotate(175deg) brightness(103%) contrast(89%)",
                                                            "margin-left": "5px",
                                                        },
                                                    ),
                                                ],
                                                id="reload-button-div",
                                            ),
                                            id="graph-reload-button",
                                            n_clicks=0,
                                            size="sm",
                                            outline=True,
                                        ),
                                        style={"max-width": "155px"},
                                        align="center",
                                    ),
                                ],
                                style={"height": "30px"},
                                align="stretch",
                                justify="between",
                            )
                        ],
                    ),
                    dbc.CardBody(
                        [
                            dcc.Store(
                                id="factory-graph-loading-state",
                                storage_type="memory",
                            ),
                            html.Div(
                                id="kg-container",
                                children=[
                                    dcc.Loading(
                                        className="kg-loading-indicator-container",
                                        id="kg-loading-indicator-container",
                                        type="dot",
                                        color="#446e9b",
                                        children=[
                                            cyto.Cytoscape(
                                                id="cytoscape-graph",
                                                layout={"name": "preset"},
                                                style={
                                                    "width": "100%",
                                                    "height": "100%",
                                                },
                                                minZoom=0.4,
                                                maxZoom=5,
                                                zoom=2,
                                                responsive=False,
                                                stylesheet=CY_GRAPH_STYLE_STATIC,
                                                className="factory-graph",
                                            ),
                                        ],
                                    )
                                ],
                            ),
                        ]
                    ),
                    dbc.CardFooter(
                        id="graph-positioning-container",
                        style={"display": "None"},
                        children=[
                            dbc.Row(
                                children=[
                                    dbc.Col(
                                        dbc.Button(
                                            "Save node position",
                                            id="graph-positioning-save-button",
                                            n_clicks=0,
                                            color="primary",
                                            size="sm",
                                        ),
                                        style={"height": "100%"},
                                    ),
                                    dbc.Col(
                                        children=[
                                            dbc.Alert(
                                                id="graph-positioning-saved-notifier",
                                                class_name="inline-alert",
                                                is_open=False,
                                                duration=5000,
                                                style={"padding-top": "8px"},
                                            )
                                        ],
                                        style={"height": "100%"},
                                        id="graph-positioning-alert-row",
                                    ),
                                ],
                                style={"height": "40px"},
                            )
                        ],
                    ),
                ],
            ),
        ],
    )
