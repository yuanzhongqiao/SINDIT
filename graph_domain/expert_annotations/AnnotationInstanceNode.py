from dataclasses import dataclass
from datetime import datetime
from enum import Enum
import json
from typing import List

from dataclasses_json import dataclass_json
from py2neo.ogm import Property, RelatedTo

from graph_domain.BaseNode import BaseNode

from graph_domain.expert_annotations.AnnotationPreIndicatorNode import (
    AnnotationPreIndicatorNodeDeep,
)
from graph_domain.expert_annotations.AnnotationTimeseriesMatcherNode import (
    AnnotationTimeseriesMatcherNodeDeep,
)
from graph_domain.main_digital_twin.DatabaseConnectionNode import DatabaseConnectionNode
from graph_domain.main_digital_twin.RuntimeConnectionNode import RuntimeConnectionNode
from graph_domain.similarities.TimeseriesClusterNode import TimeseriesClusterNode
from graph_domain.main_digital_twin.UnitNode import UnitNode
from graph_domain.factory_graph_types import (
    NodeTypes,
    RelationshipTypes,
)
from backend.exceptions.GraphNotConformantToMetamodelError import (
    GraphNotConformantToMetamodelError,
)
from util.datetime_utils import (
    datetime_to_neo4j_str,
    neo4j_str_or_datetime_to_datetime,
    neo4j_str_to_datetime,
)

LABEL = NodeTypes.ANNOTATION_INSTANCE.value


@dataclass
@dataclass_json
class AnnotationInstanceNodeFlat(BaseNode):
    """
    Flat expert annotation instance node without relationships, only containing properties
    """

    # Identifier for the node-type:
    __primarylabel__ = LABEL

    # Additional properties:
    _creation_date_time: str | datetime = Property(key="creation_date_time")

    @property
    def creation_date_time(self) -> datetime:
        return neo4j_str_or_datetime_to_datetime(self._creation_date_time)

    @creation_date_time.setter
    def creation_date_time(self, value):
        self._creation_date_time = datetime_to_neo4j_str(value)

    _occurance_start_date_time: str | datetime = Property(
        key="occurance_start_date_time"
    )

    @property
    def occurance_start_date_time(self) -> datetime:
        return neo4j_str_or_datetime_to_datetime(self._occurance_start_date_time)

    @occurance_start_date_time.setter
    def occurance_start_date_time(self, value):
        self._occurance_start_date_time = datetime_to_neo4j_str(value)

    _occurance_end_date_time: str | datetime = Property(key="occurance_end_date_time")

    @property
    def occurance_end_date_time(self) -> datetime:
        return neo4j_str_or_datetime_to_datetime(self._occurance_end_date_time)

    @occurance_end_date_time.setter
    def occurance_end_date_time(self, value):
        self._occurance_end_date_time = datetime_to_neo4j_str(value)

    def validate_metamodel_conformance(self):
        """
        Used to validate if the current node (self) and its child elements is conformant to the defined metamodel.
        Raises GraphNotConformantToMetamodelError if there are inconsistencies
        """
        super().validate_metamodel_conformance()

        if self.creation_date_time is None:
            raise GraphNotConformantToMetamodelError(self, f"Missing creation date.")

        if self.occurance_start_date_time is None:
            raise GraphNotConformantToMetamodelError(
                self, f"Missing occurance start date."
            )

        if self.occurance_end_date_time is None:
            raise GraphNotConformantToMetamodelError(
                self, f"Missing occurance end date."
            )


@dataclass
@dataclass_json
class AnnotationInstanceNodeDeep(AnnotationInstanceNodeFlat):
    """
    Deep expert annotation instance node with relationships
    """

    __primarylabel__ = LABEL

    _pre_indicators: List[AnnotationPreIndicatorNodeDeep] = RelatedTo(
        AnnotationPreIndicatorNodeDeep, RelationshipTypes.PRE_INDICATABLE_WITH.value
    )

    @property
    def pre_indicators(self) -> List[AnnotationPreIndicatorNodeDeep]:
        return [indicator for indicator in self._pre_indicators]

    _ts_matchers: List[AnnotationTimeseriesMatcherNodeDeep] = RelatedTo(
        AnnotationTimeseriesMatcherNodeDeep,
        RelationshipTypes.DETECTABLE_WITH.value,
    )

    @property
    def ts_matchers(self) -> List[AnnotationTimeseriesMatcherNodeDeep]:
        return [matcher for matcher in self._ts_matchers]

    def validate_metamodel_conformance(self):
        """
        Used to validate if the current node (self) and its child elements is conformant to the defined metamodel.
        Raises GraphNotConformantToMetamodelError if there are inconsistencies
        """
        super().validate_metamodel_conformance()

        for pre_ind in self.pre_indicators:
            pre_ind.validate_metamodel_conformance()

        for ts_matcher in self.ts_matchers:
            ts_matcher.validate_metamodel_conformance()
