from backend.api.api import app
from backend.knowledge_graph.dao.BaseNodesDao import BaseNodeDao
from backend.knowledge_graph.dao.AssetNodesDao import AssetsDao
import backend.api.python_endpoints.graph_endpoints as python_graph_endpoints

BASE_NODE_DAO: BaseNodeDao = BaseNodeDao.instance()


@app.patch("/node_position")
def update_node_position(iri: str, pos_x: float, pos_y: float):
    python_graph_endpoints.update_node_position(iri, pos_x, pos_y)
