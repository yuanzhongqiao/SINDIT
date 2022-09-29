from datetime import datetime, timedelta
import json
from dateutil import tz
from fastapi import HTTPException
from typing import List
from backend.annotation_detection.AnnotationDetectorContainer import (
    AnnotationDetectorContainer,
)
from util.inter_process_cache import memcache
from backend.api.api import app
from backend.knowledge_graph.dao.BaseNodesDao import BaseNodeDao
from graph_domain.expert_annotations.AnnotationDetectionNode import (
    AnnotationDetectionNodeFlat,
)
from util.environment_and_configuration import ConfigGroups, get_configuration
from backend.knowledge_graph.dao.AnnotationNodesDao import AnnotationNodesDao
from pydantic import BaseModel
from backend.knowledge_graph.dao.TimeseriesNodesDao import TimeseriesNodesDao
from graph_domain.expert_annotations.AnnotationTimeseriesMatcherNode import (
    AnnotationTimeseriesMatcherNodeFlat,
)
from util.log import logger


ANNOTATIONS_DAO: AnnotationNodesDao = AnnotationNodesDao.instance()
TIMESERIES_NODES_DAO: TimeseriesNodesDao = TimeseriesNodesDao.instance()
BASE_NODE_DAO: BaseNodeDao = BaseNodeDao.instance()

DATETIME_STRF_FORMAT = "%Y_%m_%d_%H_%M_%S_%f"


class AnnotationDefinitionArguments(BaseModel):
    id_short: str
    solution_proposal: str
    caption: str | None = None
    description: str | None = None


@app.post("/annotation/definition")
async def post_annotation_definition(definition: AnnotationDefinitionArguments):
    logger.info(f"Creating new annotation definition: {definition.id_short}...")
    return ANNOTATIONS_DAO.create_annotation_definition(
        id_short=definition.id_short,
        solution_proposal=definition.solution_proposal,
        caption=definition.caption,
        description=definition.description,
    )


@app.patch("/annotation/instance/toggle_occurance_scan")
async def patch_annotation_instance_toggle_occurance_scan(
    instance_iri: str, active: bool
):
    logger.info(
        f"Toggling occurance scan to active: {active} for annotation instance: {instance_iri}..."
    )
    ANNOTATIONS_DAO.toggle_annotation_instance_occurance_scan(instance_iri, active)


class AnnotationInstanceArguments(BaseModel):
    id_short: str
    asset_iri: str
    definition_iri: str
    ts_iri_list: List[str]
    start_datetime: datetime
    end_datetime: datetime
    caption: str | None = None
    description: str | None = None


def create_annotation_instance(instance: AnnotationInstanceArguments):
    logger.info(f"Creating new annotation instance: {instance.id_short}...")
    instance_iri = ANNOTATIONS_DAO.create_annotation_instance(
        id_short=instance.id_short,
        start_datetime=instance.start_datetime,
        end_datetime=instance.end_datetime,
        caption=instance.caption,
        description=instance.description,
    )
    ANNOTATIONS_DAO.create_annotation_instance_of_definition_relationship(
        definition_iri=instance.definition_iri, instance_iri=instance_iri
    )
    ANNOTATIONS_DAO.create_annotation_instance_asset_relationship(
        instance_iri=instance_iri, asset_iri=instance.asset_iri
    )

    for ts_iri in instance.ts_iri_list:
        ts_node = TIMESERIES_NODES_DAO.get_timeseries_node_flat(ts_iri)

        ts_matcher_iri = ANNOTATIONS_DAO.create_annotation_ts_matcher(
            id_short=f"ts_matcher_for_{instance.id_short}_matching_{ts_node.id_short}",
            caption=f"TS-Matcher: {ts_node.caption}",
        )
        ANNOTATIONS_DAO.create_annotation_ts_matcher_instance_relationship(
            ts_matcher_iri=ts_matcher_iri, instance_iri=instance_iri
        )
        ANNOTATIONS_DAO.create_annotation_ts_match_relationship(
            ts_matcher_iri=ts_matcher_iri, ts_iri=ts_iri, original_annotation=True
        )
    ANNOTATIONS_DAO.create_annotation_occurance_scan_relationship(
        definition_iri=instance.definition_iri, asset_iri=instance.asset_iri
    )

    return instance_iri


@app.post("/annotation/instance")
async def post_annotation_instance(instance: AnnotationInstanceArguments):
    return create_annotation_instance(instance)


@app.delete("/annotation/definition")
async def delete_annotation_definition(definition_iri: str):
    logger.info(f"Deleting annotation definition: {definition_iri}...")
    instances = ANNOTATIONS_DAO.get_instances_of_annotation_definition(definition_iri)

    if len(instances) != 0:
        logger.info("Can not delete annotation definition: Related instances exist!")
        raise HTTPException(
            status_code=403, detail="Instances have to be removed first."
        )

    ANNOTATIONS_DAO.delete_annotation_definition(definition_iri)


@app.delete("/annotation/instance")
async def delete_annotation_instance(instance_iri: str):
    """Deletes not only a instance, but also its related time-series matchers (and relationships)!

    Args:
        instance_iri (str): _description_
    """

    deletable_matchers: List[
        AnnotationTimeseriesMatcherNodeFlat
    ] = ANNOTATIONS_DAO.get_ts_matchers_only_used_for(instance_iri)

    for matcher in deletable_matchers:
        logger.info(f"Deleting time-series matcher: {matcher.id_short}")
        ANNOTATIONS_DAO.delete_annotation_ts_matcher(matcher.iri)

    logger.info(f"Deleting annotation instance: {instance_iri}...")
    ANNOTATIONS_DAO.delete_annotation_instance(instance_iri)


@app.get("/annotation/ts_matcher/original_annotated_ts")
async def get_ts_matcher_original_ts(iri: str):
    """
    Returns the originally annotated timeseries node for a matcher
    :raises IdNotFoundException: If the file is not found
    :param iri:
    :return:
    """
    return ANNOTATIONS_DAO.get_matcher_original_annotated_ts(iri)


@app.get("/annotation/ts_matcher/related_annotation_instance")
async def get_ts_matcher_annotation_instance(iri: str):
    """
    Returns the annotation instance node for a matcher
    :raises IdNotFoundException: If the file is not found
    :param iri:
    :return:
    """
    return ANNOTATIONS_DAO.get_matcher_annotation_instance(iri)


@app.get("/annotation/instance")
async def get_annotation_instance_for_definition(definition_iri: str):
    """
    Returns the list of annotation instances with the given definition
    :raises IdNotFoundException: If the file is not found
    :param iri:
    :return:
    """
    return ANNOTATIONS_DAO.get_annotation_instance_for_definition(definition_iri)


@app.get("/annotation/instance/count")
async def get_annotation_instance_count_for_definition(definition_iri: str):
    """
    Returns the count of annotation instances with the given definition
    :raises IdNotFoundException: If the file is not found
    :param iri:
    :return:
    """
    return ANNOTATIONS_DAO.get_annotation_instance_count_for_definition(definition_iri)


def get_annotation_detection_details(detection_iri: None | str = None):
    """
    Returns details of the currently detected annotation or the given one
    (or of one of them, if multiple unconfirmed yet).
    :param iri:
    :return:
    """
    if detection_iri is None:
        detection_node: AnnotationDetectionNodeFlat = (
            ANNOTATIONS_DAO.get_oldest_unconfirmed_detection()
        )
        if detection_node is None:
            # not yet open -> skip
            return None
    else:
        detection_node: AnnotationDetectionNodeFlat = BASE_NODE_DAO.get_generic_node(
            detection_iri
        )

    matched_ts_nodes = ANNOTATIONS_DAO.get_matched_ts_for_detection(detection_node.iri)
    asset = ANNOTATIONS_DAO.get_asset_for_detection(detection_node.iri)
    instance = ANNOTATIONS_DAO.get_annotation_instance_for_detection(detection_node.iri)
    definition = ANNOTATIONS_DAO.get_annotation_definition_for_instance(instance.iri)
    orig_asset = ANNOTATIONS_DAO.get_asset_for_annotation_instance(instance.iri)

    details_dict = {
        "iri": detection_node.iri,
        "asset_iri": asset.iri,
        "asset_caption": asset.caption,
        "occurance_start": detection_node.occurance_start_date_time,
        "occurance_end": detection_node.occurance_end_date_time,
        "definition_iri": definition.iri,
        "definition_caption": definition.caption,
        "definition_description": definition.description,
        "instance_iri": instance.iri,
        "instance_id_short": instance.id_short,
        "instance_caption": instance.caption,
        "instance_description": instance.description,
        "solution_proposal": definition.solution_proposal,
        "detected_timeseries_iris": [ts.iri for ts in matched_ts_nodes],
        "original_annotated_asset_iri": orig_asset.iri,
    }

    return details_dict


@app.get("/annotation/detection/details")
async def get_current_annotation_detection_details_endpoint():
    """
    Returns details of the currently detected annotation
    (or of one of them, if multiple unconfirmed yet).
    :param iri:
    :return:
    """
    return get_annotation_detection_details()


@app.delete("/annotation/detection")
async def delete_annotation_detection(detection_iri: str):
    """Deletes a detection and the relationships

    Args:
        instance_iri (str): _description_
    """

    logger.info(f"Deleting annotation detection: {detection_iri}...")

    ANNOTATIONS_DAO.delete_annotation_detection(detection_iri)


class AnnotationDetectionConfirmationArguments(BaseModel):
    detection_iri: str


@app.post("/annotation/detection/confirm")
async def confirm_annotation_detection(
    detection: AnnotationDetectionConfirmationArguments,
):
    """Confirms a detection.

    Args:
        instance_iri (str): _description_
    """

    logger.info(f"Confirming annotation detection: {detection.detection_iri}...")

    ANNOTATIONS_DAO.set_detection_confirmation_date_time(
        detection_iri=detection.detection_iri
    )

    details_dict = get_annotation_detection_details(detection.detection_iri)
    caption = f"Confirmed Occurance of: {details_dict.get('instance_caption')}"
    description = (
        f"This annotation instance has been automatically created when "
        f"the related detection of the instance '{details_dict.get('instance_caption')}' has been confirmed."
    )
    timestamp = datetime.now().astimezone(
        tz.gettz(get_configuration(group=ConfigGroups.FRONTEND, key="timezone"))
    )
    id_short = f"confirmed_occurance_of_{details_dict.get('instance_id_short')}_at_{timestamp.strftime(DATETIME_STRF_FORMAT)}"

    instance_iri = create_annotation_instance(
        AnnotationInstanceArguments(
            id_short=id_short,
            asset_iri=details_dict.get("asset_iri"),
            definition_iri=details_dict.get("definition_iri"),
            ts_iri_list=details_dict.get("detected_timeseries_iris"),
            start_datetime=details_dict.get("occurance_start"),
            end_datetime=details_dict.get("occurance_end"),
            caption=caption,
            description=description,
        )
    )

    # Relationship to detection
    ANNOTATIONS_DAO.create_confirmed_detection_instance_relationship(
        detection_iri=details_dict.get("iri"), instance_iri=instance_iri
    )


@app.get("/annotation/status")
async def get_annotation_status():
    """Combined status endpoint. Should be preferred to use less API calls.

    Returns:
        _type_: dict
    """
    status_dict = {
        "total_annotations_count": ANNOTATIONS_DAO.get_annotation_instance_count(),
        "sum_of_scans": int(memcache.get("active_annotation_detectors_count")),
        "unconfirmed_detections": ANNOTATIONS_DAO.get_annotation_detections_count(
            confirmed=False
        ),
        "confirmed_detections": ANNOTATIONS_DAO.get_annotation_detections_count(
            confirmed=True
        ),
    }

    return status_dict
