import dash
from flask import Flask
import dash_bootstrap_components as dbc

"""
Plotly dash app instance.
Separated from presentation.py to avoid circular dependencies with callback files importing the "app" instance. 
"""

# Build App
external_stylesheets = [dbc.themes.SPACELAB, dbc.icons.BOOTSTRAP]
server = Flask(__name__)
app = dash.Dash(
    __name__,
    external_stylesheets=external_stylesheets,
    suppress_callback_exceptions=True,
    assets_folder="../assets",
    update_title=None,
    title="SINDIT – SINTEF Digital Twin",
    server=server,
)

# pylint: disable=W0212
app._favicon = "favicon.png"
