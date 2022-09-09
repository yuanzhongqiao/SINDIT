from datetime import datetime
from frontend.app import app
from dash.dependencies import Input, Output
import pytz
from frontend import api_client

from frontend.left_sidebar.global_information import global_information_layout
from util.environment_and_configuration import ConfigGroups, get_configuration

print("Initializing global information callbacks...")


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
        pytz.timezone(get_configuration(group=ConfigGroups.FRONTEND, key="timezone"))
    )
    system_time_str = system_time.strftime("%H:%M:%S, %d.%m.%Y")

    active_db_connections_count = api_client.get_int(
        relative_path="/database_connections/active_count",
    )

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

    return (
        system_time_str,
        f"{active_db_connections_count} / {configured_db_connections_count}",
        f"{active_rt_connections_count} / {configured_rt_connections_count}",
        timeseries_count,
        assets_count,
    )
