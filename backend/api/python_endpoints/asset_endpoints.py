from backend.knowledge_graph.dao.AssetNodesDao import AssetsDao

ASSETS_DAO: AssetsDao = AssetsDao.instance()


def get_asset_nodes(deep: bool = True):
    if deep:
        return ASSETS_DAO.get_assets_deep()
    else:
        return ASSETS_DAO.get_assets_flat()


def add_asset_similarity(
    asset1_iri: str,
    asset2_iri: str,
    similarity_score: float,
):
    ASSETS_DAO.add_asset_similarity(
        asset1_iri=asset1_iri, asset2_iri=asset2_iri, similarity_score=similarity_score
    )


def delete_asset_similarities():
    ASSETS_DAO.delete_asset_similarities()
