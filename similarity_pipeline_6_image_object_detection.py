from datetime import date, datetime, timedelta
import sys
from typing import Dict, List
from tsfresh import extract_features
import pandas as pd
from numpy import nan
from numpy import linalg as linalg
import numpy as np
import io
import os
import numpy
from stl import mesh
import torch
from mmdet.apis import init_detector, inference_detector
import mmcv

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
# Image object detection
# #############################################################################
logger.info("\n\n\nSTEP 6: Image object detection\n")

# logger.info(f"CUDA is available: {torch.cuda.is_available()}")


# config_file = "./mm_test/yolov3_mobilenetv2_320_300e_coco.py"
# checkpoint_file = (
#     "./mm_test/yolov3_mobilenetv2_320_300e_coco_20210719_215349-d18dff72.pth"
# )
# model = init_detector(config_file, checkpoint_file, device="cpu")  # or device='cuda:0'
# inference_results = inference_detector(
#     model, "learning_factory_instance/binaries_import/dps_model.jpg"
# )

# logger.info(inference_results)

#
#
#
#############################
# Specify the path to model config and checkpoint file
#############################

# Test 1: trucks and trains...
# config_file = "./dependencies/mmdetection/configs/faster_rcnn/faster_rcnn_x101_64x4d_fpn_1x_coco.py"
# checkpoint_file = (
#     "./mmcv_models/faster_rcnn/faster_rcnn_x101_64x4d_fpn_1x_coco_20200204-833ee192.pth"
# )

# # Test 2: no outputs detected
config_file = (
    "./dependencies/mmdetection/configs/faster_rcnn/faster_rcnn_r50_fpn_1x_coco.py"
)
checkpoint_file = (
    "./mmcv_models/faster_rcnn/faster_rcnn_r50_fpn_1x_coco_20200130-047c8118.pth"
)

# # Test 3:
# config_file = "./dependencies/mmdetection/configs/faster_rcnn/faster_rcnn_x101_64x4d_fpn_1x_coco.py"
# checkpoint_file = (
#     "./mmcv_models/faster_rcnn/faster_rcnn_r50_fpn_1x_coco_20200130-047c8118.pth"
# )

# build the model from a config file and a checkpoint file
model = init_detector(config_file, checkpoint_file, device="cpu")

# test a single image and show the results
img = "./dependencies/mmdetection/demo/demo.jpg"  # or img = mmcv.imread(img), which will only load it once
result = inference_detector(model, img)
# # visualize the results in a new window
# model.show_result(img, result)
# or save the visualization results to image files
model.show_result(img, result, out_file="result.jpg")

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
    type=SupplementaryFileTypes.IMAGE_JPG.value,
    exclude_secondary_format_nodes=False,
)

################################################
logger.info("Detecting objects in picture files...")

i = 1
for file_node in file_nodes_flat:
    logger.info(
        f"\nProcessing file {i} of {len(file_nodes_flat)}: {file_node.id_short}"
    )
    logger.info("Loading file...")
    file_stream = file_endpoints.get_supplementary_file_stream(iri=file_node.iri)

    # tmp_file_path = "./temporary_cad.step"
    tmp_file_path = "./temporary_picture.jpg"

    with io.FileIO(tmp_file_path, "w") as tmp_file:
        for pdf_line in file_stream:
            tmp_file.write(pdf_line)

    logger.info("Detecting objects...")

    result = inference_detector(model, tmp_file_path)
    # # visualize the results in a new window
    # model.show_result(img, result)
    # or save the visualization results to image files
    model.show_result(tmp_file_path, result, out_file="result.jpg")

    pass

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
