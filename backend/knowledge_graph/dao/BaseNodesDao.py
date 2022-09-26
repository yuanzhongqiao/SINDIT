import json

from py2neo import Node, NodeMatcher
from graph_domain.BaseNode import BaseNode
from graph_domain.factory_graph_ogm_matches import OGM_CLASS_FOR_NODE_TYPE

from graph_domain.main_digital_twin.AssetNode import AssetNodeFlat, AssetNodeDeep
from backend.exceptions.GraphNotConformantToMetamodelError import (
    GraphNotConformantToMetamodelError,
)
from backend.knowledge_graph.KnowledgeGraphPersistenceService import (
    KnowledgeGraphPersistenceService,
)

from util.log import logger
from backend.knowledge_graph.knowledge_graph_metamodel_validator import (
    validate_result_nodes,
)
from graph_domain.main_digital_twin.TimeseriesNode import TimeseriesNodeFlat


class BaseNodeDao(object):
    """
    Data Access Object for Machines
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

        BaseNodeDao.__instance = self

        self.ps: KnowledgeGraphPersistenceService = (
            KnowledgeGraphPersistenceService.instance()
        )

    def update_node_position(self, iri: str, new_pos_x: float, new_pos_y: float):
        """
        Stores a new position for the node
        :param iri:
        :param new_pos_x:
        :param new_pos_y:
        :return:
        """
        matcher = NodeMatcher(self.ps.graph)
        node: Node = matcher.match(iri=iri).first()
        node.update(
            visualization_positioning_x=new_pos_x, visualization_positioning_y=new_pos_y
        )
        self.ps.graph_push(node)

    @validate_result_nodes
    def get_generic_node(self, iri: str):
        """
        :return:
        :raises GraphNotConformantToMetamodelError: If Graph not conformant
        """

        ogm_class = OGM_CLASS_FOR_NODE_TYPE.get(self.get_node_type(iri))

        if ogm_class is None:
            logger.error(
                f"Missing OGM-class for {self.get_node_type(iri)} in OGM_CLASS_FOR_NODE_TYPE mapping."
            )
            return None

        node_matches = self.ps.repo_match(model=ogm_class, primary_value=iri)

        return node_matches.first()

    def get_node_type(self, iri: str):
        types_table = self.ps.graph_run(
            f'MATCH (n) WHERE n.iri = "{iri}" RETURN labels(n)[0]'
        ).to_table()
        if (
            types_table is not None
            and len(types_table) > 0
            and types_table[0] is not None
            and len(types_table[0]) > 0
        ):
            return types_table[0][0]
        else:
            logger.warning(f"Node type could not be queried for {iri}")
            return None
