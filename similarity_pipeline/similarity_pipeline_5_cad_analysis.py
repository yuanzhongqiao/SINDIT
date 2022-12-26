from datetime import date, datetime, timedelta
import json
import sys
from typing import Dict, List
from tsfresh import extract_features
import pandas as pd
from numpy import nan
from numpy import linalg as linalg
import numpy as np
from sklearn.cluster import DBSCAN
from sklearn.preprocessing import StandardScaler
import textract
import io
import os
import pke
import pke.unsupervised
import cadquery
import cqkit
import numpy
import stl

# from OCP.Core.GProp import GProp_GProps
# from OCP.Core.BRepGProp import brepgprop_VolumeProperties

from backend.api.python_endpoints import asset_endpoints
from backend.api.python_endpoints import timeseries_endpoints
from backend.api.python_endpoints import file_endpoints
from graph_domain.main_digital_twin.SupplementaryFileNode import (
    SupplementaryFileNodeDeep,
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

DBSCAN_EPS = 2.5  # maximum distance between two samples for one to be considered as in the neighborhood of the other
DBSCAN_MIN_SAMPLES = 2  # The number of samples (or total weight) in a neighborhood for a point to be considered as a core point


# #############################################################################
# CAD Analysis
# #############################################################################
def similarity_pipeline_5_cad_analysis():
    logger.info("\n\n\nSTEP 5: CAD analysis\n")

    ################################################
    logger.info("Loading file-nodes...")
    main_cad_file_nodes_flat: List[
        SupplementaryFileNodeDeep
    ] = file_endpoints.get_file_nodes(
        deep=True,
        filter_by_type=True,
        type=SupplementaryFileTypes.CAD_STEP.value,
        exclude_secondary_format_nodes=True,
    )

    step_conversion_nodes = [
        [
            sec_format
            for sec_format in step_cad.secondary_formats
            if sec_format.file_type == SupplementaryFileTypes.CAD_STL.value
        ][0]
        for step_cad in main_cad_file_nodes_flat
    ]

    feature_lists = []

    ################################################
    logger.info("Extracting features per CAD file...")

    i = 0
    for main_file_node in main_cad_file_nodes_flat:
        stl_file_node = step_conversion_nodes[i]

        logger.info(
            f"\nProcessing file {i+1} of {len(main_cad_file_nodes_flat)}: {main_file_node.id_short}"
        )
        logger.info("Loading file...")
        file_stream = file_endpoints.get_supplementary_file_stream(
            iri=stl_file_node.iri
        )

        # tmp_file_path = "./temporary_cad.step"
        tmp_file_path = "./temporary_cad.stl"

        with io.FileIO(tmp_file_path, "w") as tmp_file:
            for pdf_line in file_stream:
                tmp_file.write(pdf_line)

        logger.info("Extracting features from CAD...")
        # cad_workplane = cqkit.importers.importStep(tmp_file_path)

        pass

        cad_mesh = stl.mesh.Mesh.from_file(tmp_file_path)
        # Volume
        volume, cog, inertia = cad_mesh.get_mass_properties()
        logger.info("Volume = {0}".format(volume))

        # Height, width, length
        min_x = max_x = min_y = max_y = min_z = max_z = None
        for point in cad_mesh.points:
            # p contains (x, y, z)
            if min_x is None:
                min_x = point[stl.Dimension.X]
                max_x = point[stl.Dimension.X]
                min_y = point[stl.Dimension.Y]
                max_y = point[stl.Dimension.Y]
                min_z = point[stl.Dimension.Z]
                max_z = point[stl.Dimension.Z]
            else:
                max_x = max(point[stl.Dimension.X], max_x)
                min_x = min(point[stl.Dimension.X], min_x)
                max_y = max(point[stl.Dimension.Y], max_y)
                min_y = min(point[stl.Dimension.Y], min_y)
                max_z = max(point[stl.Dimension.Z], max_z)
                min_z = min(point[stl.Dimension.Z], min_z)

        width = max_x - min_x
        height = max_y - min_y
        length = max_z - min_z

        properties_dict = {
            "length": float(length),
            "width": float(width),
            "height": float(height),
            "volume": float(volume),
        }

        feature_lists.append(
            [float(length), float(width), float(height), float(volume)]
        )

        properties_string = json.dumps(properties_dict)

        logger.info("Saving extracted properties to KG...")
        file_endpoints.save_extracted_properties(
            file_iri=main_file_node.iri, properties_string=properties_string
        )

        logger.info("Deleting temporary file...")
        os.remove(tmp_file_path)

        i += 1

    ##################################
    # Standardization and Clustering
    logger.info("Resetting current time-series clusters if available...")
    file_endpoints.reset_dimension_clusters()

    scaler = StandardScaler()
    standardized_feature_lists = scaler.fit_transform(feature_lists)

    clustering = DBSCAN(eps=DBSCAN_EPS, min_samples=DBSCAN_MIN_SAMPLES).fit(
        standardized_feature_lists
    )

    cluster_count = max(clustering.labels_) + 1
    logger.info("Cluster count: " + str(cluster_count))

    clusters = [[] for i in range(cluster_count)]
    for i in range(len(main_cad_file_nodes_flat)):
        if clustering.labels_[i] != -1:
            clusters[clustering.labels_[i]].append(main_cad_file_nodes_flat[i])

    logger.info("Clusters:")
    i = 1
    for cluster in clusters:
        logger.info(
            f"Cluster: {i}, count: {len(cluster)}: {[node.id_short for node in cluster]}"
        )
        i += 1

    logger.info("Adding clusters to KG-DT...")

    i = 0
    for cluster in clusters:
        cluster_iri = f"www.sintef.no/aas_identifiers/learning_factory/similarity_analysis/dimension_cluster_{i}"

        file_endpoints.create_dimension_cluster(
            id_short=f"dimension_cluster_{i}",
            caption=f"Dimension cluster: {i}",
            iri=cluster_iri,
            description="Node representing a cluster of assets in regards to their dimensions.",
        )
        for node in cluster:
            file_endpoints.add_file_to_dimension_cluster(
                file_iri=node.iri, cluster_iri=cluster_iri
            )

        i += 1

    SimilarityPipelineStatusManager.instance().set_active(
        active=False, stage="cad_analysis"
    )
