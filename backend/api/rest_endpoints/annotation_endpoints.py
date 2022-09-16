from datetime import datetime
import json
from typing import List
from backend.api.api import app
from backend.knowledge_graph.dao.AnnotationNodesDao import AnnotationNodesDao
from backend.knowledge_graph.dao.AssetNodesDao import AssetsDao
from pydantic import BaseModel
import backend.api.python_endpoints.asset_endpoints as python_asset_endpoints
from backend.knowledge_graph.dao.TimeseriesNodesDao import TimeseriesNodesDao


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
            id_short=f"ts_matcher_for_{ts_iri}",
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
