from random import randint
from typing import Dict, List

from dash import html, dcc
import dash_bootstrap_components as dbc
import dash_cytoscape as cyto

from frontend.app import app
from frontend import resources_manager
from graph_domain.BaseNode import BaseNode
from graph_domain.expert_annotations.AnnotationInstanceNode import (
    AnnotationInstanceNodeDeep,
)
from graph_domain.expert_annotations.AnnotationTimeseriesMatcherNode import (
    AnnotationTimeseriesMatcherNodeDeep,
)
from graph_domain.main_digital_twin.DatabaseConnectionNode import DatabaseConnectionNode
from graph_domain.main_digital_twin.AssetNode import AssetNodeDeep
from graph_domain.main_digital_twin.TimeseriesNode import TimeseriesNodeDeep
from graph_domain.main_digital_twin.UnitNode import UnitNode
from graph_domain.factory_graph_types import (
    UNSPECIFIED_LABEL,
    NodeTypes,
    RelationshipTypes,
)

CY_GRAPH_STYLE_STATIC = resources_manager.load_json("cytoscape-graph-style.json")


def get_layout():
    return html.Div(
        id="factory-graph-container",
        children=[
            # Storage for accessing the selected element
            dcc.Store(id="selected-graph-element-store", storage_type="session"),
            # Timestamp for the selected element storage
            dcc.Store(id="selected-graph-element-timestamp", storage_type="session"),
            dbc.Card(
                id="factory-graph-card",
                children=[
                    dbc.CardHeader(
                        id="graph-header-container",
                        children=[
                            dbc.Row(
                                id="graph-header-row",
                                children=[
                                    dbc.Col(
                                        html.Div("Factory graph"),
                                        align="center",
                                    ),
                                    dbc.Col(
                                        dbc.Button(
                                            html.Div(
                                                [
                                                    "Reload graph",
                                                    html.Img(
                                                        src="https://fonts.gstatic.com/s/i/short-term/release/materialsymbolsrounded/refresh/wght500/48px.svg",
                                                        height=20,
                                                        width=20,
                                                        style={
                                                            # Color applied to svg as filter. Converter: (https://isotropic.co/tool/hex-color-to-css-filter/)
                                                            "filter": "invert(40%) sepia(60%) saturate(0%) hue-rotate(175deg) brightness(103%) contrast(89%)",
                                                            "margin-left": "5px",
                                                        },
                                                    ),
                                                ],
                                                id="reload-button-div",
                                            ),
                                            id="graph-reload-button",
                                            n_clicks=0,
                                            size="sm",
                                            outline=True,
                                        ),
                                        style={"max-width": "155px"},
                                        align="center",
                                    ),
                                ],
                                style={"height": "30px"},
                                align="stretch",
                                justify="between",
                            )
                        ],
                    ),
                    dbc.CardBody(
                        html.Div(
                            id="kg-container",
                            children=[
                                dcc.Loading(
                                    className="kg-loading-indicator-container",
                                    type="dot",
                                    color="#446e9b",
                                    children=[
                                        cyto.Cytoscape(
                                            id="cytoscape-graph",
                                            layout={"name": "preset"},
                                            style={"width": "100%", "height": "100%"},
                                            minZoom=0.4,
                                            maxZoom=5,
                                            zoom=2,
                                            responsive=False,
                                            stylesheet=CY_GRAPH_STYLE_STATIC,
                                            className="factory-graph",
                                        ),
                                    ],
                                )
                            ],
                        )
                    ),
                    dbc.CardFooter(
                        id="graph-positioning-container",
                        style={"display": "None"},
                        children=[
                            dbc.Row(
                                children=[
                                    dbc.Col(
                                        dbc.Button(
                                            "Save node position",
                                            id="graph-positioning-save-button",
                                            n_clicks=0,
                                            color="primary",
                                            size="sm",
                                        ),
                                        style={"height": "100%"},
                                    ),
                                    dbc.Col(
                                        children=[
                                            dbc.Alert(
                                                id="graph-positioning-saved-notifier",
                                                class_name="inline-alert",
                                                is_open=False,
                                                duration=5000,
                                                style={"padding-top": "8px"},
                                            )
                                        ],
                                        style={"height": "100%"},
                                        id="graph-positioning-alert-row",
                                    ),
                                ],
                                style={"height": "40px"},
                            )
                        ],
                    ),
                ],
            ),
        ],
    )


def _create_cytoscape_node(node: BaseNode, node_type: str = UNSPECIFIED_LABEL):
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


def _get_ts_with_sub_elements(timeseries: TimeseriesNodeDeep) -> List:
    cytoscape_elements = []
    # Timeseries:
    cytoscape_elements.append(
        _create_cytoscape_node(timeseries, NodeTypes.TIMESERIES_INPUT.value)
    )

    # Database connection:
    cytoscape_elements.append(
        _create_cytoscape_node(
            timeseries.db_connection, NodeTypes.DATABASE_CONNECTION.value
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
            timeseries.runtime_connection, NodeTypes.RUNTIME_CONNECTION.value
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
            _create_cytoscape_node(timeseries.unit, NodeTypes.UNIT.value)
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
                timeseries.ts_cluster, NodeTypes.TIMESERIES_CLUSTER.value
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
) -> List:
    cytoscape_elements = []
    cytoscape_elements.append(
        _create_cytoscape_node(ts_matcher, NodeTypes.ANNOTATION_TS_MATCHER.value)
    )

    # Original TS:
    cytoscape_elements.extend(_get_ts_with_sub_elements(ts_matcher.original_ts))

    cytoscape_elements.append(
        _create_cytoscape_relationship(
            ts_matcher.iri,
            ts_matcher.original_ts.iri,
            RelationshipTypes.ORIGINAL_ANNOTATED.value,
        )
    )

    # Matched TS:
    for ts in ts_matcher.ts_matches:
        cytoscape_elements.extend(_get_ts_with_sub_elements(ts))

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
) -> List:
    cytoscape_elements = []
    cytoscape_elements.append(
        _create_cytoscape_node(annotation_instance, NodeTypes.ANNOTATION_INSTANCE.value)
    )

    # Pre-indicators
    for pre_ind in annotation_instance.pre_indicators:
        cytoscape_elements.append(
            _create_cytoscape_node(pre_ind, NodeTypes.ANNOTATION_PRE_INDICATOR.value)
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
            cytoscape_elements.extend(_get_ts_matchers_with_sub_elements(ts_matcher))
            cytoscape_elements.append(
                _create_cytoscape_relationship(
                    pre_ind.iri,
                    ts_matcher.iri,
                    RelationshipTypes.DETECTABLE_WITH.value,
                )
            )

    # Timeseries matchers (annotation)
    for ts_matcher in annotation_instance.ts_matchers:
        cytoscape_elements.extend(_get_ts_matchers_with_sub_elements(ts_matcher))

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
        cytoscape_elements.append(_create_cytoscape_node(asset, NodeTypes.ASSET.value))

        for timeseries in asset.timeseries:
            # Timeseries:
            cytoscape_elements.extend(_get_ts_with_sub_elements(timeseries))

            cytoscape_elements.append(
                _create_cytoscape_relationship(
                    asset.iri, timeseries.iri, RelationshipTypes.HAS_TIMESERIES.value
                )
            )

        for suppl_file in asset.supplementary_files:
            # Supplementary file:
            cytoscape_elements.append(
                _create_cytoscape_node(suppl_file, NodeTypes.SUPPLEMENTARY_FILE.value)
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
                    suppl_file.db_connection, NodeTypes.DATABASE_CONNECTION.value
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
                    _create_cytoscape_node(keyword, NodeTypes.EXTRACTED_KEYWORD.value)
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
                    secondary_suppl_file, NodeTypes.SUPPLEMENTARY_FILE.value
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
            cytoscape_elements.extend(_get_annotation_with_sub_elements(annotation))
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
                    annotation, NodeTypes.ANNOTATION_DEFINITION.value
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
                cytoscape_elements.extend(_get_annotation_with_sub_elements(instance))
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

    # Temporary dict to remove duplicates (e.g. if same timeseries is referenced from multiple assets)
    return list(
        {
            cyt_elem.get("data").get("id")
            if cyt_elem.get("data").get("id") is not None
            else (
                cyt_elem.get("data").get("source"),
                cyt_elem.get("data").get("target"),
                cyt_elem.get("classes")[0],
            ): cyt_elem
            for cyt_elem in cytoscape_elements
        }.values()
    )
