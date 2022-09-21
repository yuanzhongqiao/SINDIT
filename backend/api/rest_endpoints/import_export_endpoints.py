from typing import List
from fastapi.responses import StreamingResponse
from fastapi.responses import RedirectResponse
from fastapi.responses import PlainTextResponse
import py2neo
from util.environment_and_configuration import get_environment_variable
from backend.api.api import app
from backend.exceptions.IdNotFoundException import IdNotFoundException

from backend.knowledge_graph.dao.DatabaseConnectionsDao import DatabaseConnectionsDao
from backend.knowledge_graph.dao.SupplementaryFileNodesDao import (
    SupplementaryFileNodesDao,
)

import backend.api.python_endpoints.file_endpoints as python_file_endpoints
from graph_domain.main_digital_twin.DatabaseConnectionNode import (
    DatabaseConnectionNode,
    DatabaseConnectionTypes,
)
from neo4j import GraphDatabase
from neo4j_backup import Extractor, Importer

DB_CON_NODE_DAO: DatabaseConnectionsDao = DatabaseConnectionsDao.instance()
SUPPL_FILE_DAO: SupplementaryFileNodesDao = SupplementaryFileNodesDao.instance()

GRAPH_DATABASE_FAKE_IRI = "graph_db_iri"
GRAPH_DATABASE_LABEL = "Graph Database (Neo4J)"
DB_CONNECTION_LABEL_PREFIX = {
    DatabaseConnectionTypes.INFLUX_DB.value: "Time-series DB",
    DatabaseConnectionTypes.S3.value: "Files DB",
}

DATABASE_EXPORT_DIRECTORY = "database_export/"


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


def _test_backup_neo4j():
    print("Backing up neo4j")

    uri = "neo4j://sindit-neo4j-kg-devcontainer:7687"
    username = "neo4j"
    password = "sindit-neo4j"
    encrypted = False
    trust = "TRUST_ALL_CERTIFICATES"
    driver = GraphDatabase.driver(
        uri, auth=(username, password), encrypted=encrypted, trust=trust
    )

    database = "neo4j"

    project_dir = "database_export/neo4j_test_export"
    input_yes = False
    compress = True
    extractor = Extractor(
        project_dir=project_dir,
        driver=driver,
        database=database,
        input_yes=input_yes,
        compress=compress,
    )
    extractor.extract_data()

    pass


NEO4J_HOST = get_environment_variable(key="NEO4J_DB_HOST", optional=False)
NEO4J_PORT = get_environment_variable(key="NEO4J_DB_PORT", optional=False)
NEO4J_DB_NAME = get_environment_variable(key="NEO4J_DB_NAME", optional=False)
NEO4J_URI = NEO4J_HOST + ":" + NEO4J_PORT
NEO4J_USER = get_environment_variable(key="NEO4J_DB_USER", optional=True)
NEO4J_PW = get_environment_variable(key="NEO4J_DB_PW", optional=True)


def _get_neo4j_graph():
    if NEO4J_USER is not None and NEO4J_PW is not None:
        auth = (NEO4J_USER, NEO4J_PW)
    elif NEO4J_USER is not None:
        auth = (NEO4J_USER, None)
    else:
        auth = None

    return py2neo.Graph(NEO4J_URI, name=NEO4J_DB_NAME, auth=auth)


def _test_restore_neo4j():
    print("Restoring neo4j")
    g = _get_neo4j_graph()
    # Delete everything
    print("Deleting everything...")
    g.delete_all()
    print("Deleted everything.")

    uri = "neo4j://sindit-neo4j-kg-devcontainer:7687"
    username = "neo4j"
    password = "sindit-neo4j"
    encrypted = False
    trust = "TRUST_ALL_CERTIFICATES"
    driver = GraphDatabase.driver(
        uri, auth=(username, password), encrypted=encrypted, trust=trust
    )

    database = "neo4j"

    project_dir = "database_export/neo4j_test_export"
    input_yes = False
    importer = Importer(
        project_dir=project_dir, driver=driver, database=database, input_yes=input_yes
    )
    importer.import_data()

    pass


# influx restore ./database_export/influx_db_test --host http://sindit-influx-db-devcontainer:8086 -t sindit_influxdb_admin_token
# influx bucket delete -o sindit -n sindit --host http://sindit-influx-db-devcontainer:8086 -t sindit_influxdb_admin_token
#  influx restore ./database_export/influx_db_test --host http://sindit-influx-db-devcontainer:8086 -t sindit_influxdb_admin_token


@app.get("/export/database_dump")
def get_supplementary_file(database_iri: str | None = None, all_databases: bool = True):
    """
    Creates a new database dump or returns a current one, if existing. For single databases or all in one zip.
    :raises IdNotFoundException: If the file is not found
    :return:
    """
    # _test_backup_neo4j()
    # _test_restore_neo4j()

    if all_databases:
        db_list = [option[0] for option in get_exportable_databases_list()]
    else:
        if database_iri is None:
            raise IdNotFoundException()
        db_list = [database_iri]

    dump_file_names = []
    for db in db_list:
        # TODO: Create dump
        dump_file_names.append("test-file.txt")

    # TODO: zip together...
    zip_file_path = DATABASE_EXPORT_DIRECTORY + "test-file.txt"

    def iterfile():
        with open(zip_file_path, mode="rb") as file_like:
            yield from file_like

    return StreamingResponse(iterfile(), media_type="application/octet-stream")
