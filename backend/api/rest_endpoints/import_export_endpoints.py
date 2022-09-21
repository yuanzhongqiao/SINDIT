import base64
from datetime import datetime
import json
import os
import shutil
from typing import List
from fastapi.responses import StreamingResponse
from fastapi import UploadFile, Form, HTTPException
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

DB_CON_NODE_DAO: DatabaseConnectionsDao = DatabaseConnectionsDao.instance()
SUPPL_FILE_DAO: SupplementaryFileNodesDao = SupplementaryFileNodesDao.instance()

GRAPH_DATABASE_FAKE_IRI = "graph_database_neo4j"
GRAPH_DATABASE_LABEL = "Graph Database (Neo4J)"
GRAPH_DATABASE_BACKUP_FOLDER = "graph_database_neo4j"
DB_CONNECTION_LABEL_PREFIX = {
    DatabaseConnectionTypes.INFLUX_DB.value: "Time-series DB",
    DatabaseConnectionTypes.S3.value: "Files DB",
}

DATABASE_EXPORT_DIRECTORY = "database_export/"
DATABASE_IMPORT_DIRECTORY = "database_import/"

DATETIME_STRF_FORMAT = "%Y_%m_%d_%H_%M_%S_%f"

FILENAME_ALLOWED_CHARS = (
    "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ_-"
)
EXPORT_INFO_FILE_NAME = "sindit_export_info.txt"


@app.get("/export/database_list")
def get_exportable_databases_list():
    """
    Returns a list of all exportable databases, including the main graph database.
    :return:
    """
    additional_db_connections: List[
        DatabaseConnectionNode
    ] = DB_CON_NODE_DAO.get_database_connections()

    options = [
        (
            additional_db_node.iri,
            f"{DB_CONNECTION_LABEL_PREFIX.get(additional_db_node.type)}: {additional_db_node.caption}",
        )
        for additional_db_node in additional_db_connections
    ]

    options.insert(0, (GRAPH_DATABASE_FAKE_IRI, GRAPH_DATABASE_LABEL))

    return options


def _remplace_illegal_characters_from_iri(iri: str) -> str:
    return "".join((char if char in FILENAME_ALLOWED_CHARS else "_") for char in iri)


@app.get("/export/database_dumps")
def export_database_dumps(database_iri: str | None = None, all_databases: bool = True):
    """
    Creates a new database dump or returns a current one, if existing. For single databases or all in one zip.
    :raises IdNotFoundException: If the file is not found
    :return:
    """
    backup_date_time = datetime.now()
    backup_date_time_file_string = backup_date_time.astimezone(
        tz.gettz(get_configuration(group=ConfigGroups.FRONTEND, key="timezone"))
    ).strftime(DATETIME_STRF_FORMAT)

    backup_base_path = DATABASE_EXPORT_DIRECTORY + backup_date_time_file_string + "/"

    os.makedirs(backup_base_path)

    if all_databases:
        db_list = [option[0] for option in get_exportable_databases_list()]
    else:
        if database_iri is None:
            shutil.rmtree(backup_base_path)
            raise IdNotFoundException()
        db_list = [database_iri]

    backup_folder_names = dict()

    persistence_container = DatabasePersistenceServiceContainer.instance()

    for db in db_list:
        if db == GRAPH_DATABASE_FAKE_IRI:
            backup_folder = GRAPH_DATABASE_BACKUP_FOLDER
            backup_path = backup_base_path + backup_folder
            KnowledgeGraphPersistenceService.instance().backup(backup_path)
            backup_folder_names[db] = backup_folder
        else:
            backup_folder = _remplace_illegal_characters_from_iri(db)
            backup_path = backup_base_path + backup_folder
            persistence_service = persistence_container.get_persistence_service(db)
            persistence_service.backup(backup_path)

            backup_folder_names[db] = backup_folder

    # Create info file:
    info_dict = {
        "sindit_export_version": get_configuration(
            group=ConfigGroups.GENERIC, key="sindit_export_version"
        ),
        "export_date_time": backup_date_time.isoformat(),
        "backup_iri_mappings": backup_folder_names,
    }

    info_json = json.dumps(info_dict, indent=4)

    with open(
        backup_base_path + EXPORT_INFO_FILE_NAME, "w", encoding="utf-8"
    ) as info_file:
        info_file.write(info_json)

    # Zip the folder and delete it
    zip_file_path = DATABASE_EXPORT_DIRECTORY + backup_date_time_file_string
    zip_file_path_with_extension = zip_file_path + ".zip"
    shutil.make_archive(zip_file_path, "zip", backup_base_path)
    shutil.rmtree(backup_base_path)

    def iterfile():
        with open(zip_file_path_with_extension, mode="rb") as file_like:
            yield from file_like

    return StreamingResponse(iterfile(), media_type="application/octet-stream")


@app.post("/import/database_dumps")
def upload(file_name: str = Form(...), file_data: str = Form(...)):
    print(f"Importing database dump(s): {file_name}")
    restore_date_time = datetime.now()
    restore_date_time_file_string = restore_date_time.astimezone(
        tz.gettz(get_configuration(group=ConfigGroups.FRONTEND, key="timezone"))
    ).strftime(DATETIME_STRF_FORMAT)

    restore_base_path = DATABASE_IMPORT_DIRECTORY + restore_date_time_file_string + "/"
    os.makedirs(restore_base_path)

    content_type, content_string = file_data.split(",")
    if content_type != "data:application/zip;base64":
        shutil.rmtree(restore_base_path)
        raise HTTPException(
            status_code=403, detail="Invalid file: only zip archives allowed."
        )

    decoded_bytes = base64.b64decode(content_string)

    zip_file_name = restore_base_path + "zip_archive.zip"
    with open(zip_file_name, "wb") as f:
        f.write(decoded_bytes)

    shutil.unpack_archive(filename=zip_file_name, extract_dir=restore_base_path)
    os.remove(zip_file_name)

    # Parse info file:
    try:
        with open(
            restore_base_path + EXPORT_INFO_FILE_NAME, "r", encoding="utf-8"
        ) as info_file:
            info_file_json = info_file.read()
    except FileNotFoundError:
        print("Not a valid backup: sindit_export_info.txt file not found!")
        shutil.rmtree(restore_base_path)
        raise HTTPException(
            status_code=403, detail="Invalid backup: sindit_export_info.txt missing"
        )

    info_dict = json.loads(info_file_json)
    database_folders: dict = info_dict.get("backup_iri_mappings")
    # Restore databases:
    persistence_container = DatabasePersistenceServiceContainer.instance()
    for iri in database_folders.keys():
        db_folder_name = database_folders.get(iri)
        backup_path = restore_base_path + db_folder_name
        if iri == GRAPH_DATABASE_FAKE_IRI:
            KnowledgeGraphPersistenceService.instance().restore(backup_path)
        else:
            persistence_service = persistence_container.get_persistence_service(iri)
            persistence_service.restore(backup_path)

    shutil.rmtree(restore_base_path)

    return {"message": f"Successfuly imported {file_name}"}
