from typing import List
from numpy import linalg as linalg
import textract
import io
import os
import pke
import pke.unsupervised
from langdetect import detect
import argostranslate.package
import argostranslate.translate

from backend.api.python_endpoints import asset_endpoints
from backend.api.python_endpoints import file_endpoints
from graph_domain.main_digital_twin.AssetNode import AssetNodeFlat
from graph_domain.main_digital_twin.SupplementaryFileNode import (
    SupplementaryFileNodeFlat,
)
from graph_domain.main_digital_twin.SupplementaryFileNode import SupplementaryFileTypes

from similarity_pipeline.similarity_pipeline_status_manager import (
    SimilarityPipelineStatusManager,
)
from util.log import logger

NUMBER_OF_KEYPHRASES = 30

# #############################################################################
# Text document key-phrase extraction
# #############################################################################
def _translate_if_nescessary(text: str) -> str:
    language = detect(text)
    logger.info(f"Detected language: {language}")
    # Translation
    if language != "en":
        logger.info("Translating to English...")
        text = argostranslate.translate.translate(text, language, "en")

    return text


def _extract_keyphrases(text) -> List[str]:
    logger.info("Processing text: Searching most relevant keyphrases from the text...")

    extractor = pke.unsupervised.TopicRank()
    extractor.load_document(text, language="en")

    extractor.candidate_selection()
    extractor.candidate_weighting()
    keyphrases = extractor.get_n_best(n=NUMBER_OF_KEYPHRASES, stemming=True)

    extracted_keywords = [
        keyphrase_score_pair[0] for keyphrase_score_pair in keyphrases
    ]

    logger.info(f"Extracted {len(extracted_keywords)} keywords")
    return extracted_keywords


def similarity_pipeline_4_text_key_phrase_extraction():
    logger.info("\n\n\nSTEP 4: PDF keyword extraction\n")

    ################################################
    # Download and install Argos Translate package
    logger.info("Download and install Argos Translate package...")
    argostranslate.package.update_package_index()
    available_packages = argostranslate.package.get_available_packages()
    package_to_install = next(
        filter(lambda x: x.from_code == "de" and x.to_code == "en", available_packages)
    )
    argostranslate.package.install_from_path(package_to_install.download())

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
    logger.info("Extracting keywords per PDF file...")

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

        # Translation:
        text = _translate_if_nescessary(text)

        logger.info("Saving extracted text to KG...")
        file_endpoints.save_extracted_text(file_iri=file_node.iri, text=text)

        logger.info("Deleting temporary file...")
        os.remove(tmp_file_path)

        extracted_keywords = _extract_keyphrases(text)

        logger.info(f"Extracted {len(extracted_keywords)} keywords")

        # Save keywords and relationships to KG
        logger.info("Saving keywords to KG...")
        for keyword in extracted_keywords:
            file_endpoints.add_keyword(file_iri=file_node.iri, keyword=keyword)

        i += 1

    # get asset nodes (for descriptions)
    asset_nodes_flat: List[AssetNodeFlat] = asset_endpoints.get_asset_nodes(deep=False)

    ################################################
    logger.info("Extracting keywords for asset descriptions...")

    i = 1
    for asset_node in asset_nodes_flat:
        logger.info(
            f"\nProcessing asset description {i} of {len(asset_nodes_flat)}: {asset_node.id_short}"
        )
        text = asset_node.description

        if text is None or text == "":
            logger.info("Skipped asset: No description")
            continue

        text = _translate_if_nescessary(text)
        extracted_keywords = _extract_keyphrases(text)

        logger.info(f"Extracted {len(extracted_keywords)} keywords")

        # Save keywords and relationships to KG
        logger.info("Saving keywords to KG...")
        for keyword in extracted_keywords:
            asset_endpoints.add_keyword(asset_iri=asset_node.iri, keyword=keyword)

        i += 1

    SimilarityPipelineStatusManager.instance().set_active(
        active=False, stage="text_keyphrase_extraction"
    )
