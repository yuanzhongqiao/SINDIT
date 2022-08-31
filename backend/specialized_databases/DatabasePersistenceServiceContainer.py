from typing import Dict, List
from graph_domain.main_digital_twin.DatabaseConnectionNode import (
    DatabaseConnectionNode,
    DatabaseConnectionTypes,
)

from backend.specialized_databases.SpecializedDatabasePersistenceService import (
    SpecializedDatabasePersistenceService,
)
from backend.specialized_databases.files.s3.S3PersistenceService import (
    S3PersistenceService,
)
from backend.specialized_databases.timeseries.influx_db.InfluxDbPersistenceService import (
    InfluxDbPersistenceService,
)
from backend.knowledge_graph.dao.DatabaseConnectionsDao import DatabaseConnectionsDao


DB_CONNECTION_MAPPING = {
    DatabaseConnectionTypes.INFLUX_DB.value: InfluxDbPersistenceService,
    DatabaseConnectionTypes.S3.value: S3PersistenceService,
}


class DatabasePersistenceServiceContainer:
    """
    Holds all current connections to specialized databases
    """

    __instance = None

    @classmethod
    def instance(cls):
        if cls.__instance is None:
            cls()
            cls.__instance.initialize_connections()
        return cls.__instance

    def __init__(self):
        if self.__instance is not None:
            raise Exception("Singleton instantiated multiple times!")

        DatabasePersistenceServiceContainer.__instance = self

        self.services: Dict[str, SpecializedDatabasePersistenceService] = {}

    def get_persistence_service(self, iri: str):
        return self.services.get(iri)

    def register_persistence_service(
        self, iri: str, service: SpecializedDatabasePersistenceService
    ):
        self.services[iri] = service

    def initialize_connections(self):
        # Get connection nodes from graph:
        db_con_nodes_dao: DatabaseConnectionsDao = DatabaseConnectionsDao.instance()
        connection_nodes: List[
            DatabaseConnectionNode
        ] = db_con_nodes_dao.get_database_connections()

        con_node: DatabaseConnectionNode
        for con_node in connection_nodes:

            service_class: SpecializedDatabasePersistenceService = (
                DB_CONNECTION_MAPPING.get(con_node.type)
            )

            self.services[con_node.iri] = service_class.from_db_connection_node(
                con_node
            )
