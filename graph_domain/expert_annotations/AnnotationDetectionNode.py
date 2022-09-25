from dataclasses import dataclass
from datetime import datetime

from typing import List

from dataclasses_json import dataclass_json
from py2neo.ogm import Property, Related

from graph_domain.BaseNode import BaseNode
from graph_domain.expert_annotations.AnnotationDefinitionNode import (
    AnnotationDefinitionNodeDeep,
)
from graph_domain.expert_annotations.AnnotationInstanceNode import (
    AnnotationInstanceNodeDeep,
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

LABEL = NodeTypes.ANNOTATION_DETECTION.value


@dataclass
@dataclass_json
class AnnotationDetectionNodeFlat(BaseNode):
    """
    Flat expert annotation detection node without relationships, only containing properties
    """

    # Identifier for the node-type:
    __primarylabel__ = LABEL

    # Additional properties:
    _confirmation_date_time: str | datetime | None = Property(
        key="confirmation_date_time"
    )

    @property
    def confirmation_date_time(self) -> datetime:
        return neo4j_str_or_datetime_to_datetime(self._confirmation_date_time)

    @confirmation_date_time.setter
    def confirmation_date_time(self, value):
        self._confirmation_date_time = datetime_to_neo4j_str(value)

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
class AnnotationDetectionNodeDeep(AnnotationDetectionNodeFlat):
    """
    Deep expert annotation instance node with relationships
    """

    __primarylabel__ = LABEL

    # The OGM framework does not allow constraining to only one item!
    # Can only be one unit (checked by metamodel validator)
    _definition: List[AnnotationDefinitionNodeDeep] = Related(
        AnnotationDefinitionNodeDeep, RelationshipTypes.DETECTED_OCCURANCE.value
    )

    @property
    def definition(self) -> AnnotationDefinitionNodeDeep:
        if len(self._definition) > 0:
            return [definition for definition in self._definition][0]
        else:
            return None

    # The OGM framework does not allow constraining to only one item!
    # Can only be one unit (checked by metamodel validator)
    _matching_instance: List[AnnotationInstanceNodeDeep] = Related(
        AnnotationInstanceNodeDeep, RelationshipTypes.MATCHING_INSTANCE.value
    )

    @property
    def matching_instance(self) -> AnnotationInstanceNodeDeep:
        if len(self._matching_instance) > 0:
            return [matching_instance for matching_instance in self._matching_instance][
                0
            ]
        else:
            return None

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
                self, "Only one annotation definition per detection."
            )
        self.definition.validate_metamodel_conformance()

        if len(self._matching_instance) < 1:
            raise GraphNotConformantToMetamodelError(self, "Missing matching instance.")

        if len(self._matching_instance) > 1:
            raise GraphNotConformantToMetamodelError(
                self, "A detection can only refer to one matching instance."
            )
        self.matching_instance.validate_metamodel_conformance()
