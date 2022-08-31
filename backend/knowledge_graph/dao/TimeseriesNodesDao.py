import json
from typing import List

from py2neo import Node, NodeMatcher, Relationship

from graph_domain.main_digital_twin.factory_graph_types import (
    NodeTypes,
    RelationshipTypes,
)
from graph_domain.main_digital_twin.AssetNode import AssetNodeFlat, AssetNodeDeep
from graph_domain.main_digital_twin.TimeseriesNode import (
    TimeseriesNodeDeep,
    TimeseriesNodeFlat,
)
from graph_domain.similarities.TimeseriesClusterNode import TimeseriesClusterNode
from backend.exceptions.GraphNotConformantToMetamodelError import (
    GraphNotConformantToMetamodelError,
)
from backend.knowledge_graph.KnowledgeGraphPersistenceService import (
    KnowledgeGraphPersistenceService,
)
from backend.knowledge_graph.knowledge_graph_metamodel_validator import (
    validate_result_nodes,
)


class TimeseriesNodesDao(object):
    """
    Data Access Object for Timeseries nodes
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

        TimeseriesNodesDao.__instance = self

        self.ps: KnowledgeGraphPersistenceService = (
            KnowledgeGraphPersistenceService.instance()
        )

    @validate_result_nodes
    def get_timeseries_flat(self):
        """
        Queries all timeseries nodes. Does not follow any relationships
        :param self:
        :return:
        :raises GraphNotConformantToMetamodelError: If Graph not conformant
        """
        timeseries_flat_matches = self.ps.repo.match(model=TimeseriesNodeFlat)
        timeseries_flat = [m for m in timeseries_flat_matches]

        return timeseries_flat

    @validate_result_nodes
    def get_timeseries_deep(self):
        """
        Queries all timeseries nodes. Follows relationships to build nested objects for related nodes (e.g. connections)
        :param self:
        :return:
        """
        timeseries_deep_matches = self.ps.repo.match(model=TimeseriesNodeDeep)

        # Get rid of the 'Match' and 'RelatedObject' types in favor of normal lists automatically
        # by using the auto-generated json serializer
        return [
            TimeseriesNodeDeep.from_json(m.to_json()) for m in timeseries_deep_matches
        ]

    # validator used manually because result type is json instead of node-list
    def get_timeseries_deep_json(self):
        """
        Queries all timeseries nodes. Follows relationships to build nested objects for related nodes (e.g. sensors)
        Directly returns the serialized json instead of nested objects. This is faster than using the nested-object
        getter and serializing afterwards, as it does not require an intermediate step.
        :param self:
        :return:
        """
        timeseries_deep_matches = self.ps.repo.match(model=TimeseriesNodeDeep)

        # Validate manually:
        for timeseries in timeseries_deep_matches:
            timeseries.validate_metamodel_conformance()

        return json.dumps([m.to_json() for m in timeseries_deep_matches])

    def update_feature_dict(self, iri: str, feature_dict: dict):
        matcher = NodeMatcher(self.ps.graph)
        node: Node = matcher.match(iri=iri).first()
        feature_dict_str = json.dumps(feature_dict)
        node.update(feature_dict=feature_dict_str)
        self.ps.graph.push(node)

    def update_reduced_feature_list(self, iri: str, reduced_feature_list: List):
        matcher = NodeMatcher(self.ps.graph)
        node: Node = matcher.match(iri=iri).first()
        reduced_feature_list_str = json.dumps(reduced_feature_list)
        node.update(reduced_feature_list=reduced_feature_list_str)
        self.ps.graph.create(node)

    def create_ts_cluster(
        self, iri: str, id_short: str, description: str | None = None
    ):
        cluster_node = TimeseriesClusterNode(
            iri=iri, id_short=id_short, description=description
        )
        self.ps.graph.push(cluster_node)

    def reset_ts_clusters(self):
        self.ps.graph.run(
            f"MATCH (n:{NodeTypes.TIMESERIES_CLUSTER.value}) DETACH DELETE n"
        )

    def add_ts_to_cluster(self, ts_iri: str, cluster_iri: str):
        relationship = Relationship(
            NodeMatcher(self.ps.graph)
            .match(NodeTypes.TIMESERIES_INPUT.value, iri=ts_iri)
            .first(),
            RelationshipTypes.PART_OF_TS_CLUSTER.value,
            NodeMatcher(self.ps.graph)
            .match(NodeTypes.TIMESERIES_CLUSTER.value, iri=cluster_iri)
            .first(),
        )

        self.ps.graph.create(relationship)

    def get_cluster_list_for_asset(self, asset_iri: str) -> List[str]:
        cluster_table = self.ps.graph.run(
            "MATCH p=(a:"
            + NodeTypes.ASSET.value
            + ' {iri: "'
            + asset_iri
            + '"})-[r1:'
            + RelationshipTypes.HAS_TIMESERIES.value
            + "]->(t)-[r2:"
            + RelationshipTypes.PART_OF_TS_CLUSTER.value
            + "]->(c) RETURN c.iri"
        ).to_table()

        cluster_list = [cluster for cluster in cluster_table]

        return cluster_list
