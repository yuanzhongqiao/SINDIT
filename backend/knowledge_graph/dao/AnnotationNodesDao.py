import json
from py2neo import Node, NodeMatcher, Relationship
from graph_domain.expert_annotations.AnnotationDefinitionNode import (
    AnnotationDefinitionNodeFlat,
)

from graph_domain.main_digital_twin.AssetNode import AssetNodeFlat, AssetNodeDeep
from backend.exceptions.GraphNotConformantToMetamodelError import (
    GraphNotConformantToMetamodelError,
)
from backend.knowledge_graph.KnowledgeGraphPersistenceService import (
    KnowledgeGraphPersistenceService,
)
from backend.knowledge_graph.knowledge_graph_metamodel_validator import (
    validate_result_nodes,
)
from graph_domain.factory_graph_types import (
    NodeTypes,
    RelationshipTypes,
)

# TODO: move to a global place
IRI_PREFIX_GLOBAL = "www.sintef.no/aas_identifiers/learning_factory/"
IRI_PREFIX_ANNOTATION_INSTANCE = IRI_PREFIX_GLOBAL + "annotations/instances/"
IRI_PREFIX_ANNOTATION_DEFINITION = IRI_PREFIX_GLOBAL + "annotations/definitions/"
IRI_PREFIX_ANNOTATION_TS_MATCHER = IRI_PREFIX_GLOBAL + "annotations/ts_matchers/"
IRI_PREFIX_ANNOTATION_PRE_INDICATOR = IRI_PREFIX_GLOBAL + "annotations/pre_indicators/"


class AnnotationNodesDao(object):
    """
    Data Access Object for Annotations (definitions etc)
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

        AnnotationNodesDao.__instance = self

        self.ps: KnowledgeGraphPersistenceService = (
            KnowledgeGraphPersistenceService.instance()
        )

    def post_annotation_definition(
        self,
        id_short: str,
        solution_proposal: str,
        caption: str | None = None,
        description: str | None = None,
    ) -> str:
        """Creates a new annotation definition"""
        iri = IRI_PREFIX_ANNOTATION_DEFINITION + id_short

        definition = AnnotationDefinitionNodeFlat(
            id_short=id_short,
            iri=iri,
            solution_proposal=solution_proposal,
            caption=caption,
            description=description,
        )
        self.ps.graph.push(definition)

        return iri

    #
    #
    #
    #
    # def update_node_position(self, iri: str, new_pos_x: float, new_pos_y: float):
    #     """
    #     Stores a new position for the node
    #     :param iri:
    #     :param new_pos_x:
    #     :param new_pos_y:
    #     :return:
    #     """
    #     matcher = NodeMatcher(self.ps.graph)
    #     node: Node = matcher.match(iri=iri).first()
    #     node.update(
    #         visualization_positioning_x=new_pos_x, visualization_positioning_y=new_pos_y
    #     )
    #     self.ps.graph.push(node)

    # @validate_result_nodes
    # def get_assets_flat(self):
    #     """
    #     Queries all asset nodes. Does not follow any relationships
    #     :param self:
    #     :return:
    #     :raises GraphNotConformantToMetamodelError: If Graph not conformant
    #     """
    #     assets_flat_matches = self.ps.repo.match(model=AssetNodeFlat)

    #     return assets_flat_matches.all()

    # @validate_result_nodes
    # def get_assets_deep(self):
    #     """
    #     Queries all asset nodes. Follows relationships to build nested objects for related nodes (e.g. sensors)
    #     :param self:
    #     :return:
    #     """
    #     assets_deep_matches = self.ps.repo.match(model=AssetNodeDeep)

    #     return assets_deep_matches.all()

    # # validator used manually because result type is json instead of node-list
    # def get_assets_flat_json(self):
    #     return json.dumps([a.to_json() for a in self.get_assets_flat()])

    # def get_assets_deep_json(self):
    #     """
    #     Queries all asset nodes. Follows relationships to build nested objects for related nodes (e.g. sensors)
    #     Directly returns the serialized json instead of nested objects. This is faster than using the nested-object
    #     getter and serializing afterwards, as it does not require an intermediate step.
    #     :param self:
    #     :return:
    #     """
    #     return json.dumps([a.to_json() for a in self.get_assets_deep()])

    # def add_asset_similarity(
    #     self,
    #     asset1_iri: str,
    #     asset2_iri: str,
    #     similarity_score: float,
    # ):
    #     # Stored as single-direction relationship, as Neo4J does not
    #     # support undirected or bidirected relationships
    #     relationship = Relationship(
    #         NodeMatcher(self.ps.graph)
    #         .match(NodeTypes.ASSET.value, iri=asset1_iri)
    #         .first(),
    #         RelationshipTypes.ASSET_SIMILARITY.value,
    #         NodeMatcher(self.ps.graph)
    #         .match(NodeTypes.ASSET.value, iri=asset2_iri)
    #         .first(),
    #         similarity_score=similarity_score,
    #     )
    #     # TODO: expand to multiple scores (one for TS, one for PDF keywords...)

    #     self.ps.graph.create(relationship)

    # def delete_asset_similarities(self):
    #     self.ps.graph.run(
    #         f"MATCH p=()-[r:{RelationshipTypes.ASSET_SIMILARITY.value}]->() DELETE r"
    #     )

    # def get_asset_similarities(self):
    #     similarities_table = self.ps.graph.run(
    #         f"MATCH p=(a1)-[r:{RelationshipTypes.ASSET_SIMILARITY.value}]->(a2) RETURN a1.iri,r.similarity_score,a2.iri"
    #     ).to_table()

    #     similarities_list = [
    #         {
    #             "asset1": similarity[0],
    #             "similarity_score": similarity[1],
    #             "asset2": similarity[2],
    #         }
    #         for similarity in similarities_table
    #     ]

    #     return similarities_list

    # def get_assets_count(self):
    #     assets_count = self.ps.graph.run(
    #         f"MATCH (n:{NodeTypes.ASSET.value}) RETURN count(n)"
    #     ).to_table()[0][0]

    #     return assets_count
