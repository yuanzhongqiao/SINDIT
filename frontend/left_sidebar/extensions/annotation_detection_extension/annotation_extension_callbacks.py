from datetime import datetime
from enum import Enum
import json
from typing import List
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
    TS_SELECTION = 3
    FINISHED = 4


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


@app.callback(
    Output("annotation-creation-store-definition", "data"),
    Input("selected-graph-element-store", "data"),
    State("annotation-creation-store-step", "data"),
    prevent_initial_call=True,
)
def annotation_select_definition(selected_el_json, current_step):
    if (
        selected_el_json is None
        or current_step is None
        or current_step != CreationSteps.DEFINITION_SELECTION.value
    ):
        raise PreventUpdate()

    selected_el: GraphSelectedElement = GraphSelectedElement.from_json(selected_el_json)

    if selected_el.type == NodeTypes.ANNOTATION_DEFINITION.value:
        return selected_el.to_json()
    else:
        raise PreventUpdate()


@app.callback(
    Output("annotation-creation-store-selected-ts", "data"),
    Input("selected-graph-element-store", "data"),
    State("annotation-creation-store-step", "data"),
    prevent_initial_call=True,
)
def annotation_select_ts(selected_el_json, current_step):
    if (
        selected_el_json is None
        or current_step is None
        or current_step != CreationSteps.TS_SELECTION.value
    ):
        raise PreventUpdate()

    selected_el: GraphSelectedElement = GraphSelectedElement.from_json(selected_el_json)

    if selected_el.type == NodeTypes.TIMESERIES_INPUT.value:
        return selected_el.to_json()
    else:
        raise PreventUpdate()


@app.callback(
    Output("annotation-creation-store-ts-list", "data"),
    State("annotation-creation-store-ts-list", "data"),
    State("annotation-creation-store-selected-ts", "data"),
    Input("annotation-remove-ts-button", "n_clicks"),
    Input("annotation-add-ts-button", "n_clicks"),
    Input("annotation-creation-store-step", "data"),
    prevent_initial_call=True,
)
def annotation_select_ts_list(ts_list_json, selected_ts_json, remove, add, step):
    trigger = ctx.triggered_id

    if step is None:
        return None

    if ts_list_json is not None:
        ts_jsons_list: List = json.loads(ts_list_json)
    else:
        ts_jsons_list: List = []

    if trigger == "annotation-remove-ts-button" and len(ts_jsons_list) > 0:
        ts_jsons_list.pop()
        return json.dumps(ts_jsons_list)
    elif trigger == "annotation-add-ts-button" and selected_ts_json is not None:
        ts_jsons_list.append(selected_ts_json)
        return json.dumps(ts_jsons_list)
    else:
        raise PreventUpdate()


##########################################
# Step-management:
##########################################


@app.callback(
    Output("annotation-creation-store-step", "data"),
    State("annotation-creation-store-step", "data"),
    # Input("annotation-creation-store-asset", "data"),
    Input("continue-create-annotation-button", "n_clicks"),
    Input("cancel-create-annotation-button", "n_clicks"),
    Input("create-annotation-button", "n_clicks"),
    prevent_initial_call=True,
)
def annotation_create_step_update(current_step, contin, cancel, start):
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
    if trigger == "continue-create-annotation-button":
        return current_step + 1


##########################################
# Visual outputs:
##########################################


@app.callback(
    Output("save-create-annotation-button", "className"),
    Output("continue-create-annotation-button", "className"),
    Input("annotation-creation-store-step", "data"),
    prevent_initial_call=False,
)
def annotation_create_button_replacal(current_step):
    if current_step is None or current_step < CreationSteps.FINISHED.value:
        return HIDE, SHOW
    else:
        return SHOW, HIDE


@app.callback(
    Output("continue-create-annotation-button", "disabled"),
    Input("annotation-creation-store-step", "data"),
    Input("annotation-creation-store-asset", "data"),
    Input("annotation-creation-store-definition", "data"),
    Input("annotation-creation-store-ts-list", "data"),
    prevent_initial_call=False,
)
def annotation_next_step_button_activate(
    current_step, selected_asset, selected_definition, selected_ts_list
):

    if (
        (
            current_step == CreationSteps.ASSET_SELECTION.value
            and selected_asset is not None
        )
        or (
            current_step == CreationSteps.DEFINITION_SELECTION.value
            and selected_definition is not None
        )
        or (
            current_step == CreationSteps.TS_SELECTION.value
            and selected_ts_list is not None
        )
    ):
        return False

    return True


@app.callback(
    Output("annotation-creation-step-3-ts-form", "className"),
    Input("annotation-creation-store-step", "data"),
    prevent_initial_call=False,
)
def annotation_ts_form_hide(current_step):

    if current_step == CreationSteps.TS_SELECTION.value:
        return SHOW
    else:
        return HIDE


@app.callback(
    Output("annotation-creation-step-list-1-asset", "className"),
    Output("annotation-creation-step-list-2-definition", "className"),
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
    Input("annotation-creation-store-step", "data"),
    Input("annotation-creation-store-asset", "data"),
    prevent_initial_call=False,
)
def annotation_result_visualization_asset(current_step, asset_json):

    if (
        current_step is not None
        and current_step >= CreationSteps.ASSET_SELECTION.value
        and asset_json is not None
    ):
        asset = GraphSelectedElement.from_json(asset_json)
        return LIST_RESULT_PREFIX + asset.caption
    else:
        return ""


@app.callback(
    Output("annotation-creation-step-list-2-definition-result", "children"),
    Input("annotation-creation-store-step", "data"),
    Input("annotation-creation-store-definition", "data"),
    prevent_initial_call=False,
)
def annotation_result_visualization_definition(current_step, definition_json):

    if (
        current_step is not None
        and current_step >= CreationSteps.DEFINITION_SELECTION.value
        and definition_json is not None
    ):
        definition = GraphSelectedElement.from_json(definition_json)
        return LIST_RESULT_PREFIX + definition.caption
    else:
        return ""


@app.callback(
    Output("annotation-creation-step-list-3-ts-result", "children"),
    Input("annotation-creation-store-step", "data"),
    Input("annotation-creation-store-ts-list", "data"),
    prevent_initial_call=False,
)
def annotation_result_visualization_ts(current_step, ts_list_json):

    if (
        current_step is not None
        and current_step >= CreationSteps.TS_SELECTION.value
        and ts_list_json is not None
    ):
        ts_list = [
            GraphSelectedElement.from_json(ts_json)
            for ts_json in json.loads(ts_list_json)
        ]
        return LIST_RESULT_PREFIX + ", ".join([ts.caption for ts in ts_list])
    else:
        return ""
