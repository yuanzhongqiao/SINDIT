from datetime import datetime
from typing import List
from py2neo import NodeMatcher, Relationship
from graph_domain.expert_annotations.AnnotationDefinitionNode import (
    AnnotationDefinitionNodeFlat,
)
from dateutil import tz
from graph_domain.expert_annotations.AnnotationDetectionNode import (
    AnnotationDetectionNodeFlat,
)
from graph_domain.expert_annotations.AnnotationInstanceNode import (
    AnnotationInstanceNodeDeep,
    AnnotationInstanceNodeFlat,
)
from graph_domain.main_digital_twin.AssetNode import AssetNodeFlat

from util.environment_and_configuration import ConfigGroups, get_configuration
from graph_domain.expert_annotations.AnnotationTimeseriesMatcherNode import (
    AnnotationTimeseriesMatcherNodeFlat,
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
from graph_domain.main_digital_twin.TimeseriesNode import TimeseriesNodeFlat

# TODO: move to a global place
IRI_PREFIX_GLOBAL = "www.sintef.no/aas_identifiers/learning_factory/"
IRI_PREFIX_ANNOTATION_INSTANCE = IRI_PREFIX_GLOBAL + "annotations/instances/"
IRI_PREFIX_ANNOTATION_DETECTION = IRI_PREFIX_GLOBAL + "annotations/detections/"
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

        # pylint: disable=unexpected-keyword-arg
        definition = AnnotationDefinitionNodeFlat(
            id_short=id_short,
            iri=iri,
            solution_proposal=solution_proposal,
            caption=caption,
            description=description,
        )
        self.ps.graph_push(definition)

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

        # pylint: disable=unexpected-keyword-arg
        instance = AnnotationInstanceNodeFlat(
            id_short=id_short,
            iri=iri,
            caption=caption,
            description=description,
            creation_date_time=datetime.now(),
            occurance_start_date_time=start_datetime,
            occurance_end_date_time=end_datetime,
        )
        self.ps.graph_push(instance)

        return iri

    def create_annotation_detection(
        self,
        id_short: str,
        start_datetime: datetime,
        end_datetime: datetime,
        caption: str | None = None,
        description: str | None = None,
        confirmed: bool = False,
    ) -> str:
        """Creates a new annotation detection"""
        iri = IRI_PREFIX_ANNOTATION_DETECTION + id_short

        # pylint: disable=unexpected-keyword-arg
        instance = AnnotationDetectionNodeFlat(
            id_short=id_short,
            iri=iri,
            caption=caption,
            description=description,
            occurance_start_date_time=start_datetime,
            occurance_end_date_time=end_datetime,
            # confirmation_date_time=datetime.now() if confirmed else None,
        )
        self.ps.graph_push(instance)

        return iri

    def create_annotation_ts_matcher(self, id_short: str, caption: str) -> str:
        """Creates a new annotation instance"""
        iri = IRI_PREFIX_ANNOTATION_TS_MATCHER + id_short

        # pylint: disable=unexpected-keyword-arg
        instance = AnnotationTimeseriesMatcherNodeFlat(
            id_short=id_short, iri=iri, caption=caption
        )
        self.ps.graph_push(instance)

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
        self.ps.graph_create(relationship)

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
        self.ps.graph_create(relationship)

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
        self.ps.graph_create(relationship)

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
        self.ps.graph_create(relationship)

    def create_annotation_detection_timeseries_relationship(
        self, detection_iri: str, timeseries_iri: str
    ) -> str:

        relationship = Relationship(
            NodeMatcher(self.ps.graph)
            .match(NodeTypes.ANNOTATION_DETECTION.value, iri=detection_iri)
            .first(),
            RelationshipTypes.MATCHING_TIMESERIES.value,
            NodeMatcher(self.ps.graph)
            .match(NodeTypes.TIMESERIES_INPUT.value, iri=timeseries_iri)
            .first(),
        )
        self.ps.graph_create(relationship)

    def create_annotation_detection_instance_relationship(
        self, detection_iri: str, instance_iri: str
    ) -> str:

        relationship = Relationship(
            NodeMatcher(self.ps.graph)
            .match(NodeTypes.ANNOTATION_DETECTION.value, iri=detection_iri)
            .first(),
            RelationshipTypes.MATCHING_INSTANCE.value,
            NodeMatcher(self.ps.graph)
            .match(NodeTypes.ANNOTATION_INSTANCE.value, iri=instance_iri)
            .first(),
        )
        self.ps.graph_create(relationship)

    def create_annotation_detection_asset_relationship(
        self, detection_iri: str, asset_iri: str
    ) -> str:

        relationship = Relationship(
            NodeMatcher(self.ps.graph)
            .match(NodeTypes.ASSET.value, iri=asset_iri)
            .first(),
            RelationshipTypes.DETECTED_ANNOTATION_OCCURANCE.value,
            NodeMatcher(self.ps.graph)
            .match(NodeTypes.ANNOTATION_DETECTION.value, iri=detection_iri)
            .first(),
        )
        self.ps.graph_create(relationship)

    def create_confirmed_detection_instance_relationship(
        self, detection_iri: str, instance_iri: str
    ) -> str:

        relationship = Relationship(
            NodeMatcher(self.ps.graph)
            .match(NodeTypes.ANNOTATION_INSTANCE.value, iri=instance_iri)
            .first(),
            RelationshipTypes.CREATED_OUT_OF.value,
            NodeMatcher(self.ps.graph)
            .match(NodeTypes.ANNOTATION_DETECTION.value, iri=detection_iri)
            .first(),
        )
        self.ps.graph_create(relationship)

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
        self.ps.graph_create(match_relationship)

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
        self.ps.graph_create(match_relationship)

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
        matches = self.ps.repo_match(model=AnnotationInstanceNodeFlat).where(
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
        matches = self.ps.repo_match(model=AnnotationTimeseriesMatcherNodeFlat).where(
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
        self.ps.graph_run(
            f"MATCH (n:{NodeTypes.ANNOTATION_DEFINITION.value}) WHERE n.iri = '{definition_iri}' DETACH DELETE n"
        )

    def delete_annotation_ts_matcher(self, ts_matcher_iri):
        """Deletes a time-series matcher and the attached relationships."""
        self.ps.graph_run(
            f"MATCH (n:{NodeTypes.ANNOTATION_TS_MATCHER.value}) WHERE n.iri = '{ts_matcher_iri}' DETACH DELETE n"
        )

    def delete_annotation_instance(self, instance_iri):
        """Deletes a annotation instance and the attached relationships."""
        self.ps.graph_run(
            f"MATCH (n:{NodeTypes.ANNOTATION_INSTANCE.value}) WHERE n.iri = '{instance_iri}' DETACH DELETE n"
        )

    def delete_annotation_detection(self, detection_iri):
        """Deletes a detection and the attached relationships."""
        self.ps.graph_run(
            f"MATCH (n:{NodeTypes.ANNOTATION_DETECTION.value}) WHERE n.iri = '{detection_iri}' DETACH DELETE n"
        )

    @validate_result_nodes
    def get_matcher_annotation_instance(self, matcher_iri):
        """Returns the instance node that the matcher is related to"""
        matches = self.ps.repo_match(model=AnnotationInstanceNodeFlat).where(
            "(_)-[:"
            + RelationshipTypes.DETECTABLE_WITH.value
            + "]->(:"
            + NodeTypes.ANNOTATION_TS_MATCHER.value
            + ' {iri: "'
            + matcher_iri
            + '"}) '
        )

        return matches.first()

    @validate_result_nodes
    def get_matcher_original_annotated_ts(self, matcher_iri) -> TimeseriesNodeFlat:
        """Returns the timeseries node that the matcher is related to"""
        matches = self.ps.repo_match(model=TimeseriesNodeFlat).where(
            "(_)<-[:"
            + RelationshipTypes.ORIGINAL_ANNOTATED.value
            + "]-(:"
            + NodeTypes.ANNOTATION_TS_MATCHER.value
            + ' {iri: "'
            + matcher_iri
            + '"}) '
        )

        return matches.first()

    @validate_result_nodes
    def get_matched_ts_for_matcher(self, matcher_iri) -> List[TimeseriesNodeFlat]:
        matches = self.ps.repo_match(model=TimeseriesNodeFlat).where(
            "(_)<-[:"
            + RelationshipTypes.TS_MATCH.value
            + "]-(:"
            + NodeTypes.ANNOTATION_TS_MATCHER.value
            + ' {iri: "'
            + matcher_iri
            + '"}) '
        )

        return matches.all()

    @validate_result_nodes
    def get_annotation_instance_for_definition(self, definition_iri):
        """Returns the instances related to the given annotation definition"""
        matches = self.ps.repo_match(model=AnnotationInstanceNodeFlat).where(
            "(_)-[:"
            + RelationshipTypes.INSTANCE_OF.value
            + "]->(:"
            + NodeTypes.ANNOTATION_DEFINITION.value
            + ' {iri: "'
            + definition_iri
            + '"}) '
        )

        return matches.all()

    @validate_result_nodes
    def get_scanned_assets_for_annotation_instance(
        self, instance_iri
    ) -> List[AssetNodeFlat]:
        matches = self.ps.repo_match(model=AssetNodeFlat).where(
            "(_)-[:"
            + RelationshipTypes.OCCURANCE_SCAN.value
            + "]->(:"
            + NodeTypes.ANNOTATION_DEFINITION.value
            + ")<-[:"
            + RelationshipTypes.INSTANCE_OF.value
            + "]-(:"
            + NodeTypes.ANNOTATION_INSTANCE.value
            + ' {iri: "'
            + instance_iri
            + '"}) '
        )

        return matches.all()

    def get_annotation_instance_count_for_definition(self, definition_iri):
        """Returns the instances related to the given annotation definition"""

        return len(self.get_annotation_instance_for_definition(definition_iri))

    @validate_result_nodes
    def get_annotation_instances(self):
        matches = self.ps.repo_match(model=AnnotationInstanceNodeFlat)

        return matches.all()

    def get_annotation_instance_count(self):
        return len(self.get_annotation_instances())

    def set_detection_confirmation_date_time(self, detection_iri):

        detection_matches = self.ps.repo_match(model=AnnotationDetectionNodeFlat)

        detection_node: AnnotationDetectionNodeFlat = detection_matches.first()

        detection_node.confirmation_date_time = datetime.now().astimezone(
            tz.gettz(get_configuration(group=ConfigGroups.FRONTEND, key="timezone"))
        )
        self.ps.graph_push(detection_node)

    @validate_result_nodes
    def get_oldest_unconfirmed_detection(self) -> AnnotationDetectionNodeFlat | None:
        matches = (
            self.ps.repo_match(model=AnnotationDetectionNodeFlat)
            .where("not exists(_.confirmation_date_time)")
            .order_by("_.confirmation_date_time ASC")
        )

        return matches.first()

    @validate_result_nodes
    def get_matched_ts_for_detection(self, detection_iri) -> List[TimeseriesNodeFlat]:
        matches = self.ps.repo_match(model=TimeseriesNodeFlat).where(
            "(_)<-[:"
            + RelationshipTypes.MATCHING_TIMESERIES.value
            + "]-(:"
            + NodeTypes.ANNOTATION_DETECTION.value
            + ' {iri: "'
            + detection_iri
            + '"})'
        )

        return matches.all()

    @validate_result_nodes
    def get_asset_for_detection(self, detection_iri) -> AssetNodeFlat:
        matches = self.ps.repo_match(model=AssetNodeFlat).where(
            "(_)-[:"
            + RelationshipTypes.DETECTED_ANNOTATION_OCCURANCE.value
            + "]->(:"
            + NodeTypes.ANNOTATION_DETECTION.value
            + ' {iri: "'
            + detection_iri
            + '"})'
        )

        return matches.first()

    @validate_result_nodes
    def get_annotation_instance_for_detection(
        self, detection_iri
    ) -> AnnotationInstanceNodeFlat:
        matches = self.ps.repo_match(model=AnnotationInstanceNodeFlat).where(
            "(_)<-[:"
            + RelationshipTypes.MATCHING_INSTANCE.value
            + "]-(:"
            + NodeTypes.ANNOTATION_DETECTION.value
            + ' {iri: "'
            + detection_iri
            + '"})'
        )

        return matches.first()

    @validate_result_nodes
    def get_annotation_definition_for_instance(
        self, instance_iri
    ) -> AnnotationDefinitionNodeFlat:
        matches = self.ps.repo_match(model=AnnotationDefinitionNodeFlat).where(
            "(_)<-[:"
            + RelationshipTypes.INSTANCE_OF.value
            + "]-(:"
            + NodeTypes.ANNOTATION_INSTANCE.value
            + ' {iri: "'
            + instance_iri
            + '"})'
        )

        return matches.first()

    @validate_result_nodes
    def get_asset_for_annotation_instance(self, instance_iri) -> AssetNodeFlat:
        matches = self.ps.repo_match(model=AssetNodeFlat).where(
            "(_)-[:"
            + RelationshipTypes.ANNOTATION.value
            + "]->(:"
            + NodeTypes.ANNOTATION_INSTANCE.value
            + ' {iri: "'
            + instance_iri
            + '"})'
        )

        return matches.first()

    @validate_result_nodes
    def get_confirmed_annotation_detections(self):
        matches = self.ps.repo_match(model=AnnotationDetectionNodeFlat).where(
            "exists(_.confirmation_date_time)"
        )

        return matches.all()

    @validate_result_nodes
    def get_unconfirmed_annotation_detections(self):
        matches = self.ps.repo_match(model=AnnotationDetectionNodeFlat).where(
            "not exists(_.confirmation_date_time)"
        )

        return matches.all()

    def get_annotation_detections_count(self, confirmed: bool = False):
        if confirmed:
            return len(self.get_confirmed_annotation_detections())
        else:
            return len(self.get_unconfirmed_annotation_detections())

    @validate_result_nodes
    def get_matchers_for_annotation_instance(
        self, instance_iri
    ) -> AnnotationTimeseriesMatcherNodeFlat:
        matches = self.ps.repo_match(model=AnnotationTimeseriesMatcherNodeFlat).where(
            "(_)<-[:"
            + RelationshipTypes.DETECTABLE_WITH.value
            + "]-(:"
            + NodeTypes.ANNOTATION_INSTANCE.value
            + ' {iri: "'
            + instance_iri
            + '"})'
        )

        return matches.all()
