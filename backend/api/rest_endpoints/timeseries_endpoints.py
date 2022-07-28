import json
from datetime import datetime, timedelta
import pandas as pd

from backend.api.api import app
from backend.exceptions.IdNotFoundException import IdNotFoundException
from backend.knowledge_graph.KnowledgeGraphPersistenceService import (
    KnowledgeGraphPersistenceService,
)
from backend.knowledge_graph.dao.DatabaseConnectionsDao import DatabaseConnectionsDao
from backend.specialized_databases.DatabasePersistenceServiceContainer import (
    DatabasePersistenceServiceContainer,
)
from backend.specialized_databases.timeseries.TimeseriesPersistenceService import (
    TimeseriesPersistenceService,
)
from backend.specialized_databases.timeseries.influx_db.InfluxDbPersistenceService import (
    InfluxDbPersistenceService,
)
import backend.api.python_endpoints.timeseries_endpoints as python_timeseries_endpoints


DB_SERVICE_CONTAINER: DatabasePersistenceServiceContainer = (
    DatabasePersistenceServiceContainer.instance()
)
DB_CON_NODE_DAO: DatabaseConnectionsDao = DatabaseConnectionsDao.instance()


@app.get("/timeseries/current_range")
def get_timeseries_current_range(
    iri: str,
    duration: float,
    aggregation_window_ms: int | None = None,
):
    """
    Queries the current measurements for the given duration up to the current time.
    :raises IdNotFoundException: If no data is available for that id at the current time
    :param id_uri:
    :param duration: timespan to query in seconds
    :return: Pandas Dataframe serialized to JSON featuring the columns "time" and "value"
    """
    df = python_timeseries_endpoints.get_timeseries_current_range(
        iri, duration, aggregation_window_ms
    )
    return df.to_json(date_format="iso")


@app.get("/timeseries/range")
def get_timeseries_range(
    iri: str,
    date_time_str: str,
    duration: float,
    aggregation_window_ms: int | None = None,
):
    """
    Queries the measurements for the given duration up to the given date and time.
    :raises IdNotFoundException: If no data is available for that id at the current time
    :param id_uri:
    :param date_time: date and time to be observed in iso format
    :param duration: timespan to query in seconds
    :return: Pandas Dataframe serialized to JSON featuring the columns "time" and "value"
    """
    date_time = datetime.fromisoformat(date_time_str)
    df = python_timeseries_endpoints.get_timeseries_range(
        iri, date_time, duration, aggregation_window_ms
    )
    return df.to_json(date_format="iso")


@app.get("/timeseries/entries_count")
def get_timeseries_entries_count(iri: str, date_time_str: str, duration: float):
    """

    :raises IdNotFoundException: If no data is available for that id at the current time
    :param id_uri:
    :param date_time: date and time to be observed in iso format
    :param duration: timespan to query in seconds
    :return: Count of entries in that given range
    """
    return python_timeseries_endpoints.get_timeseries_entries_count(
        iri, date_time_str, duration
    )
