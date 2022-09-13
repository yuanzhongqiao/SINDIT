from datetime import datetime
from enum import Enum
from frontend.app import app
from dash.dependencies import Input, Output, State
import pytz
from frontend import api_client

from dash.exceptions import PreventUpdate
from dash import html, ctx

from frontend.left_sidebar.global_information import global_information_layout
from frontend.main_column.factory_graph.GraphSelectedElement import GraphSelectedElement
from graph_domain.factory_graph_types import NodeTypes
from util.environment_and_configuration import ConfigGroups, get_configuration

print("Initializing annotation extension callbacks...")

HIDE = "hide-content"
SHOW = ""

LIST_RESULT_PREFIX = "↪ "


class CreationSteps(Enum):
    ASSET_SELECTION = 1
    DEFINITION_SELECTION = 2


##########################################
# Navigation:
##########################################


@app.callback(
    Output("annotation-information-collapse", "is_open"),
    Output("annotation-create-collapse", "is_open"),
    Input("create-annotation-button", "n_clicks"),
    Input("cancel-create-annotation-button", "n_clicks"),
    Input("save-create-annotation-button", "n_clicks"),
    prevent_initial_call=True,
)
def annotation_create_collapse(n_clicks_create, n_clicks_cancel, n_clicks_save):

    button_clicked = ctx.triggered_id
    if button_clicked == "create-annotation-button":
        return False, True
    else:
        return True, False


##########################################
# Raw inputs:
##########################################


@app.callback(
    Output("annotation-creation-store-asset", "data"),
    Input("selected-graph-element-store", "data"),
    State("annotation-creation-store-step", "data"),
    prevent_initial_call=True,
)
def annotation_select_asset(selected_el_json, current_step):
    if (
        selected_el_json is None
        or current_step is None
        or current_step != CreationSteps.ASSET_SELECTION.value
    ):
        raise PreventUpdate()

    selected_el: GraphSelectedElement = GraphSelectedElement.from_json(selected_el_json)

    if selected_el.type == NodeTypes.ASSET.value:
        return selected_el.to_json()
    else:
        raise PreventUpdate()


##########################################
# Step-management:
##########################################


@app.callback(
    Output("annotation-creation-store-step", "data"),
    State("annotation-creation-store-step", "data"),
    Input("annotation-creation-store-asset", "data"),
    Input("cancel-create-annotation-button", "n_clicks"),
    Input("create-annotation-button", "n_clicks"),
    prevent_initial_call=True,
)
def annotation_create_step_update(current_step, asset, cancel, start):
    trigger = ctx.triggered_id

    if trigger == "cancel-create-annotation-button":
        # Start (reset to None):
        return None
    elif trigger == "create-annotation-button":
        # Start (to step 1):
        return 1
    elif current_step is None:
        # Cancel if not active (step none)
        raise PreventUpdate()

    # Walk through steps:
    if (
        current_step == CreationSteps.ASSET_SELECTION.value
    ) and trigger == "annotation-creation-store-asset":
        return CreationSteps.DEFINITION_SELECTION.value


##########################################
# Visual outputs:
##########################################


@app.callback(
    Output("annotation-creation-step-list-1-asset", "className"),
    Output("annotation-creation-step-list-2-type", "className"),
    Output("annotation-creation-step-list-3-ts", "className"),
    Output("annotation-creation-step-list-4-range", "className"),
    Output("annotation-creation-step-list-5-caption", "className"),
    Output("annotation-creation-step-list-6-description", "className"),
    Input("annotation-creation-store-step", "data"),
    prevent_initial_call=False,
)
def annotation_create_visualizations(current_step):

    if current_step is None:
        return HIDE, HIDE, HIDE, HIDE, HIDE, HIDE
    elif current_step == 1:
        return SHOW, HIDE, HIDE, HIDE, HIDE, HIDE
    elif current_step == 2:
        return SHOW, SHOW, HIDE, HIDE, HIDE, HIDE
    elif current_step == 3:
        return SHOW, SHOW, SHOW, HIDE, HIDE, HIDE
    elif current_step == 4:
        return SHOW, SHOW, SHOW, SHOW, HIDE, HIDE
    elif current_step == 5:
        return SHOW, SHOW, SHOW, SHOW, SHOW, HIDE
    elif current_step == 6:
        return SHOW, SHOW, SHOW, SHOW, SHOW, SHOW


@app.callback(
    Output("annotation-creation-step-list-1-asset-result", "children"),
    State("annotation-creation-store-asset", "data"),
    Input("annotation-creation-store-step", "data"),
    prevent_initial_call=False,
)
def annotation_create_visualizations(asset_json, current_step):

    if current_step is not None and current_step > CreationSteps.ASSET_SELECTION.value:
        asset = GraphSelectedElement.from_json(asset_json)
        return LIST_RESULT_PREFIX + asset.caption
    else:
        return ""
