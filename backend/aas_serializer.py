from datetime import datetime
from pathlib import Path
import random  # Used for easier handling of auxiliary file's local path

import pyecma376_2  # The base library for Open Packaging Specifications. We will use the OPCCoreProperties class.
from basyx.aas import model
from basyx.aas.adapter import aasx
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

# def _serialize_asset(asset: AssetNodeDeep):
#     pass


def _get_unique_suffix() -> str:
    date_time_str = (
        datetime.now()
        .astimezone(
            tz.gettz(get_configuration(group=ConfigGroups.FRONTEND, key="timezone"))
        )
        .strftime(DATETIME_STRF_FORMAT)
    )
    return date_time_str + "_" + str(random.randrange(0, 99999, 1))


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

            actual_file_name = file_store.add_file(
                file_name_with_aasx_path, file_stream, "application/pdf"
            )
            suppl_file_submodel.submodel_element.add(
                model.File(
                    id_short=suppl_file.id_short,
                    mime_type="application/pdf",
                    value=actual_file_name,
                )
            )

        object_store.add(suppl_file_submodel)
        all_identifiers_list.append(suppl_file_submodel.identification)
        aas.submodel.add(model.AASReference.from_referable(suppl_file_submodel))
        aas.update()

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
