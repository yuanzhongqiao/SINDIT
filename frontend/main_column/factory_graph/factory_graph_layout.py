from random import randint
from typing import Dict, List

from dash import html, dcc
import dash_bootstrap_components as dbc
import dash_cytoscape as cyto

from frontend.app import app
from frontend import resources_manager
from graph_domain.BaseNode import BaseNode
from graph_domain.DatabaseConnectionNode import DatabaseConnectionNode
from graph_domain.AssetNode import AssetNodeDeep
from graph_domain.TimeseriesNode import TimeseriesNodeDeep
from graph_domain.UnitNode import UnitNode
from graph_domain.factory_graph_types import (
    UNSPECIFIED_LABEL,
    NodeTypes,
    RelationshipTypes,
)

CY_GRAPH_STYLE_STATIC = resources_manager.load_json("cytoscape-graph-style.json")


def get_layout():
    return html.Div(
        [
            # Storage for accessing the selected element
            dcc.Store(id="selected-graph-element-store", storage_type="session"),
            # Timestamp for the selected element storage
            dcc.Store(id="selected-graph-element-timestamp", storage_type="session"),
            dbc.Card(
                [
                    dbc.CardHeader(
                        id="graph-header-container",
                        children=[
                            dbc.Row(
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
                                                ]
                                            ),
                                            id="graph-reload-button",
                                            n_clicks=0,
                                            size="sm",
                                            outline=True,
                                        ),
                                        style={"height": "100%", "max-width": "155px"},
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
                                cyto.Cytoscape(
                                    id="cytoscape-graph",
                                    layout={"name": "preset"},
                                    style={"width": "100%", "height": "75vh"},
                                    stylesheet=CY_GRAPH_STYLE_STATIC,
                                    className="factory-graph",
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
                                            )
                                        ],
                                        style={"height": "100%"},
                                    ),
                                ],
                                style={"height": "40px"},
                            )
                        ],
                    ),
                ]
            ),
        ]
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


def get_cytoscape_elements(
    assets_deep: List[AssetNodeDeep], asset_similarities: List[Dict]
):
    cytoscape_elements = []
    cluster_nodes = {}

    for asset in assets_deep:
        # Assets (machines):
        cytoscape_elements.append(_create_cytoscape_node(asset, NodeTypes.ASSET.value))

        for timeseries in asset.timeseries:
            # Timeseries:
            cytoscape_elements.append(
                _create_cytoscape_node(timeseries, NodeTypes.TIMESERIES_INPUT.value)
            )
            cytoscape_elements.append(
                _create_cytoscape_relationship(
                    asset.iri, timeseries.iri, RelationshipTypes.HAS_TIMESERIES.value
                )
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
                if cluster_nodes.get(timeseries.ts_cluster.iri) is None:
                    cluster_node = _create_cytoscape_node(
                        timeseries.ts_cluster, NodeTypes.TIMESERIES_CLUSTER.value
                    )
                    cytoscape_elements.append(cluster_node)

                cytoscape_elements.append(
                    _create_cytoscape_relationship(
                        timeseries.iri,
                        timeseries.ts_cluster.iri,
                        RelationshipTypes.PART_OF_TS_CLUSTER.value,
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

    # Temporary dict to remove duplicates (e.g. if same timeseries is referenced from multiple assets)
    return list(
        {
            cyt_elem.get("data").get("id")
            if cyt_elem.get("data").get("id") is not None
            else (
                cyt_elem.get("data").get("source"),
                cyt_elem.get("data").get("target"),
            ): cyt_elem
            for cyt_elem in cytoscape_elements
        }.values()
    )
