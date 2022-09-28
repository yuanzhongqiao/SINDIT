from typing import List, Tuple
from dash import html
from frontend.main_column.factory_graph.GraphSelectedElement import GraphSelectedElement
from graph_domain.BaseNode import BaseNode
from frontend import api_client
from frontend.right_sidebar.node_data_tab.timeseries_graph import (
    timeseries_graph_layout,
)
from frontend.right_sidebar.node_data_tab.file_visualization import (
    file_visualization_layout,
)
from graph_domain.expert_annotations.AnnotationDefinitionNode import (
    AnnotationDefinitionNodeFlat,
)
from graph_domain.expert_annotations.AnnotationDetectionNode import (
    AnnotationDetectionNodeFlat,
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
from graph_domain.factory_graph_ogm_matches import OGM_CLASS_FOR_NODE_TYPE
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

STRF_DATETIME_FORMAT = "%d.%m.%Y, %H:%M:%S"


def get_visualized_attributes_for_node_type(node: BaseNode) -> List[Tuple[str, str]]:
    attributes_list = []

    # Generic Attributes for all node types:
    attributes_list.append(("IRI", node.iri))
    attributes_list.append(
        (
            "Description",
            node.description
            if node.description is not None and node.description != ""
            else "No description available",
        )
    )
    # Additional Attributes by type:
    if isinstance(node, AssetNodeFlat):
        pass
    elif isinstance(node, TimeseriesNodeFlat):
        attributes_list.append(("Connection Topic", node.connection_topic))
        attributes_list.append(("Connection Keyword", node.connection_keyword))
        attributes_list.append(("Value Type", node.value_type))
        if node.feature_dict is not None:
            attributes_list.append(
                (
                    "Extracted Features",
                    ", ".join(
                        [
                            f"{feature_tuple[0]}: {feature_tuple[1]}"
                            for feature_tuple in node.feature_dict.items()
                        ]
                    ),
                )
            )
        if node.reduced_feature_list is not None:
            attributes_list.append(
                (
                    "PCA-reduced Features",
                    ", ".join([str(feature) for feature in node.reduced_feature_list]),
                )
            )
    elif isinstance(node, SupplementaryFileNodeFlat):
        attributes_list.append(("File Name", node.file_name))
        attributes_list.append(("File Type", node.file_type))
    elif isinstance(node, DatabaseConnectionNode):
        attributes_list.append(("Database Type", node.type))
        attributes_list.append(("Database Instance", node.database))
        attributes_list.append(("Database group", node.group))
    elif isinstance(node, RuntimeConnectionNode):
        attributes_list.append(("Connection Type", node.type))
    elif isinstance(node, UnitNode):
        pass
    elif isinstance(node, TimeseriesClusterNode):
        pass
    elif isinstance(node, ExtractedKeywordNode):
        attributes_list.append(("Keyphrase", node.keyword))
    elif isinstance(node, AnnotationDefinitionNodeFlat):
        attributes_list.append(("Solution Proposal", node.solution_proposal))
    elif isinstance(node, AnnotationInstanceNodeFlat):
        attributes_list.append(
            (
                "Annotation created at",
                node.creation_date_time.strftime(STRF_DATETIME_FORMAT),
            )
        )
        attributes_list.append(
            (
                "Start of the Situation",
                node.occurance_start_date_time.strftime(STRF_DATETIME_FORMAT),
            )
        )
        attributes_list.append(
            (
                "End of the Situation",
                node.occurance_end_date_time.strftime(STRF_DATETIME_FORMAT),
            )
        )
    elif isinstance(node, AnnotationPreIndicatorNodeFlat):
        attributes_list.append(
            (
                "Start of the Indication",
                node.indicator_start_date_time.strftime(STRF_DATETIME_FORMAT),
            )
        )
        attributes_list.append(
            (
                "End of the Indication",
                node.indicator_end_date_time.strftime(STRF_DATETIME_FORMAT),
            )
        )
    elif isinstance(node, AnnotationDetectionNodeFlat):
        attributes_list.append(
            (
                "Annotation confirmed at",
                node.confirmation_date_time.strftime(STRF_DATETIME_FORMAT)
                if node.confirmation_date_time is not None
                else "Not yet confirmed or declined.",
            )
        )
        attributes_list.append(
            (
                "Start of the Situation",
                node.occurance_start_date_time.strftime(STRF_DATETIME_FORMAT),
            )
        )
        attributes_list.append(
            (
                "End of the Situation",
                node.occurance_end_date_time.strftime(STRF_DATETIME_FORMAT),
            )
        )
    elif isinstance(node, AnnotationPreIndicatorNodeFlat):
        attributes_list.append(
            (
                "Start of the Indication",
                node.indicator_start_date_time.strftime(STRF_DATETIME_FORMAT),
            )
        )
        attributes_list.append(
            (
                "End of the Indication",
                node.indicator_end_date_time.strftime(STRF_DATETIME_FORMAT),
            )
        )
    elif isinstance(node, AnnotationTimeseriesMatcherNodeFlat):
        pass

    return attributes_list


def get_layout(selected_el: GraphSelectedElement):
    """
    Layout of the node-details tab: e.g. iri, description...
    :param selected_el:
    :return:
    """

    if selected_el is None or not selected_el.is_node:
        # No node selected
        return html.Div("No node selected!")
    else:
        node_details_json = api_client.get_json("/node_details", iri=selected_el.iri)
        node_class = OGM_CLASS_FOR_NODE_TYPE.get(selected_el.type)
        node: BaseNode = node_class.from_dict(node_details_json)

        return html.Div(
            children=[
                html.Div(
                    className="node-information-attribute-block",
                    children=[
                        html.Div(
                            className="node-information-attribute-header",
                            children=f"{attribute[0]}:",
                        ),
                        html.Div(
                            className="node-information-attribute-content",
                            children=attribute[1],
                        ),
                    ],
                )
                for attribute in get_visualized_attributes_for_node_type(node)
            ]
        )
