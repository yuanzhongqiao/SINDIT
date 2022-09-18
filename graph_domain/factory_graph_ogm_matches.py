from enum import Enum
from itertools import chain
from graph_domain.expert_annotations.AnnotationDefinitionNode import (
    AnnotationDefinitionNodeFlat,
)
from graph_domain.expert_annotations.AnnotationInstanceNode import (
    AnnotationInstanceNodeFlat,
)
from graph_domain.expert_annotations.AnnotationPreIndicatorNode import (
    AnnotationPreIndicatorNodeFlat,
)
from graph_domain.expert_annotations.AnnotationTimeseriesMatcherNode import (
    AnnotationTimeseriesMatcherNodeFlat,
)
from graph_domain.factory_graph_types import NodeTypes
from graph_domain.main_digital_twin.AssetNode import AssetNodeFlat
from graph_domain.main_digital_twin.DatabaseConnectionNode import DatabaseConnectionNode
from graph_domain.main_digital_twin.RuntimeConnectionNode import RuntimeConnectionNode
from graph_domain.main_digital_twin.SupplementaryFileNode import (
    SupplementaryFileNodeFlat,
)

from graph_domain.main_digital_twin.TimeseriesNode import TimeseriesNodeFlat
from graph_domain.main_digital_twin.UnitNode import UnitNode
from graph_domain.similarities.ExtractedKeywordNode import ExtractedKeywordNode
from graph_domain.similarities.TimeseriesClusterNode import TimeseriesClusterNode


OGM_CLASS_FOR_NODE_TYPE = {
    NodeTypes.ASSET.value: AssetNodeFlat,
    NodeTypes.TIMESERIES_INPUT.value: TimeseriesNodeFlat,
    NodeTypes.SUPPLEMENTARY_FILE.value: SupplementaryFileNodeFlat,
    NodeTypes.DATABASE_CONNECTION.value: DatabaseConnectionNode,
    NodeTypes.RUNTIME_CONNECTION.value: RuntimeConnectionNode,
    NodeTypes.UNIT.value: UnitNode,
    NodeTypes.TIMESERIES_CLUSTER.value: TimeseriesClusterNode,
    NodeTypes.EXTRACTED_KEYWORD.value: ExtractedKeywordNode,
    NodeTypes.ANNOTATION_DEFINITION.value: AnnotationDefinitionNodeFlat,
    NodeTypes.ANNOTATION_INSTANCE.value: AnnotationInstanceNodeFlat,
    NodeTypes.ANNOTATION_PRE_INDICATOR.value: AnnotationPreIndicatorNodeFlat,
    NodeTypes.ANNOTATION_TS_MATCHER.value: AnnotationTimeseriesMatcherNodeFlat,
}
