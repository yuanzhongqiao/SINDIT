from backend.knowledge_graph.dao.BaseNodesDao import BaseNodeDao
from backend.knowledge_graph.dao.AssetNodesDao import AssetsDao

BASE_NODE_DAO: BaseNodeDao = BaseNodeDao.instance()


def update_node_position(iri: str, pos_x: float, pos_y: float):
    BASE_NODE_DAO.update_node_position(iri=iri, new_pos_x=pos_x, new_pos_y=pos_y)
