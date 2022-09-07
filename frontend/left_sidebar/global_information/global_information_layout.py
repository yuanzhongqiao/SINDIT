from dash import html
import dash_bootstrap_components as dbc
from dash import html, dcc


def get_layout():
    return dbc.Card(
        [
            dbc.CardHeader(
                id="global-information-container-card",
                children=[
                    html.Div("Connectivity status"),
                ],
            ),
            dbc.CardBody(
                html.Div(
                    id="global-information-container",
                    children=[
                        dcc.Loading(
                            type="dot",
                            color="#446e9b",
                            children=[],
                        )
                    ],
                )
            ),
        ],
        style={"margin-bottom": "1rem"},
    )


def get_content():
    return html.Div("Will contain connection status etc...")
    # TODO: connection status, time, node count, edge count...
    # Directly load from the API as this will be reloaded frequently
