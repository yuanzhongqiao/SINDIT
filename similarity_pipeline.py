import backend.api.python_endpoints.timeseries_endpoints as timeseries_endpoints
from graph_domain.TimeseriesNode import TimeseriesNodeFlat

# #############################################################################
# Connection setup etc
# #############################################################################


# #############################################################################
# Timeseries feature extraction
# #############################################################################

timeseries_nodes_flat = timeseries_endpoints.get_timeseries_nodes(deep=False)

timeseries_node: TimeseriesNodeFlat
for timeseries_node in timeseries_nodes_flat:
    # Note that this can result in very large ranges, if enough data is present!
    ts_range_df = timeseries_endpoints.get_timeseries_range(
        iri=timeseries_node.iri,
        date_time=None,  # forever
        duration=None,  # forever
        aggregation_window_ms=None,  # raw values
    )
    pass

pass

# #############################################################################
# Timeseries dimensionality reduction
# #############################################################################


# #############################################################################
# Timeseries clustering
# #############################################################################
