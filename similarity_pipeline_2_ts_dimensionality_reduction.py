from cProfile import label
from datetime import date, datetime, timedelta
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
from graph_domain.TimeseriesNode import TimeseriesNodeFlat, TimeseriesValueTypes

# #############################################################################
# Timeseries dimensionality reduction
# #############################################################################
print("\n\n\nSTEP 2: Timeseries dimensionality reduction\n")

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


pca = PCA(n_components=3)
reduced_feature_lists = pca.fit_transform(feature_lists)

print("Writing to KG-DT...")
i = 0
for timeseries_node in timeseries_nodes_flat:
    timeseries_endpoints.set_ts_reduced_feature_list(
        timeseries_node.iri, list(reduced_feature_lists[i])
    )
    i += 1

pass

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

# produce a legend with the unique colors from the scatter
# legend1 = ax.legend(*scatter.legend_elements(), loc="lower left", title="Classes")
# ax.add_artist(legend1)

# # produce a legend with a cross section of sizes from the scatter

# for i, txt in enumerate(labels):
#     ax.annotate(txt, (x[i], y[i], z[i]))

fig.savefig("scatter-output.png")

pass
