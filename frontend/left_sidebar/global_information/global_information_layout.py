from dash import html
import dash_bootstrap_components as dbc


def get_layout():
    return dbc.Card([html.Div(id="global-information-container")])


def get_content():
    return html.Div("Will contain connection status etc...")
    # TODO: connection status, time, node count, edge count...
    # Directly load from the API as this will be reloaded frequently
