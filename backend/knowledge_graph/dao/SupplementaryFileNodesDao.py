import json
from typing import List
from graph_domain.main_digital_twin.DatabaseConnectionNode import DatabaseConnectionNode
from py2neo import Node, NodeMatcher, Relationship


from graph_domain.main_digital_twin.AssetNode import AssetNodeFlat, AssetNodeDeep
from graph_domain.main_digital_twin.SupplementaryFileNode import (
    SupplementaryFileNodeDeep,
    SupplementaryFileNodeFlat,
)
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
from graph_domain.similarities.DimensionClusterNode import DimensionClusterNode
from graph_domain.similarities.ExtractedKeywordNode import ExtractedKeywordNode


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
        suppl_file_match = self.ps.repo_match(
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
        suppl_file_matches = self.ps.repo_match(model=SupplementaryFileNodeFlat).where(
            '(_)<-[:SECONDARY_FORMAT *0..]-(: SUPPLEMENTARY_FILE {iri: "' + iri + '"}) '
        )

        return suppl_file_matches.all()

    @validate_result_nodes
    def get_file_nodes_flat(self, exclude_secondary_format_nodes: bool = True):
        """
        Queries all file nodes (excluding secondary format noded). Does not follow any relationships
        :param self:
        :return:
        :raises GraphNotConformantToMetamodelError: If Graph not conformant
        """
        exclude_secondary_format_filter = (
            '" AND NOT (_:SUPPLEMENTARY_FILE)<-[:SECONDARY_FORMAT]-(: SUPPLEMENTARY_FILE)'
            if exclude_secondary_format_nodes
            else '"'
        )

        files_flat_matches = self.ps.repo_match(model=SupplementaryFileNodeFlat).where(
            exclude_secondary_format_filter
        )

        return files_flat_matches.all()

    @validate_result_nodes
    def get_file_nodes_deep(self, exclude_secondary_format_nodes: bool = True):
        """
        Queries all asset nodes (excluding secondary format noded). Follows relationships to build nested objects for related nodes (e.g. sensors)
        :param self:
        :return:
        """
        exclude_secondary_format_filter = (
            '" AND NOT (_:SUPPLEMENTARY_FILE)<-[:SECONDARY_FORMAT]-(: SUPPLEMENTARY_FILE)'
            if exclude_secondary_format_nodes
            else '"'
        )

        file_deep_matches = self.ps.repo_match(model=SupplementaryFileNodeDeep).where(
            exclude_secondary_format_filter
        )

        return file_deep_matches.all()

    @validate_result_nodes
    def get_file_nodes_flat_by_type(
        self, type: str, exclude_secondary_format_nodes: bool = True
    ):
        """
        Queries all file nodes. Does not follow any relationships
        :param self:
        :return:
        :raises GraphNotConformantToMetamodelError: If Graph not conformant
        """
        exclude_secondary_format_filter = (
            '" AND NOT (_:SUPPLEMENTARY_FILE)<-[:SECONDARY_FORMAT]-(: SUPPLEMENTARY_FILE)'
            if exclude_secondary_format_nodes
            else '"'
        )

        files_flat_matches = self.ps.repo_match(model=SupplementaryFileNodeFlat).where(
            '_.type="' + type + exclude_secondary_format_filter
        )

        return files_flat_matches.all()

    @validate_result_nodes
    def get_file_nodes_deep_by_type(
        self, type: str, exclude_secondary_format_nodes: bool = True
    ):
        """
        Queries all asset nodes. Follows relationships to build nested objects for related nodes (e.g. sensors)
        :param self:
        :return:
        """
        exclude_secondary_format_filter = (
            '" AND NOT (_:SUPPLEMENTARY_FILE)<-[:SECONDARY_FORMAT]-(: SUPPLEMENTARY_FILE)'
            if exclude_secondary_format_nodes
            else '"'
        )

        file_deep_matches = self.ps.repo_match(model=SupplementaryFileNodeDeep).where(
            '_.type="' + type + exclude_secondary_format_filter
        )

        return file_deep_matches.all()

    def reset_extracted_keywords(self):
        self.ps.graph_run(
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
            _explizit_caption=keyword,
        )
        self.ps.graph_merge(node)

        relationship = Relationship(
            NodeMatcher(self.ps.graph)
            .match(NodeTypes.SUPPLEMENTARY_FILE.value, iri=file_iri)
            .first(),
            RelationshipTypes.KEYWORD_EXTRACTION.value,
            NodeMatcher(self.ps.graph)
            .match(NodeTypes.EXTRACTED_KEYWORD.value, iri=node.iri)
            .first(),
        )

        self.ps.graph_create(relationship)

    def save_extracted_properties(self, file_iri: str, properties_string: str):
        matcher = NodeMatcher(self.ps.graph)
        node: Node = matcher.match(iri=file_iri).first()
        node.update(extracted_properties=properties_string)
        self.ps.graph_push(node)

    def save_extracted_text(self, file_iri: str, text: str):
        matcher = NodeMatcher(self.ps.graph)
        node: Node = matcher.match(iri=file_iri).first()
        node.update(extracted_text=text)
        self.ps.graph_push(node)

    def get_keywords_set_for_asset(self, asset_iri: str):
        keywords_table = self.ps.graph_run(
            "MATCH p=(a:"
            + NodeTypes.ASSET.value
            + ' {iri: "'
            + asset_iri
            + '"})-[r1:'
            + RelationshipTypes.HAS_SUPPLEMENTARY_FILE.value
            + "]->(t)-[r2:"
            + RelationshipTypes.KEYWORD_EXTRACTION.value
            + "]->(c) RETURN c.keyword"
        ).to_table()

        keyword_list = [keyword[0] for keyword in keywords_table]

        return set(keyword_list)

    def reset_dimension_clusters(self):
        self.ps.graph_run(
            f"MATCH (n:{NodeTypes.DIMENSION_CLUSTER.value}) DETACH DELETE n"
        )

    def create_dimension_cluster(
        self,
        iri: str,
        id_short: str,
        description: str | None = None,
        caption: str | None = None,
    ):
        cluster_node = DimensionClusterNode(
            iri=iri, id_short=id_short, description=description, caption=caption
        )
        self.ps.graph_push(cluster_node)

    def add_file_to_dimension_cluster(self, file_iri: str, cluster_iri: str):
        relationship = Relationship(
            NodeMatcher(self.ps.graph)
            .match(NodeTypes.SUPPLEMENTARY_FILE.value, iri=file_iri)
            .first(),
            RelationshipTypes.PART_OF_DIMENSION_CLUSTER.value,
            NodeMatcher(self.ps.graph)
            .match(NodeTypes.DIMENSION_CLUSTER.value, iri=cluster_iri)
            .first(),
        )

        self.ps.graph_create(relationship)
