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

            print(len(ts_array))

        # TODO: if not equal amount of entries -> skip?
        self.current_ts_arrays[reading_iri] = ts_array
        pass

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

        self.original_ts_iris_ordered = [t[0] for t in self.original_ts_arrays]
        self.original_ts_combined_array = np.concatenate(
            [ts_array for ts_array in self.original_ts_arrays.values()], axis=0
        )

        # Map the arrays and lengths directly to the iris of the scanned ts:

        self.current_ts_arrays: Dict[str, np.array] = dict()
