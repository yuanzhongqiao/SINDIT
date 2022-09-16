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
