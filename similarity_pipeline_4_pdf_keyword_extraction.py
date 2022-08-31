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
import textract
import io
import os
import pke
import pke.unsupervised

from backend.api.python_endpoints import asset_endpoints
from backend.api.python_endpoints import timeseries_endpoints
from backend.api.python_endpoints import file_endpoints
from graph_domain.main_digital_twin.SupplementaryFileNode import (
    SupplementaryFileNodeFlat,
)
from graph_domain.main_digital_twin.SupplementaryFileNode import SupplementaryFileTypes

from graph_domain.main_digital_twin.TimeseriesNode import (
    TimeseriesNodeFlat,
    TimeseriesValueTypes,
)

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

i = 1
for file_node in file_nodes_flat:
    print(f"\nProcessing file {i} of {len(file_nodes_flat)}: {file_node.id_short}")
    print("Loading file...")
    file_stream = file_endpoints.get_supplementary_file_stream(iri=file_node.iri)

    tmp_file_path = "./temporary_pdf.pdf"

    with io.FileIO(tmp_file_path, "w") as tmp_file:
        for pdf_line in file_stream:
            tmp_file.write(pdf_line)

    print("Extracting text from PDF...")
    text_encoded = textract.process(
        tmp_file_path,
        method="tesseract",
        # language="eng",
    )
    # Decode
    text = str(text_encoded, "UTF-8")

    print(f"Extracted text letter-count: {len(text)}")

    # TODO: language detection and translation to english

    print("Saving to KG...")
    file_endpoints.save_extracted_text(file_iri=file_node.iri, text=text)

    print("Deleting temporary file...")
    os.remove(tmp_file_path)

    # print("Processing text: lemmatizing words")

    print("Processing text: Searching most relevant keyphrases from the text...")

    extractor = pke.unsupervised.TopicRank()
    extractor.load_document(text, language="en")

    extractor.candidate_selection()
    extractor.candidate_weighting()
    keyphrases = extractor.get_n_best(n=30)

    # TODO: evtl. nachfiltern (redundanzen entfernen etc.)

    # print("\n TopicRank")
    # print(keyphrases)

    # TODO

    extracted_keywords = [
        keyphrase_score_pair[0] for keyphrase_score_pair in keyphrases
    ]

    print(f"Extracted {len(extracted_keywords)} keywords")

    # Save keywords and relationships to KG
    print("Saving keywords to KG...")
    for keyword in extracted_keywords:
        file_endpoints.add_keyword(file_iri=file_node.iri, keyword=keyword)

    i += 1

pass
