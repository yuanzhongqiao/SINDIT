import json
from backend.api.api import app
from backend.knowledge_graph.dao.AssetNodesDao import AssetsDao

import backend.api.python_endpoints.asset_endpoints as python_asset_endpoints


ASSETS_DAO: AssetsDao = AssetsDao.instance()


@app.get("/assets")
async def get_assets_deep(deep: bool = True):
    if deep:
        return ASSETS_DAO.get_assets_deep_json()
    else:
        return ASSETS_DAO.get_assets_flat_json()


@app.get("/assets/similarities")
async def get_asset_similarities():
    return json.dumps(python_asset_endpoints.get_asset_similarities())


@app.get("/assets/count")
async def get_assets_count():
    return python_asset_endpoints.get_assets_count()
