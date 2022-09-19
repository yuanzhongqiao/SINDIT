import json
from typing import List
from graph_domain.main_digital_twin.DatabaseConnectionNode import DatabaseConnectionNode

from graph_domain.main_digital_twin.AssetNode import AssetNodeFlat, AssetNodeDeep
from graph_domain.factory_graph_types import (
    NodeTypes,
    RelationshipTypes,
)
from backend.exceptions.GraphNotConformantToMetamodelError import (
    GraphNotConformantToMetamodelError,
)
from backend.knowledge_graph.KnowledgeGraphPersistenceService import (
    KnowledgeGraphPersistenceService,
)
from backend.knowledge_graph.knowledge_graph_metamodel_validator import (
    validate_result_nodes,
)


class RuntimeConnectionsDao(object):
    """
    Data Access Object for RuntimeConnections (KG-nodes representing)
    """

    __instance = None

    @classmethod
    def instance(cls):
        if cls.__instance is None:
            cls()
        return cls.__instance

    def __init__(self):
        if self.__instance is not None:
            raise Exception("Singleton instantiated multiple times!")

        RuntimeConnectionsDao.__instance = self

        self.ps: KnowledgeGraphPersistenceService = (
            KnowledgeGraphPersistenceService.instance()
        )

    def get_rt_connections_count(self):
        rt_connections_count = self.ps.graph_run(
            f"MATCH (n:{NodeTypes.RUNTIME_CONNECTION.value}) RETURN count(n)"
        ).to_table()[0][0]

        return rt_connections_count
