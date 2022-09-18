from dataclasses import dataclass
from enum import Enum
import json
from typing import List

from dataclasses_json import dataclass_json
from py2neo.ogm import Property, RelatedTo

from graph_domain.BaseNode import BaseNode
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

LABEL = NodeTypes.TIMESERIES_INPUT.value
UNIT_RELATIONSHIP_LABEL = RelationshipTypes.HAS_UNIT.value
DB_CONNECTION_RELATIONSHIP_LABEL = RelationshipTypes.TIMESERIES_DB_ACCESS.value
RUNTIME_CONNECTION_RELATIONSHIP_LABEL = RelationshipTypes.RUNTIME_ACCESS.value
TS_CLUSTER_RELATIONSHIP_LABEL = RelationshipTypes.PART_OF_TS_CLUSTER.value


class TimeseriesValueTypes(Enum):
    DECIMAL = "DECIMAL"
    INT = "INTEGER"
    STRING = "STRING"
    BOOL = "BOOLEAN"


TIMESERIES_VALUE_TYPES = [con_type.value for con_type in TimeseriesValueTypes]


@dataclass
@dataclass_json
class TimeseriesNodeFlat(BaseNode):
    """
    Flat timeseries node without relationships, only containing properties
    """

    # Identifier for the node-type:
    __primarylabel__ = LABEL

    # Additional properties:
    connection_topic: str = Property()
    connection_keyword: str | None = (
        Property()
    )  # additional keyword as id inside the topic (optional)

    # Type of the value stored per time
    value_type: str = Property(default=TimeseriesValueTypes.DECIMAL.value)

    # Extracted features
    _feature_dict: str | None = Property(key="feature_dict")
    _reduced_feature_list: str | None = Property(key="reduced_feature_list")

    @property
    def feature_dict(self) -> dict:
        return (
            json.loads(self._feature_dict) if self._feature_dict is not None else None
        )

    @property
    def reduced_feature_list(self) -> dict:
        return (
            json.loads(self._reduced_feature_list)
            if self._reduced_feature_list is not None
            else None
        )

    def validate_metamodel_conformance(self):
        """
        Used to validate if the current node (self) and its child elements is conformant to the defined metamodel.
        Raises GraphNotConformantToMetamodelError if there are inconsistencies
        """
        super().validate_metamodel_conformance()

        if self.value_type is None:
            raise GraphNotConformantToMetamodelError(self, f"Missing timeseries type.")

        if not self.value_type in TIMESERIES_VALUE_TYPES:
            raise GraphNotConformantToMetamodelError(
                self,
                f"Unrecognized type of timeseries: {self.value_type}. Known types: {TIMESERIES_VALUE_TYPES}.",
            )

        if self.connection_topic is None:
            raise GraphNotConformantToMetamodelError(self, f"Missing connection topic")


@dataclass
@dataclass_json
class TimeseriesNodeDeep(TimeseriesNodeFlat):
    """
    Deep timeseries node with relationships
    """

    __primarylabel__ = LABEL

    # The OGM framework does not allow constraining to only one item!
    # Can only be one unit (checked by metamodel validator)
    _units: List[UnitNode] = RelatedTo(UnitNode, UNIT_RELATIONSHIP_LABEL)

    # The OGM framework does not allow constraining to only one item!
    # Can only be one unit (checked by metamodel validator)
    _db_connections: List[DatabaseConnectionNode] = RelatedTo(
        DatabaseConnectionNode, DB_CONNECTION_RELATIONSHIP_LABEL
    )

    # The OGM framework does not allow constraining to only one item!
    # Can only be one unit (checked by metamodel validator)
    _runtime_connections: List[RuntimeConnectionNode] = RelatedTo(
        RuntimeConnectionNode, RUNTIME_CONNECTION_RELATIONSHIP_LABEL
    )

    # The OGM framework does not allow constraining to only one item!
    # Can only be one unit (checked by metamodel validator)
    _ts_clusters: List[TimeseriesClusterNode] = RelatedTo(
        TimeseriesClusterNode, TS_CLUSTER_RELATIONSHIP_LABEL
    )

    @property
    def unit(self) -> UnitNode | None:
        if len(self._units) > 0:
            return [unit for unit in self._units][0]
        else:
            return None

    @property
    def db_connection(self) -> DatabaseConnectionNode:
        return [connection for connection in self._db_connections][0]

    @property
    def runtime_connection(self) -> RuntimeConnectionNode | None:
        if len(self._runtime_connections) > 0:
            return [connection for connection in self._runtime_connections][0]
        else:
            return None

    @property
    def ts_cluster(self) -> TimeseriesClusterNode | None:
        clusters = [cluster for cluster in self._ts_clusters]
        return clusters[0] if len(clusters) > 0 else None

    def validate_metamodel_conformance(self):
        """
        Used to validate if the current node (self) and its child elements is conformant to the defined metamodel.
        Raises GraphNotConformantToMetamodelError if there are inconsistencies
        """
        super().validate_metamodel_conformance()

        if len(self._units) > 1:
            raise GraphNotConformantToMetamodelError(
                self,
                f"More than one unit referenced to timeseries. Number of referenced units: {len(self._units)}",
            )

        if self.unit is not None:
            self.unit.validate_metamodel_conformance()

        if not len(self._db_connections) == 1:
            raise GraphNotConformantToMetamodelError(
                self,
                f"Invalid number of referenced database connections: {len(self._db_connections)}",
            )

        self.db_connection.validate_metamodel_conformance()

        if not len(self._runtime_connections) == 1:
            raise GraphNotConformantToMetamodelError(
                self,
                f"Invalid number of referenced runtime connections: {len(self._runtime_connections)}",
            )

        self.runtime_connection.validate_metamodel_conformance()

        if not len(self._ts_clusters) <= 1:
            raise GraphNotConformantToMetamodelError(
                self,
                f"Invalid number of referenced timeseries clusters: {len(self._ts_clusters)}",
            )

        if self.ts_cluster is not None:
            self.ts_cluster.validate_metamodel_conformance()
