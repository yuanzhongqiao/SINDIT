from cProfile import label
from datetime import date, datetime, timedelta
from sklearn.preprocessing import StandardScaler
import sys
from typing import Dict, List
from tsfresh import extract_features
import pandas as pd
from numpy import nan
import numpy as np
from sklearn.cluster import DBSCAN
from sklearn.decomposition import PCA
import matplotlib.pyplot as plt

import backend.api.python_endpoints.timeseries_endpoints as timeseries_endpoints
from graph_domain.main_digital_twin.TimeseriesNode import (
    TimeseriesNodeFlat,
    TimeseriesValueTypes,
)
from similarity_pipeline.similarity_pipeline_status_manager import (
    SimilarityPipelineStatusManager,
)
from util.log import logger

N_COMPONENTS = 3

# #############################################################################
# Timeseries dimensionality reduction
# #############################################################################
def similarity_pipeline_2_ts_dimensionality_reduction():

    logger.info("\n\n\nSTEP 2: Timeseries dimensionality reduction\n")

    # Freshly read the nodes with the newest feature vectors
    timeseries_nodes_flat: List[
        TimeseriesNodeFlat
    ] = timeseries_endpoints.get_timeseries_nodes(deep=False)

    # Reset values for string time-series if still present (legacy)
    string_timeseries_nodes_flat = [
        ts_node
        for ts_node in timeseries_nodes_flat
        if ts_node.value_type == TimeseriesValueTypes.STRING.value
    ]
    for ts_node in string_timeseries_nodes_flat:
        timeseries_endpoints.set_ts_reduced_feature_list(ts_node.iri, None)

    # Filter out all time-series with string type -> they do note have extracted features because of incompability:
    timeseries_nodes_flat = [
        ts_node
        for ts_node in timeseries_nodes_flat
        if ts_node.value_type != TimeseriesValueTypes.STRING.value
    ]

    feature_dicts = [ts_node.feature_dict for ts_node in timeseries_nodes_flat]

    feature_keys_list = list(timeseries_nodes_flat[0].feature_dict.keys())

    # Ignore all nan features (algorithm will fail otherwise)
    for key in feature_keys_list:
        ts_node: TimeseriesNodeFlat
        if any(
            [
                (True if np.isnan(ts_node.feature_dict[key]) else False)
                for ts_node in timeseries_nodes_flat
            ]
        ):
            logger.info(f"Removing feature {key} because of NaN occurances...")
            for f_dict in feature_dicts:
                f_dict.pop(key)

    # Update feature keys to included ones
    feature_keys_list = list(feature_dicts[0].keys())

    # Prepare algorithm input
    feature_lists = [
        [f_dict.get(key) for key in feature_keys_list] if f_dict is not None else []
        for f_dict in feature_dicts
    ]

    # Some statistics emphasizing why Standardization is required here:
    values_per_feature = [[] for feature in feature_lists[0]]

    for feature_list in feature_lists:
        i = 0
        for feature in feature_list:
            values_per_feature[i].append(feature)
            i += 1

    minimal_max_range = (
        min(values_per_feature[0]),
        max(values_per_feature[0]),
        max(values_per_feature[0]) - min(values_per_feature[0]),
    )
    minimal_max_range_id = feature_keys_list[0]
    maximum_max_range = (
        min(values_per_feature[0]),
        max(values_per_feature[0]),
        max(values_per_feature[0]) - min(values_per_feature[0]),
    )
    maximum_max_range_id = feature_keys_list[0]
    i = 0
    for key in feature_keys_list[0:-5]:
        minimum = min(values_per_feature[i])
        maximum = max(values_per_feature[i])
        range = maximum - minimum

        if range < minimal_max_range[2]:
            minimal_max_range = minimum, maximum, range
            minimal_max_range_id = key

        if range > maximum_max_range[2]:
            maximum_max_range = minimum, maximum, range
            maximum_max_range_id = key

        i += 1

    logger.info("Feature value range extremes (besides unit-associations):")
    logger.info(minimal_max_range_id)
    logger.info(
        f"Min: {minimal_max_range[0]}, Max: {minimal_max_range[1]}, Range: {minimal_max_range[2]}"
    )
    logger.info(maximum_max_range_id)
    logger.info(
        f"Min: {maximum_max_range[0]}, Max: {maximum_max_range[1]}, Range: {maximum_max_range[2]}"
    )

    # Standardize the input
    logger.info("Standardizing the input...")
    scaler = StandardScaler()
    standardized_feature_lists = scaler.fit_transform(feature_lists)

    # Calculate the PCA
    logger.info("Running the PCA...")
    pca = PCA(n_components=N_COMPONENTS)
    reduced_feature_lists = pca.fit_transform(standardized_feature_lists)

    print(pca.explained_variance_ratio_)

    cumsum_array = np.cumsum(pca.explained_variance_ratio_)
    cumsum_string = ""
    i = 1
    for cumsum in cumsum_array:
        cumsum_string = cumsum_string + f"({i}, {cumsum})"
        i += 1

    logger.info("Cumulative scree plot values:")
    logger.info(cumsum_string)

    logger.info("Writing to KG-DT...")
    i = 0
    for timeseries_node in timeseries_nodes_flat:
        timeseries_endpoints.set_ts_reduced_feature_list(
            timeseries_node.iri, list(reduced_feature_lists[i])
        )
        i += 1

    # Visualization:
    x = [red_features[0] for red_features in reduced_feature_lists]
    y = [red_features[1] for red_features in reduced_feature_lists]

    if len(list(reduced_feature_lists[0])) == 3:
        z = [red_features[2] for red_features in reduced_feature_lists]
    else:
        z = [0 for red_features in reduced_feature_lists]

    labels = [ts_node.id_short for ts_node in timeseries_nodes_flat]

    fig = plt.figure()

    ax = fig.add_subplot(projection="3d")

    scatter = ax.scatter(x, y, z, label=labels)

    fig.savefig("scatter-output.png")

    SimilarityPipelineStatusManager.instance().set_active(
        active=False, stage="time_series_dimensionality_reduction"
    )
