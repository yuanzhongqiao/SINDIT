"""
Main entry point for the application layer
Handles the sensor-connections and provides a API
Introducing services for querying the KG
Separated from api.py to avoid circular dependencies with endpoint
files importing the "app" instance.
"""

import time
import uvicorn

from backend.api.api import app
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
def init_database_connections():
    print("Initializing database connections...")

    # pylint: disable=W0612
    kg_service = KnowledgeGraphPersistenceService.instance()

    db_con_container: DatabasePersistenceServiceContainer = (
        DatabasePersistenceServiceContainer.instance()
    )

    print("Done!")


def init_database_data_if_not_available():
    asset_dao = AssetsDao.instance()
    assets_count = asset_dao.get_assets_count()

    if assets_count == 0:
        print("No assets found! Initializing databases in 60 seconds, if not canceled.")
        time.sleeep(60)

        setup_knowledge_graph()
        import_binary_data()
        generate_alternative_cad_format()


def init_sensors():
    print("Initializing timeseries inputs...")

    # pylint: disable=W0612
    kg_service: KnowledgeGraphPersistenceService = (
        KnowledgeGraphPersistenceService.instance()
    )
    timeseries_nodes_dao: TimeseriesNodesDao = TimeseriesNodesDao.instance()

    runtime_con_container: RuntimeConnectionContainer = (
        RuntimeConnectionContainer.instance()
    )

    timeseries_deep_nodes = timeseries_nodes_dao.get_all_timeseries_nodes_deep()

    runtime_con_container.initialize_connections_inputs_and_handlers(
        timeseries_deep_nodes
    )

    runtime_con_container.start_connections()

    print("Done!")


# #############################################################################
# Launch backend
# #############################################################################
if __name__ == "__main__":
    init_database_connections()

    init_database_data_if_not_available()

    init_sensors()

    # Run fast API
    # noinspection PyTypeChecker
    uvicorn.run(
        app,
        host=get_environment_variable("FAST_API_HOST"),
        port=get_environment_variable_int("FAST_API_PORT"),
    )