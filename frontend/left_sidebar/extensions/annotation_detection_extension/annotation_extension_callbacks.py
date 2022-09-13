from datetime import datetime
from frontend.app import app
from dash.dependencies import Input, Output
import pytz
from frontend import api_client

from dash import html, ctx

from frontend.left_sidebar.global_information import global_information_layout
from util.environment_and_configuration import ConfigGroups, get_configuration

print("Initializing annotation extension callbacks...")


@app.callback(
    Output("annotation-information-collapse", "is_open"),
    Output("annotation-create-collapse", "is_open"),
    Input("create-annotation-button", "n_clicks"),
    Input("cancel-create-annotation-button", "n_clicks"),
    Input("save-create-annotation-button", "n_clicks"),
    prevent_initial_call=True,
)
def select_similarity_pipeline_sidebar(n_clicks_create, n_clicks_cancel, n_clicks_save):

    button_clicked = ctx.triggered_id
    if button_clicked == "create-annotation-button":
        return False, True
    else:
        return True, False
