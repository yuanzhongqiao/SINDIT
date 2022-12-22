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
from similarity_pipeline.similarity_pipeline_status_manager import (
    SimilarityPipelineStatusManager,
)
from util.log import logger

# #############################################################################
# PDF keyword extraction
# #############################################################################
def similarity_pipeline_4_text_key_phrase_extraction():
    logger.info("\n\n\nSTEP 4: PDF keyword extraction\n")

    ################################################
    logger.info("Deleting old PDF keyword relationships...")
    file_endpoints.reset_extracted_keywords()

    ################################################
    logger.info("Loading file-nodes...")

    # get file nodes flat (just for iris)
    file_nodes_flat: List[SupplementaryFileNodeFlat] = file_endpoints.get_file_nodes(
        deep=False, filter_by_type=True, type=SupplementaryFileTypes.DOCUMENT_PDF.value
    )

    ################################################
    logger.info("Extracting keywords per file...")

    i = 1
    for file_node in file_nodes_flat:
        logger.info(
            f"\nProcessing file {i} of {len(file_nodes_flat)}: {file_node.id_short}"
        )
        logger.info("Loading file...")
        file_stream = file_endpoints.get_supplementary_file_stream(iri=file_node.iri)

        tmp_file_path = "./temporary_pdf.pdf"

        with io.FileIO(tmp_file_path, "w") as tmp_file:
            for pdf_line in file_stream:
                tmp_file.write(pdf_line)

        logger.info("Extracting text from PDF...")
        text_encoded = textract.process(
            tmp_file_path,
            method="tesseract",
            # language="eng",
        )
        # Decode
        text = str(text_encoded, "UTF-8")

        logger.info(f"Extracted text letter-count: {len(text)}")

        # TODO: language detection and translation to english

        logger.info("Saving to KG...")
        file_endpoints.save_extracted_text(file_iri=file_node.iri, text=text)

        logger.info("Deleting temporary file...")
        os.remove(tmp_file_path)

        # logger.info("Processing text: lemmatizing words")

        logger.info(
            "Processing text: Searching most relevant keyphrases from the text..."
        )

        extractor = pke.unsupervised.TopicRank()
        extractor.load_document(text, language="en")

        extractor.candidate_selection()
        extractor.candidate_weighting()
        keyphrases = extractor.get_n_best(n=30)

        # TODO: evtl. nachfiltern (redundanzen entfernen etc.)

        # logger.info("\n TopicRank")
        # logger.info(keyphrases)

        # TODO

        extracted_keywords = [
            keyphrase_score_pair[0] for keyphrase_score_pair in keyphrases
        ]

        logger.info(f"Extracted {len(extracted_keywords)} keywords")

        # Save keywords and relationships to KG
        logger.info("Saving keywords to KG...")
        for keyword in extracted_keywords:
            file_endpoints.add_keyword(file_iri=file_node.iri, keyword=keyword)

        i += 1

    SimilarityPipelineStatusManager.instance().set_active(
        active=False, stage="text_keyphrase_extraction"
    )
