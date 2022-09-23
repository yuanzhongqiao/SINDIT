from datetime import datetime
from backend.api.api import app
from backend.knowledge_graph.dao.BaseNodesDao import BaseNodeDao
from backend.knowledge_graph.dao.DatabaseConnectionsDao import DatabaseConnectionsDao
from backend.knowledge_graph.dao.RuntimeConnectionsDao import RuntimeConnectionsDao
from backend.runtime_connections.RuntimeConnectionContainer import (
    RuntimeConnectionContainer,
)
import json
import backend.api.python_endpoints.status_endpoints as python_status_endpoints

BASE_NODE_DAO: BaseNodeDao = BaseNodeDao.instance()
DB_CON_DAO: DatabaseConnectionsDao = DatabaseConnectionsDao.instance()
RT_CON_DAO: RuntimeConnectionsDao = RuntimeConnectionsDao.instance()

RT_CON_CONTAINER: RuntimeConnectionContainer = RuntimeConnectionContainer.instance()


@app.get("/system_time")
async def get_system_time():
    return python_status_endpoints.get_system_time()


@app.get("/database_connections/total_count")
async def get_db_connections_count():
    return python_status_endpoints.get_db_connections_count()


@app.get("/runtime_connections/total_count")
async def get_rt_connections_count():
    return python_status_endpoints.get_rt_connections_count()


@app.get("/runtime_connections/active_count")
async def get_rt_active_connections_count():
    return python_status_endpoints.get_rt_active_connections_count()


@app.get("/status")
async def get_status():
    """Combined status endpoint. Should be preferred to use less API calls.

    Returns:
        _type_: json
    """
    status_dict = python_status_endpoints.get_status()

    return status_dict
