from dataclasses import dataclass
from enum import Enum
import json
from typing import List

from dataclasses_json import dataclass_json
from py2neo.ogm import Property, RelatedTo

from graph_domain.BaseNode import BaseNode
from graph_domain.expert_annotations.AnnotationInstanceNode import (
    AnnotationInstanceNodeDeep,
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

LABEL = NodeTypes.ANNOTATION_DEFINITION.value


@dataclass
@dataclass_json
class AnnotationDefinitionNodeFlat(BaseNode):
    """
    Flat expert annotation node without relationships, only containing properties
    """

    # Identifier for the node-type:
    __primarylabel__ = LABEL

    # Additional properties:
    solution_proposal: str = Property()

    def validate_metamodel_conformance(self):
        """
        Used to validate if the current node (self) and its child elements is conformant to the defined metamodel.
        Raises GraphNotConformantToMetamodelError if there are inconsistencies
        """
        super().validate_metamodel_conformance()

        if self.solution_proposal is None:
            raise GraphNotConformantToMetamodelError(
                self, f"Missing solution proposal."
            )


@dataclass
@dataclass_json
class AnnotationDefinitionNodeDeep(AnnotationDefinitionNodeFlat):
    """
    Deep expert annotation node with relationships
    """

    __primarylabel__ = LABEL

    _instances: List[AnnotationInstanceNodeDeep] = RelatedTo(
        AnnotationInstanceNodeDeep, RelationshipTypes.INSTANCE_OF.value
    )

    @property
    def instances(self) -> List[AnnotationInstanceNodeDeep]:
        return [annotation for annotation in self._instances]

    def validate_metamodel_conformance(self):
        """
        Used to validate if the current node (self) and its child elements is conformant to the defined metamodel.
        Raises GraphNotConformantToMetamodelError if there are inconsistencies
        """
        super().validate_metamodel_conformance()

        for instance in self.instances:
            instance.validate_metamodel_conformance()
