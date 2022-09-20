from dash import html
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
                                src=app.get_asset_url("sindit_logo_text_large.png"),
                                height="32px",
                            )
                        ),
                    ],
                    align="center",
                ),
                href="https://www.sintef.no",
            ),
            dbc.Button(
                [html.I(className="bi bi-info-circle-fill me-2"), "Help"],
                id="help-button",
                n_clicks=0,
                color="primary",
                size="sm",
                style={"border": "none"},
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
