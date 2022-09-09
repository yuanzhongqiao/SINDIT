from datetime import datetime
from backend.api.api import app
from backend.knowledge_graph.dao.BaseNodesDao import BaseNodeDao
from backend.knowledge_graph.dao.AssetNodesDao import AssetsDao
import backend.api.python_endpoints.graph_endpoints as python_graph_endpoints
from backend.knowledge_graph.dao.DatabaseConnectionsDao import DatabaseConnectionsDao
from backend.knowledge_graph.dao.RuntimeConnectionsDao import RuntimeConnectionsDao
from backend.runtime_connections.RuntimeConnectionContainer import (
    RuntimeConnectionContainer,
)
from util.environment_and_configuration import ConfigGroups, get_configuration

BASE_NODE_DAO: BaseNodeDao = BaseNodeDao.instance()
DB_CON_DAO: DatabaseConnectionsDao = DatabaseConnectionsDao.instance()
RT_CON_DAO: RuntimeConnectionsDao = RuntimeConnectionsDao.instance()

RT_CON_CONTAINER: RuntimeConnectionContainer = RuntimeConnectionContainer.instance()


@app.get("/system_time")
def get_system_time():
    return datetime.now().astimezone()


@app.get("/database_connections/total_count")
def get_assets_count():
    return DB_CON_DAO.get_db_connections_count()


@app.get("/runtime_connections/total_count")
def get_assets_count():
    return RT_CON_DAO.get_rt_connections_count()


@app.get("/database_connections/active_count")
def get_assets_count():
    return 0  # TODO: implement alive checker


@app.get("/runtime_connections/active_count")
def get_assets_count():
    return RT_CON_CONTAINER.get_active_connections_count()
