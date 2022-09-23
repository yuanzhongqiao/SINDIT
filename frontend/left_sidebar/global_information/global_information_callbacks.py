from datetime import datetime
from frontend.app import app
from dash.dependencies import Input, Output
from frontend import api_client
from dateutil import tz

from dash import html

from frontend.left_sidebar.global_information import global_information_layout
from util.environment_and_configuration import ConfigGroups, get_configuration
from util.log import logger

logger.info("Initializing global information callbacks...")


@app.callback(
    Output("status-system-time", "children"),
    Output("status-db-connections", "children"),
    Output("status-ts-connections", "children"),
    Output("status-ts-inputs", "children"),
    Output("status-assets-count", "children"),
    Input("interval-component", "n_intervals"),
)
def update_connectivity_information(n):
    """
    Periodically refreshes the global information
    :param n:
    :return:
    """

    system_time = datetime.fromisoformat(
        api_client.get_str(
            relative_path="/system_time",
        )[1:-1]
    ).astimezone(
        tz.gettz(get_configuration(group=ConfigGroups.FRONTEND, key="timezone"))
    )
    system_time_str = system_time.strftime("%H:%M:%S, %d.%m.%Y")

    configured_db_connections_count = api_client.get_int(
        relative_path="/database_connections/total_count",
    )

    active_rt_connections_count = api_client.get_int(
        relative_path="/runtime_connections/active_count",
    )

    configured_rt_connections_count = api_client.get_int(
        relative_path="/runtime_connections/total_count",
    )

    assets_count = api_client.get_int(
        relative_path="/assets/count",
    )

    timeseries_count = api_client.get_int(
        relative_path="/timeseries/count",
    )

    rt_con_str = f"{active_rt_connections_count} / {configured_rt_connections_count}"

    return (
        system_time_str,
        configured_db_connections_count,
        rt_con_str
        if active_rt_connections_count == configured_rt_connections_count
        else html.Div(
            rt_con_str, style={"font-weight": "bold", "color": "red", "padding": "0"}
        ),
        timeseries_count,
        assets_count,
    )
