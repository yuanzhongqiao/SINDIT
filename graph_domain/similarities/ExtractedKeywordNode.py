from dataclasses import dataclass
from enum import Enum
import json
from typing import List

from dataclasses_json import dataclass_json
from py2neo.ogm import Property, RelatedTo

from graph_domain.BaseNode import BaseNode
from graph_domain.main_digital_twin.DatabaseConnectionNode import DatabaseConnectionNode
from graph_domain.main_digital_twin.RuntimeConnectionNode import RuntimeConnectionNode
from graph_domain.main_digital_twin.UnitNode import UnitNode
from graph_domain.main_digital_twin.factory_graph_types import (
    NodeTypes,
    RelationshipTypes,
)
from backend.exceptions.GraphNotConformantToMetamodelError import (
    GraphNotConformantToMetamodelError,
)

LABEL = NodeTypes.EXTRACTED_KEYWORD.value


@dataclass
@dataclass_json
class ExtractedKeywordNode(BaseNode):
    """
    Keyword node without relationships, only containing properties
    """

    # Identifier for the node-type:
    __primarylabel__ = LABEL

    # Additional properties:
    keyword: str = Property()

    def validate_metamodel_conformance(self):
        """
        Used to validate if the current node (self) and its child elements is conformant to the defined metamodel.
        Raises GraphNotConformantToMetamodelError if there are inconsistencies
        """
        super().validate_metamodel_conformance()
