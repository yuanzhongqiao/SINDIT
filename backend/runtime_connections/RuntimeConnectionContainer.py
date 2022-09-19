from typing import Dict, List
from graph_domain.main_digital_twin.RuntimeConnectionNode import (
    RuntimeConnectionNode,
    RuntimeConnectionTypes,
)
from graph_domain.main_digital_twin.TimeseriesNode import (
    TimeseriesNodeDeep,
)
from backend.runtime_connections.RuntimeConnection import RuntimeConnection

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

# Maps node-types to the connection / input classes
RT_CONNECTION_MAPPING = {
    RuntimeConnectionTypes.MQTT.value: MqttRuntimeConnection,
    RuntimeConnectionTypes.OPC_UA.value: OpcuaRuntimeConnection,
}
RT_INPUT_MAPPING = {
    RuntimeConnectionTypes.MQTT.value: MqttTimeseriesInput,
    RuntimeConnectionTypes.OPC_UA.value: OpcuaTimeseriesInput,
}


class RuntimeConnectionContainer:
    """
    Holds and manages all current runtime connection services
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

        RuntimeConnectionContainer.__instance = self

        self.connections: Dict[str, RuntimeConnection] = {}

    def refresh_connection_inputs_and_handlers(
        self, updated_ts_nodes_deep: List[TimeseriesNodeDeep]
    ):
        """Refreshes the inputs and handlers, creating new ones if available in the graph, or deleting old ones.

        Args:
            timeseries_nodes_deep (List[TimeseriesNodeDeep]): _description_
        """
        #
        # Check if ts inputs or connections have been removed:
        #
        updated_connection_iri_list = set(
            [ts_node.runtime_connection.iri for ts_node in updated_ts_nodes_deep]
        )
        updated_ts_input_iri_list = set(
            [ts_node.iri for ts_node in updated_ts_nodes_deep]
        )

        removed_connections = [
            con
            for con in self.connections.values()
            if con.iri not in updated_connection_iri_list
        ]
        for con in removed_connections:
            # Whole connection was removed!
            # Unregister all inputs and the connection
            con.disconnect()
            self.connections.pop(con.iri)
            del con

        removed_inputs = []
        for con in self.connections.values():
            removed_inputs.extend(
                [
                    (ts_input, con)
                    for ts_input in con.timeseries_inputs.values()
                    if ts_input.iri not in updated_ts_input_iri_list
                ]
            )

        ts_input: TimeseriesInput
        con: RuntimeConnection
        for (ts_input, con) in removed_inputs:
            con.remove_ts_input(ts_input.iri)

        #
        # Initialize new ts inputs and connections
        #
        old_ts_connection_iris = [con.iri for con in self.connections.values()]
        old_ts_input_iris = set()
        for con in self.connections.values():
            for ts in con.timeseries_inputs.values():
                old_ts_input_iris.add(ts.iri)

        # Prepare nodes to avoid redundand connections:
        # Get current connection nodes
        # Dict to remove duplicate connections (multiple inputs for one connection each having a different child...)
        new_connection_nodes: Dict[str, RuntimeConnectionNode] = {}
        new_ts_inputs_per_connection: Dict[str, List[TimeseriesInput]] = {}

        ts_node: TimeseriesNodeDeep
        for ts_node in updated_ts_nodes_deep:
            if ts_node.iri in old_ts_input_iris:
                # Node already exists
                continue

            new_connection = False
            if ts_node.runtime_connection.iri not in old_ts_connection_iris:
                # Add the connection node (dict so that it is not created multiple times)
                new_connection_nodes[
                    ts_node.runtime_connection.iri
                ] = ts_node.runtime_connection
                new_connection = True

            # Create the timeseries input
            input_class: TimeseriesInput = RT_INPUT_MAPPING.get(
                ts_node.runtime_connection.type
            )
            ts_input: TimeseriesInput = input_class.from_timeseries_node(ts_node)

            # Add the input to the list of its connection
            ts_inputs_dict = new_ts_inputs_per_connection.get(
                ts_node.runtime_connection.iri
            )

            if ts_inputs_dict is None:
                ts_inputs_dict = dict()

            ts_inputs_dict[ts_input.iri] = ts_input

            new_ts_inputs_per_connection[
                ts_node.runtime_connection.iri
            ] = ts_inputs_dict

            # Get the persistence handler method and activate it
            ts_service: InfluxDbPersistenceService = (
                DatabasePersistenceServiceContainer.instance().get_persistence_service(
                    iri=ts_node.db_connection.iri
                )
            )

            ts_input.register_handler(handler_method=ts_service.write_measurement)

            if not new_connection:
                self.connections.get(ts_node.runtime_connection.iri).timeseries_inputs[
                    ts_node.iri
                ] = ts_input

        # Add new connections
        rt_con_node: RuntimeConnectionNode
        for rt_con_node in new_connection_nodes.values():

            # Create actual connections:
            input_class = RT_CONNECTION_MAPPING.get(rt_con_node.type)

            rt_connection: RuntimeConnection = input_class.from_runtime_connection_node(
                rt_con_node
            )

            self.connections[rt_con_node.iri] = rt_connection

            # Link the inputs to its connections:
            rt_connection.timeseries_inputs = new_ts_inputs_per_connection.get(
                rt_con_node.iri
            )
            # Start the connection

            rt_connection.start_connection()

    def get_runtime_connection(self, iri: str):
        return self.connections.get(iri)

    def register_runtime_connection(self, iri: str, connection: RuntimeConnection):
        self.connections[iri] = connection

    def get_all_inputs(self) -> List[TimeseriesInput]:
        """
        :return: All sensor inputs (both MQTT and OPCUA)
        """
        inputs = []
        con: RuntimeConnection
        for con in self.connections.values():
            inputs.extend(con.timeseries_inputs)

        return inputs

    def get_active_connections_count(self) -> int:

        return len([True for con in self.connections.values() if con.is_active()])
