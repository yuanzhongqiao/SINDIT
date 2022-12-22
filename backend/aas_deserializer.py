import datetime
import json
from pathlib import Path  # Used for easier handling of auxiliary file's local path

import pyecma376_2  # The base library for Open Packaging Specifications. We will use the OPCCoreProperties class.
from basyx.aas import model
from basyx.aas.adapter import aasx
from basyx.aas.model.base import Identifier

from typing import Dict, List, Set
from backend.knowledge_graph.KnowledgeGraphPersistenceService import (
    KnowledgeGraphPersistenceService,
)
from graph_domain.main_digital_twin.SupplementaryFileNode import (
    SupplementaryFileNodeDeep,
)
from graph_domain.main_digital_twin.DatabaseConnectionNode import DatabaseConnectionNode
from graph_domain.main_digital_twin.AssetNode import AssetNodeDeep
from graph_domain.main_digital_twin.RuntimeConnectionNode import RuntimeConnectionNode
from graph_domain.main_digital_twin.TimeseriesNode import TimeseriesNodeDeep
from graph_domain.main_digital_twin.UnitNode import UnitNode
from graph_domain.similarities.ExtractedKeywordNode import ExtractedKeywordNode
from graph_domain.similarities.TimeseriesClusterNode import TimeseriesClusterNode

# def _serialize_asset(asset: AssetNodeDeep):
#     pass


def deserialize_from_aasx(
    aasx_file_path: str,
):
    # aas_list: List[model.AssetAdministrationShell] = []
    object_store = model.DictObjectStore([])
    file_store = aasx.DictSupplementaryFileContainer()

    # Read the archive
    with aasx.AASXReader(aasx_file_path) as reader:
        identifiers: Set[Identifier] = reader.read_into(
            object_store=object_store, file_store=file_store
        )

    # Extract asset identifiers:
    asset_identifiers = [
        id
        for id in identifiers
        if isinstance(object_store.get(id), model.AssetAdministrationShell)
    ]

    assets_list: List[AssetNodeDeep] = []

    for asset_identifier in asset_identifiers:
        print(f"Importing asset: {asset_identifier.id}")

        aas = object_store.get_identifiable(asset_identifier)
        aas_asset = object_store.get_identifiable(
            model.Identifier(aas.asset.key[0].value, model.IdentifierType.IRI)
        )
        aas_submodels = [
            object_store.get_identifiable(
                model.Identifier(sm_ref.key[0].value, model.IdentifierType.IRI)
            )
            for sm_ref in aas.submodel
        ]
        sindit_submodel = [
            sm for sm in aas_submodels if sm.id_short == "sindit_details"
        ][0]
        timeseries_submodel = [
            sm for sm in aas_submodels if sm.id_short == "time_series"
        ][0]
        files_submodel = [
            sm for sm in aas_submodels if sm.id_short == "supplementary_files"
        ][0]

        asset = AssetNodeDeep(
            iri=aas_asset.identification.id,
            id_short=aas_asset.id_short,
            description=aas_asset.description.get("en"),
        )

        # Files
        for file_meta in files_submodel.submodel_element:
            submodel_elements = [el for el in file_meta.value]
            iri_property = [el for el in submodel_elements if el.id_short == "IRI"][0]
            caption_property = [
                el for el in submodel_elements if el.id_short == "CAPTION"
            ][0]
            file_property = [
                el for el in submodel_elements if el.id_short == file_meta.id_short
            ][0]

            # Filename
            file_path = file_property.value
            file_name = file_path.split("/")[-1]

            # File type
            file_type_concept = object_store.get_identifiable(
                model.Identifier(
                    file_property.semantic_id.key[0].value, model.IdentifierType.IRI
                )
            )

            file = SupplementaryFileNodeDeep(
                id_short=file_meta.id_short,
                description=file_meta.description.get("en"),
                iri=iri_property.value,
                _explizit_caption=caption_property.value,
                file_name=file_name,
                file_type=file_type_concept.id_short,
            )

            # Extracted keyphrases
            key_phrase_properties = [
                el for el in submodel_elements if el.id_short == "key_phrases"
            ]
            if len(key_phrase_properties) > 0:
                key_phrases_json = key_phrase_properties[0].value
                key_phrases_list = json.loads(key_phrases_json)

                for kp in key_phrases_list:
                    file._extracted_keywords.add(
                        ExtractedKeywordNode(
                            iri=f"www.sintef.no/aas_identifiers/learning_factory/similarity_analysis/extracted_keyword_{kp}",
                            id_short=f"extracted_keyword_{kp}",
                            keyword=kp,
                            _explizit_caption=kp,
                        )
                    )

            # DB connection
            db_con_property_collection = [
                el for el in submodel_elements if el.id_short == "database_connection"
            ][0]
            db_con_type = object_store.get_identifiable(
                model.Identifier(
                    db_con_property_collection.semantic_id.key[0].value,
                    model.IdentifierType.IRI,
                )
            )

            db_con_properties = [el for el in db_con_property_collection.value]
            db_con_iri = [
                el
                for el in db_con_properties
                if el.id_short == "database_connection_iri"
            ][0]
            db_con_id_short = [
                el
                for el in db_con_properties
                if el.id_short == "database_connection_id_short"
            ][0]
            db_con_instance = [
                el for el in db_con_properties if el.id_short == "database_instance"
            ][0]
            db_con_group = [
                el for el in db_con_properties if el.id_short == "database_group"
            ][0]
            db_con_host = [
                el
                for el in db_con_properties
                if el.id_short == "host_environmental_variable"
            ][0]
            db_con_port = [
                el
                for el in db_con_properties
                if el.id_short == "port_environmental_variable"
            ][0]
            db_con_user = [
                el
                for el in db_con_properties
                if el.id_short == "user_environmental_variable"
            ][0]
            db_con_key = [
                el
                for el in db_con_properties
                if el.id_short == "key_environmental_variable"
            ][0]

            file._db_connections.add(
                DatabaseConnectionNode(
                    iri=db_con_iri.value,
                    id_short=db_con_id_short.value,
                    type=db_con_type.id_short,
                    database=db_con_instance.value,
                    group=db_con_group.value,
                    host_environment_variable=db_con_host.value,
                    port_environment_variable=db_con_port.value,
                    user_environment_variable=db_con_user.value,
                    key_environment_variable=db_con_key.value,
                )
            )

            asset._supplementary_files.add(file)

        # Timeseries
        for ts_meta in timeseries_submodel.submodel_element:
            submodel_elements = [el for el in ts_meta.value]
            iri_property = [el for el in submodel_elements if el.id_short == "IRI"][0]
            caption_property = [
                el for el in submodel_elements if el.id_short == "CAPTION"
            ][0]
            # Value type
            value_type_property = [
                el for el in submodel_elements if el.id_short == "value_type"
            ][0]
            value_type_object = object_store.get_identifiable(
                model.Identifier(
                    value_type_property.value_id.key[0].value, model.IdentifierType.IRI
                )
            )

            # Reduced features
            reduced_features_properties = [
                el
                for el in submodel_elements
                if el.id_short == "pca_reduced_feature_list"
            ]
            if len(reduced_features_properties) > 0:
                reduced_features = reduced_features_properties[0].value
            else:
                reduced_features = None

            # Feature dict
            features_properties = [
                el for el in submodel_elements if el.id_short == "extracted_features"
            ]
            if len(features_properties) > 0:
                features_property_collection = features_properties[0].value
                feature_dict = dict()
                for feature in features_property_collection:
                    feature_dict[feature.id_short] = float(feature.value)
                feature_json = json.dumps(feature_dict)
            else:
                feature_json = None

            ts = TimeseriesNodeDeep(
                id_short=ts_meta.id_short,
                description=ts_meta.description.get("en"),
                iri=iri_property.value,
                _explizit_caption=caption_property.value,
                value_type=value_type_object.id_short,
                _reduced_feature_list=reduced_features,
                _feature_dict=feature_json,
            )

            # Unit
            unit_properties = [el for el in submodel_elements if el.id_short == "unit"]
            if len(unit_properties) > 0:
                unit_property = unit_properties[0]
                unit_object = object_store.get_identifiable(
                    model.Identifier(
                        unit_property.value_id.key[0].value, model.IdentifierType.IRI
                    )
                )

                ts._units.add(
                    UnitNode(
                        iri=unit_object.identification.id,
                        id_short=unit_object.id_short,
                        description=unit_object.description.get("en"),
                    )
                )

            # CLuster
            cluster_properties = [
                el for el in submodel_elements if el.id_short == "cluster_affiliation"
            ]
            if len(cluster_properties) > 0:
                cluster_property = cluster_properties[0]
                cluster_object = object_store.get_identifiable(
                    model.Identifier(
                        cluster_property.value_id.key[0].value, model.IdentifierType.IRI
                    )
                )

                ts._ts_clusters.add(
                    TimeseriesClusterNode(
                        iri=cluster_object.identification.id,
                        id_short=cluster_object.id_short,
                        description=cluster_object.description.get("en"),
                    )
                )

            # DB connection
            db_con_property_collection = [
                el for el in submodel_elements if el.id_short == "database_connection"
            ][0]
            db_con_type = object_store.get_identifiable(
                model.Identifier(
                    db_con_property_collection.semantic_id.key[0].value,
                    model.IdentifierType.IRI,
                )
            )

            db_con_properties = [el for el in db_con_property_collection.value]
            db_con_iri = [
                el
                for el in db_con_properties
                if el.id_short == "database_connection_iri"
            ][0]
            db_con_id_short = [
                el
                for el in db_con_properties
                if el.id_short == "database_connection_id_short"
            ][0]
            db_con_instance = [
                el for el in db_con_properties if el.id_short == "database_instance"
            ][0]
            db_con_group = [
                el for el in db_con_properties if el.id_short == "database_group"
            ][0]
            db_con_host = [
                el
                for el in db_con_properties
                if el.id_short == "host_environmental_variable"
            ][0]
            db_con_port = [
                el
                for el in db_con_properties
                if el.id_short == "port_environmental_variable"
            ][0]
            db_con_user = [
                el
                for el in db_con_properties
                if el.id_short == "user_environmental_variable"
            ][0]
            db_con_key = [
                el
                for el in db_con_properties
                if el.id_short == "key_environmental_variable"
            ][0]

            ts._db_connections.add(
                DatabaseConnectionNode(
                    iri=db_con_iri.value,
                    id_short=db_con_id_short.value,
                    type=db_con_type.id_short,
                    database=db_con_instance.value,
                    group=db_con_group.value,
                    host_environment_variable=db_con_host.value,
                    port_environment_variable=db_con_port.value,
                    user_environment_variable=db_con_user.value,
                    key_environment_variable=db_con_key.value,
                )
            )

            # Runtime connection
            rt_con_property_collection = [
                el for el in submodel_elements if el.id_short == "runtime_connection"
            ][0]
            rt_con_type = object_store.get_identifiable(
                model.Identifier(
                    rt_con_property_collection.semantic_id.key[0].value,
                    model.IdentifierType.IRI,
                )
            )

            rt_con_properties = [el for el in rt_con_property_collection.value]
            rt_con_iri = [
                el
                for el in rt_con_properties
                if el.id_short == "runtime_connection_iri"
            ][0]
            rt_con_id_short = [
                el
                for el in rt_con_properties
                if el.id_short == "runtime_connection_id_short"
            ][0]
            rt_con_topic = [
                el for el in rt_con_properties if el.id_short == "connection_topic"
            ][0]
            rt_con_keyword = [
                el for el in rt_con_properties if el.id_short == "connection_keyword"
            ][0]
            rt_con_host = [
                el
                for el in rt_con_properties
                if el.id_short == "host_environmental_variable"
            ][0]
            rt_con_port = [
                el
                for el in rt_con_properties
                if el.id_short == "port_environmental_variable"
            ][0]
            rt_con_user = [
                el
                for el in rt_con_properties
                if el.id_short == "user_environmental_variable"
            ][0]
            rt_con_key = [
                el
                for el in rt_con_properties
                if el.id_short == "key_environmental_variable"
            ][0]

            ts._runtime_connections.add(
                RuntimeConnectionNode(
                    iri=rt_con_iri.value,
                    id_short=rt_con_id_short.value,
                    type=rt_con_type.id_short,
                    host_environment_variable=rt_con_host.value,
                    port_environment_variable=rt_con_port.value,
                    user_environment_variable=rt_con_user.value,
                    key_environment_variable=rt_con_key.value,
                )
            )
            ts.connection_topic = rt_con_topic.value
            ts.connection_keyword = rt_con_keyword.value

            asset._timeseries.add(ts)

        assets_list.append(asset)

    ps: KnowledgeGraphPersistenceService = KnowledgeGraphPersistenceService.instance()

    for asset in assets_list:
        ps.graph.push(asset)

    pass

    # Create the AAS objects
    # for sindit_asset in assets:

    #     aas_asset = model.Asset(
    #         kind=model.AssetKind.INSTANCE,
    #         identification=model.Identifier(
    #             id_=sindit_asset.iri, id_type=model.IdentifierType.IRI
    #         ),
    #     )
    #     aas = model.AssetAdministrationShell(
    #         identification=model.Identifier(
    #             sindit_asset.iri + "_administration_shell", model.IdentifierType.IRI
    #         ),
    #         asset=model.AASReference.from_referable(aas_asset),
    #         submodel={},
    #     )

    #     aas_list.append(aas)
    #     object_store.add(aas_asset)
    #     object_store.add(aas)
