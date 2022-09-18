from dataclasses import dataclass
from datetime import datetime
from enum import Enum
import json
from typing import List

from dataclasses_json import dataclass_json
from py2neo.ogm import Property, RelatedTo

from graph_domain.BaseNode import BaseNode
from graph_domain.main_digital_twin.TimeseriesNode import TimeseriesNodeDeep
from graph_domain.similarities.TimeseriesClusterNode import TimeseriesClusterNode
from graph_domain.main_digital_twin.UnitNode import UnitNode
from graph_domain.factory_graph_types import (
    NodeTypes,
    RelationshipTypes,
)
from backend.exceptions.GraphNotConformantToMetamodelError import (
    GraphNotConformantToMetamodelError,
)

LABEL = NodeTypes.ANNOTATION_TS_MATCHER.value


@dataclass
@dataclass_json
class AnnotationTimeseriesMatcherNodeFlat(BaseNode):
    """
    Flat expert annotation instance node without relationships, only containing properties
    """

    # Identifier for the node-type:
    __primarylabel__ = LABEL

    def validate_metamodel_conformance(self):
        """
        Used to validate if the current node (self) and its child elements is conformant to the defined metamodel.
        Raises GraphNotConformantToMetamodelError if there are inconsistencies
        """
        super().validate_metamodel_conformance()


@dataclass
@dataclass_json
class AnnotationTimeseriesMatcherNodeDeep(AnnotationTimeseriesMatcherNodeFlat):
    """
    Deep expert annotation instance node with relationships
    """

    __primarylabel__ = LABEL

    _ts_matches: List[TimeseriesNodeDeep] = RelatedTo(
        TimeseriesNodeDeep,
        RelationshipTypes.TS_MATCH.value,
    )

    # The OGM framework does not allow constraining to only one item!
    # Can only be one unit (checked by metamodel validator)
    _original_ts: List[TimeseriesNodeDeep] = RelatedTo(
        TimeseriesNodeDeep, RelationshipTypes.ORIGINAL_ANNOTATED.value
    )

    @property
    def original_ts(self) -> TimeseriesNodeDeep:
        if len(self._original_ts) > 0:
            return [ts for ts in self._original_ts][0]
        else:
            return None

    @property
    def ts_matches(self) -> List[TimeseriesNodeDeep]:
        return [match for match in self._ts_matches]

    def validate_metamodel_conformance(self):
        """
        Used to validate if the current node (self) and its child elements is conformant to the defined metamodel.
        Raises GraphNotConformantToMetamodelError if there are inconsistencies
        """
        super().validate_metamodel_conformance()

        for ts in self.ts_matches:
            ts.validate_metamodel_conformance()

        if not len(self._original_ts) == 1:
            raise GraphNotConformantToMetamodelError(
                self,
                f"Invalid number of original timeseries connected to a annotation TS matcher: {len(self._original_ts)}",
            )

        self.original_ts.validate_metamodel_conformance()
