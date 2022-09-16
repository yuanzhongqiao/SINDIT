import json
from datetime import datetime, timedelta
from typing import Dict, List
import pandas as pd

from backend.exceptions.IdNotFoundException import IdNotFoundException
from backend.knowledge_graph.KnowledgeGraphPersistenceService import (
    KnowledgeGraphPersistenceService,
)
from backend.knowledge_graph.dao.DatabaseConnectionsDao import DatabaseConnectionsDao
from backend.knowledge_graph.dao.TimeseriesNodesDao import TimeseriesNodesDao
from backend.specialized_databases.DatabasePersistenceServiceContainer import (
    DatabasePersistenceServiceContainer,
)
from backend.specialized_databases.timeseries.TimeseriesPersistenceService import (
    TimeseriesPersistenceService,
)
from backend.specialized_databases.timeseries.influx_db.InfluxDbPersistenceService import (
    InfluxDbPersistenceService,
)


DB_SERVICE_CONTAINER: DatabasePersistenceServiceContainer = (
    DatabasePersistenceServiceContainer.instance()
)
DB_CON_NODE_DAO: DatabaseConnectionsDao = DatabaseConnectionsDao.instance()

TIMESERIES_NODES_DAO: TimeseriesNodesDao = TimeseriesNodesDao.instance()


def get_ts_details_flat(iri: str):
    """
    Reads the details (e.g. type and file-name) for a time-series node from the graph
    :raises IdNotFoundException: If the file is not found
    :param iri:
    :return:
    """
    return TIMESERIES_NODES_DAO.get_supplementary_file_node_flat(iri)


def get_timeseries_current_range(
    iri: str,
    duration: float | None,
    aggregation_window_ms: int | None = None,
):
    """
    Queries the current measurements for the given duration up to the current time.
    :raises IdNotFoundException: If no data is available for that id at the current time
    :param id_uri:
    :param duration: timespan to query in seconds or None (forever)
    :return: Pandas Dataframe serialized to JSON featuring the columns "time" and "value"
    """
    return get_timeseries_range(
        iri=iri,
        duration=duration,
        date_time=datetime.now(),
        aggregation_window_ms=aggregation_window_ms,
    )


def _get_related_timeseries_database_service(iri: str) -> TimeseriesPersistenceService:
    try:
        # Get related timeseries-database service:
        ts_con_node: DatabaseConnectionsDao = (
            DB_CON_NODE_DAO.get_database_connection_for_node(iri)
        )

        if ts_con_node is None:
            print("Timeseries requested, but database connection node does not exist")
            return pd.DataFrame(columns=["time", "value"])

        ts_service: TimeseriesPersistenceService = (
            DB_SERVICE_CONTAINER.get_persistence_service(ts_con_node.iri)
        )
        return ts_service
    except IdNotFoundException as exc:
        raise exc


def get_timeseries_range(
    iri: str,
    date_time: datetime | None,
    duration: float | None,
    aggregation_window_ms: int | None = None,
):
    """
    Queries the measurements for the given duration up to the given date and time.
    :raises IdNotFoundException: If no data is available for that id at the current time
    :param id_uri:
    :param date_time: date and time to be observed in iso format or None (forever)
    :param duration: timespan to query in seconds or None (forever)
    :return: Pandas Dataframe serialized to JSON featuring the columns "time" and "value"
    """

    try:
        # Get related timeseries-database service:
        ts_service: TimeseriesPersistenceService = (
            _get_related_timeseries_database_service(iri)
        )

        # Read the actual measurements:
        readings_df = ts_service.read_period_to_dataframe(
            id_uri=iri,
            begin_time=date_time - timedelta(seconds=duration)
            if duration is not None
            else None,
            end_time=date_time,
            aggregation_window_ms=aggregation_window_ms,
        )

        return readings_df
    except IdNotFoundException:
        return pd.DataFrame(columns=["time", "value"])


def get_timeseries_entries_count(
    iri: str, date_time: datetime | None, duration: float | None
):
    """

    :raises IdNotFoundException: If no data is available for that id at the current time
    :param id_uri:
    :param date_time: date and time to be observed in iso format
    :param duration: timespan to query in seconds
    :return: Count of entries in that given range
    """

    try:
        # Get related timeseries-database service:
        ts_service: TimeseriesPersistenceService = (
            _get_related_timeseries_database_service(iri)
        )

        return ts_service.count_entries_for_period(
            id_uri=iri,
            begin_time=date_time - timedelta(seconds=duration)
            if duration is not None
            else None,
            end_time=date_time,
        )
    except IdNotFoundException:
        return 0


def get_timeseries_nodes(deep: bool = True):
    if deep:
        return TIMESERIES_NODES_DAO.get_all_timeseries_nodes_deep()
    else:
        return TIMESERIES_NODES_DAO.get_all_timeseries_nodes_flat()


def set_ts_feature_dict(iri: str, feature_set: Dict):
    TIMESERIES_NODES_DAO.update_feature_dict(iri=iri, feature_dict=feature_set)


def set_ts_reduced_feature_list(iri: str, reduced_feature_list: List):
    TIMESERIES_NODES_DAO.update_reduced_feature_list(
        iri=iri, reduced_feature_list=reduced_feature_list
    )


def create_ts_cluster(iri: str, id_short: str, description: str | None = None):
    TIMESERIES_NODES_DAO.create_ts_cluster(
        iri=iri, id_short=id_short, description=description
    )


def reset_ts_clusters():
    TIMESERIES_NODES_DAO.reset_ts_clusters()


def add_ts_to_cluster(ts_iri: str, cluster_iri: str):
    TIMESERIES_NODES_DAO.add_ts_to_cluster(ts_iri=ts_iri, cluster_iri=cluster_iri)


def get_cluster_list_for_asset(asset_iri: str):
    return TIMESERIES_NODES_DAO.get_cluster_list_for_asset(asset_iri=asset_iri)


def get_timeseries_count():
    return TIMESERIES_NODES_DAO.get_timeseries_count()
