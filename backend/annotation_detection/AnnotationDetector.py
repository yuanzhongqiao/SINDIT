from __future__ import annotations
import abc
from re import A
from threading import Thread
import time
from typing import Dict, List
from backend.exceptions.EnvironmentalVariableNotFoundError import (
    EnvironmentalVariableNotFoundError,
)
from backend.knowledge_graph.dao.BaseNodesDao import BaseNodeDao
from backend.knowledge_graph.dao.TimeseriesNodesDao import TimeseriesNodesDao
from backend.specialized_databases.DatabasePersistenceServiceContainer import (
    DatabasePersistenceServiceContainer,
)
from backend.specialized_databases.SpecializedDatabasePersistenceService import (
    SpecializedDatabasePersistenceService,
)
from graph_domain.expert_annotations.AnnotationInstanceNode import (
    AnnotationInstanceNodeFlat,
)
from graph_domain.main_digital_twin.AssetNode import AssetNodeDeep, AssetNodeFlat
from util.environment_and_configuration import (
    ConfigGroups,
    get_configuration,
)
from dateutil import tz
from backend.knowledge_graph.dao.AnnotationNodesDao import AnnotationNodesDao
from datetime import datetime, timedelta
from graph_domain.main_digital_twin.RuntimeConnectionNode import RuntimeConnectionNode
from backend.runtime_connections.TimeseriesInput import TimeseriesInput
from util.environment_and_configuration import (
    get_environment_variable,
    get_environment_variable_int,
)
from util.log import logger


DATETIME_STRF_FORMAT_CAPTION = "%d.%m.%Y, %H:%M:%S"
DATETIME_STRF_FORMAT_ID = "%Y_%m_%d_%H_%M_%S_%f"


class AnnotationDetector:
    """
    Annotation detector scanning the related time-series inputs of one asset for occurances of a annotation instance
    """

    def __init__(
        self,
        scanned_timeseries_iris: Dict[str, str],
        scanned_asset: AssetNodeFlat,
        scanned_annotation_instance: AnnotationInstanceNodeFlat,
        persistence_services: Dict[str, SpecializedDatabasePersistenceService],
    ) -> None:

        self.active = False
        self.stop_signal = False

        # Dict: annotated ts iri -> scanned ts iri
        self.scanned_timeseries_iris: Dict[str, str] = scanned_timeseries_iris
        self.scanned_asset: AssetNodeFlat = scanned_asset
        self.scanned_annotation_instance: AnnotationInstanceNodeFlat = (
            scanned_annotation_instance
        )
        # Connections
        self.annotations_dao: AnnotationNodesDao = AnnotationNodesDao.instance()
        self.persistence_services = persistence_services
        # Scanner thread:
        self.detector_thread = Thread(target=self._detector_loop)
        # Get original timeseries excerpt:
        self.original_ts_range = None  # TODO

    def _detector_loop(self):
        while not self.stop_signal:
            logger.info(
                f"Scanning {self.scanned_asset.caption} for occurances of {self.scanned_annotation_instance.caption}"
            )
            self.active = True
            time.sleep(20)

    @classmethod
    def from_annotation_instance_and_asset(cls, instance_iri: str, asset_iri: str):

        basenode_dao = BaseNodeDao.instance()
        timeseries_dao = TimeseriesNodesDao.instance()
        annotations_dao = AnnotationNodesDao.instance()

        instance: AnnotationInstanceNodeFlat = basenode_dao.get_generic_node(
            instance_iri
        )

        asset: AssetNodeFlat = basenode_dao.get_generic_node(asset_iri)

        asset_ts_iris = [
            ts.iri for ts in timeseries_dao.get_timeseries_of_asset(asset_iri)
        ]
        matched_ts_dict: Dict[str, str] = dict()
        for matcher in annotations_dao.get_matchers_for_annotation_instance(
            instance_iri
        ):
            matched_ts_dict[
                annotations_dao.get_matcher_original_annotated_ts(matcher.iri).iri
            ] = [
                ts.iri
                for ts in annotations_dao.get_matched_ts_for_matcher(matcher.iri)
                if ts.iri in asset_ts_iris
            ].pop()

        all_relevant_ts_iris = set(matched_ts_dict.keys()).union(
            set(matched_ts_dict.values())
        )

        persistence_services_per_ts: Dict[
            str, SpecializedDatabasePersistenceService
        ] = dict()

        for ts_iri in all_relevant_ts_iris:
            persistence_services_per_ts[
                ts_iri
            ] = DatabasePersistenceServiceContainer.instance().get_persistence_service(
                ts_iri
            )

        return cls(
            scanned_timeseries_iris=matched_ts_dict,
            scanned_asset=asset,
            scanned_annotation_instance=instance,
            persistence_services=persistence_services_per_ts,
        )

    def start_detection(self):
        logger.info(
            f"Starting detection of {self.scanned_annotation_instance.caption} on {self.scanned_asset.caption}"
        )
        self.stop_signal = False
        self.detector_thread.start()

    def stop_detection(self):
        logger.info(
            f"Stopping detection of {self.scanned_annotation_instance.caption} on {self.scanned_asset.caption}"
        )
        self.stop_signal = True
        self.detector_thread.join()
        self.active = False

    def is_active(self) -> bool:
        return self.active

    def _create_new_detection(self, start_date_time: datetime, end_date_time: datetime):

        id_short = (
            f"detection_of_{self.scanned_annotation_instance.id_short}_on_"
            f"{self.scanned_asset.caption}_at_{end_date_time.strftime(DATETIME_STRF_FORMAT_ID)}"
        )
        caption = (
            f"Detection of {self.scanned_annotation_instance.caption} on "
            f"{self.scanned_asset.caption} at {end_date_time.strftime(DATETIME_STRF_FORMAT_CAPTION)}"
        )

        detection_iri = self.annotations_dao.create_annotation_detection(
            id_short=id_short,
            start_datetime=start_date_time,
            end_datetime=end_date_time,
            caption=caption,
        )

        # Relationships to the scanned timeseries:
        for matched_ts_iri in self.scanned_timeseries_iris.values():
            self.annotations_dao.create_annotation_detection_timeseries_relationship(
                detection_iri=detection_iri,
                timeseries_iri=matched_ts_iri,
            )

        # Relationship to the scanned asset:
        self.annotations_dao.create_annotation_detection_asset_relationship(
            detection_iri=detection_iri,
            asset_iri=self.scanned_asset.iri,
        )

        # Relationship to the matched instance
        self.annotations_dao.create_annotation_detection_instance_relationship(
            detection_iri=detection_iri,
            instance_iri=self.scanned_annotation_instance.iri,
        )
