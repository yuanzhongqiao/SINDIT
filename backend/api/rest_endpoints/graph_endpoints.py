from backend.api.api import app
from backend.knowledge_graph.dao.BaseNodesDao import BaseNodeDao
from backend.knowledge_graph.dao.AssetNodesDao import AssetsDao
import backend.api.python_endpoints.graph_endpoints as python_graph_endpoints

BASE_NODE_DAO: BaseNodeDao = BaseNodeDao.instance()


@app.patch("/node_position")
async def update_node_position(iri: str, pos_x: float, pos_y: float):
    python_graph_endpoints.update_node_position(iri, pos_x, pos_y)


@app.get("/node_details")
async def get_node_details(iri: str):

    node = BASE_NODE_DAO.get_generic_node(iri)

    if node is not None:
        return node.to_json()
    else:
        return None
