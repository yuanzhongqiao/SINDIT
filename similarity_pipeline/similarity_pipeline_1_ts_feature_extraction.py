from datetime import datetime, timedelta
import random
import sys
from typing import Dict, List
from tsfresh import extract_features
import pandas as pd

import backend.api.python_endpoints.timeseries_endpoints as timeseries_endpoints
from graph_domain.main_digital_twin.TimeseriesNode import (
    TimeseriesNodeFlat,
    TimeseriesValueTypes,
)
from similarity_pipeline.similarity_pipeline_status_manager import (
    SimilarityPipelineStatusManager,
)
from util.log import logger


# #############################################################################
# Timeseries feature extraction
# #############################################################################
def similarity_pipeline_1_ts_feature_extraction():

    logger.info("\n\n\nSTEP 1: Timeseries feature extraction\n")

    # Restricted comparison time (since the factory is not running all the time, a specific range was selected)
    comparison_end_date_time = datetime(
        year=2022, month=7, day=29, hour=11, minute=0, second=0
    )
    comparison_duration = timedelta(hours=2).total_seconds()

    timeseries_nodes = timeseries_endpoints.get_timeseries_nodes(deep=True)

    # Get empty feature set to be applied to all not compatible TS:
    test_ts_dataframe = pd.DataFrame(columns=["time", "value"], data=[[0, 1], [1, 2]])

    # Add id row that is required by tsfresh
    test_ts_dataframe.insert(loc=0, column="id", value=0)

    logger.info("Finished loading dataframe. Extracting features...")
    extracted_test_features: pd.DataFrame = extract_features(
        test_ts_dataframe, column_id="id", column_sort="time", column_value="value"
    )
    extracted_test_features = extracted_test_features.transpose()
    empty_feature_dict = extracted_test_features.to_dict()[0]
    for key in empty_feature_dict.keys():
        empty_feature_dict[key] = sys.maxsize
        # pseudo value to build a cluster of not supported TS

    #######################
    logger.info("Preparing units for transformation into an additional feature")
    NO_UNIT = "no_unit"
    all_unit_ids_not_unique = [
        ts.unit.iri for ts in timeseries_nodes if ts.unit is not None
    ]
    all_unit_ids = list(set(all_unit_ids_not_unique))
    all_unit_ids.append(NO_UNIT)

    # Create feature number assignments for units (multiple times to enhance randomness)
    unit_numbers: List[Dict] = []
    for i in range(5):
        random.shuffle(all_unit_ids)
        unit_numbers.append(dict())
        j = 0
        for unit in all_unit_ids:
            unit_numbers[i][unit] = j
            j += 1

    i = 1
    pipeline_start_datetime = datetime.now()
    logger.info(f"Timeseries analysis started at {pipeline_start_datetime}")
    timeseries_node: TimeseriesNodeFlat
    for timeseries_node in timeseries_nodes:
        pipeline_single_node_start_datetime = datetime.now()

        logger.info(
            f"\n\nAnalyzing timeseries {i} of {len(timeseries_nodes)}: {timeseries_node.id_short}"
        )
        # Note that this can result in very large ranges, if enough data is present!
        ts_entry_count = timeseries_endpoints.get_timeseries_entries_count(
            iri=timeseries_node.iri,
            date_time=comparison_end_date_time,
            duration=comparison_duration,
        )
        logger.info(f"Total entry count: {ts_entry_count}")

        if ts_entry_count > 10000:
            logger.warning(
                f"Skipped extracting features for {timeseries_node.caption} because it has over 10000 entries."
            )
            continue

        # Cancel, if not int or float
        if timeseries_node.value_type in [
            TimeseriesValueTypes.DECIMAL.value,
            TimeseriesValueTypes.INT.value,
        ]:
            logger.info("Loading dataframe...")
            ts_range_df = timeseries_endpoints.get_timeseries_range(
                iri=timeseries_node.iri,
                date_time=comparison_end_date_time,
                duration=comparison_duration,
                aggregation_window_ms=None,  # raw values
            )

            # Add id row that is required by tsfresh
            ts_range_df.insert(loc=0, column="id", value=0)

            logger.info("Finished loading dataframe. Extracting features...")
            extracted_features: pd.DataFrame = extract_features(
                ts_range_df, column_id="id", column_sort="time", column_value="value"
            )
            extracted_features = extracted_features.transpose()
            feature_dict = extracted_features.to_dict()[0]
        else:
            logger.info(
                f"Feature calculation with normal timeseries libraries not possible: Unsupported type: {timeseries_node.value_type}"
            )
            logger.info("Applying empty feature dict...")
            feature_dict = empty_feature_dict

        pipeline_single_node_end_datetime = datetime.now()
        logger.info(
            f"Timeseries analysis finished at {pipeline_single_node_end_datetime} after {pipeline_single_node_end_datetime - pipeline_single_node_start_datetime}"
        )

        #######################
        logger.info("Converting unit-relationship into an additional feature")
        unit_iri = (
            timeseries_node.unit.iri if timeseries_node.unit is not None else NO_UNIT
        )
        for j in range(5):
            feature_dict[f"unit_association_shuffle_{j}"] = unit_numbers[j].get(
                unit_iri
            )

        #######################
        logger.info("Writing to KG-DT...")
        timeseries_endpoints.set_ts_feature_dict(timeseries_node.iri, feature_dict)

        i += 1

    pipeline_end_datetime = datetime.now()

    logger.info(
        f"Timeseries analysis finished at {pipeline_end_datetime} after {pipeline_end_datetime - pipeline_start_datetime}"
    )
    SimilarityPipelineStatusManager.instance().set_active(
        active=False, stage="time_series_feature_extraction"
    )
