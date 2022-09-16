from datetime import datetime
import json
from typing import List
from py2neo import Node, NodeMatcher, Relationship
from graph_domain.expert_annotations.AnnotationDefinitionNode import (
    AnnotationDefinitionNodeFlat,
)
from graph_domain.expert_annotations.AnnotationInstanceNode import (
    AnnotationInstanceNodeFlat,
)
from graph_domain.expert_annotations.AnnotationTimeseriesMatcherNode import (
    AnnotationTimeseriesMatcherNodeFlat,
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

    def create_annotation_definition(
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

    def create_annotation_instance(
        self,
        id_short: str,
        start_datetime: datetime,
        end_datetime: datetime,
        caption: str | None = None,
        description: str | None = None,
    ) -> str:
        """Creates a new annotation instance"""
        iri = IRI_PREFIX_ANNOTATION_INSTANCE + id_short

        instance = AnnotationInstanceNodeFlat(
            id_short=id_short,
            iri=iri,
            caption=caption,
            description=description,
            creation_date_time=datetime.now(),
            occurance_start_date_time=start_datetime,
            occurance_end_date_time=end_datetime,
        )
        self.ps.graph.push(instance)

        return iri

    def create_annotation_ts_matcher(self, id_short: str, caption: str) -> str:
        """Creates a new annotation instance"""
        iri = IRI_PREFIX_ANNOTATION_TS_MATCHER + id_short

        instance = AnnotationTimeseriesMatcherNodeFlat(
            id_short=id_short, iri=iri, caption=caption
        )
        self.ps.graph.push(instance)

        return iri

    def create_annotation_instance_of_definition_relationship(
        self, definition_iri: str, instance_iri: str
    ) -> str:

        relationship = Relationship(
            NodeMatcher(self.ps.graph)
            .match(NodeTypes.ANNOTATION_INSTANCE.value, iri=instance_iri)
            .first(),
            RelationshipTypes.INSTANCE_OF.value,
            NodeMatcher(self.ps.graph)
            .match(NodeTypes.ANNOTATION_DEFINITION.value, iri=definition_iri)
            .first(),
        )
        self.ps.graph.create(relationship)

    def create_annotation_instance_asset_relationship(
        self, instance_iri: str, asset_iri: str
    ) -> str:

        relationship = Relationship(
            NodeMatcher(self.ps.graph)
            .match(NodeTypes.ASSET.value, iri=asset_iri)
            .first(),
            RelationshipTypes.ANNOTATION.value,
            NodeMatcher(self.ps.graph)
            .match(NodeTypes.ANNOTATION_INSTANCE.value, iri=instance_iri)
            .first(),
        )
        self.ps.graph.create(relationship)

    def create_annotation_occurance_scan_relationship(
        self, definition_iri: str, asset_iri: str
    ) -> str:

        relationship = Relationship(
            NodeMatcher(self.ps.graph)
            .match(NodeTypes.ASSET.value, iri=asset_iri)
            .first(),
            RelationshipTypes.OCCURANCE_SCAN.value,
            NodeMatcher(self.ps.graph)
            .match(NodeTypes.ANNOTATION_DEFINITION.value, iri=definition_iri)
            .first(),
        )
        self.ps.graph.create(relationship)

    def create_annotation_ts_matcher_instance_relationship(
        self, ts_matcher_iri: str, instance_iri: str
    ) -> str:

        relationship = Relationship(
            NodeMatcher(self.ps.graph)
            .match(NodeTypes.ANNOTATION_INSTANCE.value, iri=instance_iri)
            .first(),
            RelationshipTypes.DETECTABLE_WITH.value,
            NodeMatcher(self.ps.graph)
            .match(NodeTypes.ANNOTATION_TS_MATCHER.value, iri=ts_matcher_iri)
            .first(),
        )
        self.ps.graph.create(relationship)

    def create_annotation_ts_match_relationship(
        self, ts_matcher_iri: str, ts_iri: str, original_annotation: bool
    ) -> str:
        """Relationship for a ts-match

        Args:
            ts_matcher_iri (str): _description_
            ts_iri (str): _description_
            original_annotation (bool): If yes, an additional relationship of the
            "ORIGINAL_ANNOTATION" type will be creted as well

        Returns:
            str: _description_
        """

        match_relationship = Relationship(
            NodeMatcher(self.ps.graph)
            .match(NodeTypes.ANNOTATION_TS_MATCHER.value, iri=ts_matcher_iri)
            .first(),
            RelationshipTypes.TS_MATCH.value,
            NodeMatcher(self.ps.graph)
            .match(NodeTypes.TIMESERIES_INPUT.value, iri=ts_iri)
            .first(),
        )
        self.ps.graph.create(match_relationship)

        if original_annotation:
            match_relationship = Relationship(
                NodeMatcher(self.ps.graph)
                .match(NodeTypes.ANNOTATION_TS_MATCHER.value, iri=ts_matcher_iri)
                .first(),
                RelationshipTypes.ORIGINAL_ANNOTATED.value,
                NodeMatcher(self.ps.graph)
                .match(NodeTypes.TIMESERIES_INPUT.value, iri=ts_iri)
                .first(),
            )
        self.ps.graph.create(match_relationship)

    @validate_result_nodes
    def get_instances_of_annotation_definition(
        self, definition_iri: str
    ) -> List[AnnotationInstanceNodeFlat]:
        """
        Queries all available instances for the specified annotation definition node.
        :param self:
        :return:
        :raises GraphNotConformantToMetamodelError: If Graph not conformant
        """
        matches = self.ps.repo.match(model=AnnotationInstanceNodeFlat).where(
            "(_)-[:"
            + RelationshipTypes.INSTANCE_OF.value
            + "]->(: "
            + NodeTypes.ANNOTATION_DEFINITION.value
            + ' {iri: "'
            + definition_iri
            + '"}) '
        )

        return matches.all()

    @validate_result_nodes
    def get_ts_matchers_only_used_for(
        self, instance_iri: str
    ) -> List[AnnotationTimeseriesMatcherNodeFlat]:
        """
        Queries time-series matchers for the specified annotation instance node.
        Only returns matchers exclusively used by this instance (They could be reused).
        :param self:
        :return:
        :raises GraphNotConformantToMetamodelError: If Graph not conformant
        """
        matches = self.ps.repo.match(model=AnnotationTimeseriesMatcherNodeFlat).where(
            "(_)<-[:"
            + RelationshipTypes.DETECTABLE_WITH.value
            + " *..1]-(: "
            + NodeTypes.ANNOTATION_INSTANCE.value
            + ") AND (_)<-[:"
            + RelationshipTypes.DETECTABLE_WITH.value
            + "]-(:"
            + NodeTypes.ANNOTATION_INSTANCE.value
            + ' {iri: "'
            + instance_iri
            + '"}) '
        )

        return matches.all()

    def delete_annotation_definition(self, definition_iri):
        """Deletes a definition and the attached relationships.
        Make sure to delete instances before,
        as they would be missing their definition instead!

        Args:
            definition_iri (_type_): _description_
        """
        self.ps.graph.run(
            f"MATCH (n:{NodeTypes.ANNOTATION_DEFINITION.value}) WHERE n.iri = '{definition_iri}' DETACH DELETE n"
        )

    def delete_annotation_ts_matcher(self, ts_matcher_iri):
        """Deletes a time-series matcher and the attached relationships."""
        self.ps.graph.run(
            f"MATCH (n:{NodeTypes.ANNOTATION_TS_MATCHER.value}) WHERE n.iri = '{ts_matcher_iri}' DETACH DELETE n"
        )

    def delete_annotation_instance(self, instance_iri):
        """Deletes a annotation instance and the attached relationships."""
        self.ps.graph.run(
            f"MATCH (n:{NodeTypes.ANNOTATION_INSTANCE.value}) WHERE n.iri = '{instance_iri}' DETACH DELETE n"
        )
