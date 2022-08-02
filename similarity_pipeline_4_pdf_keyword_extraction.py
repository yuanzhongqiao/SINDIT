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
from backend.api.python_endpoints import file_endpoints
from graph_domain.SupplementaryFileNode import SupplementaryFileNodeFlat
from graph_domain.SupplementaryFileNode import SupplementaryFileTypes

from graph_domain.TimeseriesNode import TimeseriesNodeFlat, TimeseriesValueTypes

# #############################################################################
# PDF keyword extraction
# #############################################################################
print("\n\n\nSTEP 4: PDF keyword extraction\n")

################################################
print("Deleting old PDF keyword relationships...")
file_endpoints.reset_extracted_keywords()

################################################
print("Loading file-nodes...")

# get file nodes flat (just for iris)
file_nodes_flat: List[SupplementaryFileNodeFlat] = file_endpoints.get_file_nodes(
    deep=False, filter_by_type=True, type=SupplementaryFileTypes.DOCUMENT_PDF.value
)


################################################
print("Extracting keywords per file...")

for file_node in file_nodes_flat:
    print(f"\nProcessing file {file_node.id_short}")

    # TODO

    extracted_keywords = ["Test-Keyword"]

    print(f"Extracted {len(extracted_keywords)} keywords")

    # Save keywords and relationships to KG
    for keyword in extracted_keywords:
        file_endpoints.add_keyword(file_iri=file_node.iri, keyword=keyword)

pass
