from datetime import date, datetime, timedelta
from tsfresh import extract_features
import pandas as pd
from numpy import nan

import backend.api.python_endpoints.timeseries_endpoints as timeseries_endpoints
from graph_domain.TimeseriesNode import TimeseriesNodeFlat, TimeseriesValueTypes

# #############################################################################
# Connection setup etc
# #############################################################################


# #############################################################################
# Timeseries feature extraction
# #############################################################################

# Restricted comparison time
comparison_end_date_time = datetime(
    year=2022, month=7, day=29, hour=11, minute=0, second=0
)
# comparison_duration = timedelta(hours=20).total_seconds()  # ~ 30 sec per timeseries
comparison_duration = timedelta(hours=12).total_seconds()  # ~ 10 sec per timeseries

# Forever. Huge amount of entries!
# comparison_end_date_time = None
# comparison_duration = None

timeseries_nodes_flat = timeseries_endpoints.get_timeseries_nodes(deep=False)

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
    if timeseries_node.value_type not in [
        TimeseriesValueTypes.DECIMAL.value,
        TimeseriesValueTypes.INT.value,
    ]:
        print(
            f"Feature calculation with normal timeseries libraries not possible: Unsupported type: {timeseries_node.value_type}"
        )

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
    extracted_features.reset_index(inplace=True)
    extracted_features.columns = ["feature_key", "value"]

    pipeline_single_node_end_datetime = datetime.now()
    print(
        f"Timeseries analysis finished at {pipeline_single_node_end_datetime} after {pipeline_single_node_end_datetime - pipeline_single_node_start_datetime}"
    )
    i += 1
    pass

pipeline_end_datetime = datetime.now()

print(
    f"Timeseries analysis finished at {pipeline_end_datetime} after {pipeline_end_datetime - pipeline_start_datetime}"
)

pass

# #############################################################################
# Timeseries dimensionality reduction
# #############################################################################


# #############################################################################
# Timeseries clustering
# #############################################################################
