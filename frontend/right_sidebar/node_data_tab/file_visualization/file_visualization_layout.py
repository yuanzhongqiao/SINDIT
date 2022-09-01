from dash import dcc
from dash import html
import plotly.subplots
import plotly.graph_objects as go
import dash_bootstrap_components as dbc


def get_layout():
    graph = html.Div(
        children=[
            html.Td("Supplementary file"),
            html.Div(
                [
                    dbc.Button("Download file", id="suppl_file_download_button"),
                    dcc.Download(id="suppl_file_download"),
                ]
            ),
            dbc.Alert(
                id="suppl_file_notifier",
                class_name="inline-alert",
                is_open=False,
                duration=5000,
            ),
            dcc.Loading(
                type="dot",
                color="#446e9b",
                children=[html.Div(id="suppl_file_visualization_container")],
            ),
        ]
    )
    return graph
