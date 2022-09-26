from ast import Set
from datetime import datetime, timedelta
from enum import Enum
import json
from frontend.app import app
from dash.dependencies import Input, Output, State
from frontend import api_client
from dateutil import tz

from dash.exceptions import PreventUpdate
from dash import html, ctx

from dateutil import tz
from frontend.main_column.factory_graph.GraphSelectedElement import GraphSelectedElement
from graph_domain.factory_graph_types import NodeTypes
from util.environment_and_configuration import ConfigGroups, get_configuration
from util.log import logger

logger.info("Initializing annotation creation callbacks...")

HIDE = "hide-content"
SHOW = ""

LIST_RESULT_PREFIX = "↪ "

DATETIME_STRF_FORMAT = "%Y_%m_%d_%H_%M_%S_%f"


class CreationSteps(Enum):
    ASSET_SELECTION = 1
    DEFINITION_SELECTION = 2
    TS_SELECTION = 3
    RANGE_SELECTION = 4
    CAPTION_DESCRIPTION = 5
    FINISHED = 6


@app.callback(
    Output("annotation-creation-saved", "data"),
    Input("save-create-annotation-button", "n_clicks"),
    State("annotation-creation-store-step", "data"),
    State("annotation-creation-store-asset", "data"),
    State("annotation-creation-store-definition", "data"),
    State("annotation-creation-store-ts-list", "data"),
    State("annotation-creation-store-range-start", "data"),
    State("annotation-creation-store-range-end", "data"),
    State("annotation-caption-input", "value"),
    State("annotation-description-input", "value"),
    State("new-annotation-definition-switch-input", "value"),
    State("annotation-definition-id-short-input", "value"),
    State("annotation-definition-caption-input", "value"),
    State("annotation-definition-proposal-input", "value"),
    State("annotation-definition-description-input", "value"),
    prevent_initial_call=True,
)
def save_annotation(
    save_button,
    current_step,
    selected_asset_json,
    selected_definition_json,
    selected_ts_list_json,
    selected_start_datetime_str,
    selected_end_datetime_str,
    caption,
    description,
    new_annotation_switch,
    new_annotation_id_short,
    new_annotation_caption,
    new_annotation_proposal,
    new_annotation_description,
):
    if current_step is None or current_step != CreationSteps.FINISHED.value:
        logger.info("Tried to save early")
        raise PreventUpdate

    asset: GraphSelectedElement = GraphSelectedElement.from_json(selected_asset_json)

    ts_list = [
        GraphSelectedElement.from_json(ts_json)
        for ts_json in json.loads(selected_ts_list_json)
    ]

    if True in new_annotation_switch:
        logger.info(
            f"Storing new annotation definition:\n Caption: {new_annotation_caption}\nid_short: {new_annotation_id_short}"
        )
        used_definition_iri = api_client.post(
            "/annotation/definition",
            json={
                "id_short": new_annotation_id_short,
                "solution_proposal": new_annotation_proposal,
                "caption": new_annotation_caption,
                "description": new_annotation_description,
            },
        )
        used_definition_id_short = new_annotation_id_short
    else:
        definition: GraphSelectedElement = GraphSelectedElement.from_json(
            selected_definition_json
        )
        used_definition_iri = definition.iri
        used_definition_id_short = definition.id_short

    instance_id_short = f"{used_definition_id_short}_{asset.id_short}_{datetime.now().strftime(DATETIME_STRF_FORMAT)}"

    logger.info(
        f"Storing new annotation:\n Caption: {caption}\nid_short: {instance_id_short}"
    )

    api_client.post(
        "/annotation/instance",
        json={
            "id_short": instance_id_short,
            "asset_iri": asset.iri,
            "definition_iri": used_definition_iri,
            "ts_iri_list": [ts.iri for ts in ts_list],
            "start_datetime": selected_start_datetime_str,
            "end_datetime": selected_end_datetime_str,
            "caption": caption,
            "description": description,
        },
    )
    logger.info("Finished storing annotation")
    return datetime.now()


@app.callback(
    Output("confirm-cancel-annotation-creation", "displayed"),
    Input("cancel-create-annotation-button", "n_clicks"),
    prevent_initial_call=True,
)
def display_confirm(n):
    return True


##########################################
# Raw inputs:
##########################################


@app.callback(
    Output("annotation-creation-store-asset", "data"),
    Input("selected-graph-element-store", "data"),
    State("annotation-creation-store-step", "data"),
    Input("annotation-creation-saved", "data"),
    Input("confirm-cancel-annotation-creation", "submit_n_clicks"),
    prevent_initial_call=True,
)
def annotation_select_asset(selected_el_json, current_step, save_btn, cancel_btn):
    if ctx.triggered_id in [
        "annotation-creation-saved",
        "confirm-cancel-annotation-creation",
    ]:
        return None

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
    Input("annotation-creation-saved", "data"),
    Input("confirm-cancel-annotation-creation", "submit_n_clicks"),
    prevent_initial_call=True,
)
def annotation_select_definition(selected_el_json, current_step, save_btn, cancel_btn):
    if ctx.triggered_id in [
        "annotation-creation-saved",
        "confirm-cancel-annotation-creation",
    ]:
        return None

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
        return None


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
        ts_jsons_set: Set = set(json.loads(ts_list_json))
    else:
        ts_jsons_set: Set = set()

    if trigger == "annotation-remove-ts-button" and len(ts_jsons_set) > 0:
        ts_jsons_set.pop()
        return json.dumps(list(ts_jsons_set))
    elif trigger == "annotation-add-ts-button" and selected_ts_json is not None:
        ts_jsons_set.add(selected_ts_json)
        return json.dumps(list(ts_jsons_set))
    else:
        raise PreventUpdate()


@app.callback(
    Output("annotation-creation-store-range-start", "data"),
    Output("annotation-creation-store-range-end", "data"),
    Input("timeseries-graph", "selectedData"),
    State("annotation-creation-store-step", "data"),
    Input("annotation-creation-saved", "data"),
    Input("confirm-cancel-annotation-creation", "submit_n_clicks"),
    prevent_initial_call=True,
)
def annotation_select_range(selected_range, current_step, save_btn, cancel_btn):
    if ctx.triggered_id in [
        "annotation-creation-saved",
        "confirm-cancel-annotation-creation",
    ]:
        return None, None

    if (
        selected_range is None
        or current_step is None
        or current_step != CreationSteps.RANGE_SELECTION.value
        or len(selected_range["range"]) == 0
    ):
        raise PreventUpdate()
    start_datetime_str = selected_range["range"]["x"][0]
    end_datetime_str = selected_range["range"]["x"][-1]
    if len(start_datetime_str) == 24:
        start_datetime_str = start_datetime_str[0:-1]
    elif len(start_datetime_str) == 22:
        start_datetime_str = start_datetime_str + "0"
    if len(end_datetime_str) == 24:
        end_datetime_str = end_datetime_str[0:-1]
    elif len(end_datetime_str) == 22:
        end_datetime_str = end_datetime_str + "0"

    start_datetime = datetime.fromisoformat(start_datetime_str).replace(
        tzinfo=tz.gettz(get_configuration(group=ConfigGroups.FRONTEND, key="timezone"))
    )
    end_datetime = datetime.fromisoformat(end_datetime_str).replace(
        tzinfo=tz.gettz(get_configuration(group=ConfigGroups.FRONTEND, key="timezone"))
    )

    return start_datetime, end_datetime


@app.callback(
    Output("annotation-caption-input", "value"),
    Output("annotation-description-input", "value"),
    Input("annotation-creation-saved", "data"),
    Input("confirm-cancel-annotation-creation", "submit_n_clicks"),
    prevent_initial_call=True,
)
def annotation_reset_caption_description(save_btn, cancel_btn):
    if ctx.triggered_id in [
        "annotation-creation-saved",
        "confirm-cancel-annotation-creation",
    ]:
        return None, None
    else:
        raise PreventUpdate()


@app.callback(
    Output("annotation-definition-id-short-input", "value"),
    Output("annotation-definition-caption-input", "value"),
    Output("annotation-definition-proposal-input", "value"),
    Output("annotation-definition-description-input", "value"),
    Input("annotation-creation-saved", "data"),
    Input("confirm-cancel-annotation-creation", "submit_n_clicks"),
    prevent_initial_call=True,
)
def annotation_reset_definition_form(save_btn, cancel_btn):
    if ctx.triggered_id in [
        "annotation-creation-saved",
        "confirm-cancel-annotation-creation",
    ]:
        return None, None, None, None
    else:
        raise PreventUpdate()


##########################################
# Step-management:
##########################################


@app.callback(
    Output("annotation-creation-store-step", "data"),
    State("annotation-creation-store-step", "data"),
    Input("continue-create-annotation-button", "n_clicks"),
    Input("confirm-cancel-annotation-creation", "submit_n_clicks"),
    Input("create-annotation-button", "n_clicks"),
    Input("back-create-annotation-button", "n_clicks"),
    Input("annotation-creation-saved", "data"),
    prevent_initial_call=True,
)
def annotation_create_step_update(current_step, contin, cancel, start, back, save):
    trigger = ctx.triggered_id

    if trigger == "confirm-cancel-annotation-creation":
        # Start (reset to None):
        return None
    elif trigger == "save-create-annotation-button":
        # Reset creation state:
        return None
    elif trigger == "create-annotation-button":
        # Start (to step 1):
        return 1
    elif trigger == "back-create-annotation-button":
        return current_step - 1
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
    Input("annotation-creation-store-range-start", "data"),
    Input("annotation-creation-store-range-end", "data"),
    Input("annotation-caption-input", "value"),
    Input("new-annotation-definition-switch-input", "value"),
    Input("annotation-definition-id-short-input", "value"),
    Input("annotation-definition-caption-input", "value"),
    Input("annotation-definition-proposal-input", "value"),
    prevent_initial_call=False,
)
def annotation_next_step_button_activate(
    current_step,
    selected_asset,
    selected_definition,
    selected_ts_list,
    selected_start_datetime_str,
    selected_end_datetime_str,
    caption,
    new_definition_switch,
    new_definition_id_short,
    new_definition_caption,
    new_definition_proposal,
):
    selected_start_datetime = None
    selected_end_datetime = None
    if (
        selected_start_datetime_str is not None
        and selected_end_datetime_str is not None
    ):
        selector_tz = tz.gettz(
            get_configuration(group=ConfigGroups.FRONTEND, key="timezone")
        )
        selected_start_datetime = datetime.fromisoformat(selected_start_datetime_str)
        selected_end_datetime = datetime.fromisoformat(selected_end_datetime_str)

    if (
        (
            current_step == CreationSteps.ASSET_SELECTION.value
            and selected_asset is not None
        )
        or (
            current_step == CreationSteps.DEFINITION_SELECTION.value
            and (
                (selected_definition is not None and True not in new_definition_switch)
                or (
                    True in new_definition_switch
                    and new_definition_id_short is not None
                    and new_definition_id_short != ""
                    and not " " in new_definition_id_short
                    # Disallow special characters other than - and _ as well as whitespaces
                    and not any(
                        (not c.isalnum() and c != "-" and c != "_")
                        for c in new_definition_id_short
                    )
                    and new_definition_caption is not None
                    and new_definition_caption != ""
                    and new_definition_proposal is not None
                    and new_definition_proposal != ""
                )
            )
        )
        or (
            current_step == CreationSteps.TS_SELECTION.value
            and selected_ts_list is not None
        )
        or (
            current_step == CreationSteps.RANGE_SELECTION.value
            and selected_start_datetime is not None
            and selected_end_datetime is not None
            and selected_start_datetime < selected_end_datetime
            and selected_end_datetime
            < datetime.now().astimezone(
                tz.gettz(get_configuration(group=ConfigGroups.FRONTEND, key="timezone"))
            )
        )
        or (
            current_step == CreationSteps.CAPTION_DESCRIPTION.value
            and caption is not None
            and caption != ""
        )
    ):
        return False

    return True


@app.callback(
    Output("back-create-annotation-button", "disabled"),
    Input("annotation-creation-store-step", "data"),
    prevent_initial_call=False,
)
def annotation_previous_step_button_activate(current_step):
    if current_step is not None and current_step > 1:
        return False
    else:
        return True


@app.callback(
    Output("annotation-definition-id-short-input", "disabled"),
    Output("annotation-definition-caption-input", "disabled"),
    Output("annotation-definition-proposal-input", "disabled"),
    Output("annotation-definition-description-input", "disabled"),
    Input("new-annotation-definition-switch-input", "value"),
    prevent_initial_call=False,
)
def annotation_definition_form_activate(switch):
    if switch is not None and switch == [True]:
        return False, False, False, False
    else:
        return True, True, True, True


@app.callback(
    Output("annotation-creation-step-2-definition-form", "className"),
    Input("annotation-creation-store-step", "data"),
    prevent_initial_call=False,
)
def annotation_definition_form_hide(current_step):

    if current_step == CreationSteps.DEFINITION_SELECTION.value:
        return SHOW
    else:
        return HIDE


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
    Output("annotation-creation-step-4-range-form", "className"),
    Input("annotation-creation-store-step", "data"),
    prevent_initial_call=False,
)
def annotation_range_form_hide(current_step):

    if current_step == CreationSteps.RANGE_SELECTION.value:
        return SHOW
    else:
        return HIDE


@app.callback(
    Output("annotation-creation-step-5-caption-description-form", "className"),
    Input("annotation-creation-store-step", "data"),
    prevent_initial_call=False,
)
def annotation_caption_description_form_hide(current_step):

    if current_step == CreationSteps.CAPTION_DESCRIPTION.value:
        return SHOW
    else:
        return HIDE


@app.callback(
    Output("annotation-creation-step-list-1-asset", "className"),
    Output("annotation-creation-step-list-2-definition", "className"),
    Output("annotation-creation-step-list-3-ts", "className"),
    Output("annotation-creation-step-list-4-range", "className"),
    Output("annotation-creation-step-list-5-caption-description", "className"),
    # Output("annotation-creation-step-list-6-description", "className"),
    Input("annotation-creation-store-step", "data"),
    prevent_initial_call=False,
)
def annotation_create_visualizations(current_step):

    if current_step is None:
        return HIDE, HIDE, HIDE, HIDE, HIDE  # , HIDE
    elif current_step == 1:
        return SHOW, HIDE, HIDE, HIDE, HIDE  # , HIDE
    elif current_step == 2:
        return SHOW, SHOW, HIDE, HIDE, HIDE  # , HIDE
    elif current_step == 3:
        return SHOW, SHOW, SHOW, HIDE, HIDE  # , HIDE
    elif current_step == 4:
        return SHOW, SHOW, SHOW, SHOW, HIDE  # , HIDE
    elif current_step == 5:
        return SHOW, SHOW, SHOW, SHOW, SHOW  # , HIDE
    elif current_step == 6:
        return SHOW, SHOW, SHOW, SHOW, SHOW  # , SHOW


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
    Input("new-annotation-definition-switch-input", "value"),
    Input("annotation-definition-caption-input", "value"),
    prevent_initial_call=False,
)
def annotation_result_visualization_definition(
    current_step, definition_json, new_definition_switch, new_caption
):

    if (
        current_step is not None
        and current_step >= CreationSteps.DEFINITION_SELECTION.value
    ):
        if (
            True in new_definition_switch
            and new_caption is not None
            and new_caption != ""
        ):
            return LIST_RESULT_PREFIX + new_caption
        elif (not True in new_definition_switch) and definition_json is not None:
            definition = GraphSelectedElement.from_json(definition_json)
            return LIST_RESULT_PREFIX + definition.caption

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


@app.callback(
    Output("annotation-creation-step-list-4-range-result", "children"),
    Input("annotation-creation-store-step", "data"),
    Input("annotation-creation-store-range-start", "data"),
    Input("annotation-creation-store-range-end", "data"),
    prevent_initial_call=False,
)
def annotation_result_visualization_range(
    current_step,
    selected_start_datetime_str,
    selected_end_datetime_str,
):

    if (
        current_step is not None
        and current_step >= CreationSteps.RANGE_SELECTION.value
        and selected_start_datetime_str is not None
        and selected_end_datetime_str is not None
    ):
        selector_tz = tz.gettz(
            get_configuration(group=ConfigGroups.FRONTEND, key="timezone")
        )
        start_datetime = datetime.fromisoformat(selected_start_datetime_str)
        end_datetime = datetime.fromisoformat(selected_end_datetime_str)

        return f"{LIST_RESULT_PREFIX}{start_datetime.strftime('%d.%m.%Y, %H:%M:%S')} – {end_datetime.strftime('%d.%m.%Y, %H:%M:%S')}"

    else:
        return ""


@app.callback(
    Output("annotation-creation-step-list-5-caption-description-result", "children"),
    Input("annotation-creation-store-step", "data"),
    Input("annotation-caption-input", "value"),
    prevent_initial_call=False,
)
def annotation_result_visualization_caption_description(current_step, caption):

    if (
        current_step is not None
        and current_step >= CreationSteps.CAPTION_DESCRIPTION.value
        and caption is not None
        and caption != ""
    ):

        return f"{LIST_RESULT_PREFIX}Caption: {caption}"

    else:
        return ""


@app.callback(
    Output("annotation-creation-date-selector-start", "value"),
    Output("annotation-creation-time-selector-start", "value"),
    Output("annotation-creation-date-selector-end", "value"),
    Output("annotation-creation-time-selector-end", "value"),
    Input("annotation-creation-store-step", "data"),
    State("annotation-creation-date-selector-end", "value"),
)
def init_date_time_pickers(current_step, selected_end_time):
    if (
        current_step is not None
        and current_step == CreationSteps.RANGE_SELECTION.value
        and (selected_end_time is None or selected_end_time == "")
    ):
        now = (
            datetime.now()
            .replace(tzinfo=tz.gettz("UTC"))
            .astimezone(
                tz.gettz(get_configuration(group=ConfigGroups.FRONTEND, key="timezone"))
            )
        )
        last_hour = now - timedelta(hours=1)
        return last_hour, last_hour, now, now
    else:
        raise PreventUpdate


##########################################
# Deleting:
##########################################


@app.callback(
    Output("delete-annotation-button", "disabled"),
    Input("selected-graph-element-store", "data"),
    Input("annotation-deleted", "modified_timestamp"),
    prevent_initial_call=False,
)
def annotation_delete_button_activate(selected_el_json, deleted):
    if ctx.triggered_id == "annotation-deleted":
        return True

    selected_el: GraphSelectedElement = (
        GraphSelectedElement.from_json(selected_el_json)
        if selected_el_json is not None
        else None
    )
    if selected_el is not None and selected_el.type in [
        NodeTypes.ANNOTATION_DEFINITION.value,
        NodeTypes.ANNOTATION_INSTANCE.value,
    ]:
        return False
    else:
        return True


@app.callback(
    Output("annotation-deleted", "data"),
    Input("delete-annotation-button-confirm", "submit_n_clicks"),
    State("selected-graph-element-store", "data"),
    prevent_initial_call=True,
)
def delete_annotation(
    delete_button,
    selected_el_json,
):
    selected_el: GraphSelectedElement = GraphSelectedElement.from_json(selected_el_json)

    if selected_el.type == NodeTypes.ANNOTATION_INSTANCE.value:
        logger.info(f"Deleting annotation instance: {selected_el.id_short}")
        api_client.delete(
            f"/annotation/instance/",
            instance_iri=selected_el.iri,
        )
    elif selected_el.type == NodeTypes.ANNOTATION_DEFINITION.value:
        logger.info(f"Deleting annotation definition: {selected_el.id_short}")
        api_client.delete(f"/annotation/definition/", definition_iri=selected_el.iri)
    else:
        logger.info("Tried to remove annotation, but different object selected")
        raise PreventUpdate

    return datetime.now()
