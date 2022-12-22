from datetime import datetime
import json
from pathlib import Path
import re
import random  # Used for easier handling of auxiliary file's local path

import pyecma376_2  # The base library for Open Packaging Specifications. We will use the OPCCoreProperties class.
from basyx.aas import model
from basyx.aas.adapter import aasx
from graph_domain import BaseNode
from graph_domain.main_digital_twin import UnitNode
from graph_domain.main_digital_twin.RuntimeConnectionNode import RuntimeConnectionTypes
from graph_domain.main_digital_twin.SupplementaryFileNode import SupplementaryFileTypes
from graph_domain.main_digital_twin.TimeseriesNode import TimeseriesValueTypes
from graph_domain.similarities.TimeseriesClusterNode import TimeseriesClusterNode
from util.environment_and_configuration import (
    ConfigGroups,
    get_configuration,
)
from backend.specialized_databases.files.FilesPersistenceService import (
    FilesPersistenceService,
)
from backend.specialized_databases.DatabasePersistenceServiceContainer import (
    DatabasePersistenceServiceContainer,
)
from util.log import logger
from backend.knowledge_graph.dao.DatabaseConnectionsDao import DatabaseConnectionsDao
from dateutil import tz

from typing import Dict, List
from graph_domain.main_digital_twin.AssetNode import AssetNodeDeep

DB_CON_NODE_DAO: DatabaseConnectionsDao = DatabaseConnectionsDao.instance()

DATETIME_STRF_FORMAT = "%Y_%m_%d_%H_%M_%S_%f"

BASE_IRI_PATH = "www.sintef.no/aas_identifiers/"
SUBMODEL_BASE_IRI_PATH = BASE_IRI_PATH + "submodels/"
CONCEPT_DESCRIPTION_IRI_PATH = BASE_IRI_PATH + "concepts/"


def _get_unique_suffix() -> str:
    date_time_str = (
        datetime.now()
        .astimezone(
            tz.gettz(get_configuration(group=ConfigGroups.FRONTEND, key="timezone"))
        )
        .strftime(DATETIME_STRF_FORMAT)
    )
    return date_time_str + "_" + str(random.randrange(0, 99999, 1))


def _load_or_create_concept_descr_reference(
    node: BaseNode,
    concepts_dict: Dict[str, model.Identifiable],
    object_store: model.DictObjectStore,
    all_identifiers_list: List[model.Identifier],
):
    if node is None:
        return None
    if node.iri not in concepts_dict.keys():
        concept = model.concept.ConceptDescription(
            identification=model.Identifier(
                node.iri,
                model.IdentifierType.IRI,
            ),
            id_short=node.id_short,
            description=dict(en=node.description),
        )
        object_store.add(concept)
        all_identifiers_list.append(concept.identification)
        concepts_dict[node.iri] = model.AASReference.from_referable(concept)

    return concepts_dict.get(node.iri)


def serialize_to_aasx(
    aasx_file_path: str,
    assets: List[AssetNodeDeep],
    asset_similarities: Dict[str, float],
):

    # Prepare AAS objects
    aas_list: List[model.AssetAdministrationShell] = []
    object_store = model.DictObjectStore([])
    file_store = aasx.DictSupplementaryFileContainer()
    all_identifiers_list: List[model.Identifier] = []

    dynamic_concepts_dict: Dict[str, model.Identifiable] = dict()

    ###############################
    # Concept descriptions
    iri_concept = model.concept.ConceptDescription(
        identification=model.Identifier(
            CONCEPT_DESCRIPTION_IRI_PATH + "iri", model.IdentifierType.IRI
        ),
        id_short="IRI",
        description=dict(en="Internationalized Resource Identifier"),
    )
    object_store.add(iri_concept)
    all_identifiers_list.append(iri_concept.identification)

    id_short_concept = model.concept.ConceptDescription(
        identification=model.Identifier(
            CONCEPT_DESCRIPTION_IRI_PATH + "id_short", model.IdentifierType.IRI
        ),
        id_short="ID_SHORT",
        description=dict(en="Short identifier"),
    )
    object_store.add(id_short_concept)
    all_identifiers_list.append(id_short_concept.identification)

    caption_concept = model.concept.ConceptDescription(
        identification=model.Identifier(
            CONCEPT_DESCRIPTION_IRI_PATH + "caption", model.IdentifierType.IRI
        ),
        id_short="CAPTION",
        description=dict(en="Internationalized Resource Identifier"),
    )
    object_store.add(caption_concept)
    all_identifiers_list.append(caption_concept.identification)

    database_instance_concept = model.concept.ConceptDescription(
        identification=model.Identifier(
            CONCEPT_DESCRIPTION_IRI_PATH + "database_instance", model.IdentifierType.IRI
        ),
        id_short="DATABASE_INSTANCE",
    )
    object_store.add(database_instance_concept)
    all_identifiers_list.append(database_instance_concept.identification)

    database_group_concept = model.concept.ConceptDescription(
        identification=model.Identifier(
            CONCEPT_DESCRIPTION_IRI_PATH + "database_group", model.IdentifierType.IRI
        ),
        id_short="DATABASE_GROUP",
    )
    object_store.add(database_group_concept)
    all_identifiers_list.append(database_group_concept.identification)

    env_concept = model.concept.ConceptDescription(
        identification=model.Identifier(
            CONCEPT_DESCRIPTION_IRI_PATH + "environment_variable",
            model.IdentifierType.IRI,
        ),
        id_short="ENVIRONMENT_VARIABLE",
    )
    object_store.add(env_concept)
    all_identifiers_list.append(env_concept.identification)

    key_phrases_concept = model.concept.ConceptDescription(
        identification=model.Identifier(
            CONCEPT_DESCRIPTION_IRI_PATH + "key_phrases", model.IdentifierType.IRI
        ),
        id_short="KEY_PHRASES",
        description=dict(en="Collection of extracted key-phrases, separated by comma."),
    )
    object_store.add(key_phrases_concept)
    all_identifiers_list.append(key_phrases_concept.identification)

    feature_concept = model.concept.ConceptDescription(
        identification=model.Identifier(
            CONCEPT_DESCRIPTION_IRI_PATH + "extracted_feature", model.IdentifierType.IRI
        ),
        id_short="EXTRACTED_FEATURE",
        description=dict(en="A feature extracted by some algorithms."),
    )
    object_store.add(feature_concept)
    all_identifiers_list.append(feature_concept.identification)

    reduced_features_concept = model.concept.ConceptDescription(
        identification=model.Identifier(
            CONCEPT_DESCRIPTION_IRI_PATH + "reduced_feature_list",
            model.IdentifierType.IRI,
        ),
        id_short="REDUCED_FEATURE_LIST",
        description=dict(
            en="List of features, separated by comma. Computed with dimensionality reduction techniques."
        ),
    )
    object_store.add(reduced_features_concept)
    all_identifiers_list.append(reduced_features_concept.identification)

    similarities_concept = model.concept.ConceptDescription(
        identification=model.Identifier(
            CONCEPT_DESCRIPTION_IRI_PATH + "asset_similarities",
            model.IdentifierType.IRI,
        ),
        id_short="ASSET_SIMILARITIES",
        description=dict(
            en="List of similarity relationships between assets in JSON format."
        ),
    )
    object_store.add(similarities_concept)
    all_identifiers_list.append(similarities_concept.identification)

    node_positions_concept = model.concept.ConceptDescription(
        identification=model.Identifier(
            CONCEPT_DESCRIPTION_IRI_PATH + "sindit_node_positions",
            model.IdentifierType.IRI,
        ),
        id_short="SINDIT_NODE_POSITIONS",
        description=dict(
            en="Dict containing positions the different nodes can be represented with. Encoded in the JSON format."
        ),
    )
    object_store.add(node_positions_concept)
    all_identifiers_list.append(node_positions_concept.identification)

    # File types:

    jpg_concept = model.concept.ConceptDescription(
        identification=model.Identifier(
            CONCEPT_DESCRIPTION_IRI_PATH + "image_jpg", model.IdentifierType.IRI
        ),
        id_short="IMAGE_JPG",
    )
    object_store.add(jpg_concept)
    all_identifiers_list.append(jpg_concept.identification)

    pdf_concept = model.concept.ConceptDescription(
        identification=model.Identifier(
            CONCEPT_DESCRIPTION_IRI_PATH + "document_pdf", model.IdentifierType.IRI
        ),
        id_short="DOCUMENT_PDF",
    )
    object_store.add(pdf_concept)
    all_identifiers_list.append(pdf_concept.identification)

    step_concept = model.concept.ConceptDescription(
        identification=model.Identifier(
            CONCEPT_DESCRIPTION_IRI_PATH + "cad_step", model.IdentifierType.IRI
        ),
        id_short="CAD_STEP",
    )
    object_store.add(step_concept)
    all_identifiers_list.append(step_concept.identification)

    stl_concept = model.concept.ConceptDescription(
        identification=model.Identifier(
            CONCEPT_DESCRIPTION_IRI_PATH + "cad_stl", model.IdentifierType.IRI
        ),
        id_short="CAD_STL",
    )
    object_store.add(stl_concept)
    all_identifiers_list.append(stl_concept.identification)

    # Database types:
    s3_connection_concept = model.concept.ConceptDescription(
        identification=model.Identifier(
            CONCEPT_DESCRIPTION_IRI_PATH + "database_s3", model.IdentifierType.IRI
        ),
        id_short="S3",
    )
    object_store.add(s3_connection_concept)
    all_identifiers_list.append(s3_connection_concept.identification)

    influx_connection_concept = model.concept.ConceptDescription(
        identification=model.Identifier(
            CONCEPT_DESCRIPTION_IRI_PATH + "database_influx_db",
            model.IdentifierType.IRI,
        ),
        id_short="INFLUX_DB",
    )
    object_store.add(influx_connection_concept)
    all_identifiers_list.append(influx_connection_concept.identification)

    # Runtime connection types:
    mqtt_connection_concept = model.concept.ConceptDescription(
        identification=model.Identifier(
            CONCEPT_DESCRIPTION_IRI_PATH + "runtime_connection_mqtt",
            model.IdentifierType.IRI,
        ),
        id_short="MQTT",
    )
    object_store.add(mqtt_connection_concept)
    all_identifiers_list.append(mqtt_connection_concept.identification)

    opc_ua_connection_concept = model.concept.ConceptDescription(
        identification=model.Identifier(
            CONCEPT_DESCRIPTION_IRI_PATH + "runtime_connection_opc_ua",
            model.IdentifierType.IRI,
        ),
        id_short="OPC_UA",
    )
    object_store.add(opc_ua_connection_concept)
    all_identifiers_list.append(opc_ua_connection_concept.identification)

    con_topic_connection_concept = model.concept.ConceptDescription(
        identification=model.Identifier(
            CONCEPT_DESCRIPTION_IRI_PATH + "runtime_connection_topic",
            model.IdentifierType.IRI,
        ),
        id_short="CONNECTION_TOPIC",
    )
    object_store.add(con_topic_connection_concept)
    all_identifiers_list.append(con_topic_connection_concept.identification)

    con_keyword_connection_concept = model.concept.ConceptDescription(
        identification=model.Identifier(
            CONCEPT_DESCRIPTION_IRI_PATH + "runtime_connection_keyword",
            model.IdentifierType.IRI,
        ),
        id_short="CONNECTION_KEYWORD",
    )
    object_store.add(con_keyword_connection_concept)
    all_identifiers_list.append(con_keyword_connection_concept.identification)

    # Datatypes
    integer_concept = model.concept.ConceptDescription(
        identification=model.Identifier(
            CONCEPT_DESCRIPTION_IRI_PATH + "integer",
            model.IdentifierType.IRI,
        ),
        id_short="INTEGER",
    )
    object_store.add(integer_concept)
    all_identifiers_list.append(integer_concept.identification)

    bool_concept = model.concept.ConceptDescription(
        identification=model.Identifier(
            CONCEPT_DESCRIPTION_IRI_PATH + "boolean",
            model.IdentifierType.IRI,
        ),
        id_short="BOOLEAN",
    )
    object_store.add(bool_concept)
    all_identifiers_list.append(bool_concept.identification)

    decimal_concept = model.concept.ConceptDescription(
        identification=model.Identifier(
            CONCEPT_DESCRIPTION_IRI_PATH + "decimal",
            model.IdentifierType.IRI,
        ),
        id_short="DECIMAL",
    )
    object_store.add(decimal_concept)
    all_identifiers_list.append(decimal_concept.identification)

    string_concept = model.concept.ConceptDescription(
        identification=model.Identifier(
            CONCEPT_DESCRIPTION_IRI_PATH + "string",
            model.IdentifierType.IRI,
        ),
        id_short="STRING",
    )
    object_store.add(string_concept)
    all_identifiers_list.append(string_concept.identification)

    # Units

    ###############################

    # Create the AAS objects
    for sindit_asset in assets:
        aas_asset = model.Asset(
            kind=model.AssetKind.INSTANCE,
            identification=model.Identifier(
                id_=sindit_asset.iri, id_type=model.IdentifierType.IRI
            ),
            id_short=sindit_asset.id_short,
            category="ASSET",
            description=dict(en=sindit_asset.description),
        )
        aas = model.AssetAdministrationShell(
            identification=model.Identifier(
                sindit_asset.iri + "_aas", model.IdentifierType.IRI
            ),
            id_short=sindit_asset.id_short + "_aas",
            asset=model.AASReference.from_referable(aas_asset),
            submodel=set(),
        )

        ###############################
        # SINDIT details: graph positions, asset caption and asset similarities
        sindit_submodel = model.Submodel(
            identification=model.Identifier(
                SUBMODEL_BASE_IRI_PATH + "sindit_details/" + _get_unique_suffix(),
                model.IdentifierType.IRI,
            ),
            id_short="sindit_details",
        )

        # Caption
        sindit_submodel.submodel_element.add(
            model.Property(
                id_short="CAPTION",
                value=sindit_asset.caption,
                value_type=model.datatypes.String,
                semantic_id=model.AASReference.from_referable(caption_concept),
            )
        )

        # Similarities
        filtered_similarities_list = [
            similarity
            for similarity in asset_similarities
            if similarity.get("asset1") == sindit_asset.iri
        ]
        filtered_similarities_json = json.dumps(filtered_similarities_list)
        sindit_submodel.submodel_element.add(
            model.Property(
                id_short="asset_similarities",
                value=filtered_similarities_json,
                value_type=model.datatypes.String,
                semantic_id=model.AASReference.from_referable(similarities_concept),
            )
        )

        # Node positions
        positions_dict: Dict[str, tuple(float | None, float | None)] = dict()
        positions_dict[sindit_asset.iri] = (
            sindit_asset.visualization_positioning_x,
            sindit_asset.visualization_positioning_y,
        )
        for ts in sindit_asset.timeseries:
            positions_dict[ts.iri] = (
                ts.visualization_positioning_x,
                ts.visualization_positioning_y,
            )
            positions_dict[ts.db_connection.iri] = (
                ts.db_connection.visualization_positioning_x,
                ts.db_connection.visualization_positioning_y,
            )
            positions_dict[ts.runtime_connection.iri] = (
                ts.runtime_connection.visualization_positioning_x,
                ts.runtime_connection.visualization_positioning_y,
            )
            if ts.unit is not None:
                positions_dict[ts.unit.iri] = (
                    ts.unit.visualization_positioning_x,
                    ts.unit.visualization_positioning_y,
                )
            if ts.ts_cluster is not None:
                positions_dict[ts.ts_cluster.iri] = (
                    ts.ts_cluster.visualization_positioning_x,
                    ts.ts_cluster.visualization_positioning_y,
                )
        for file in sindit_asset.supplementary_files:
            positions_dict[file.iri] = (
                file.visualization_positioning_x,
                file.visualization_positioning_y,
            )
            positions_dict[file.db_connection.iri] = (
                file.db_connection.visualization_positioning_x,
                file.db_connection.visualization_positioning_y,
            )
            for keyword in file.extracted_keywords:
                positions_dict[keyword.iri] = (
                    keyword.visualization_positioning_x,
                    keyword.visualization_positioning_y,
                )

        positions_json = json.dumps(positions_dict)
        sindit_submodel.submodel_element.add(
            model.Property(
                id_short="sindit_node_positions",
                value=positions_json,
                value_type=model.datatypes.String,
                semantic_id=model.AASReference.from_referable(node_positions_concept),
            )
        )

        # Create submodel
        object_store.add(sindit_submodel)
        all_identifiers_list.append(sindit_submodel.identification)
        aas.submodel.add(model.AASReference.from_referable(sindit_submodel))
        aas.update()

        ###############################
        # Time-series
        ts_submodel = model.Submodel(
            identification=model.Identifier(
                SUBMODEL_BASE_IRI_PATH + "time_series/" + _get_unique_suffix(),
                model.IdentifierType.IRI,
            ),
            id_short="time_series",
        )
        for ts in sindit_asset.timeseries:
            sub_submodels = []

            # Iri and the caption
            sub_submodels.append(
                model.Property(
                    id_short="IRI",
                    value=ts.iri,
                    value_type=model.datatypes.String,
                    semantic_id=model.AASReference.from_referable(iri_concept),
                )
            )
            if ts.caption != ts.id_short:
                sub_submodels.append(
                    model.Property(
                        id_short="CAPTION",
                        value=ts.caption,
                        value_type=model.datatypes.String,
                        semantic_id=model.AASReference.from_referable(caption_concept),
                    )
                )

            # Value type
            if ts.value_type == TimeseriesValueTypes.DECIMAL.value:
                value_semantic = model.AASReference.from_referable(decimal_concept)
            elif ts.value_type == TimeseriesValueTypes.BOOL.value:
                value_semantic = model.AASReference.from_referable(bool_concept)
            elif ts.value_type == TimeseriesValueTypes.STRING.value:
                value_semantic = model.AASReference.from_referable(string_concept)
            else:
                value_semantic = model.AASReference.from_referable(integer_concept)

            sub_submodels.append(
                model.Property(
                    id_short="value_type",
                    value_type=model.datatypes.String,
                    value_id=value_semantic,
                )
            )

            # Attached unit if present
            if ts.unit is not None:
                sub_submodels.append(
                    model.Property(
                        id_short="unit",
                        value_type=model.datatypes.String,
                        value_id=_load_or_create_concept_descr_reference(
                            ts.unit,
                            dynamic_concepts_dict,
                            object_store,
                            all_identifiers_list,
                        ),
                    )
                )

            # Attached cluster if present
            if ts.ts_cluster is not None:
                sub_submodels.append(
                    model.Property(
                        id_short="cluster_affiliation",
                        value_type=model.datatypes.String,
                        value_id=_load_or_create_concept_descr_reference(
                            ts.ts_cluster,
                            dynamic_concepts_dict,
                            object_store,
                            all_identifiers_list,
                        ),
                    )
                )

            # Extracted features if present
            if len(ts.feature_dict) > 0:
                sub_submodels.append(
                    model.SubmodelElementCollectionOrdered(
                        id_short="extracted_features",
                        semantic_id=model.AASReference.from_referable(
                            influx_connection_concept
                        ),
                        value=[
                            model.Property(
                                id_short=re.sub(
                                    "[^a-zA-Z0-9_]+", "", key.replace("-", "_minus_")
                                ),
                                value=str(value),
                                value_type=model.datatypes.String,
                                semantic_id=model.AASReference.from_referable(
                                    feature_concept
                                ),
                            )
                            for key, value in ts.feature_dict.items()
                        ],
                    )
                )
            if ts.reduced_feature_list is not None:
                sub_submodels.append(
                    model.Property(
                        id_short="pca_reduced_feature_list",
                        value=", ".join([str(val) for val in ts.reduced_feature_list]),
                        value_type=model.datatypes.String,
                        semantic_id=model.AASReference.from_referable(
                            reduced_features_concept
                        ),
                    )
                )

            # Databse connection
            sub_submodels.append(
                model.SubmodelElementCollectionOrdered(
                    id_short="database_connection",
                    semantic_id=model.AASReference.from_referable(
                        influx_connection_concept
                    ),
                    value=[
                        model.Property(
                            id_short="database_connection_iri",
                            value=ts.db_connection.iri,
                            value_type=model.datatypes.String,
                            semantic_id=model.AASReference.from_referable(iri_concept),
                        ),
                        model.Property(
                            id_short="database_connection_id_short",
                            value=ts.db_connection.id_short,
                            value_type=model.datatypes.String,
                            semantic_id=model.AASReference.from_referable(
                                id_short_concept
                            ),
                        ),
                        model.Property(
                            id_short="database_instance",
                            value_type=model.datatypes.String,
                            value=ts.db_connection.database,
                            semantic_id=model.AASReference.from_referable(
                                database_instance_concept
                            ),
                        ),
                        model.Property(
                            id_short="database_group",
                            value_type=model.datatypes.String,
                            value=ts.db_connection.group,
                            semantic_id=model.AASReference.from_referable(
                                database_group_concept
                            ),
                        ),
                        model.Property(
                            id_short="host_environmental_variable",
                            value_type=model.datatypes.String,
                            value=ts.db_connection.host_environment_variable,
                            semantic_id=model.AASReference.from_referable(env_concept),
                        ),
                        model.Property(
                            id_short="port_environmental_variable",
                            value_type=model.datatypes.String,
                            value=ts.db_connection.port_environment_variable,
                            semantic_id=model.AASReference.from_referable(env_concept),
                        ),
                        model.Property(
                            id_short="user_environmental_variable",
                            value_type=model.datatypes.String,
                            value=ts.db_connection.user_environment_variable,
                            semantic_id=model.AASReference.from_referable(env_concept),
                        ),
                        model.Property(
                            id_short="key_environmental_variable",
                            value_type=model.datatypes.String,
                            value=ts.db_connection.key_environment_variable,
                            semantic_id=model.AASReference.from_referable(env_concept),
                        ),
                    ],
                ),
            )

            # Runtime connection
            sub_submodels.append(
                model.SubmodelElementCollectionOrdered(
                    id_short="runtime_connection",
                    semantic_id=model.AASReference.from_referable(
                        mqtt_connection_concept
                        if ts.runtime_connection.type
                        == RuntimeConnectionTypes.MQTT.value
                        else opc_ua_connection_concept
                    ),
                    value=[
                        model.Property(
                            id_short="runtime_connection_iri",
                            value=ts.runtime_connection.iri,
                            value_type=model.datatypes.String,
                            semantic_id=model.AASReference.from_referable(iri_concept),
                        ),
                        model.Property(
                            id_short="runtime_connection_id_short",
                            value=ts.runtime_connection.id_short,
                            value_type=model.datatypes.String,
                            semantic_id=model.AASReference.from_referable(
                                id_short_concept
                            ),
                        ),
                        model.Property(
                            id_short="connection_topic",
                            value_type=model.datatypes.String,
                            value=ts.connection_topic,
                            semantic_id=model.AASReference.from_referable(
                                con_topic_connection_concept
                            ),
                        ),
                        model.Property(
                            id_short="connection_keyword",
                            value_type=model.datatypes.String,
                            value=ts.connection_keyword,
                            semantic_id=model.AASReference.from_referable(
                                con_keyword_connection_concept
                            ),
                        ),
                        model.Property(
                            id_short="host_environmental_variable",
                            value_type=model.datatypes.String,
                            value=ts.runtime_connection.host_environment_variable,
                            semantic_id=model.AASReference.from_referable(env_concept),
                        ),
                        model.Property(
                            id_short="port_environmental_variable",
                            value_type=model.datatypes.String,
                            value=ts.runtime_connection.port_environment_variable,
                            semantic_id=model.AASReference.from_referable(env_concept),
                        ),
                        model.Property(
                            id_short="user_environmental_variable",
                            value_type=model.datatypes.String,
                            value=ts.runtime_connection.user_environment_variable,
                            semantic_id=model.AASReference.from_referable(env_concept),
                        ),
                        model.Property(
                            id_short="key_environmental_variable",
                            value_type=model.datatypes.String,
                            value=ts.runtime_connection.key_environment_variable,
                            semantic_id=model.AASReference.from_referable(env_concept),
                        ),
                    ],
                ),
            )

            # Create the meta-submodel for the time-series
            ts_submodel.submodel_element.add(
                model.SubmodelElementCollectionOrdered(
                    id_short=ts.id_short,
                    value=sub_submodels,
                    description=dict(en=ts.description),
                    category="TIMESERIES",
                )
            )

        object_store.add(ts_submodel)
        all_identifiers_list.append(ts_submodel.identification)
        aas.submodel.add(model.AASReference.from_referable(ts_submodel))
        aas.update()

        ###############################
        # Supplementary Files

        suppl_file_submodel = model.Submodel(
            identification=model.Identifier(
                SUBMODEL_BASE_IRI_PATH + "supplementary_files/" + _get_unique_suffix(),
                model.IdentifierType.IRI,
            ),
            id_short="supplementary_files",
        )
        for suppl_file in sindit_asset.supplementary_files:
            # Get related database service:
            file_con_node: DatabaseConnectionsDao = (
                DB_CON_NODE_DAO.get_database_connection_for_node(suppl_file.iri)
            )
            if file_con_node is None:
                logger.info(
                    "File requested, but database connection node does not exist"
                )
                return None
            file_service: FilesPersistenceService = (
                DatabasePersistenceServiceContainer.instance().get_persistence_service(
                    file_con_node.iri
                )
            )

            file_stream = file_service.stream_file(suppl_file.iri)

            file_name_with_aasx_path = "/aasx/suppl/" + suppl_file.file_name

            if suppl_file.file_type == SupplementaryFileTypes.DOCUMENT_PDF.value:
                mime_type = "application/pdf"
                file_semantic_id = model.AASReference.from_referable(pdf_concept)
            elif suppl_file.file_type == SupplementaryFileTypes.IMAGE_JPG.value:
                mime_type = "image/jpeg"
                file_semantic_id = model.AASReference.from_referable(jpg_concept)
            elif suppl_file.file_type == SupplementaryFileTypes.CAD_STEP.value:
                mime_type = "application/step"
                file_semantic_id = model.AASReference.from_referable(step_concept)
            elif suppl_file.file_type == SupplementaryFileTypes.CAD_STL.value:
                mime_type = "application/stl"
                file_semantic_id = model.AASReference.from_referable(stl_concept)
            else:
                mime_type = "undefined"
                file_semantic_id = None

            actual_file_name = file_store.add_file(
                file_name_with_aasx_path, file_stream, "application/pdf"
            )

            sub_submodels = []

            # The file itself
            sub_submodels.append(
                model.File(
                    id_short=suppl_file.id_short,
                    mime_type=mime_type,
                    value=actual_file_name,
                    semantic_id=file_semantic_id,
                )
            )

            # Iri and the caption
            sub_submodels.append(
                model.Property(
                    id_short="IRI",
                    value=suppl_file.iri,
                    value_type=model.datatypes.String,
                    semantic_id=model.AASReference.from_referable(iri_concept),
                )
            )
            if suppl_file.caption != suppl_file.id_short:
                sub_submodels.append(
                    model.Property(
                        id_short="CAPTION",
                        value=suppl_file.caption,
                        value_type=model.datatypes.String,
                        semantic_id=model.AASReference.from_referable(caption_concept),
                    )
                )

            # Extracted key_phrases if present
            if len(suppl_file.extracted_keywords) > 0:
                sub_submodels.append(
                    model.Property(
                        id_short="key_phrases",
                        value=", ".join(
                            [
                                key_phrase.keyword
                                for key_phrase in suppl_file.extracted_keywords
                            ]
                        ),
                        value_type=model.datatypes.String,
                        semantic_id=model.AASReference.from_referable(
                            key_phrases_concept
                        ),
                    )
                )

            # Databse connection
            sub_submodels.append(
                model.SubmodelElementCollectionOrdered(
                    id_short="database_connection",
                    semantic_id=model.AASReference.from_referable(
                        s3_connection_concept
                    ),
                    value=[
                        model.Property(
                            id_short="database_connection_iri",
                            value=suppl_file.db_connection.iri,
                            value_type=model.datatypes.String,
                            semantic_id=model.AASReference.from_referable(iri_concept),
                        ),
                        model.Property(
                            id_short="database_connection_id_short",
                            value=suppl_file.db_connection.id_short,
                            value_type=model.datatypes.String,
                            semantic_id=model.AASReference.from_referable(
                                id_short_concept
                            ),
                        ),
                        model.Property(
                            id_short="database_instance",
                            value_type=model.datatypes.String,
                            value=suppl_file.db_connection.database,
                            semantic_id=model.AASReference.from_referable(
                                database_instance_concept
                            ),
                        ),
                        model.Property(
                            id_short="database_group",
                            value_type=model.datatypes.String,
                            value=suppl_file.db_connection.group,
                            semantic_id=model.AASReference.from_referable(
                                database_group_concept
                            ),
                        ),
                        model.Property(
                            id_short="host_environmental_variable",
                            value_type=model.datatypes.String,
                            value=suppl_file.db_connection.host_environment_variable,
                            semantic_id=model.AASReference.from_referable(env_concept),
                        ),
                        model.Property(
                            id_short="port_environmental_variable",
                            value_type=model.datatypes.String,
                            value=suppl_file.db_connection.port_environment_variable,
                            semantic_id=model.AASReference.from_referable(env_concept),
                        ),
                        model.Property(
                            id_short="user_environmental_variable",
                            value_type=model.datatypes.String,
                            value=suppl_file.db_connection.user_environment_variable,
                            semantic_id=model.AASReference.from_referable(env_concept),
                        ),
                        model.Property(
                            id_short="key_environmental_variable",
                            value_type=model.datatypes.String,
                            value=suppl_file.db_connection.key_environment_variable,
                            semantic_id=model.AASReference.from_referable(env_concept),
                        ),
                    ],
                ),
            )

            # Create the meta-submodel for the supplementary file
            suppl_file_submodel.submodel_element.add(
                model.SubmodelElementCollectionOrdered(
                    id_short=suppl_file.id_short,
                    value=sub_submodels,
                    description=dict(en=suppl_file.description),
                    category="SUPPLEMENTARY_FILE",
                )
            )

        object_store.add(suppl_file_submodel)
        all_identifiers_list.append(suppl_file_submodel.identification)
        aas.submodel.add(model.AASReference.from_referable(suppl_file_submodel))
        aas.update()
        ###############################

        aas_list.append(aas)
        object_store.add(aas_asset)
        all_identifiers_list.append(aas_asset.identification)
        object_store.add(aas)
        all_identifiers_list.append(aas.identification)

    # Write the AAS objects to an AASX package
    with aasx.AASXWriter(aasx_file_path) as writer:

        # Use the low level writer since the higher level "write_aas" is
        # still incompatible with the AASX Package Explorer for multiple AAS
        writer.write_aas_objects(
            part_name="/aasx/data.xml",
            object_ids=all_identifiers_list,
            object_store=object_store,
            file_store=file_store,
        )

        # Metadata
        meta_data = pyecma376_2.OPCCoreProperties()
        meta_data.creator = "SINDIT (SIntef DIgital Twin)"
        meta_data.created = datetime.now()
        writer.write_core_properties(meta_data)

        # Package thumbnail
        with open("./assets/sindit_aas_thumbnail.png", "rb") as thumbnail:
            thumbnail_content = thumbnail.read()
            writer.write_thumbnail(
                name="/aasx/suppl/sindit_aas_thumbnail.png",
                data=thumbnail_content,
                content_type="image/png",
            )
