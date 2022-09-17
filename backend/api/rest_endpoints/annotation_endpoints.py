from datetime import datetime
import json
from fastapi import FastAPI, HTTPException
from typing import List
from backend.api.api import app
from backend.knowledge_graph.dao.AnnotationNodesDao import AnnotationNodesDao
from backend.knowledge_graph.dao.AssetNodesDao import AssetsDao
from pydantic import BaseModel
import backend.api.python_endpoints.asset_endpoints as python_asset_endpoints
from backend.knowledge_graph.dao.TimeseriesNodesDao import TimeseriesNodesDao
from graph_domain.expert_annotations.AnnotationTimeseriesMatcherNode import (
    AnnotationTimeseriesMatcherNodeDeep,
    AnnotationTimeseriesMatcherNodeFlat,
)


ANNOTATIONS_DAO: AnnotationNodesDao = AnnotationNodesDao.instance()
TIMESERIES_NODES_DAO: TimeseriesNodesDao = TimeseriesNodesDao.instance()


class AnnotationDefinitionArguments(BaseModel):
    id_short: str
    solution_proposal: str
    caption: str | None = None
    description: str | None = None


@app.post("/annotation/definition")
def post_annotation_definition(definition: AnnotationDefinitionArguments):
    print(f"Creating new annotation definition: {definition.id_short}...")
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


@app.post("/annotation/instance")
def post_annotation_definition(instance: AnnotationInstanceArguments):
    print(f"Creating new annotation instance: {instance.id_short}...")
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


@app.delete("/annotation/definition")
def delete_annotation_definition(definition_iri: str):
    print(f"Deleting annotation definition: {definition_iri}...")
    instances = ANNOTATIONS_DAO.get_instances_of_annotation_definition(definition_iri)

    if len(instances) != 0:
        print("Can not delete annotation definition: Related instances exist!")
        raise HTTPException(
            status_code=403, detail="Instances have to be removed first."
        )

    ANNOTATIONS_DAO.delete_annotation_definition(definition_iri)


@app.delete("/annotation/instance")
def delete_annotation_definition(instance_iri: str):
    """Deletes not only a instance, but also its related time-series matchers (and relationships)!

    Args:
        instance_iri (str): _description_
    """

    deletable_matchers: List[
        AnnotationTimeseriesMatcherNodeFlat
    ] = ANNOTATIONS_DAO.get_ts_matchers_only_used_for(instance_iri)

    for matcher in deletable_matchers:
        print(f"Deleting time-series matcher: {matcher.id_short}")
        ANNOTATIONS_DAO.delete_annotation_ts_matcher(matcher.iri)

    print(f"Deleting annotation definition: {instance_iri}...")
    ANNOTATIONS_DAO.delete_annotation_instance(instance_iri)


@app.get("/annotation/ts_matcher/original_annotated_ts")
def get_ts_matcher_original_ts(iri: str):
    """
    Returns the originally annotated timeseries node for a matcher
    :raises IdNotFoundException: If the file is not found
    :param iri:
    :return:
    """
    return ANNOTATIONS_DAO.get_matcher_original_annotated_ts(iri)


@app.get("/annotation/ts_matcher/related_annotation_instance")
def get_ts_matcher_annotation_instance(iri: str):
    """
    Returns the annotation instance node for a matcher
    :raises IdNotFoundException: If the file is not found
    :param iri:
    :return:
    """
    return ANNOTATIONS_DAO.get_matcher_annotation_instance(iri)
