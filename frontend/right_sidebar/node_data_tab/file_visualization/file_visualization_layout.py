from dash import dcc
from dash import html
import plotly.subplots
import plotly.graph_objects as go
import dash_bootstrap_components as dbc


def get_layout():
    graph = html.Div(
        className="tab-content-inner-container",
        children=[
            html.Div(
                id="suppl_file_container",
                children=[
                    dcc.Loading(
                        type="dot",
                        color="#446e9b",
                        children=[html.Div(id="suppl_file_visualization_container")],
                    ),
                    dbc.Alert(
                        id="suppl_file_notifier",
                        class_name="inline-alert",
                        is_open=False,
                        duration=3000,
                    ),
                    html.Div(
                        [
                            dbc.Button(
                                "Download file",
                                id="suppl_file_download_button",
                                color="primary",
                                size="sm",
                            ),
                            dcc.Download(id="suppl_file_download"),
                        ],
                        id="suppl_file_download_button_container",
                    ),
                ],
            )
        ],
    )
    return graph
