from datetime import datetime
from typing import Dict
from frontend.app import app
from dash.dependencies import Input, Output
from frontend import api_client
from dateutil import tz
from dash import html

from frontend.left_sidebar.global_information import global_information_layout
from util.environment_and_configuration import ConfigGroups, get_configuration
from util.log import logger

logger.info("Initializing global information callbacks...")


def _warning_message(text: str = "Connection lost!"):
    return html.Div(text, style={"font-weight": "bold", "color": "red", "padding": "0"})


@app.callback(
    Output("status-system-time", "children"),
    Output("status-db-connections", "children"),
    Output("status-ts-connections", "children"),
    Output("status-ts-inputs", "children"),
    Output("status-assets-count", "children"),
    Output("status-unconfirmed-annotation-detection", "data"),
    Input("interval-component", "n_intervals"),
)
def update_system_status(n):
    """
    Periodically refreshes the global information
    :param n:
    :return:
    """

    status_dict: Dict = api_client.get_json(relative_path="/status", retries=0)

    if status_dict is None:
        return (_warning_message(), "", "", "", "", False)

    system_time = datetime.fromisoformat(status_dict.get("system_time")).astimezone(
        tz.gettz(get_configuration(group=ConfigGroups.FRONTEND, key="timezone"))
    )
    system_time_str = system_time.strftime("%H:%M:%S, %d.%m.%Y")

    active_rt_connections_count = status_dict.get("active_runtime_connections")
    configured_rt_connections_count = status_dict.get("runtime_connections")

    rt_con_str = f"{active_rt_connections_count} / {configured_rt_connections_count}"

    return (
        system_time_str,
        status_dict.get("database_connections"),
        rt_con_str
        if active_rt_connections_count == configured_rt_connections_count
        else _warning_message(rt_con_str),
        status_dict.get("timeseries_count"),
        status_dict.get("assets_count"),
        status_dict.get("unconfirmed_annotation_detection"),
    )
