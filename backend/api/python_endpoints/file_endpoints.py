import json
from datetime import datetime, timedelta
import pandas as pd
from fastapi.responses import StreamingResponse
from fastapi.responses import RedirectResponse
from fastapi.responses import PlainTextResponse

from backend.exceptions.IdNotFoundException import IdNotFoundException
from backend.knowledge_graph.KnowledgeGraphPersistenceService import (
    KnowledgeGraphPersistenceService,
)
from backend.knowledge_graph.dao.DatabaseConnectionsDao import DatabaseConnectionsDao
from backend.knowledge_graph.dao.SupplementaryFileNodesDao import (
    SupplementaryFileNodesDao,
)
from backend.specialized_databases.DatabasePersistenceServiceContainer import (
    DatabasePersistenceServiceContainer,
)
from backend.specialized_databases.files.FilesPersistenceService import (
    FilesPersistenceService,
)
from backend.specialized_databases.timeseries.TimeseriesPersistenceService import (
    TimeseriesPersistenceService,
)
from backend.specialized_databases.timeseries.influx_db.InfluxDbPersistenceService import (
    InfluxDbPersistenceService,
)
from backend.knowledge_graph.dao.AssetNodesDao import AssetsDao
from util.log import logger

DB_CON_NODE_DAO: DatabaseConnectionsDao = DatabaseConnectionsDao.instance()
SUPPL_FILE_DAO: SupplementaryFileNodesDao = SupplementaryFileNodesDao.instance()


def get_supplementary_file_stream(iri: str):
    """
    Reads the specified file from the file storage
    :raises IdNotFoundException: If the file is not found
    :param iri:
    :return:
    """
    try:
        # Get related database service:
        file_con_node: DatabaseConnectionsDao = (
            DB_CON_NODE_DAO.get_database_connection_for_node(iri)
        )

        if file_con_node is None:
            logger.info("File requested, but database connection node does not exist")
            return None

        file_service: FilesPersistenceService = (
            DatabasePersistenceServiceContainer.instance().get_persistence_service(
                file_con_node.iri
            )
        )

        return file_service.stream_file(
            iri=iri,
        )

    except IdNotFoundException:
        return None


def get_supplementary_file_temporary_link(iri: str):
    """
    Creates a temporary link to the specified file from the file storage
    :raises IdNotFoundException: If the file is not found
    :param iri:
    :return:
    """
    try:
        # Get related database service:
        file_con_node: DatabaseConnectionsDao = (
            DB_CON_NODE_DAO.get_database_connection_for_node(iri)
        )

        if file_con_node is None:
            logger.info("File requested, but database connection node does not exist")
            return None

        file_service: FilesPersistenceService = (
            DatabasePersistenceServiceContainer.instance().get_persistence_service(
                file_con_node.iri
            )
        )

        # Create the temporary redirect link:
        redirect_url = file_service.get_temp_file_url(
            iri=iri,
        )

        return redirect_url

    except IdNotFoundException:
        return None


def get_supplementary_file_details_flat(iri: str):
    """
    Reads the details (e.g. type and file-name) for a supplementary file from the graph
    :raises IdNotFoundException: If the file is not found
    :param iri:
    :return:
    """
    return SUPPL_FILE_DAO.get_supplementary_file_node_flat(iri)


def get_supplementary_file_available_formats(iri: str):
    """
    Returns a list of all available format nodes for a supplementary file (works on both secondary and primary ones as input iri)
    :raises IdNotFoundException: If the file is not found
    :param iri:
    :return:
    """
    return SUPPL_FILE_DAO.get_supplementary_file_available_formats(iri)


def get_file_nodes(
    deep: bool = False,
    filter_by_type: bool = False,
    type: str = "",
    exclude_secondary_format_nodes: bool = True,
):
    if deep and not filter_by_type:
        return SUPPL_FILE_DAO.get_file_nodes_deep(exclude_secondary_format_nodes)
    elif not deep and not filter_by_type:
        return SUPPL_FILE_DAO.get_file_nodes_flat(exclude_secondary_format_nodes)
    elif deep and filter_by_type:
        return SUPPL_FILE_DAO.get_file_nodes_deep_by_type(
            type, exclude_secondary_format_nodes
        )
    else:
        return SUPPL_FILE_DAO.get_file_nodes_flat_by_type(
            type, exclude_secondary_format_nodes
        )


def reset_extracted_keywords():
    SUPPL_FILE_DAO.reset_extracted_keywords()


def add_keyword(file_iri: str, keyword: str):
    """Adds the keyword by creating a relationship to the keyword and optionally creating the keyword node,
    if it does not yet exist

    Args:
        file_iri (str): _description_
        keyword (str): _description_
    """
    SUPPL_FILE_DAO.add_keyword(file_iri=file_iri, keyword=keyword)


def save_extracted_properties(file_iri: str, properties_string: str):
    SUPPL_FILE_DAO.save_extracted_properties(
        file_iri=file_iri, properties_string=properties_string
    )


def save_extracted_text(file_iri: str, text: str):
    SUPPL_FILE_DAO.save_extracted_text(file_iri=file_iri, text=text)


def get_keywords_set_for_asset(asset_iri: str):
    return SUPPL_FILE_DAO.get_keywords_set_for_asset(asset_iri=asset_iri)


def reset_dimension_clusters():
    SUPPL_FILE_DAO.reset_dimension_clusters()


def create_dimension_cluster(
    iri: str, id_short: str, description: str | None = None, caption: str | None = None
):
    SUPPL_FILE_DAO.create_dimension_cluster(
        iri=iri, id_short=id_short, description=description, caption=caption
    )


def add_file_to_dimension_cluster(file_iri: str, cluster_iri: str):
    SUPPL_FILE_DAO.add_file_to_dimension_cluster(
        file_iri=file_iri, cluster_iri=cluster_iri
    )
