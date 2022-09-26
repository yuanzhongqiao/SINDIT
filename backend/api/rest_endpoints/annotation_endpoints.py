from datetime import datetime, timedelta
import json
from dateutil import tz
from fastapi import HTTPException
from typing import List
from backend.api.api import app
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


@app.get("/annotation/detection/details")
async def get_current_annotation_detection_details():
    """
    Returns details of the currently detected annotation
    (or of one of them, if multiple unconfirmed yet).
    :param iri:
    :return:
    """
    details_dict = {
        "iri": "www.sintef.no/aas_identifiers/learning_factory/annotations/detections/test-detection",
        "asset_iri": "www.sintef.no/aas_identifiers/learning_factory/machines/hbw",
        "asset_caption": "asset-caption",
        "occurance_start": datetime.now().astimezone(
            tz.gettz(get_configuration(group=ConfigGroups.FRONTEND, key="timezone"))
        )
        - timedelta(minutes=5),
        "occurance_end": datetime.now().astimezone(
            tz.gettz(get_configuration(group=ConfigGroups.FRONTEND, key="timezone"))
        ),
        "definition_iri": "def iri",
        "definition_caption": "def cap",
        "definition_description": None,
        "instance_iri": "inst iri",
        "instance_caption": "inst cap",
        "instance_description": "inst desc",
        "solution_proposal": "solution",
        "detected_timeseries_iris": [
            "www.sintef.no/aas_identifiers/learning_factory/sensors/hbw_actual_pos_vertical",
            "www.sintef.no/aas_identifiers/learning_factory/sensors/factory_humidity_raw",
        ],
        "original_annotated_asset_iri": "www.sintef.no/aas_identifiers/learning_factory/machines/vgr",
    }

    return details_dict


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

    # create_annotation_instance(AnnotationInstanceArguments(
    #     id_short="",
    #     asset_iri="",
    #     definition_iri="",
    #     ts_iri_list=[],
    #     start_datetime=None,
    #     end_datetime=None,
    #     caption="",
    #     description=""
    # ))

    # TODO
    # create ts-matchers
    # create
