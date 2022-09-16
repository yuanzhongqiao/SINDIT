from random import randint
from typing import Dict, List

from graph_domain.BaseNode import BaseNode
from graph_domain.expert_annotations.AnnotationInstanceNode import (
    AnnotationInstanceNodeDeep,
)
from graph_domain.expert_annotations.AnnotationTimeseriesMatcherNode import (
    AnnotationTimeseriesMatcherNodeDeep,
)
from graph_domain.main_digital_twin.AssetNode import AssetNodeDeep, AssetNodeFlat
from graph_domain.main_digital_twin.TimeseriesNode import TimeseriesNodeDeep
from graph_domain.factory_graph_types import (
    UNSPECIFIED_LABEL,
    NodeTypes,
    RelationshipTypes,
)


def _create_cytoscape_node(
    node: BaseNode,
    node_type: str = UNSPECIFIED_LABEL,
    associated_asset: AssetNodeFlat | None = None,
):
    # Restore node positioning where available:
    pos_x = (
        node.visualization_positioning_x
        if node.visualization_positioning_x is not None
        else randint(-300, 300)
    )
    pos_y = (
        node.visualization_positioning_y
        if node.visualization_positioning_y is not None
        else randint(-300, 300)
    )

    return {
        "data": {
            "id": node.iri,
            "label": node.caption,
            "type": node_type,
            "iri": node.iri,
            "id_short": node.id_short,
            "description": node.description,
            "persisted_pos": {
                "x": node.visualization_positioning_x,
                "y": node.visualization_positioning_y,
            },
            "associated_assets": associated_asset.iri
            if associated_asset is not None
            else None,
        },
        "classes": [node_type],
        "position": {"x": pos_x, "y": pos_y},
    }


def _create_cytoscape_relationship(
    iri_from: str, iri_to: str, edge_type: str = UNSPECIFIED_LABEL, label: str = ""
):
    return {
        "data": {"source": iri_from, "target": iri_to, "label": label},
        "classes": [edge_type],
    }


def _get_ts_with_sub_elements(
    timeseries: TimeseriesNodeDeep, associated_asset: AssetNodeFlat | None = None
) -> List:
    cytoscape_elements = []

    # Timeseries:
    cytoscape_elements.append(
        _create_cytoscape_node(
            timeseries, NodeTypes.TIMESERIES_INPUT.value, associated_asset
        )
    )

    # Database connection:
    cytoscape_elements.append(
        _create_cytoscape_node(
            timeseries.db_connection,
            NodeTypes.DATABASE_CONNECTION.value,
            associated_asset,
        )
    )
    cytoscape_elements.append(
        _create_cytoscape_relationship(
            timeseries.iri,
            timeseries.db_connection.iri,
            RelationshipTypes.TIMESERIES_DB_ACCESS.value,
        )
    )

    # Runtime connection:
    cytoscape_elements.append(
        _create_cytoscape_node(
            timeseries.runtime_connection,
            NodeTypes.RUNTIME_CONNECTION.value,
            associated_asset,
        )
    )
    cytoscape_elements.append(
        _create_cytoscape_relationship(
            timeseries.iri,
            timeseries.runtime_connection.iri,
            RelationshipTypes.RUNTIME_ACCESS.value,
        )
    )

    # Unit:
    if timeseries.unit is not None:
        cytoscape_elements.append(
            _create_cytoscape_node(
                timeseries.unit, NodeTypes.UNIT.value, associated_asset
            )
        )
        cytoscape_elements.append(
            _create_cytoscape_relationship(
                timeseries.iri,
                timeseries.unit.iri,
                RelationshipTypes.HAS_UNIT.value,
            )
        )

    # Cluster:
    if timeseries.ts_cluster is not None:

        cytoscape_elements.append(
            _create_cytoscape_node(
                timeseries.ts_cluster,
                NodeTypes.TIMESERIES_CLUSTER.value,
                associated_asset,
            )
        )

        cytoscape_elements.append(
            _create_cytoscape_relationship(
                timeseries.iri,
                timeseries.ts_cluster.iri,
                RelationshipTypes.PART_OF_TS_CLUSTER.value,
            )
        )
    return cytoscape_elements


def _get_ts_matchers_with_sub_elements(
    ts_matcher: AnnotationTimeseriesMatcherNodeDeep,
    associated_asset: AssetNodeFlat | None = None,
) -> List:
    cytoscape_elements = []
    cytoscape_elements.append(
        _create_cytoscape_node(
            ts_matcher, NodeTypes.ANNOTATION_TS_MATCHER.value, associated_asset
        )
    )

    # Original TS:
    cytoscape_elements.extend(_get_ts_with_sub_elements(ts_matcher.original_ts, None))

    cytoscape_elements.append(
        _create_cytoscape_relationship(
            ts_matcher.iri,
            ts_matcher.original_ts.iri,
            RelationshipTypes.ORIGINAL_ANNOTATED.value,
        )
    )

    # Matched TS:
    for ts in ts_matcher.ts_matches:
        cytoscape_elements.extend(_get_ts_with_sub_elements(ts, None))

        cytoscape_elements.append(
            _create_cytoscape_relationship(
                ts_matcher.iri,
                ts.iri,
                RelationshipTypes.TS_MATCH.value,
            )
        )

    return cytoscape_elements


def _get_annotation_with_sub_elements(
    annotation_instance: AnnotationInstanceNodeDeep,
    associated_asset: AssetNodeFlat | None = None,
) -> List:
    cytoscape_elements = []
    cytoscape_elements.append(
        _create_cytoscape_node(
            annotation_instance, NodeTypes.ANNOTATION_INSTANCE.value, associated_asset
        )
    )

    # Pre-indicators
    for pre_ind in annotation_instance.pre_indicators:
        cytoscape_elements.append(
            _create_cytoscape_node(
                pre_ind, NodeTypes.ANNOTATION_PRE_INDICATOR.value, associated_asset
            )
        )
        cytoscape_elements.append(
            _create_cytoscape_relationship(
                annotation_instance.iri,
                pre_ind.iri,
                RelationshipTypes.PRE_INDICATABLE_WITH.value,
            )
        )

        # Timeseries matchers (pre-ind)
        for ts_matcher in pre_ind.ts_matchers:
            cytoscape_elements.extend(
                _get_ts_matchers_with_sub_elements(ts_matcher, associated_asset)
            )
            cytoscape_elements.append(
                _create_cytoscape_relationship(
                    pre_ind.iri,
                    ts_matcher.iri,
                    RelationshipTypes.DETECTABLE_WITH.value,
                )
            )

    # Timeseries matchers (annotation)
    for ts_matcher in annotation_instance.ts_matchers:
        cytoscape_elements.extend(
            _get_ts_matchers_with_sub_elements(ts_matcher, associated_asset)
        )

        cytoscape_elements.append(
            _create_cytoscape_relationship(
                annotation_instance.iri,
                ts_matcher.iri,
                RelationshipTypes.DETECTABLE_WITH.value,
            )
        )

    return cytoscape_elements


def get_cytoscape_elements(
    assets_deep: List[AssetNodeDeep], asset_similarities: List[Dict]
):
    cytoscape_elements = []

    for asset in assets_deep:
        # Assets (machines):
        cytoscape_elements.append(
            _create_cytoscape_node(asset, NodeTypes.ASSET.value, asset)
        )

        for timeseries in asset.timeseries:
            # Timeseries:
            cytoscape_elements.extend(_get_ts_with_sub_elements(timeseries, asset))

            cytoscape_elements.append(
                _create_cytoscape_relationship(
                    asset.iri, timeseries.iri, RelationshipTypes.HAS_TIMESERIES.value
                )
            )

        for suppl_file in asset.supplementary_files:
            # Supplementary file:
            cytoscape_elements.append(
                _create_cytoscape_node(
                    suppl_file, NodeTypes.SUPPLEMENTARY_FILE.value, asset
                )
            )
            cytoscape_elements.append(
                _create_cytoscape_relationship(
                    asset.iri,
                    suppl_file.iri,
                    RelationshipTypes.HAS_SUPPLEMENTARY_FILE.value,
                )
            )

            # Database connection:
            cytoscape_elements.append(
                _create_cytoscape_node(
                    suppl_file.db_connection, NodeTypes.DATABASE_CONNECTION.value, asset
                )
            )
            cytoscape_elements.append(
                _create_cytoscape_relationship(
                    suppl_file.iri,
                    suppl_file.db_connection.iri,
                    RelationshipTypes.FILE_DB_ACCESS.value,
                )
            )

            # Extracted keywords:
            for keyword in suppl_file.extracted_keywords:
                cytoscape_elements.append(
                    _create_cytoscape_node(
                        keyword, NodeTypes.EXTRACTED_KEYWORD.value, asset
                    )
                )
                cytoscape_elements.append(
                    _create_cytoscape_relationship(
                        suppl_file.iri,
                        keyword.iri,
                        RelationshipTypes.KEYWORD_EXTRACTION.value,
                    )
                )

            # Alternative formats (always connected to one main type)
            for secondary_suppl_file in suppl_file.secondary_formats:
                # Supplementary file (alternative format):
                secondary_file_node = _create_cytoscape_node(
                    secondary_suppl_file, NodeTypes.SUPPLEMENTARY_FILE.value, asset
                )

                secondary_file_node["classes"].append("")

                cytoscape_elements.append(secondary_file_node)
                cytoscape_elements.append(
                    _create_cytoscape_relationship(
                        suppl_file.iri,
                        secondary_suppl_file.iri,
                        RelationshipTypes.SECONDARY_FORMAT.value,
                    )
                )

                # Database connection:
                cytoscape_elements.append(
                    _create_cytoscape_node(
                        secondary_suppl_file.db_connection,
                        NodeTypes.DATABASE_CONNECTION.value,
                        asset,
                    )
                )
                cytoscape_elements.append(
                    _create_cytoscape_relationship(
                        secondary_suppl_file.iri,
                        secondary_suppl_file.db_connection.iri,
                        RelationshipTypes.FILE_DB_ACCESS.value,
                    )
                )

        # Own Annotations:
        for annotation in asset.annotations:
            cytoscape_elements.extend(
                _get_annotation_with_sub_elements(annotation, asset)
            )
            cytoscape_elements.append(
                _create_cytoscape_relationship(
                    asset.iri,
                    annotation.iri,
                    RelationshipTypes.ANNOTATION.value,
                )
            )

        # Scanned anotations (not nescessarly own):
        for annotation in asset.scanned_annotations:
            cytoscape_elements.append(
                _create_cytoscape_node(
                    annotation, NodeTypes.ANNOTATION_DEFINITION.value, asset
                )
            )
            cytoscape_elements.append(
                _create_cytoscape_relationship(
                    asset.iri,
                    annotation.iri,
                    RelationshipTypes.OCCURANCE_SCAN.value,
                )
            )
            # Instances:
            for instance in annotation.instances:
                cytoscape_elements.extend(
                    _get_annotation_with_sub_elements(instance, asset)
                )
                cytoscape_elements.append(
                    _create_cytoscape_relationship(
                        annotation.iri,
                        instance.iri,
                        RelationshipTypes.INSTANCE_OF.value,
                    )
                )

    # asset similarity relationships:
    for similarity in asset_similarities:
        cytoscape_elements.append(
            _create_cytoscape_relationship(
                iri_from=similarity.get("asset1"),
                iri_to=similarity.get("asset2"),
                edge_type=RelationshipTypes.ASSET_SIMILARITY.value,
                label=f"similarity:\n\n{similarity.get('similarity_score')}",
            )
        )

    # TODO: maybe change the thickness of the relationship-representations according to the rank of similarity

    # Remove duplicates and join filter attibute(s) of copies (e.g. related asset iris):
    temporary_elements_dict = {
        cyt_elem.get("data").get("id")
        if cyt_elem.get("data").get("id") is not None
        else (
            cyt_elem.get("data").get("source"),
            cyt_elem.get("data").get("target"),
            cyt_elem.get("classes")[0],
        ): cyt_elem
        for cyt_elem in cytoscape_elements
    }

    for elem in cytoscape_elements:
        # Only nodes, not relationships:
        if elem.get("data").get("id") is not None:
            dict_elem = temporary_elements_dict.get(elem.get("data").get("id"))
            related_asset_iris = dict_elem.get("data").get("associated_assets")
            new_related_asset_iri = elem.get("data").get("associated_assets")
            if new_related_asset_iri is not None and (
                related_asset_iris is None
                or new_related_asset_iri not in related_asset_iris
            ):

                dict_elem["data"]["associated_assets"] = (
                    (related_asset_iris + " " + new_related_asset_iri)
                    if related_asset_iris is not None
                    else new_related_asset_iri
                )

    return list(temporary_elements_dict.values())
