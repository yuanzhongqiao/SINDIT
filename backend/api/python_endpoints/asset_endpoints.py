from backend.knowledge_graph.dao.AssetNodesDao import AssetsDao

ASSETS_DAO: AssetsDao = AssetsDao.instance()


def get_asset_nodes(deep: bool = True):
    if deep:
        return ASSETS_DAO.get_assets_deep()
    else:
        return ASSETS_DAO.get_assets_flat()


def get_asset_similarities():
    return ASSETS_DAO.get_asset_similarities()


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


def get_assets_count():
    return ASSETS_DAO.get_assets_count()


def add_keyword(asset_iri: str, keyword: str):
    """Adds the keyword by creating a relationship to the keyword and optionally creating the keyword node,
    if it does not yet exist

    Args:
        asset_iri (str): _description_
        keyword (str): _description_
    """
    ASSETS_DAO.add_keyword(asset_iri=asset_iri, keyword=keyword)


def get_keywords_set_for_asset(asset_iri: str):
    return ASSETS_DAO.get_keywords_set_for_asset(asset_iri=asset_iri)
