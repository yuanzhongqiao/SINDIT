from datetime import date, datetime, timedelta
import sys
from typing import Dict, List
from tsfresh import extract_features
import pandas as pd
from numpy import nan
import langdetect
from numpy import linalg as linalg
import numpy as np
import textract
import io
import os
import numpy
import torch
from mmdet.apis import init_detector, inference_detector
import mmcv

# from OCP.Core.GProp import GProp_GProps
# from OCP.Core.BRepGProp import brepgprop_VolumeProperties

from backend.api.python_endpoints import asset_endpoints
from backend.api.python_endpoints import file_endpoints
from graph_domain.main_digital_twin.SupplementaryFileNode import (
    SupplementaryFileNodeFlat,
)
from graph_domain.main_digital_twin.SupplementaryFileNode import SupplementaryFileTypes
from similarity_pipeline.similarity_pipeline_4_text_key_phrase_extraction import (
    _extract_keyphrases,
    _translate_if_nescessary,
)

from similarity_pipeline.similarity_pipeline_status_manager import (
    SimilarityPipelineStatusManager,
)
from util.log import logger

CONFIG_FILE = "./mmdetection/configs/faster_rcnn/faster_rcnn_r50_fpn_1x_coco.py"
CHECKPOINT_FILE = "./mmdetection/checkpoints/faster_rcnn/faster_rcnn_r50_fpn_1x_coco_20200130-047c8118.pth"

CONFIDENCE_THRESHOLD = 0.8

# #############################################################################
# Image object detection
# #############################################################################
def similarity_pipeline_6_image_analysis():
    logger.info("\n\n\nSTEP 6: Image object detection\n")

    model = init_detector(CONFIG_FILE, CHECKPOINT_FILE, device="cpu")

    ################################################
    logger.info("Loading file-nodes...")

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
            for file_line in file_stream:
                tmp_file.write(file_line)

        logger.info("Detecting objects...")

        result = inference_detector(model, tmp_file_path)
        # Save the visualization results to image files
        model.show_result(
            tmp_file_path,
            result,
            out_file=f"./object_detection_outputs/{file_node.id_short}.jpg",
        )

        # Extract detected labels
        detected_labels = set()
        j = 0
        for inf_class in model.CLASSES:
            class_result = result[j]
            if class_result is not None and len(class_result) > 0:
                for bounding_box in class_result:
                    confidence = bounding_box[4]
                    if confidence >= CONFIDENCE_THRESHOLD:
                        detected_labels.add(inf_class)

            j += 1

        # Save key-phrases and relationships to KG
        for keyword in detected_labels:
            file_endpoints.add_keyword(file_iri=file_node.iri, keyword=keyword)

        #######################################
        # OCR text detection:

        logger.info("Extracting text from PDF...")
        text_encoded = textract.process(
            tmp_file_path,
            method="tesseract-ocr",
            # language="eng",
        )
        text = str(text_encoded, "UTF-8")

        # translate:
        try:
            text = _translate_if_nescessary(text)
        except langdetect.lang_detect_exception.LangDetectException:
            pass

        extracted_key_phrases = _extract_keyphrases(text)

        # Save key-phrases and relationships to KG
        for keyword in extracted_key_phrases:
            file_endpoints.add_keyword(file_iri=file_node.iri, keyword=keyword)

        # Cleanup
        logger.info("Deleting temporary file...")
        os.remove(tmp_file_path)

        i += 1

    SimilarityPipelineStatusManager.instance().set_active(
        active=False, stage="image_analysis"
    )
