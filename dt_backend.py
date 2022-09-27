"""
Main entry point for the application layer
Handles the sensor-connections and provides a API
Introducing services for querying the KG
Separated from api.py to avoid circular dependencies with endpoint
files importing the "app" instance.
"""

from datetime import timedelta
import time
import uvicorn

from dateutil import tz
from threading import Thread
from util.environment_and_configuration import (
    ConfigGroups,
    get_configuration,
)
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
from util.log import logger


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
        logger.info(
            "No assets found! Initializing databases in 60 seconds, if not canceled."
        )
        time.sleep(60)

        setup_knowledge_graph()
        import_binary_data()
        generate_alternative_cad_format()
        logger.info("Finished initilization.")


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
        logger.info("Refreshing time-series inputs and connections...")
        refresh_ts_inputs()

        logger.info("Done refreshing time-series inputs and connections.")


# #############################################################################
# Launch backend
# #############################################################################
if __name__ == "__main__":

    logger.info("Initializing Knowledge Graph...")

    # pylint: disable=W0612
    kg_service = KnowledgeGraphPersistenceService.instance()

    logger.info("Done initializing Knowledge Graph.")

    logger.info("Checking, if data is present...")
    init_database_data_if_not_available()

    logger.info("Initializing specialized databases...")
    db_con_container: DatabasePersistenceServiceContainer = (
        DatabasePersistenceServiceContainer.instance()
    )
    logger.info("Done initializing specialized databases.")

    logger.info("Loading time-series inputs and connections...")
    refresh_ts_inputs()
    logger.info("Done loading time-series inputs and connections.")

    # Thread checking regulary, if timeseries inputs and runtime-connections have been added / removed
    ts_refresh_thread = Thread(target=refresh_time_series_thread_loop)
    ts_refresh_thread.start()

    # Start cleanup thread deleting obsolete backups:
    start_storage_cleanup_thread()

    #
    # TODO: remove this. Just for
    #
    # from backend.knowledge_graph.dao.AnnotationNodesDao import AnnotationNodesDao
    # from datetime import datetime

    # annotations_dao: AnnotationNodesDao = AnnotationNodesDao.instance()

    # detection_iri = annotations_dao.create_annotation_detection(
    #     id_short="test-detection",
    #     start_datetime=datetime.now().astimezone(
    #         tz.gettz(get_configuration(group=ConfigGroups.FRONTEND, key="timezone"))
    #     )
    #     - timedelta(minutes=10),
    #     end_datetime=datetime.now().astimezone(
    #         tz.gettz(get_configuration(group=ConfigGroups.FRONTEND, key="timezone"))
    #     ),
    #     caption="Test Detection",
    # )

    # annotations_dao.create_annotation_detection_timeseries_relationship(
    #     detection_iri=detection_iri,
    #     timeseries_iri="www.sintef.no/aas_identifiers/learning_factory/sensors/hbw_actual_pos_vertical",
    # )
    # annotations_dao.create_annotation_detection_timeseries_relationship(
    #     detection_iri=detection_iri,
    #     timeseries_iri="www.sintef.no/aas_identifiers/learning_factory/sensors/factory_humidity_raw",
    # )

    # annotations_dao.create_annotation_detection_asset_relationship(
    #     detection_iri=detection_iri,
    #     asset_iri="www.sintef.no/aas_identifiers/learning_factory/machines/hbw",
    # )

    # annotations_dao.create_annotation_detection_instance_relationship(
    #     detection_iri=detection_iri,
    #     instance_iri="www.sintef.no/aas_identifiers/learning_factory/annotations/instances/test_annotation_definition_hbw_2022-09-18T20:30:29.263466",
    # )

    #
    #
    #

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
