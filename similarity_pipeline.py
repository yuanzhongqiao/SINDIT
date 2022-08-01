from datetime import date, datetime, timedelta
import sys
from typing import Dict, List
from tsfresh import extract_features
import pandas as pd
from numpy import nan
import numpy as np
from sklearn.cluster import DBSCAN

import backend.api.python_endpoints.timeseries_endpoints as timeseries_endpoints
from graph_domain.TimeseriesNode import TimeseriesNodeFlat, TimeseriesValueTypes

# #############################################################################
# Connection setup etc
# #############################################################################


# #############################################################################
# Timeseries feature extraction
# #############################################################################
# print("\n\n\nSTEP 1: Timeseries feature extraction\n")

# # Restricted comparison time
# comparison_end_date_time = datetime(
#     year=2022, month=7, day=29, hour=11, minute=0, second=0
# )
# comparison_duration = timedelta(hours=20).total_seconds()  # ~ 30 sec per timeseries

# # comparison_duration = timedelta(hours=12).total_seconds()  # ~ 10 sec per timeseries

# # Fast testing:
# # comparison_duration = timedelta(minutes=10).total_seconds()

# # carful! to short durations lead to nan values for some features. This is afterwards not supported by DBSCAN

# # Forever. Huge amount of entries!
# # comparison_end_date_time = None
# # comparison_duration = None

# timeseries_nodes_flat = timeseries_endpoints.get_timeseries_nodes(deep=False)

# # Get empty feature set to be applied to all not compatible TS:
# test_ts_dataframe = pd.DataFrame(columns=["time", "value"], data=[[0, 1], [1, 2]])

# # Add id row that is required by tsfresh
# test_ts_dataframe.insert(loc=0, column="id", value=0)

# print("Finished loading dataframe. Extracting features...")
# extracted_test_features: pd.DataFrame = extract_features(
#     test_ts_dataframe, column_id="id", column_sort="time", column_value="value"
# )
# extracted_test_features = extracted_test_features.transpose()
# empty_feature_dict = extracted_test_features.to_dict()[0]
# for key in empty_feature_dict.keys():
#     empty_feature_dict[key] = sys.maxsize
#     # pseudo value to build a cluster of not supported TS
#     # TODO: to be reimplemented later

# i = 1
# pipeline_start_datetime = datetime.now()
# print(f"Timeseries analysis started at {pipeline_start_datetime}")
# timeseries_node: TimeseriesNodeFlat
# for timeseries_node in timeseries_nodes_flat:
#     pipeline_single_node_start_datetime = datetime.now()

#     print(
#         f"\n\nAnalyzing timeseries {i} of {len(timeseries_nodes_flat)}: {timeseries_node.id_short}"
#     )
#     # Note that this can result in very large ranges, if enough data is present!
#     ts_entry_count = timeseries_endpoints.get_timeseries_entries_count(
#         iri=timeseries_node.iri,
#         date_time=comparison_end_date_time,
#         duration=comparison_duration,
#     )
#     print(f"Total entry count: {ts_entry_count}")

#     # Cancel, if not int or float
#     if timeseries_node.value_type in [
#         TimeseriesValueTypes.DECIMAL.value,
#         TimeseriesValueTypes.INT.value,
#     ]:
#         print("Loading dataframe...")
#         ts_range_df = timeseries_endpoints.get_timeseries_range(
#             iri=timeseries_node.iri,
#             date_time=comparison_end_date_time,
#             duration=comparison_duration,
#             aggregation_window_ms=None,  # raw values
#         )

#         # Add id row that is required by tsfresh
#         ts_range_df.insert(loc=0, column="id", value=0)

#         print("Finished loading dataframe. Extracting features...")
#         extracted_features: pd.DataFrame = extract_features(
#             ts_range_df, column_id="id", column_sort="time", column_value="value"
#         )
#         extracted_features = extracted_features.transpose()
#         feature_dict = extracted_features.to_dict()[0]
#         # extracted_features.reset_index(inplace=True)
#         # extracted_features.columns = ["feature_key", "value"]
#     else:
#         print(
#             f"Feature calculation with normal timeseries libraries not possible: Unsupported type: {timeseries_node.value_type}"
#         )
#         print("Applying empty feature dict...")
#         feature_dict = empty_feature_dict

#     pipeline_single_node_end_datetime = datetime.now()
#     print(
#         f"Timeseries analysis finished at {pipeline_single_node_end_datetime} after {pipeline_single_node_end_datetime - pipeline_single_node_start_datetime}"
#     )

#     print("Writing to KG-DT...")
#     timeseries_endpoints.set_ts_feature_set(timeseries_node.iri, feature_dict)

#     i += 1
#     pass

# pipeline_end_datetime = datetime.now()

# print(
#     f"Timeseries analysis finished at {pipeline_end_datetime} after {pipeline_end_datetime - pipeline_start_datetime}"
# )

# pass

# #############################################################################
# Timeseries dimensionality reduction
# #############################################################################
print("\n\n\nSTEP 2: Timeseries dimensionality reduction\n")

print("not yet implemented...")
# TODO

# #############################################################################
# Timeseries clustering
# #############################################################################
print("\n\n\nSTEP 3: Timeseries clustering\n")

DBSCAN_EPS = 0.3  # maximum distance between two samples for one to be considered as in the neighborhood of the other
DBSCAN_MIN_SAMPLES = 2  # The number of samples (or total weight) in a neighborhood for a point to be considered as a core point

# Freshly read the nodes with the newest feature vectors
timeseries_nodes_flat: List[
    TimeseriesNodeFlat
] = timeseries_endpoints.get_timeseries_nodes(deep=False)

feature_dicts = [ts_node.feature_dict for ts_node in timeseries_nodes_flat]

# Ignore all nan features (algorithm will fail otherwise)
for key in timeseries_nodes_flat[0].feature_dict.keys():
    ts_node: TimeseriesNodeFlat
    if any(
        [
            (True if np.isnan(ts_node.feature_dict[key]) else False)
            for ts_node in timeseries_nodes_flat
        ]
    ):
        print(f"Removing feature {key} because of NaN occurances...")
        for f_dict in feature_dicts:
            f_dict.pop(key)

# Prepare algorithm input
feature_lists = [
    [value for value in f_dict.values()] if f_dict is not None else []
    for f_dict in feature_dicts
]

# Execute the DBSCAN algorithm:
clustering = DBSCAN(eps=DBSCAN_EPS, min_samples=DBSCAN_MIN_SAMPLES).fit(feature_lists)

cluster_count = max(clustering.labels_) + 1
print("Cluster count: " + str(cluster_count))

clusters = [[] for i in range(cluster_count)]
for i in range(len(timeseries_nodes_flat)):
    if clustering.labels_[i] != -1:
        clusters[clustering.labels_[i]].append(timeseries_nodes_flat[i])

print(f"Clusters: {clusters}")
pass
# clusters
