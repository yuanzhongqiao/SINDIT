from multiprocessing import Process
from backend.knowledge_graph.dao.AnnotationNodesDao import AnnotationNodesDao
from backend.knowledge_graph.dao.BaseNodesDao import BaseNodeDao
from backend.knowledge_graph.dao.DatabaseConnectionsDao import DatabaseConnectionsDao
from backend.knowledge_graph.dao.RuntimeConnectionsDao import RuntimeConnectionsDao
from backend.runtime_connections.RuntimeConnectionContainer import (
    RuntimeConnectionContainer,
)
from similarity_pipeline.similarity_pipeline_1_ts_feature_extraction import (
    similarity_pipeline_1_ts_feature_extraction,
)
from similarity_pipeline.similarity_pipeline_2_ts_dimensionality_reduction import (
    similarity_pipeline_2_ts_dimensionality_reduction,
)
from similarity_pipeline.similarity_pipeline_3_ts_clustering import (
    similarity_pipeline_3_ts_clustering,
)
from similarity_pipeline.similarity_pipeline_4_text_key_phrase_extraction import (
    similarity_pipeline_4_text_key_phrase_extraction,
)
from similarity_pipeline.similarity_pipeline_5_cad_analysis import similarity_pipeline_5_cad_analysis
from similarity_pipeline.similarity_pipeline_6_image_analysis import similarity_pipeline_6_image_analysis
from similarity_pipeline.similarity_pipeline_7_asset_similarity import similarity_pipeline_7_asset_similarity
from similarity_pipeline.similarity_pipeline_status_manager import (
    SimilarityPipelineStatusManager,
)

BASE_NODE_DAO: BaseNodeDao = BaseNodeDao.instance()
ANNOTATIONS_DAO: AnnotationNodesDao = AnnotationNodesDao.instance()
DB_CON_DAO: DatabaseConnectionsDao = DatabaseConnectionsDao.instance()
RT_CON_DAO: RuntimeConnectionsDao = RuntimeConnectionsDao.instance()

RT_CON_CONTAINER: RuntimeConnectionContainer = RuntimeConnectionContainer.instance()

SIMILARITY_MANAGER = SimilarityPipelineStatusManager.instance()


def get_pipeline_status():
    """Combined status endpoint. Should be preferred to use less API calls.

    Returns:
        _type_: dict
    """

    return SIMILARITY_MANAGER.read_status()


def post_time_series_feature_extraction():
    SIMILARITY_MANAGER.set_active(active=True, stage="time_series_feature_extraction")
    pipeline_process: Process = Process(
        target=similarity_pipeline_1_ts_feature_extraction,
    )
    pipeline_process.start()


def post_time_series_dimensionality_reduction():
    SIMILARITY_MANAGER.set_active(
        active=True, stage="time_series_dimensionality_reduction"
    )
    pipeline_process: Process = Process(
        target=similarity_pipeline_2_ts_dimensionality_reduction,
    )
    pipeline_process.start()


def post_time_series_clustering():
    SIMILARITY_MANAGER.set_active(active=True, stage="time_series_clustering")
    pipeline_process: Process = Process(
        target=similarity_pipeline_3_ts_clustering,
    )
    pipeline_process.start()


def post_text_keyphrase_extraction():
    SIMILARITY_MANAGER.set_active(active=True, stage="text_keyphrase_extraction")
    pipeline_process: Process = Process(
        target=similarity_pipeline_4_text_key_phrase_extraction,
    )
    pipeline_process.start()


def post_cad_analysis():
    SIMILARITY_MANAGER.set_active(active=True, stage="cad_analysis")
    pipeline_process: Process = Process(
        target=similarity_pipeline_5_cad_analysis,
    )
    pipeline_process.start()


def post_image_analysis():
    SIMILARITY_MANAGER.set_active(active=True, stage="image_analysis")
    pipeline_process: Process = Process(
        target=similarity_pipeline_6_image_analysis,
    )
    pipeline_process.start()


def post_asset_similarity():
    SIMILARITY_MANAGER.set_active(active=True, stage="asset_similarity")
    pipeline_process: Process = Process(
        target=similarity_pipeline_7_asset_similarity,
    )
    pipeline_process.start()
