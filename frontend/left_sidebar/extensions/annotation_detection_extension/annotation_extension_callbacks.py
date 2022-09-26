from frontend.app import app
from dash.dependencies import Input, Output, State

from dash import ctx

from util.log import logger

logger.info("Initializing annotation extension callbacks...")

HIDE = "hide-content"
SHOW = ""

LIST_RESULT_PREFIX = "↪ "

DATETIME_STRF_FORMAT = "%Y_%m_%d_%H_%M_%S_%f"


##########################################
# Navigation:
##########################################


@app.callback(
    Output("annotation-information-collapse", "is_open"),
    Output("annotation-create-collapse", "is_open"),
    Input("create-annotation-button", "n_clicks"),
    Input("confirm-cancel-annotation-creation", "submit_n_clicks"),
    Input("annotation-creation-saved", "data"),
    State("annotation-creation-store-step", "data"),
    Input("status-unconfirmed-annotation-detection", "modified_timestamp"),
    Input("status-unconfirmed-annotation-detection", "data"),
    prevent_initial_call=False,
)
def annotation_create_collapse(
    n_clicks_create, n_clicks_cancel, n_clicks_save, step, _, new_detection
):
    trigger_id = ctx.triggered_id
    if new_detection is not None and new_detection:
        return True, False
    elif trigger_id == "create-annotation-button":
        return False, True
    elif trigger_id in [
        "confirm-cancel-annotation-creation",
        "annotation-creation-saved",
    ]:
        return True, False
    elif step is not None:
        return False, True
    else:
        return True, False
