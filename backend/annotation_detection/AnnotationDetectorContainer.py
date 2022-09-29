import time
from typing import Dict, List, Tuple
from backend.annotation_detection.AnnotationDetector import AnnotationDetector
from backend.annotation_detection.EuclidianDistanceAnnotationDetector import (
    EuclidianDistanceAnnotationDetector,
)
from backend.knowledge_graph.dao.AnnotationNodesDao import AnnotationNodesDao
from graph_domain.expert_annotations.AnnotationInstanceNode import (
    AnnotationInstanceNodeDeep,
    AnnotationInstanceNodeFlat,
)
from graph_domain.main_digital_twin.RuntimeConnectionNode import (
    RuntimeConnectionNode,
    RuntimeConnectionTypes,
)
from backend.runtime_connections.TimeseriesInput import TimeseriesInput
from backend.runtime_connections.mqtt.MqttRuntimeConnection import (
    MqttRuntimeConnection,
)
from backend.runtime_connections.mqtt.MqttTimeseriesInput import MqttTimeseriesInput
from backend.runtime_connections.opcua.OpcuaRuntimeConnection import (
    OpcuaRuntimeConnection,
)
from backend.runtime_connections.opcua.OpcuaTimeseriesInput import OpcuaTimeseriesInput
from backend.specialized_databases.DatabasePersistenceServiceContainer import (
    DatabasePersistenceServiceContainer,
)
from backend.specialized_databases.timeseries.influx_db.InfluxDbPersistenceService import (
    InfluxDbPersistenceService,
)
from graph_domain.main_digital_twin.TimeseriesNode import (
    TimeseriesNodeDeep,
)
from backend.runtime_connections.RuntimeConnection import RuntimeConnection
from backend.exceptions.EnvironmentalVariableNotFoundError import (
    EnvironmentalVariableNotFoundError,
)

from util.log import logger
from threading import Thread
from util.inter_process_cache import memcache

# Maps node-types to the connection / input classes
RT_CONNECTION_MAPPING = {
    RuntimeConnectionTypes.MQTT.value: MqttRuntimeConnection,
    RuntimeConnectionTypes.OPC_UA.value: OpcuaRuntimeConnection,
}
RT_INPUT_MAPPING = {
    RuntimeConnectionTypes.MQTT.value: MqttTimeseriesInput,
    RuntimeConnectionTypes.OPC_UA.value: OpcuaTimeseriesInput,
}


class AnnotationDetectorContainer:
    """
    Holds and manages all current annotation detector services
    """

    __instance = None

    @classmethod
    def instance(cls):
        if cls.__instance is None:
            cls()
        return cls.__instance

    def __init__(self):
        if self.__instance is not None:
            raise Exception("Singleton instantiated multiple times!")

        AnnotationDetectorContainer.__instance = self

        # Dict: (instance_iri, asset_iri) -> AnnotationDetector
        self.detectors: Dict[Tuple[str, str], AnnotationDetector] = {}
        self._active_detectors_status_thread = None

    def start_active_detectors_status_thread(self):
        self._active_detectors_status_thread = Thread(
            target=self._active_detectors_write_to_cache_loop
        )
        self._active_detectors_status_thread.start()

    def refresh_annotation_detectors(self):
        """Refreshes the annotation detectors, creating new ones if available in the graph, or deleting old ones."""
        annotations_dao: AnnotationNodesDao = AnnotationNodesDao.instance()
        updated_instance_nodes_flat: List[
            AnnotationInstanceNodeFlat
        ] = annotations_dao.get_annotation_instances(only_active_scanned_instances=True)

        updated_detector_tuples: List[Tuple[str, str]] = []
        for instance in updated_instance_nodes_flat:
            updated_detector_tuples.extend(
                [
                    (instance.iri, asset.iri)
                    for asset in annotations_dao.get_scanned_assets_for_annotation_instance(
                        instance.iri
                    )
                ]
            )

        #
        # Check if detectors have been removed:
        #

        removed_detector_tuples = [
            tuple
            for tuple in self.detectors.keys()
            if tuple not in updated_detector_tuples
        ]

        for old_tuple in removed_detector_tuples:
            old_detector = self.detectors.get(old_tuple)
            old_detector.stop_detection()
            self.detectors.pop(old_tuple)
            del old_detector

        #
        # Initialize new detectors
        #
        new_detector_tuples = [
            tuple
            for tuple in updated_detector_tuples
            if tuple not in self.detectors.keys()
        ]

        for new_tuple in new_detector_tuples:
            new_detector = (
                EuclidianDistanceAnnotationDetector.from_annotation_instance_and_asset(
                    instance_iri=new_tuple[0], asset_iri=new_tuple[1]
                )
            )

            self.detectors[new_tuple] = new_detector

            new_detector.start_detection()

    def get_active_detectors_count(self) -> int:

        return len(
            [True for detector in self.detectors.values() if detector.is_active()]
        )

    def _active_detectors_write_to_cache_loop(self):
        while True:
            memcache.set(
                "active_annotation_detectors_count", self.get_active_detectors_count()
            )

            time.sleep(3)
