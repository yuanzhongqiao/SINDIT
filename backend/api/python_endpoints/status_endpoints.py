from datetime import datetime
from backend.api.python_endpoints import asset_endpoints
from backend.api.python_endpoints import timeseries_endpoints
from backend.knowledge_graph.dao.AnnotationNodesDao import AnnotationNodesDao
from backend.knowledge_graph.dao.BaseNodesDao import BaseNodeDao
from backend.knowledge_graph.dao.DatabaseConnectionsDao import DatabaseConnectionsDao
from backend.knowledge_graph.dao.RuntimeConnectionsDao import RuntimeConnectionsDao
from backend.runtime_connections.RuntimeConnectionContainer import (
    RuntimeConnectionContainer,
)
from util.inter_process_cache import memcache

BASE_NODE_DAO: BaseNodeDao = BaseNodeDao.instance()
ANNOTATIONS_DAO: AnnotationNodesDao = AnnotationNodesDao.instance()
DB_CON_DAO: DatabaseConnectionsDao = DatabaseConnectionsDao.instance()
RT_CON_DAO: RuntimeConnectionsDao = RuntimeConnectionsDao.instance()

RT_CON_CONTAINER: RuntimeConnectionContainer = RuntimeConnectionContainer.instance()


def get_system_time():
    return datetime.now().astimezone()


def get_db_connections_count():
    return DB_CON_DAO.get_db_connections_count()


def get_rt_connections_count():
    return RT_CON_DAO.get_rt_connections_count()


def get_rt_active_connections_count():
    return int(memcache.get("active_runtime_connections_count"))


def get_status():
    """Combined status endpoint. Should be preferred to use less API calls.

    Returns:
        _type_: dict
    """
    unconfirmed_detection = (
        ANNOTATIONS_DAO.get_oldest_unconfirmed_detection() is not None
    )

    status_dict = {
        "system_time": get_system_time(),
        "database_connections": get_db_connections_count(),
        "runtime_connections": get_rt_connections_count(),
        "active_runtime_connections": get_rt_active_connections_count(),
        "assets_count": asset_endpoints.get_assets_count(),
        "timeseries_count": timeseries_endpoints.get_timeseries_nodes_count(),
        "unconfirmed_annotation_detection": unconfirmed_detection,
    }

    return status_dict
