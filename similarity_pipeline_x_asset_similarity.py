from datetime import date, datetime, timedelta
import sys
from typing import Dict, List
from tsfresh import extract_features
import pandas as pd
from numpy import nan
from numpy import linalg as linalg
import numpy as np
from sklearn.cluster import DBSCAN
from sklearn.decomposition import PCA

from backend.api.python_endpoints import asset_endpoints
from backend.api.python_endpoints import timeseries_endpoints
from graph_domain.TimeseriesNode import TimeseriesNodeFlat, TimeseriesValueTypes

# #############################################################################
# Asset similarity
# #############################################################################
print("\n\n\nSTEP X: Asset similarity\n")

################################################
print("Deleting old asset similarity relationships...")
asset_endpoints.delete_asset_similarities()

################################################
print("Loading assets and related nodes...")

# get assets flat (just for iris)
asset_nodes_flat: List[TimeseriesNodeFlat] = asset_endpoints.get_asset_nodes(deep=False)

# per asset: get connected ts-clusters, keywords... (seperated, so they can be easily weighted differently)
timeseries_clusters = []
for asset_node in asset_nodes_flat:
    timeseries_clusters.append(
        timeseries_endpoints.get_cluster_list_for_asset(asset_iri=asset_node.iri)
    )

################################################
# print("Calculating similarity scores...") TODO

# Between every pair of assets (one direction only)
for i in range(0, len(asset_nodes_flat)):
    for j in range(i + 1, len(asset_nodes_flat)):
        asset1 = asset_nodes_flat[i]
        asset2 = asset_nodes_flat[j]
        ts_clusters1: List = timeseries_clusters[i]
        ts_clusters2: List = timeseries_clusters[j]

        # For timeseries, count multiple occurences multiple times!
        # -> Cosinus similarity
        unique_ts_clusters = list(set(ts_clusters1 + ts_clusters2))

        vector1 = [ts_clusters1.count(cluster) for cluster in unique_ts_clusters]
        vector2 = [ts_clusters2.count(cluster) for cluster in unique_ts_clusters]

        cosine_similarity = round(
            number=float(
                np.dot(vector1, vector2) / (linalg.norm(vector1) * linalg.norm(vector2))
            ),
            ndigits=4,
        )

        # For keywords, use set-based logic
        # -> Jaccard similarity
        # TODO

        print(
            f"Similarity between {asset1.id_short} and {asset2.id_short}:\t{cosine_similarity}"
        )

        # Save similarity relationship
        asset_endpoints.add_asset_similarity(
            asset1_iri=asset1.iri,
            asset2_iri=asset2.iri,
            similarity_score=cosine_similarity,
        )


################################################
# print("Building clusters...") TODO
