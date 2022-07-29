from backend.api.api import app
from backend.knowledge_graph.dao.AssetNodesDao import AssetsDao

ASSETS_DAO: AssetsDao = AssetsDao.instance()


@app.get("/assets")
def get_assets_deep(deep: bool = True):
    if deep:
        return ASSETS_DAO.get_assets_deep_json()
    else:
        return ASSETS_DAO.get_assets_flat()
