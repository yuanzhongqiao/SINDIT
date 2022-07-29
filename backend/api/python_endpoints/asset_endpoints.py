from backend.knowledge_graph.dao.AssetNodesDao import AssetsDao

ASSETS_DAO: AssetsDao = AssetsDao.instance()


def get_assets_deep(deep: bool = True):
    if deep:
        return ASSETS_DAO.get_assets_deep()
    else:
        return ASSETS_DAO.get_assets_flat()
