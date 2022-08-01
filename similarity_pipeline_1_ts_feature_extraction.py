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
# Timeseries feature extraction
# #############################################################################
print("\n\n\nSTEP 1: Timeseries feature extraction\n")

# Restricted comparison time
comparison_end_date_time = datetime(
    year=2022, month=7, day=29, hour=11, minute=0, second=0
)
comparison_duration = timedelta(hours=20).total_seconds()  # ~ 30 sec per timeseries

# comparison_duration = timedelta(hours=12).total_seconds()  # ~ 10 sec per timeseries

# Fast testing:
# comparison_duration = timedelta(minutes=10).total_seconds()

# carful! to short durations lead to nan values for some features. This is afterwards not supported by DBSCAN

# Forever. Huge amount of entries!
# comparison_end_date_time = None
# comparison_duration = None

timeseries_nodes_flat = timeseries_endpoints.get_timeseries_nodes(deep=False)

# Get empty feature set to be applied to all not compatible TS:
test_ts_dataframe = pd.DataFrame(columns=["time", "value"], data=[[0, 1], [1, 2]])

# Add id row that is required by tsfresh
test_ts_dataframe.insert(loc=0, column="id", value=0)

print("Finished loading dataframe. Extracting features...")
extracted_test_features: pd.DataFrame = extract_features(
    test_ts_dataframe, column_id="id", column_sort="time", column_value="value"
)
extracted_test_features = extracted_test_features.transpose()
empty_feature_dict = extracted_test_features.to_dict()[0]
for key in empty_feature_dict.keys():
    empty_feature_dict[key] = sys.maxsize
    # pseudo value to build a cluster of not supported TS
    # TODO: to be reimplemented later

i = 1
pipeline_start_datetime = datetime.now()
print(f"Timeseries analysis started at {pipeline_start_datetime}")
timeseries_node: TimeseriesNodeFlat
for timeseries_node in timeseries_nodes_flat:
    pipeline_single_node_start_datetime = datetime.now()

    print(
        f"\n\nAnalyzing timeseries {i} of {len(timeseries_nodes_flat)}: {timeseries_node.id_short}"
    )
    # Note that this can result in very large ranges, if enough data is present!
    ts_entry_count = timeseries_endpoints.get_timeseries_entries_count(
        iri=timeseries_node.iri,
        date_time=comparison_end_date_time,
        duration=comparison_duration,
    )
    print(f"Total entry count: {ts_entry_count}")

    # Cancel, if not int or float
    if timeseries_node.value_type in [
        TimeseriesValueTypes.DECIMAL.value,
        TimeseriesValueTypes.INT.value,
    ]:
        print("Loading dataframe...")
        ts_range_df = timeseries_endpoints.get_timeseries_range(
            iri=timeseries_node.iri,
            date_time=comparison_end_date_time,
            duration=comparison_duration,
            aggregation_window_ms=None,  # raw values
        )

        # Add id row that is required by tsfresh
        ts_range_df.insert(loc=0, column="id", value=0)

        print("Finished loading dataframe. Extracting features...")
        extracted_features: pd.DataFrame = extract_features(
            ts_range_df, column_id="id", column_sort="time", column_value="value"
        )
        extracted_features = extracted_features.transpose()
        feature_dict = extracted_features.to_dict()[0]
        # extracted_features.reset_index(inplace=True)
        # extracted_features.columns = ["feature_key", "value"]
    else:
        print(
            f"Feature calculation with normal timeseries libraries not possible: Unsupported type: {timeseries_node.value_type}"
        )
        print("Applying empty feature dict...")
        feature_dict = empty_feature_dict

    pipeline_single_node_end_datetime = datetime.now()
    print(
        f"Timeseries analysis finished at {pipeline_single_node_end_datetime} after {pipeline_single_node_end_datetime - pipeline_single_node_start_datetime}"
    )

    print("Writing to KG-DT...")
    timeseries_endpoints.set_ts_feature_dict(timeseries_node.iri, feature_dict)

    i += 1
    pass

pipeline_end_datetime = datetime.now()

print(
    f"Timeseries analysis finished at {pipeline_end_datetime} after {pipeline_end_datetime - pipeline_start_datetime}"
)

pass
