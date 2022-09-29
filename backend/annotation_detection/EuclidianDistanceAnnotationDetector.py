from backend.annotation_detection.AnnotationDetector import AnnotationDetector
import pandas as pd
import numpy as np
from typing import Dict
from util.log import logger


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

        ts_array: np.array = self.current_ts_arrays.get(reading_iri)
        if ts_array is None:
            ts_array = np.array([])
            self.current_ts_arrays[reading_iri] = ts_array

        ts_array = np.append(ts_array, [value])

        if len(ts_array) > self.original_ts_lens_mapped_to_scans.get(reading_iri):
            ts_array = np.delete(ts_array, 0)

        self.current_ts_arrays[reading_iri] = ts_array
        # print(len(ts_array))

        if all(
            [
                len(current_reading[1])
                == self.original_ts_lens_mapped_to_scans.get(current_reading[0])
                for current_reading in self.current_ts_arrays.items()
            ]
        ) and len(self.current_ts_arrays.keys()) == len(self.original_ts_arrays.keys()):
            current_combined_array = np.concatenate(
                [
                    self.current_ts_arrays.get(self.scanned_timeseries_iris.get(iri))
                    for iri in self.original_ts_iris_ordered
                ],
                axis=0,
            )

            euclidian_distance = np.linalg.norm(
                self.original_ts_combined_array - current_combined_array
            )

            print(
                f"Matching {self.scanned_annotation_instance.caption} on {self.scanned_asset.caption}. Euclidian distance: {euclidian_distance}"
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

        self.original_ts_iris_ordered = [iri for iri in self.original_ts_arrays.keys()]
        self.original_ts_iris_ordered.sort()
        self.original_ts_combined_array = np.concatenate(
            [self.original_ts_arrays.get(iri) for iri in self.original_ts_iris_ordered],
            axis=0,
        )

        # Map the arrays and lengths directly to the iris of the scanned ts:

        self.current_ts_arrays: Dict[str, np.array] = dict()
