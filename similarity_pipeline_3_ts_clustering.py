from datetime import date, datetime, timedelta
import sys
from typing import Dict, List
from tsfresh import extract_features
import pandas as pd
from numpy import nan
import numpy as np
from sklearn.cluster import DBSCAN
from sklearn.decomposition import PCA

import backend.api.python_endpoints.timeseries_endpoints as timeseries_endpoints
from graph_domain.TimeseriesNode import TimeseriesNodeFlat, TimeseriesValueTypes

# #############################################################################
# Timeseries clustering
# #############################################################################
print("\n\n\nSTEP 3: Timeseries clustering\n")

DBSCAN_EPS = 0.3 * (
    10**9
)  # maximum distance between two samples for one to be considered as in the neighborhood of the other
DBSCAN_MIN_SAMPLES = 2  # The number of samples (or total weight) in a neighborhood for a point to be considered as a core point

# Freshly read the nodes with the newest feature vectors
timeseries_nodes_flat: List[
    TimeseriesNodeFlat
] = timeseries_endpoints.get_timeseries_nodes(deep=False)

reduced_feature_lists = [
    ts_node.reduced_feature_list for ts_node in timeseries_nodes_flat
]

# feature_dicts = [ts_node.feature_dict for ts_node in timeseries_nodes_flat]

# # Ignore all nan features (algorithm will fail otherwise)
# for key in timeseries_nodes_flat[0].feature_dict.keys():
#     ts_node: TimeseriesNodeFlat
#     if any(
#         [
#             (True if np.isnan(ts_node.feature_dict[key]) else False)
#             for ts_node in timeseries_nodes_flat
#         ]
#     ):
#         print(f"Removing feature {key} because of NaN occurances...")
#         for f_dict in feature_dicts:
#             f_dict.pop(key)

# # Prepare algorithm input
# feature_lists = [
#     [value for value in f_dict.values()] if f_dict is not None else []
#     for f_dict in feature_dicts
# ]

# Execute the DBSCAN algorithm:
clustering = DBSCAN(eps=DBSCAN_EPS, min_samples=DBSCAN_MIN_SAMPLES).fit(
    reduced_feature_lists
)

cluster_count = max(clustering.labels_) + 1
print("Cluster count: " + str(cluster_count))

clusters = [[] for i in range(cluster_count)]
for i in range(len(timeseries_nodes_flat)):
    if clustering.labels_[i] != -1:
        clusters[clustering.labels_[i]].append(timeseries_nodes_flat[i])

print("Clusters:")
i = 1
for cluster in clusters:
    print(
        f"Cluster: {i}, count: {len(cluster)}: {[ts_node.id_short for ts_node in cluster]}"
    )
    i += 1

pass

print("Adding clusters to KG-DT...")
timeseries_endpoints.reset_ts_clusters()

i = 0
for cluster in clusters:
    cluster_iri = f"www.sintef.no/aas_identifiers/learning_factory/similarity_analysis/timeseries_cluster_{i}"

    timeseries_endpoints.create_ts_cluster(
        id_short=f"timeseries_cluster_{i}",
        iri=cluster_iri,
        description="Node representing a cluster of timeseries inputs",
    )
    # TODO: maybe add mean values of the features
    for ts_node in cluster:
        timeseries_endpoints.add_ts_to_cluster(
            ts_iri=ts_node.iri, cluster_iri=cluster_iri
        )

    i += 1

pass
