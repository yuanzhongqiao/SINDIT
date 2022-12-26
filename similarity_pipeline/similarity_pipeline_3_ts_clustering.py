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
from graph_domain.main_digital_twin.TimeseriesNode import (
    TimeseriesNodeFlat,
    TimeseriesValueTypes,
)
from similarity_pipeline.similarity_pipeline_status_manager import (
    SimilarityPipelineStatusManager,
)
from util.log import logger

# #############################################################################
# Timeseries clustering
# #############################################################################
def similarity_pipeline_3_ts_clustering():
    logger.info("\n\n\nSTEP 3: Timeseries clustering\n")

    DBSCAN_EPS = 5  # maximum distance between two samples for one to be considered as in the neighborhood of the other
    DBSCAN_MIN_SAMPLES = 2  # The number of samples (or total weight) in a neighborhood for a point to be considered as a core point

    # Freshly read the nodes with the newest feature vectors
    timeseries_nodes_flat: List[
        TimeseriesNodeFlat
    ] = timeseries_endpoints.get_timeseries_nodes(deep=False)

    # Separate string and non-string time-series
    string_timeseries_nodes_flat = [
        ts_node
        for ts_node in timeseries_nodes_flat
        if ts_node.value_type == TimeseriesValueTypes.STRING.value
    ]
    timeseries_nodes_flat = [
        ts_node
        for ts_node in timeseries_nodes_flat
        if ts_node.value_type != TimeseriesValueTypes.STRING.value
    ]

    # Prepare input
    reduced_feature_lists = [
        ts_node.reduced_feature_list for ts_node in timeseries_nodes_flat
    ]

    logger.info("Resetting current time-series clusters if available...")
    timeseries_endpoints.reset_ts_clusters()

    # Cluster for all incompatible time-series nodes:
    if len(string_timeseries_nodes_flat) > 0:
        logger.info(
            "Adding string-type time-series to separate cluster due to incompability..."
        )
        cluster_iri = f"www.sintef.no/aas_identifiers/learning_factory/similarity_analysis/timeseries_cluster_incompatible_value_type_string"

        timeseries_endpoints.create_ts_cluster(
            id_short=f"timeseries_cluster_incompatible_value_type_string",
            caption=f"Cluster of string-type time-series",
            iri=cluster_iri,
            description="Node representing a cluster of timeseries inputs",
        )
        for ts_node in string_timeseries_nodes_flat:
            timeseries_endpoints.add_ts_to_cluster(
                ts_iri=ts_node.iri, cluster_iri=cluster_iri
            )

    # Execute the DBSCAN algorithm:
    clustering = DBSCAN(eps=DBSCAN_EPS, min_samples=DBSCAN_MIN_SAMPLES).fit(
        reduced_feature_lists
    )

    cluster_count = max(clustering.labels_) + 1
    logger.info("Cluster count: " + str(cluster_count))

    clusters = [[] for i in range(cluster_count)]
    for i in range(len(timeseries_nodes_flat)):
        if clustering.labels_[i] != -1:
            clusters[clustering.labels_[i]].append(timeseries_nodes_flat[i])

    logger.info("Clusters:")
    i = 1
    for cluster in clusters:
        logger.info(
            f"Cluster: {i}, count: {len(cluster)}: {[ts_node.id_short for ts_node in cluster]}"
        )
        i += 1

    pass

    logger.info("Adding clusters to KG-DT...")

    i = 0
    for cluster in clusters:
        cluster_iri = f"www.sintef.no/aas_identifiers/learning_factory/similarity_analysis/timeseries_cluster_{i}"

        timeseries_endpoints.create_ts_cluster(
            id_short=f"timeseries_cluster_{i}",
            caption=f"Time-series cluster: {i}",
            iri=cluster_iri,
            description="Node representing a cluster of timeseries inputs",
        )
        for ts_node in cluster:
            timeseries_endpoints.add_ts_to_cluster(
                ts_iri=ts_node.iri, cluster_iri=cluster_iri
            )

        i += 1

    SimilarityPipelineStatusManager.instance().set_active(
        active=False, stage="time_series_clustering"
    )
