from datetime import datetime
from dash import ctx

from util.log import logger
from frontend.app import app
from dash.dependencies import Input, Output, State
from frontend import api_client

from dash.exceptions import PreventUpdate

from frontend.main_column.factory_graph.GraphSelectedElement import GraphSelectedElement
from graph_domain.factory_graph_types import NodeTypes

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
    Output("annotation-confirmation-collapse", "is_open"),
    Input("create-annotation-button", "n_clicks"),
    Input("confirm-cancel-annotation-creation", "submit_n_clicks"),
    Input("annotation-creation-saved", "data"),
    State("annotation-creation-store-step", "data"),
    Input("status-unconfirmed-annotation-detection", "modified_timestamp"),
    State("status-unconfirmed-annotation-detection", "data"),
    prevent_initial_call=False,
)
def annotation_create_collapse(
    n_clicks_create, n_clicks_cancel, n_clicks_save, step, _, new_detection
):
    trigger_id = ctx.triggered_id
    if new_detection is not None and new_detection:
        return False, False, True
    elif trigger_id == "create-annotation-button":
        return False, True, False
    elif trigger_id in [
        "confirm-cancel-annotation-creation",
        "annotation-creation-saved",
    ]:
        return True, False, False
    elif step is not None:
        return False, True, False
    else:
        return True, False, False


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
    if (
        selected_el is not None
        and selected_el.type == NodeTypes.ANNOTATION_DEFINITION.value
    ):
        # Check, if instances of that definition exist:
        instances_count = api_client.get_int(
            "/annotation/instance/count", definition_iri=selected_el.iri
        )
        return instances_count != 0
    elif (
        selected_el is not None
        and selected_el.type == NodeTypes.ANNOTATION_INSTANCE.value
    ):
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
            "/annotation/instance",
            instance_iri=selected_el.iri,
        )
    elif selected_el.type == NodeTypes.ANNOTATION_DEFINITION.value:
        logger.info(f"Deleting annotation definition: {selected_el.id_short}")
        api_client.delete("/annotation/definition", definition_iri=selected_el.iri)
    else:
        logger.info("Tried to remove annotation, but different object selected")
        raise PreventUpdate

    return datetime.now()
