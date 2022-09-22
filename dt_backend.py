"""
Main entry point for the application layer
Handles the sensor-connections and provides a API
Introducing services for querying the KG
Separated from api.py to avoid circular dependencies with endpoint
files importing the "app" instance.
"""

import time
import uvicorn

from threading import Thread
from backend.api.api import app
from backend.cleanup_thread import start_storage_cleanup_thread
from backend.knowledge_graph.KnowledgeGraphPersistenceService import (
    KnowledgeGraphPersistenceService,
)
from backend.knowledge_graph.dao.AssetNodesDao import AssetsDao
from backend.knowledge_graph.dao.TimeseriesNodesDao import TimeseriesNodesDao
from backend.runtime_connections.RuntimeConnectionContainer import (
    RuntimeConnectionContainer,
)
from backend.specialized_databases.DatabasePersistenceServiceContainer import (
    DatabasePersistenceServiceContainer,
)


# Import endpoint files (indirectly used through annotation)


# pylint: disable=unused-import
# noinspection PyUnresolvedReferences
from backend.api.rest_endpoints import status_endpoints

# noinspection PyUnresolvedReferences
from backend.api.rest_endpoints import timeseries_endpoints

# noinspection PyUnresolvedReferences
from backend.api.rest_endpoints import file_endpoints

# noinspection PyUnresolvedReferences
from backend.api.rest_endpoints import asset_endpoints

# noinspection PyUnresolvedReferences
from backend.api.rest_endpoints import annotation_endpoints

# noinspection PyUnresolvedReferences
from backend.api.rest_endpoints import graph_endpoints

# noinspection PyUnresolvedReferences
from backend.api.rest_endpoints import import_export_endpoints

from init_learning_factory_from_cypher_file import (
    generate_alternative_cad_format,
    import_binary_data,
    setup_knowledge_graph,
)
from util.environment_and_configuration import (
    get_environment_variable,
    get_environment_variable_int,
)


# #############################################################################
# Setup sensor connections and timeseries persistence
# #############################################################################


def init_database_data_if_not_available():
    asset_dao = AssetsDao.instance()
    assets_count = asset_dao.get_assets_count()

    if assets_count == 0:
        print("No assets found! Initializing databases in 60 seconds, if not canceled.")
        time.sleep(60)

        setup_knowledge_graph()
        import_binary_data()
        generate_alternative_cad_format()
        print("Finished initilization.")


def refresh_ts_inputs():
    timeseries_nodes_dao: TimeseriesNodesDao = TimeseriesNodesDao.instance()
    runtime_con_container: RuntimeConnectionContainer = (
        RuntimeConnectionContainer.instance()
    )
    timeseries_deep_nodes = timeseries_nodes_dao.get_all_timeseries_nodes_deep()

    runtime_con_container.refresh_connection_inputs_and_handlers(timeseries_deep_nodes)


def refresh_time_series_thread_loop():

    while True:
        time.sleep(120)
        print("Refreshing time-series inputs and connections...")
        refresh_ts_inputs()

        print("Done refreshing time-series inputs and connections.")


# #############################################################################
# Launch backend
# #############################################################################
if __name__ == "__main__":

    print("Initializing Knowledge Graph...")

    # pylint: disable=W0612
    kg_service = KnowledgeGraphPersistenceService.instance()

    print("Done initializing Knowledge Graph.")

    print("Checking, if data is present...")
    init_database_data_if_not_available()

    print("Initializing specialized databases...")
    db_con_container: DatabasePersistenceServiceContainer = (
        DatabasePersistenceServiceContainer.instance()
    )
    print("Done initializing specialized databases.")

    print("Loading time-series inputs and connections...")
    refresh_ts_inputs()
    print("Done loading time-series inputs and connections.")

    # Thread checking regulary, if timeseries inputs and runtime-connections have been added / removed
    ts_refresh_thread = Thread(target=refresh_time_series_thread_loop)
    ts_refresh_thread.start()

    # Start cleanup thread deleting obsolete backups:
    start_storage_cleanup_thread()

    # Run fast API
    # noinspection PyTypeChecker
    uvicorn.run(
        "dt_backend:app",
        host=get_environment_variable("FAST_API_HOST"),
        port=get_environment_variable_int("FAST_API_PORT"),
        # workers=4,
        # # TODO: decide whether to introduce inter-process communication
        # (e.g. for runtime-connection status) and to activate workers!
        access_log=False,
    )
