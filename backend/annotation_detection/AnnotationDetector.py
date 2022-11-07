from __future__ import annotations
from multiprocessing import Queue, Process
import abc
from queue import Empty
from re import A
from threading import Thread
import time
import numpy as np
from typing import Dict, List
from backend.exceptions.EnvironmentalVariableNotFoundError import (
    EnvironmentalVariableNotFoundError,
)
from backend.knowledge_graph.dao.BaseNodesDao import BaseNodeDao
from backend.knowledge_graph.dao.TimeseriesNodesDao import TimeseriesNodesDao
from backend.runtime_connections.RuntimeConnectionContainer import (
    RuntimeConnectionContainer,
)
from backend.api.python_endpoints import timeseries_endpoints
import pandas as pd
from backend.specialized_databases.DatabasePersistenceServiceContainer import (
    DatabasePersistenceServiceContainer,
)
from backend.specialized_databases.SpecializedDatabasePersistenceService import (
    SpecializedDatabasePersistenceService,
)
from backend.specialized_databases.timeseries.TimeseriesPersistenceService import (
    TimeseriesPersistenceService,
)
from graph_domain.expert_annotations.AnnotationInstanceNode import (
    AnnotationInstanceNodeFlat,
)
from graph_domain.expert_annotations.AnnotationTimeseriesMatcherNode import (
    AnnotationTimeseriesMatcherNodeDeep,
    AnnotationTimeseriesMatcherNodeFlat,
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


class AnnotationDetector(abc.ABC):
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
        self.last_detection_timestamp = datetime.fromtimestamp(0).astimezone(
            tz.gettz(get_configuration(group=ConfigGroups.FRONTEND, key="timezone"))
        )

        # Dict: annotated ts iri -> scanned ts iri
        self.scanned_timeseries_iris: Dict[str, str] = scanned_timeseries_iris
        self.scanned_asset: AssetNodeFlat = scanned_asset
        self.scanned_annotation_instance: AnnotationInstanceNodeFlat = (
            scanned_annotation_instance
        )
        self.input_handler_id = (
            f"detector_{self.scanned_asset.iri}_{self.scanned_annotation_instance.iri}"
        )
        # Connections
        self.annotations_dao: AnnotationNodesDao = AnnotationNodesDao.instance()
        self.persistence_services = persistence_services

        # Get original timeseries excerpt:
        self.original_ts_dataframes: Dict[str, pd.DataFrame] = dict()
        for ts_iri in self.scanned_timeseries_iris.keys():
            service: TimeseriesPersistenceService = self.persistence_services.get(
                ts_iri
            )
            dataframe = service.read_period_to_dataframe(
                iri=ts_iri,
                begin_time=self.scanned_annotation_instance.occurance_start_date_time,
                end_time=self.scanned_annotation_instance.occurance_end_date_time,
            )

            # Convert bools to integers to allow comparison
            if len(dataframe["value"]) > 0 and isinstance(
                dataframe["value"][0], np.bool_
            ):
                dataframe["value"] = dataframe["value"].astype(int)

            self.original_ts_dataframes[ts_iri] = dataframe

        # Detection precision
        self.scanned_timeseries_detection_precisions_relative: Dict[str, float] = dict()
        annotations_dao = AnnotationNodesDao.instance()
        matcher: AnnotationTimeseriesMatcherNodeFlat
        for matcher in annotations_dao.get_matchers_for_annotation_instance(
            self.scanned_annotation_instance.iri
        ):
            ts_iri = annotations_dao.get_matcher_original_annotated_ts(matcher.iri).iri
            self.scanned_timeseries_detection_precisions_relative[
                ts_iri
            ] = matcher.detection_precision

        # Min max
        self.timeseries_min_values_for_original: Dict[str, float] = dict()
        self.timeseries_min_values_for_scanned: Dict[str, float] = dict()
        self.timeseries_max_values_for_original: Dict[str, float] = dict()
        self.timeseries_max_values_for_scanned: Dict[str, float] = dict()
        for ts_iri in self.scanned_timeseries_iris.keys():
            self.timeseries_max_values_for_original[
                ts_iri
            ] = self.persistence_services.get(ts_iri).max_value_for_period(ts_iri)
            self.timeseries_min_values_for_original[
                ts_iri
            ] = self.persistence_services.get(ts_iri).min_value_for_period(ts_iri)
            self.timeseries_min_values_for_scanned[
                self.scanned_timeseries_iris.get(ts_iri)
            ] = self.timeseries_min_values_for_original.get(ts_iri)
            self.timeseries_max_values_for_scanned[
                self.scanned_timeseries_iris.get(ts_iri)
            ] = self.timeseries_max_values_for_original.get(ts_iri)

        self._prepare_original_dataset()

        self.runtime_con_container = RuntimeConnectionContainer.instance()

    @abc.abstractmethod
    def _handle_new_reading(self, reading):
        pass

    @abc.abstractmethod
    def _prepare_original_dataset(self):
        pass

    def _detector_loop(self):
        active = True
        while True:
            if (
                self.detector_stop_queue.qsize() > 0
                and self.detector_stop_queue.get() == True
            ):
                logger.info(
                    f"Stopping process scanning {self.scanned_asset.caption} for occurances of {self.scanned_annotation_instance.caption}"
                )
                return

            try:
                reading = self.detector_input_queue.get(block=True, timeout=3)
                no_reading = reading is None or reading[1] is None
            except Empty:
                no_reading = True

            if no_reading:
                if active and self.detector_active_status_queue.qsize() == 0:
                    try:
                        self.detector_active_status_queue.get_nowait()
                    except Empty:
                        pass
                    self.detector_active_status_queue.put(False)
                active = False
                continue

            self._handle_new_reading(reading)

            if not active and self.detector_active_status_queue.qsize() == 0:
                try:
                    self.detector_active_status_queue.get_nowait()
                except Empty:
                    pass
                self.detector_active_status_queue.put(True)
                active = False

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
            ] = timeseries_endpoints.get_related_timeseries_database_service(ts_iri)

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
        # Scanner process and inter-process communication:
        self.detector_input_queue: Queue = Queue()
        self.detector_stop_queue: Queue = Queue()
        self.detector_active_status_queue: Queue = Queue()
        self.detector_process: Process = Process(
            target=self._detector_loop,
        )
        self.detector_process.start()

        # Register handlers in order to receive new time-series data
        rt_con_container = RuntimeConnectionContainer.instance()
        for ts_iri in self.scanned_timeseries_iris.values():
            ts_input = rt_con_container.get_timeseries_input_by_iri(ts_iri)
            ts_input.register_handler(
                self._reading_handler, handler_id=self.input_handler_id
            )

        self.active = True

    def _reading_handler(self, ts_iri, reading_value, reading_time):
        # Convert bool values to integers
        if isinstance(reading_value, bool):
            reading_value = 1 if reading_value else 0
        self.detector_input_queue.put((ts_iri, reading_value, reading_time))

    def stop_detection(self):
        logger.info(
            f"Stopping detection of {self.scanned_annotation_instance.caption} on {self.scanned_asset.caption}"
        )
        # stop handlers
        rt_con_container = RuntimeConnectionContainer.instance()
        for ts_iri in self.scanned_timeseries_iris.values():
            ts_input = rt_con_container.get_timeseries_input_by_iri(ts_iri)
            ts_input.remove_handler(handler_id=self.input_handler_id)

        # send stop signal
        self.detector_stop_queue.put(True)
        # wait for stop
        self.detector_process.join()
        self.active = False
        # quit
        self.detector_process.terminate()
        # quit queues
        self.detector_input_queue.close()
        del self.detector_input_queue
        self.detector_stop_queue.close()
        del self.detector_stop_queue
        self.detector_active_status_queue.close()
        del self.detector_active_status_queue
        logger.info(
            f"Detection of {self.scanned_annotation_instance.caption} on {self.scanned_asset.caption} stopped succesfully."
        )

    def is_active(self) -> bool:

        # check, if new active message:
        if self.detector_active_status_queue.qsize() > 0:
            self.active = self.detector_active_status_queue.get()

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
