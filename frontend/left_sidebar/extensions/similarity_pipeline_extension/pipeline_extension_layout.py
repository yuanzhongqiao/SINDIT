from dash import html
import dash_bootstrap_components as dbc
from dash import html, dcc


def get_layout():
    return dbc.Card(
        [
            dbc.CardHeader(
                id="similarity-pipeline-container-card",
                class_name="tertiary-color",
                children=[
                    html.Div("Similarity Pipeline"),
                ],
            ),
            dbc.CardBody(
                html.Div(
                    "TEST 2",
                )
            ),
        ],
        class_name="left-sidebar-full-height-card",
    )
