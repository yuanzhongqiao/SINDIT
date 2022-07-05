import json
from datetime import datetime, timedelta
import pandas as pd

from service.api.api import app
from service.exceptions.IdNotFoundException import IdNotFoundException
from service.knowledge_graph.KnowledgeGraphPersistenceService import (
    KnowledgeGraphPersistenceService,
)
from service.knowledge_graph.dao.DatabaseConnectionsDao import DatabaseConnectionsDao
from service.specialized_databases.DatabasePersistenceServiceContainer import (
    DatabasePersistenceServiceContainer,
)
from service.specialized_databases.timeseries.TimeseriesPersistenceService import (
    TimeseriesPersistenceService,
)
from service.specialized_databases.timeseries.influx_db.InfluxDbPersistenceService import (
    InfluxDbPersistenceService,
)


DB_SERVICE_CONTAINER: DatabasePersistenceServiceContainer = (
    DatabasePersistenceServiceContainer.instance()
)
DB_CON_NODE_DAO: DatabaseConnectionsDao = DatabaseConnectionsDao.instance()


@app.get("/timeseries/current_range")
def get_timeseries_range(iri: str, duration: float):
    """
    Queries the current measurements for the given duration up to the current time.
    :raises IdNotFoundException: If no data is available for that id at the current time
    :param id_uri:
    :param duration: timespan to query in milliseconds
    :return: Pandas Dataframe serialized to JSON featuring the columns "time" and "value"
    """
    try:
        # Get related timeseries-database service:
        ts_con_node: DatabaseConnectionsDao = (
            DB_CON_NODE_DAO.get_database_connection_for_node(iri)
        )

        ts_service: TimeseriesPersistenceService = (
            DB_SERVICE_CONTAINER.get_persistence_service(ts_con_node.iri)
        )

        # Read the actual measurements:
        readings_df = ts_service.read_period_to_dataframe(
            id_uri=iri,
            begin_time=datetime.now() - timedelta(milliseconds=duration),
            end_time=datetime.now(),
        )

        return readings_df.to_json(date_format="iso")
    except IdNotFoundException:
        return pd.DataFrame(columns=["time", "value"])


@app.get("/timeseries/range")
def get_timeseries_range(iri: str, date_time_str: str, duration: float):
    """
    Queries the measurements for the given duration up to the given date and time.
    :raises IdNotFoundException: If no data is available for that id at the current time
    :param id_uri:
    :param date_time: date and time to be observed in iso format
    :param duration: timespan to query in milliseconds
    :return: Pandas Dataframe serialized to JSON featuring the columns "time" and "value"
    """
    date_time = datetime.fromisoformat(date_time_str)

    try:
        # Get related timeseries-database service:
        ts_con_node: DatabaseConnectionsDao = (
            DB_CON_NODE_DAO.get_database_connection_for_node(iri)
        )

        ts_service: TimeseriesPersistenceService = (
            DB_SERVICE_CONTAINER.get_persistence_service(ts_con_node.iri)
        )

        # Read the actual measurements:
        readings_df = ts_service.read_period_to_dataframe(
            id_uri=iri,
            begin_time=date_time - timedelta(milliseconds=duration),
            end_time=date_time,
        )

        return readings_df.to_json(date_format="iso")
    except IdNotFoundException:
        return pd.DataFrame(columns=["time", "value"])
