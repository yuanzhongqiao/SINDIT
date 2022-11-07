from backend.annotation_detection.AnnotationDetector import AnnotationDetector
import pandas as pd
import numpy as np
from typing import Dict
from util.log import logger
from backend.specialized_databases.timeseries.TimeseriesPersistenceService import (
    TimeseriesPersistenceService,
)
from util.environment_and_configuration import (
    ConfigGroups,
    get_configuration,
)
from datetime import datetime, timedelta
from dateutil import tz

DATETIME_STRF_FORMAT_CAPTION = "%d.%m.%Y, %H:%M:%S"
DATETIME_STRF_FORMAT_ID = "%Y_%m_%d_%H_%M_%S_%f"


class EuclidianDistanceAnnotationDetector(AnnotationDetector):
    """
    Annotation detector scanning the related time-series inputs of one asset for occurances of a annotation instance

    Based on the Euclidian Distance Similarity Measure
    """

    # override
    def _handle_new_reading(self, reading):
        reading_iri = reading[0]
        value = reading[1]
        time = reading[2]

        # Load the watched array or create it
        ts_array: np.array = self.current_ts_arrays.get(reading_iri)
        if ts_array is None:
            ts_array = np.array([])
            self.current_ts_arrays[reading_iri] = ts_array

        # Move the watched window
        ts_array = np.append(ts_array, [value])
        if len(ts_array) > self.original_ts_lens_mapped_to_scans.get(reading_iri):
            ts_array = np.delete(ts_array, 0)

        self.current_ts_arrays[reading_iri] = ts_array

        if all(
            [
                len(current_reading[1])
                == self.original_ts_lens_mapped_to_scans.get(current_reading[0])
                for current_reading in self.current_ts_arrays.items()
            ]
        ) and len(self.current_ts_arrays.keys()) == len(self.original_ts_arrays.keys()):
            # current_combined_array = np.concatenate(
            #     [
            #         self._normalize_array(
            #             self.current_ts_arrays.get(
            #                 self.scanned_timeseries_iris.get(iri)
            #             ),
            #             min_value=self.timeseries_min_values_for_scanned.get(iri),
            #             max_value=self.timeseries_max_values_for_scanned.get(iri),
            #         )
            #         for iri in self.original_ts_iris_ordered
            #     ],
            #     axis=0,
            # )
            # Overall euclidian distance:
            # euclidian_distance = np.linalg.norm(
            #     self.original_ts_combined_array_normalized - current_combined_array
            # )
            # print(
            #     f"Matching {self.scanned_annotation_instance.caption} on {self.scanned_asset.caption}. Euclidian distance: {euclidian_distance}"
            # )

            # Individual euclidian distances:
            euclidian_distances: Dict[str, float] = dict()
            euclidian_distances_by_len: Dict[str, float] = dict()
            for iri in self.original_ts_iris_ordered:
                normalized_current = self._normalize_array(
                    self.current_ts_arrays.get(self.scanned_timeseries_iris.get(iri)),
                    min_value=self.timeseries_min_values_for_scanned.get(iri),
                    max_value=self.timeseries_max_values_for_scanned.get(iri),
                )
                euclidian_distances[iri] = np.linalg.norm(
                    self.original_ts_arrays_normalized.get(iri) - normalized_current
                )
                euclidian_distances_by_len[iri] = euclidian_distances.get(
                    iri
                ) / self.original_ts_lens.get(iri)
            # print(
            #     f"Euclidian distances for {self.scanned_annotation_instance.caption} on {self.scanned_asset.caption}: {', '.join([str(dist) for dist in euclidian_distances.values()])}"
            # )
            print(
                f"Euclidian distances divided by array-len for {self.scanned_annotation_instance.caption} on {self.scanned_asset.caption}: {', '.join([f'{dist[0][-20:-1]}: {str(dist[1])}' for dist in euclidian_distances_by_len.items()])}"
            )

            if all(
                [
                    dist_pair[1]
                    < (
                        1
                        - self.scanned_timeseries_detection_precisions_relative.get(
                            dist_pair[0]
                        )
                    )
                    for dist_pair in euclidian_distances_by_len.items()
                ]
            ):
                # ignore, if just recently already detected:
                now = datetime.now().astimezone(
                    tz.gettz(
                        get_configuration(group=ConfigGroups.FRONTEND, key="timezone")
                    )
                )
                if now > self.last_detection_timestamp + timedelta(seconds=30):
                    self.last_detection_timestamp = datetime.now().astimezone(
                        tz.gettz(
                            get_configuration(
                                group=ConfigGroups.FRONTEND, key="timezone"
                            )
                        )
                    )
                    logger.info(
                        f"Match for: {self.scanned_annotation_instance.caption} on {self.scanned_asset.caption}!"
                    )
                    self._create_new_detection(
                        start_date_time=now
                        - (
                            self.scanned_annotation_instance.occurance_end_date_time
                            - self.scanned_annotation_instance.occurance_start_date_time
                        ),
                        end_date_time=now,
                    )

    # override
    def _prepare_original_dataset(self):

        self.original_ts_dataframes_only_values: Dict[str, pd.DataFrame] = dict()

        for ts_df in self.original_ts_dataframes.items():
            self.original_ts_dataframes_only_values[ts_df[0]] = ts_df[1].copy(deep=True)
            self.original_ts_dataframes_only_values[ts_df[0]].drop(
                columns=["time"], axis=1, inplace=True
            )

        self.original_ts_arrays: Dict[str, np.array] = dict()
        self.original_ts_arrays_normalized: Dict[str, np.array] = dict()
        self.original_ts_lens: Dict[str, int] = dict()
        self.original_ts_lens_mapped_to_scans: Dict[str, int] = dict()

        for ts_df in self.original_ts_dataframes_only_values.items():
            self.original_ts_arrays[ts_df[0]] = ts_df[1]["value"].to_numpy(
                copy=True,
            )
            self.original_ts_lens[ts_df[0]] = len(self.original_ts_arrays.get(ts_df[0]))
            self.original_ts_lens_mapped_to_scans[
                self.scanned_timeseries_iris.get(ts_df[0])
            ] = self.original_ts_lens.get(ts_df[0])
            self.original_ts_arrays_normalized[ts_df[0]] = self._normalize_array(
                self.original_ts_arrays.get(ts_df[0]),
                min_value=self.timeseries_min_values_for_original.get(ts_df[0]),
                max_value=self.timeseries_max_values_for_original.get(ts_df[0]),
            )

        self.original_ts_iris_ordered = [iri for iri in self.original_ts_arrays.keys()]
        self.original_ts_iris_ordered.sort()
        self.original_ts_combined_array_normalized = np.concatenate(
            [
                self.original_ts_arrays_normalized.get(iri)
                for iri in self.original_ts_iris_ordered
            ],
            axis=0,
        )

        # Map the arrays and lengths directly to the iris of the scanned ts:

        self.current_ts_arrays: Dict[str, np.array] = dict()

        # Calculate the threshold to be used for detections:
        for ts_iri in self.scanned_timeseries_iris.keys():
            service: TimeseriesPersistenceService = self.persistence_services.get(
                ts_iri
            )
            dataframe = service.read_period_to_dataframe(
                iri=ts_iri,
                begin_time=self.scanned_annotation_instance.occurance_start_date_time,
                end_time=self.scanned_annotation_instance.occurance_end_date_time,
            )
            self.original_ts_dataframes[ts_iri] = dataframe

    def _normalize_array(self, array: np.array, min_value, max_value) -> np.array:
        if min_value is None or max_value is None:
            # This can happen for data types not supporting min / max like bool
            return array
        # Subtract min value (get to starting at 0)
        non_negative_array = np.subtract(array, min_value)
        # Divide through (max-value - min-value)
        normalized_array = np.divide(non_negative_array, (max_value - min_value))

        return normalized_array
