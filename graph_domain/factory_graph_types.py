from enum import Enum
from itertools import chain


class NodeTypes(Enum):
    # Main digital twin:
    ASSET = "ASSET"
    TIMESERIES_INPUT = "TIMESERIES"
    SUPPLEMENTARY_FILE = "SUPPLEMENTARY_FILE"
    DATABASE_CONNECTION = "DATABASE_CONNECTION"
    RUNTIME_CONNECTION = "RUNTIME_CONNECTION"
    UNIT = "UNIT"
    # Similarities:
    TIMESERIES_CLUSTER = "TIMESERIES_CLUSTER"
    EXTRACTED_KEYWORD = "EXTRACTED_KEYWORD"
    # Expert annotations:
    ANNOTATION_DEFINITION = "ANNOTATION_DEFINITION"
    ANNOTATION_INSTANCE = "ANNOTATION_INSTANCE"
    ANNOTATION_PRE_INDICATOR = "ANNOTATION_PRE_INDICATOR"
    ANNOTATION_TS_MATCHER = "ANNOTATION_TS_MATCHER"


class RelationshipTypes(Enum):
    # Main digital twin:
    HAS_TIMESERIES = "HAS_TIMESERIES"
    HAS_SUPPLEMENTARY_FILE = "HAS_SUPPLEMENTARY_FILE"
    TIMESERIES_DB_ACCESS = "TIMESERIES_DB_ACCESS"
    FILE_DB_ACCESS = "FILE_DB_ACCESS"
    SECONDARY_FORMAT = "SECONDARY_FORMAT"
    RUNTIME_ACCESS = "RUNTIME_ACCESS"
    HAS_UNIT = "HAS_UNIT"
    # Similarities:
    PART_OF_TS_CLUSTER = "PART_OF_TS_CLUSTER"
    ASSET_SIMILARITY = "ASSET_SIMILARITY"
    KEYWORD_EXTRACTION = "KEYWORD_EXTRACTION"
    # Expert annotations:
    INSTANCE_OF = "INSTANCE_OF"
    OCCURANCE_SCAN = "OCCURANCE_SCAN"
    PRE_INDICATABLE_WITH = "PRE_INDICATABLE_WITH"
    TS_MATCH = "TS_MATCH"
    ORIGINAL_ANNOTATED = "ORIGINAL_ANNOTATION"
    ANNOTATION = "ANNOTATION"
    DETECTABLE_WITH = "DETECTABLE_WITH"


class PseudoNodeTypes(Enum):
    ASSET_SIMILARITY_PSEUDO_NODE = "ASSET_SIMILARITY_PSEUDO_NODE"


NODE_TYPE_STRINGS = [nd_type.value for nd_type in NodeTypes] + [
    nd_type.value for nd_type in PseudoNodeTypes
]
RELATIONSHIP_TYPE_STRINGS = [rl_type.value for rl_type in RelationshipTypes]
ELEMENT_TYPE_STRINGS = list(chain(NODE_TYPE_STRINGS, RELATIONSHIP_TYPE_STRINGS))

UNSPECIFIED_LABEL = "UNSPECIFIED"

RELATIONSHIP_TYPES_FOR_NODE_TYPE = {
    NodeTypes.ASSET.value: [
        RelationshipTypes.HAS_TIMESERIES.value,
        RelationshipTypes.HAS_SUPPLEMENTARY_FILE.value,
        RelationshipTypes.OCCURANCE_SCAN.value,
        RelationshipTypes.ANNOTATION.value,
        RelationshipTypes.ASSET_SIMILARITY.value,
    ],
    NodeTypes.TIMESERIES_INPUT.value: [
        RelationshipTypes.HAS_TIMESERIES.value,
        RelationshipTypes.HAS_UNIT.value,
        RelationshipTypes.RUNTIME_ACCESS.value,
        RelationshipTypes.TIMESERIES_DB_ACCESS.value,
        RelationshipTypes.PART_OF_TS_CLUSTER.value,
        RelationshipTypes.ORIGINAL_ANNOTATED.value,
        RelationshipTypes.TS_MATCH.value,
    ],
    NodeTypes.SUPPLEMENTARY_FILE.value: [
        RelationshipTypes.HAS_SUPPLEMENTARY_FILE.value,
        RelationshipTypes.FILE_DB_ACCESS.value,
        RelationshipTypes.SECONDARY_FORMAT.value,
        RelationshipTypes.KEYWORD_EXTRACTION.value,
    ],
    NodeTypes.DATABASE_CONNECTION.value: [
        RelationshipTypes.TIMESERIES_DB_ACCESS.value,
        RelationshipTypes.FILE_DB_ACCESS.value,
    ],
    NodeTypes.UNIT.value: [RelationshipTypes.HAS_UNIT.value],
    NodeTypes.RUNTIME_CONNECTION.value: [RelationshipTypes.RUNTIME_ACCESS.value],
    NodeTypes.TIMESERIES_CLUSTER.value: [RelationshipTypes.PART_OF_TS_CLUSTER.value],
    NodeTypes.EXTRACTED_KEYWORD.value: [RelationshipTypes.KEYWORD_EXTRACTION.value],
    PseudoNodeTypes.ASSET_SIMILARITY_PSEUDO_NODE.value: [
        RelationshipTypes.ASSET_SIMILARITY.value
    ],
    NodeTypes.ANNOTATION_DEFINITION.value: [
        RelationshipTypes.INSTANCE_OF.value,
        RelationshipTypes.OCCURANCE_SCAN.value,
    ],
    NodeTypes.ANNOTATION_INSTANCE.value: [
        RelationshipTypes.INSTANCE_OF.value,
        RelationshipTypes.ANNOTATION.value,
        RelationshipTypes.PRE_INDICATABLE_WITH.value,
        RelationshipTypes.DETECTABLE_WITH.value,
    ],
    NodeTypes.ANNOTATION_PRE_INDICATOR.value: [
        RelationshipTypes.PRE_INDICATABLE_WITH.value,
        RelationshipTypes.DETECTABLE_WITH.value,
    ],
    NodeTypes.ANNOTATION_TS_MATCHER.value: [
        RelationshipTypes.ORIGINAL_ANNOTATED.value,
        RelationshipTypes.TS_MATCH.value,
    ],
}
