import dash_bootstrap_components as dbc

from dash import html

from frontend.main_column.factory_graph import factory_graph_layout


def get_layout():
    """
    Layout of the main column
    :return:
    """

    return html.Div(
        children=[
            factory_graph_layout.get_layout(),
        ],
        style={"flex": "5", "padding": "1rem", "width": "400px"},
    )
