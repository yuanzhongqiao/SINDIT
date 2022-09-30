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
                    "This is the place where you will soon be able to view some information about the similarity pipeline (and maybe start it). Currently, the pipeline has to be manually executet via a script.",
                )
            ),
        ],
        class_name="left-sidebar-full-height-card",
    )
