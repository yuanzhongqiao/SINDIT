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
    Input("status-unconfirmed-annotation-detection", "modified_timestamp"),
    State("status-unconfirmed-annotation-detection", "data"),
    prevent_initial_call=False,
)
def get_detection_info(_, new_detection):
    if ctx.triggered_id == "annotation-deleted":
        return True

    details_dict = api_client.get_json("/annotation/detection/details")

    if details_dict is None:
        raise PreventUpdate
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
        )
