import json
from typing import List
from graph_domain.DatabaseConnectionNode import DatabaseConnectionNode
from py2neo import Node, NodeMatcher, Relationship


from graph_domain.AssetNode import AssetNodeFlat, AssetNodeDeep
from graph_domain.SupplementaryFileNode import (
    SupplementaryFileNodeDeep,
    SupplementaryFileNodeFlat,
)
from graph_domain.factory_graph_types import NodeTypes, RelationshipTypes
from backend.exceptions.GraphNotConformantToMetamodelError import (
    GraphNotConformantToMetamodelError,
)
from backend.knowledge_graph.KnowledgeGraphPersistenceService import (
    KnowledgeGraphPersistenceService,
)
from backend.knowledge_graph.knowledge_graph_metamodel_validator import (
    validate_result_nodes,
)
from graph_domain.ExtractedKeywordNode import ExtractedKeywordNode


class SupplementaryFileNodesDao(object):
    """
    Data Access Object for SupplementaryFiles (KG-nodes representing)
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

        SupplementaryFileNodesDao.__instance = self

        self.ps: KnowledgeGraphPersistenceService = (
            KnowledgeGraphPersistenceService.instance()
        )

    @validate_result_nodes
    def get_supplementary_file_node_flat(self, iri: str) -> SupplementaryFileNodeFlat:
        """
        Queries the specified supplementary file node. Does not follow any relationships
        :param self:
        :return:
        :raises GraphNotConformantToMetamodelError: If Graph not conformant
        """
        suppl_file_match = self.ps.repo.match(
            model=SupplementaryFileNodeFlat, primary_value=iri
        )

        return suppl_file_match.first()

    @validate_result_nodes
    def get_supplementary_file_available_formats(
        self, iri: str
    ) -> List[SupplementaryFileNodeFlat]:
        """
        Queries all available formats for the specified supplementary file node.
        :param self:
        :return:
        :raises GraphNotConformantToMetamodelError: If Graph not conformant
        """

        suppl_file_matches = self.ps.repo.match(model=SupplementaryFileNodeFlat).where(
            '(_)<-[:SECONDARY_FORMAT *0..]-(: SUPPLEMENTARY_FILE {iri: "' + iri + '"}) '
        )

        return [
            SupplementaryFileNodeFlat.from_json(m.to_json()) for m in suppl_file_matches
        ]

    @validate_result_nodes
    def get_file_nodes_flat(self):
        """
        Queries all file nodes (excluding secondary format noded). Does not follow any relationships
        :param self:
        :return:
        :raises GraphNotConformantToMetamodelError: If Graph not conformant
        """
        files_flat_matches = self.ps.repo.match(model=SupplementaryFileNodeFlat).where(
            "NOT (_:SUPPLEMENTARY_FILE)<-[:SECONDARY_FORMAT]-(: SUPPLEMENTARY_FILE)"
        )

        files_flat = [m for m in files_flat_matches]

        return files_flat

    @validate_result_nodes
    def get_file_nodes_deep(self):
        """
        Queries all asset nodes (excluding secondary format noded). Follows relationships to build nested objects for related nodes (e.g. sensors)
        :param self:
        :return:
        """
        file_deep_matches = self.ps.repo.match(model=SupplementaryFileNodeDeep).where(
            "NOT (_:SUPPLEMENTARY_FILE)<-[:SECONDARY_FORMAT]-(: SUPPLEMENTARY_FILE)"
        )

        # Get rid of the 'Match' and 'RelatedObject' types in favor of normal lists automatically
        # by using the auto-generated json serializer
        return [
            SupplementaryFileNodeDeep.from_json(m.to_json()) for m in file_deep_matches
        ]

    @validate_result_nodes
    def get_file_nodes_flat_by_type(self, type: str):
        """
        Queries all file nodes (excluding secondary format noded). Does not follow any relationships
        :param self:
        :return:
        :raises GraphNotConformantToMetamodelError: If Graph not conformant
        """
        files_flat_matches = self.ps.repo.match(model=SupplementaryFileNodeFlat).where(
            '_.type="'
            + type
            + '" AND NOT (_:SUPPLEMENTARY_FILE)<-[:SECONDARY_FORMAT]-(: SUPPLEMENTARY_FILE)'
        )

        files_flat = [m for m in files_flat_matches]

        return files_flat

    @validate_result_nodes
    def get_file_nodes_deep_by_type(self, type: str):
        """
        Queries all asset nodes (excluding secondary format noded). Follows relationships to build nested objects for related nodes (e.g. sensors)
        :param self:
        :return:
        """
        file_deep_matches = self.ps.repo.match(model=SupplementaryFileNodeDeep).where(
            '_.type="'
            + type
            + '" AND NOT (_:SUPPLEMENTARY_FILE)<-[:SECONDARY_FORMAT]-(: SUPPLEMENTARY_FILE)'
        )

        # Get rid of the 'Match' and 'RelatedObject' types in favor of normal lists automatically
        # by using the auto-generated json serializer
        return [
            SupplementaryFileNodeDeep.from_json(m.to_json()) for m in file_deep_matches
        ]

    def reset_extracted_keywords(self):
        self.ps.graph.run(
            f"MATCH (n:{NodeTypes.EXTRACTED_KEYWORD.value}) DETACH DELETE n"
        )

    def add_keyword(self, file_iri: str, keyword: str):
        """Adds the keyword by creating a relationship to the keyword and optionally creating the keyword node,
        if it does not yet exist

        Args:
            file_iri (str): _description_
            keyword (str): _description_
        """
        node = ExtractedKeywordNode(
            id_short=f"extracted_keyword_{keyword}",
            iri=f"www.sintef.no/aas_identifiers/learning_factory/similarity_analysis/extracted_keyword_{keyword}",
            keyword=keyword,
        )
        self.ps.graph.merge(node)

        relationship = Relationship(
            NodeMatcher(self.ps.graph)
            .match(NodeTypes.SUPPLEMENTARY_FILE.value, iri=file_iri)
            .first(),
            RelationshipTypes.KEYWORD_EXTRACTION.value,
            NodeMatcher(self.ps.graph)
            .match(NodeTypes.EXTRACTED_KEYWORD.value, iri=node.iri)
            .first(),
        )

        self.ps.graph.create(relationship)
