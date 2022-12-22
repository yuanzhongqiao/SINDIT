import base64
from datetime import datetime
import json
import os
import shutil
from typing import List
from fastapi.responses import StreamingResponse
from fastapi import Form, HTTPException
from backend.aas_deserializer import deserialize_from_aasx
from backend.aas_serializer import serialize_to_aasx
from backend.knowledge_graph.KnowledgeGraphPersistenceService import (
    KnowledgeGraphPersistenceService,
)
from backend.specialized_databases.DatabasePersistenceServiceContainer import (
    DatabasePersistenceServiceContainer,
)
from util.environment_and_configuration import (
    ConfigGroups,
    get_configuration,
)
from dateutil import tz
from backend.api.api import app
from backend.exceptions.IdNotFoundException import IdNotFoundException

from backend.knowledge_graph.dao.DatabaseConnectionsDao import DatabaseConnectionsDao
from backend.knowledge_graph.dao.SupplementaryFileNodesDao import (
    SupplementaryFileNodesDao,
)

from graph_domain.main_digital_twin.DatabaseConnectionNode import (
    DatabaseConnectionNode,
    DatabaseConnectionTypes,
)
from util.file_name_utils import _replace_illegal_characters_from_iri
from util.log import logger
from backend.knowledge_graph.dao.AssetNodesDao import AssetsDao


ASSETS_DAO: AssetsDao = AssetsDao.instance()

DB_CON_NODE_DAO: DatabaseConnectionsDao = DatabaseConnectionsDao.instance()
SUPPL_FILE_DAO: SupplementaryFileNodesDao = SupplementaryFileNodesDao.instance()

GRAPH_DATABASE_FAKE_IRI = "graph_database_neo4j"
GRAPH_DATABASE_LABEL = "Graph Database (Neo4J)"
GRAPH_DATABASE_BACKUP_FOLDER = "graph_database_neo4j"
DB_CONNECTION_LABEL_PREFIX = {
    DatabaseConnectionTypes.INFLUX_DB.value: "Time-series DB",
    DatabaseConnectionTypes.S3.value: "Files DB",
}

AAS_EXPORT_DIRECTORY = "aas_export/"
AAS_IMPORT_DIRECTORY = "aas_import/"
AAS_EXPORT_FILE_NAME_PREFIX = "sindit_aas_"

DATETIME_STRF_FORMAT = "%Y_%m_%d_%H_%M_%S_%f"


EXPORT_INFO_FILE_NAME = "sindit_export_info.txt"


@app.get("/export/aas")
async def export_database_dumps():
    """
    Serializes the graph to AASX, including supplementary files (not timeseries values).
    """
    logger.info("Started AASX export...")

    backup_date_time = datetime.now()
    backup_date_time_file_string = backup_date_time.astimezone(
        tz.gettz(get_configuration(group=ConfigGroups.FRONTEND, key="timezone"))
    ).strftime(DATETIME_STRF_FORMAT)

    os.makedirs(AAS_EXPORT_DIRECTORY, exist_ok=True)

    # Load the content:
    assets = ASSETS_DAO.get_assets_deep()
    asset_similarities = ASSETS_DAO.get_asset_similarities()

    # Create the AASX package
    aas_file_path = (
        AAS_EXPORT_DIRECTORY
        + AAS_EXPORT_FILE_NAME_PREFIX
        + backup_date_time_file_string
    )
    aasx_file_path_with_extension = aas_file_path + ".aasx"
    serialize_to_aasx(
        aasx_file_path=aasx_file_path_with_extension,
        assets=assets,
        asset_similarities=asset_similarities,
    )

    def iterfile():
        with open(aasx_file_path_with_extension, mode="rb") as file_like:
            yield from file_like

    return StreamingResponse(iterfile(), media_type="application/octet-stream")


@app.post("/import/aas")
async def upload(file_name: str = Form(...), file_data: str = Form(...)):
    logger.info(f"Importing AASX package: {file_name}")

    # Retrieve and prepare file:
    restore_date_time = datetime.now()
    restore_date_time_file_string = restore_date_time.astimezone(
        tz.gettz(get_configuration(group=ConfigGroups.FRONTEND, key="timezone"))
    ).strftime(DATETIME_STRF_FORMAT)

    restore_base_path = AAS_IMPORT_DIRECTORY + restore_date_time_file_string + "/"
    os.makedirs(restore_base_path)

    content_type, content_string = file_data.split(",")
    if content_type != "data:application/octet-stream;base64":
        shutil.rmtree(restore_base_path)
        raise HTTPException(
            status_code=403, detail="Invalid file: only AASX zip archives allowed."
        )

    decoded_bytes = base64.b64decode(content_string)

    aasx_file_name = restore_base_path + "zip_archive.zip"
    with open(aasx_file_name, "wb") as f:
        f.write(decoded_bytes)

    # Deserialize
    deserialize_from_aasx(aasx_file_path=aasx_file_name)

    # Cleanup
    os.remove(aasx_file_name)

    return {"message": f"Successfuly imported {file_name}"}

    # shutil.unpack_archive(filename=aasx_file_name, extract_dir=restore_base_path)
    # # Parse info file:
    # try:
    #     with open(
    #         restore_base_path + EXPORT_INFO_FILE_NAME, "r", encoding="utf-8"
    #     ) as info_file:
    #         info_file_json = info_file.read()
    # except FileNotFoundError:
    #     logger.info("Not a valid backup: sindit_export_info.txt file not found!")
    #     shutil.rmtree(restore_base_path)
    #     raise HTTPException(
    #         status_code=403, detail="Invalid backup: sindit_export_info.txt missing"
    #     )

    # info_dict = json.loads(info_file_json)
    # database_folders: dict = info_dict.get("backup_iri_mappings")
    # # Restore databases:
    # persistence_container = DatabasePersistenceServiceContainer.instance()
    # database_iris = list(database_folders.keys())

    # # Make sure, the main graph database is being restored first
    # if GRAPH_DATABASE_FAKE_IRI in database_iris:
    #     database_iris.remove(GRAPH_DATABASE_FAKE_IRI)
    #     database_iris.insert(0, GRAPH_DATABASE_FAKE_IRI)

    # for iri in database_iris:
    #     db_folder_name = database_folders.get(iri)
    #     backup_path = restore_base_path + db_folder_name
    #     if iri == GRAPH_DATABASE_FAKE_IRI:
    #         KnowledgeGraphPersistenceService.instance().restore(backup_path)
    #     else:
    #         persistence_service = persistence_container.get_persistence_service(iri)
    #         persistence_service.restore(backup_path)

    # shutil.rmtree(restore_base_path)

    # return {"message": f"Successfuly imported {file_name}"}
