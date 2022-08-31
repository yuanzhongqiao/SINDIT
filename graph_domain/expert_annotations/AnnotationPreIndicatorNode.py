from dataclasses import dataclass
from datetime import datetime
from enum import Enum
import json
from typing import List

from dataclasses_json import dataclass_json
from py2neo.ogm import Property, RelatedTo

from graph_domain.BaseNode import BaseNode
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

LABEL = NodeTypes.ANNOTATION_PRE_INDICATOR.value


@dataclass
@dataclass_json
class AnnotationPreIndicatorNodeFlat(BaseNode):
    """
    Flat expert annotation pre indicator node without relationships, only containing properties
    """

    # Identifier for the node-type:
    __primarylabel__ = LABEL

    # Additional properties:
    creation_date_time: datetime = Property()
    indicator_start_date_time: datetime = Property()
    indicator_end_date_time: datetime = Property()

    def validate_metamodel_conformance(self):
        """
        Used to validate if the current node (self) and its child elements is conformant to the defined metamodel.
        Raises GraphNotConformantToMetamodelError if there are inconsistencies
        """
        super().validate_metamodel_conformance()

        if self.creation_date_time is None:
            raise GraphNotConformantToMetamodelError(self, f"Missing creation date.")

        if self.indicator_start_date_time is None:
            raise GraphNotConformantToMetamodelError(
                self, f"Missing indicator start date."
            )

        if self.indicator_end_date_time is None:
            raise GraphNotConformantToMetamodelError(
                self, f"Missing indicator end date."
            )


@dataclass
@dataclass_json
class AnnotationPreIndicatorNodeDeep(AnnotationPreIndicatorNodeFlat):
    """
    Deep expert annotation pre indicator node with relationships
    """

    __primarylabel__ = LABEL

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

        for ts_matcher in self.ts_matchers:
            ts_matcher.validate_metamodel_conformance()
