from fastapi.responses import StreamingResponse
from fastapi.responses import RedirectResponse
from fastapi.responses import PlainTextResponse

from backend.api.api import app

from backend.knowledge_graph.dao.DatabaseConnectionsDao import DatabaseConnectionsDao
from backend.knowledge_graph.dao.SupplementaryFileNodesDao import (
    SupplementaryFileNodesDao,
)

import backend.api.python_endpoints.file_endpoints as python_file_endpoints


DB_CON_NODE_DAO: DatabaseConnectionsDao = DatabaseConnectionsDao.instance()
SUPPL_FILE_DAO: SupplementaryFileNodesDao = SupplementaryFileNodesDao.instance()


@app.get("/supplementary_file/data")
def get_supplementary_file(iri: str, proxy_mode: bool = False):
    """
    Reads the specified file from the file storage
    :raises IdNotFoundException: If the file is not found
    :param iri:
    :return:
    """
    if proxy_mode:
        return get_supplementary_file_proxy_mode(iri)
    else:
        return get_supplementary_file_redirect(iri)


@app.get("/supplementary_file/temporary_link")
def get_supplementary_file_temporary_link(iri: str):
    """
    Creates a temporary link to the specified file from the file storage
    :raises IdNotFoundException: If the file is not found
    :param iri:
    :return:
    """
    return PlainTextResponse(
        content=python_file_endpoints.get_supplementary_file_temporary_link(iri)
    )


def get_supplementary_file_proxy_mode(iri: str):

    # Read the actual file:
    file_stream = python_file_endpoints.get_supplementary_file_stream(
        iri=iri,
    )

    if file_stream is None:
        return None

    stream_response = StreamingResponse(
        file_stream.iter_chunks(), media_type="application/octet-stream"
    )

    return stream_response


def get_supplementary_file_redirect(iri: str):
    redirect_url = python_file_endpoints.get_supplementary_file_temporary_link(iri)
    return RedirectResponse(redirect_url)


@app.get("/supplementary_file/details")
def get_supplementary_file_details_flat(iri: str):
    """
    Reads the details (e.g. type and file-name) for a supplementary file from the graph
    :raises IdNotFoundException: If the file is not found
    :param iri:
    :return:
    """
    return python_file_endpoints.get_supplementary_file_details_flat(iri)


@app.get("/supplementary_file/alternative_formats")
def get_supplementary_file_available_formats(iri: str):
    """
    Returns a list of all available format nodes for a supplementary file (works on both secondary and primary ones as input iri)
    :raises IdNotFoundException: If the file is not found
    :param iri:
    :return:
    """
    return python_file_endpoints.get_supplementary_file_available_formats(iri)
