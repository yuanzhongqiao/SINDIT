import json
from py2neo import Node, NodeMatcher, Relationship

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


class AssetsDao(object):
    """
    Data Access Object for Assets
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

        AssetsDao.__instance = self

        self.ps: KnowledgeGraphPersistenceService = (
            KnowledgeGraphPersistenceService.instance()
        )

    @validate_result_nodes
    def get_assets_flat(self):
        """
        Queries all asset nodes. Does not follow any relationships
        :param self:
        :return:
        :raises GraphNotConformantToMetamodelError: If Graph not conformant
        """
        assets_flat_matches = self.ps.repo.match(model=AssetNodeFlat)
        assets_flat = [m for m in assets_flat_matches]

        return assets_flat

    @validate_result_nodes
    def get_assets_deep(self):
        """
        Queries all asset nodes. Follows relationships to build nested objects for related nodes (e.g. sensors)
        :param self:
        :return:
        """
        assets_deep_matches = self.ps.repo.match(model=AssetNodeDeep)

        # Get rid of the 'Match' and 'RelatedObject' types in favor of normal lists automatically
        # by using the auto-generated json serializer
        return [AssetNodeDeep.from_json(m.to_json()) for m in assets_deep_matches]

    # validator used manually because result type is json instead of node-list
    def get_assets_deep_json(self):
        """
        Queries all asset nodes. Follows relationships to build nested objects for related nodes (e.g. sensors)
        Directly returns the serialized json instead of nested objects. This is faster than using the nested-object
        getter and serializing afterwards, as it does not require an intermediate step.
        :param self:
        :return:
        """
        assets_deep_matches = self.ps.repo.match(model=AssetNodeDeep)

        # Validate manually:
        for asset in assets_deep_matches:
            asset.validate_metamodel_conformance()

        return json.dumps([m.to_json() for m in assets_deep_matches])

    def add_asset_similarity(
        self,
        asset1_iri: str,
        asset2_iri: str,
        similarity_score: float,
    ):
        # Stored as single-direction relationship, as Neo4J does not
        # support undirected or bidirected relationships
        relationship = Relationship(
            NodeMatcher(self.ps.graph)
            .match(NodeTypes.ASSET.value, iri=asset1_iri)
            .first(),
            RelationshipTypes.ASSET_SIMILARITY.value,
            NodeMatcher(self.ps.graph)
            .match(NodeTypes.ASSET.value, iri=asset2_iri)
            .first(),
            similarity_score=similarity_score,
        )
        # TODO: expand to multiple scores (one for TS, one for PDF keywords...)

        self.ps.graph.create(relationship)

    def delete_asset_similarities(self):
        self.ps.graph.run(
            f"MATCH p=()-[r:{RelationshipTypes.ASSET_SIMILARITY.value}]->() DELETE r"
        )

    def get_asset_similarities(self):
        similarities_table = self.ps.graph.run(
            f"MATCH p=(a1)-[r:{RelationshipTypes.ASSET_SIMILARITY.value}]->(a2) RETURN a1.iri,r.similarity_score,a2.iri"
        ).to_table()

        similarities_list = [
            {
                "asset1": similarity[0],
                "similarity_score": similarity[1],
                "asset2": similarity[2],
            }
            for similarity in similarities_table
        ]

        return similarities_list
