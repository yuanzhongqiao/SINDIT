from dataclasses import dataclass
from datetime import datetime

from typing import List

from dataclasses_json import dataclass_json
from py2neo.ogm import Property, Related

from graph_domain.BaseNode import BaseNode
from graph_domain.expert_annotations.AnnotationDefinitionNode import (
    AnnotationDefinitionNodeDeep,
)

from graph_domain.expert_annotations.AnnotationPreIndicatorNode import (
    AnnotationPreIndicatorNodeDeep,
)
from graph_domain.expert_annotations.AnnotationTimeseriesMatcherNode import (
    AnnotationTimeseriesMatcherNodeDeep,
)

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
    activate_occurance_scan: bool = Property(default=True)

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
            raise GraphNotConformantToMetamodelError(self, "Missing creation date.")

        if self.occurance_start_date_time is None:
            raise GraphNotConformantToMetamodelError(
                self, "Missing occurance start date."
            )

        if self.occurance_end_date_time is None:
            raise GraphNotConformantToMetamodelError(
                self, "Missing occurance end date."
            )


@dataclass
@dataclass_json
class AnnotationInstanceNodeDeep(AnnotationInstanceNodeFlat):
    """
    Deep expert annotation instance node with relationships
    """

    __primarylabel__ = LABEL

    # The OGM framework does not allow constraining to only one item!
    # Can only be one unit (checked by metamodel validator)
    _definition: List[AnnotationDefinitionNodeDeep] = Related(
        AnnotationDefinitionNodeDeep, RelationshipTypes.INSTANCE_OF.value
    )

    @property
    def definition(self) -> AnnotationDefinitionNodeDeep:
        if len(self._definition) > 0:
            return [definition for definition in self._definition][0]
        else:
            return None

    _pre_indicators: List[AnnotationPreIndicatorNodeDeep] = Related(
        AnnotationPreIndicatorNodeDeep, RelationshipTypes.PRE_INDICATABLE_WITH.value
    )

    @property
    def pre_indicators(self) -> List[AnnotationPreIndicatorNodeDeep]:
        return [indicator for indicator in self._pre_indicators]

    _ts_matchers: List[AnnotationTimeseriesMatcherNodeDeep] = Related(
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

        if len(self._definition) < 1:
            raise GraphNotConformantToMetamodelError(
                self, "Missing annotation definition."
            )

        if len(self._definition) > 1:
            raise GraphNotConformantToMetamodelError(
                self, "Only one annotation definition per instance."
            )
        self.definition.validate_metamodel_conformance()

        for pre_ind in self.pre_indicators:
            pre_ind.validate_metamodel_conformance()

        for ts_matcher in self.ts_matchers:
            ts_matcher.validate_metamodel_conformance()
