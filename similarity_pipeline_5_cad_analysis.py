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
import cadquery
import cqkit
import numpy
from stl import mesh

# from OCP.Core.GProp import GProp_GProps
# from OCP.Core.BRepGProp import brepgprop_VolumeProperties

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
from util.log import logger

# #############################################################################
# CAD Analysis
# #############################################################################
logger.info("\n\n\nSTEP 5: CAD analysis\n")

################################################
# logger.info("Deleting previosly calculated features...")
# file_endpoints.reset_extracted_keywords()
# TODO

################################################
logger.info("Loading file-nodes...")

# get file nodes flat (just for iris)
# file_nodes_flat: List[SupplementaryFileNodeFlat] = file_endpoints.get_file_nodes(
#     deep=False, filter_by_type=True, type=SupplementaryFileTypes.CAD_STEP.value
# )
file_nodes_flat: List[SupplementaryFileNodeFlat] = file_endpoints.get_file_nodes(
    deep=False,
    filter_by_type=True,
    type=SupplementaryFileTypes.CAD_STL.value,
    exclude_secondary_format_nodes=False,
)

################################################
logger.info("Extracting features per CAD file...")

i = 1
for file_node in file_nodes_flat:
    logger.info(
        f"\nProcessing file {i} of {len(file_nodes_flat)}: {file_node.id_short}"
    )
    logger.info("Loading file...")
    file_stream = file_endpoints.get_supplementary_file_stream(iri=file_node.iri)

    # tmp_file_path = "./temporary_cad.step"
    tmp_file_path = "./temporary_cad.stl"

    with io.FileIO(tmp_file_path, "w") as tmp_file:
        for pdf_line in file_stream:
            tmp_file.write(pdf_line)

    logger.info("Extracting features from CAD...")
    # cad_workplane = cqkit.importers.importStep(tmp_file_path)

    pass

    your_mesh = mesh.Mesh.from_file(tmp_file_path)
    volume, cog, inertia = your_mesh.get_mass_properties()
    logger.info("Volume = {0}".format(volume))

    # prop = GProp_GProps()
    # tolerance = 1e-5  # Adjust to your liking
    # volume = brepgprop_VolumeProperties(cad_workplane, prop, tolerance)
    # logger.info(volume)

    pass

    # logger.info("Saving to KG...")
    # file_endpoints.save_extracted_text(file_iri=file_node.iri, text=text)
    # TODO

    logger.info("Deleting temporary file...")
    os.remove(tmp_file_path)

    # logger.info("Processing text: Searching most relevant keyphrases from the text...")

    # extractor = pke.unsupervised.TopicRank()
    # extractor.load_document(text, language="en")

    # extractor.candidate_selection()
    # extractor.candidate_weighting()
    # keyphrases = extractor.get_n_best(n=30)

    # TODO: evtl. nachfiltern (redundanzen entfernen etc.)

    # logger.info("\n TopicRank")
    # logger.info(keyphrases)

    # TODO

    # extracted_keywords = [
    #     keyphrase_score_pair[0] for keyphrase_score_pair in keyphrases
    # ]

    # logger.info(f"Extracted {len(extracted_keywords)} keywords")

    # # Save keywords and relationships to KG
    # logger.info("Saving keywords to KG...")
    # for keyword in extracted_keywords:
    #     file_endpoints.add_keyword(file_iri=file_node.iri, keyword=keyword)

    i += 1

pass
