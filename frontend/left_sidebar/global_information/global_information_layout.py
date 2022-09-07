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
                        dbc.Table(
                            [
                                html.Tr(
                                    [
                                        html.Td("System time:"),
                                        html.Td(
                                            id="status-system-time",
                                            children=[],
                                            className="content-td",
                                        ),
                                    ]
                                ),
                                html.Tr(
                                    [
                                        html.Td("Database connections:"),
                                        html.Td(
                                            id="status-db-connections",
                                            children=[],
                                            className="content-td",
                                        ),
                                    ]
                                ),
                                html.Tr(
                                    [
                                        html.Td("Time-series connections:"),
                                        html.Td(
                                            id="status-ts-connections",
                                            children=[],
                                            className="content-td",
                                        ),
                                    ]
                                ),
                                html.Tr(
                                    [
                                        html.Td("Time-series inputs:"),
                                        html.Td(
                                            id="status-ts-inputs",
                                            children=[],
                                            className="content-td",
                                        ),
                                    ]
                                ),
                                html.Tr(
                                    [
                                        html.Td("Assets"),
                                        html.Td(
                                            id="status-assets-count",
                                            children=[],
                                            className="content-td",
                                        ),
                                    ]
                                ),
                            ]
                        ),
                    ],
                )
            ),
        ],
        style={"margin-bottom": "1rem"},
    )


# def get_content():
#     return html.Div("Will contain connection status etc...")
#     # TODO: connection status, time, node count, edge count...
#     # Directly load from the API as this will be reloaded frequently
