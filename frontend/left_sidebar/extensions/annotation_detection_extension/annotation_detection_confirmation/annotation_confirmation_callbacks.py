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


DATETIME_STRF_FORMAT = "%H:%M:%S, %d.%m.%Y"


@app.callback(
    Output("detection-info-asset", "children"),
    Output("detection-info-occurance-start", "children"),
    Output("detection-info-occurance-end", "children"),
    Output("detection-info-definition", "children"),
    Output("detection-info-instance", "children"),
    Output("detection-info-solution-proposal", "children"),
    Output("detection-info-definition-description", "children"),
    Output("detection-info-instance-description", "children"),
    Output("annotation-detection-details-store", "data"),
    Input("status-unconfirmed-annotation-detection", "modified_timestamp"),
    State("status-unconfirmed-annotation-detection", "data"),
    Input("annotation-detection-declined", "data"),
    Input("annotation-detection-confirmed", "data"),
    prevent_initial_call=False,
)
def get_detection_info(_, new_detection, declined, confirmed):

    details_dict = api_client.get_json("/annotation/detection/details")

    if details_dict is None or ctx.triggered_id in [
        "annotation-detection-declined",
        "annotation-detection-confirmed",
    ]:
        return None, None, None, None, None, None, None, None, None
    else:
        instance_desc = details_dict.get("instance_description")
        definition_desc = details_dict.get("definition_description")

        return (
            details_dict.get("asset_caption"),
            datetime.fromisoformat(details_dict.get("occurance_start")).strftime(
                DATETIME_STRF_FORMAT
            ),
            datetime.fromisoformat(details_dict.get("occurance_end")).strftime(
                DATETIME_STRF_FORMAT
            ),
            details_dict.get("definition_caption"),
            details_dict.get("instance_caption"),
            details_dict.get("solution_proposal"),
            definition_desc
            if definition_desc is not None
            else "No description provided.",
            instance_desc if instance_desc is not None else "No description provided.",
            details_dict,
        )


@app.callback(
    Output("annotation-detection-confirmed", "data"),
    Input("confirm-detection-confirm", "submit_n_clicks"),
    State("annotation-detection-details-store", "data"),
    prevent_initial_call=True,
)
def confirm_annotation(_, details):
    logger.info(f"Confirming annotation: {details.get('iri')}")
    api_client.post(
        "/annotation/detection/confirm", json={"detection_iri": details.get("iri")}
    )

    return datetime.now()


@app.callback(
    Output("annotation-detection-declined", "data"),
    Input("decline-detection-confirm", "submit_n_clicks"),
    State("annotation-detection-details-store", "data"),
    prevent_initial_call=True,
)
def decline_annotation(_, details):
    logger.info(f"Declining annotation: {details.get('iri')}")
    api_client.delete("/annotation/detection", detection_iri=details.get("iri"))

    return datetime.now()
